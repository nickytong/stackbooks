from flask import Flask, render_template, redirect, \
    url_for, request, session, flash, g, jsonify
from functools import wraps
import sqlite3
import pdb
import json

# Initialize the Flask application
application = Flask(__name__)

# config
#application.secret_key = 'my precious'
application.database = 'so_production.db'

fig_maxbook = 10

def format_desc(desc):
    res = desc if desc is not None else ''
    res = '' if res== 'nan' else res
    return res

# Define a route for the default URL, which loads the form
@application.route('/')
def home():
    g.db = connect_db()
    #cur = g.db.execute('select * from tab_book_tag_long order by mentioned desc;')
    # select *, SUM(mentioned) as M from tab_master group by ISBN order by M desc limit 10
    cur = g.db.execute('select *, SUM(mentioned) as M, group_concat(tag) as tag_csv from tab_master group by ISBN order by M desc limit 50;')
    # index     variable    value
    fetr = cur.fetchall()
    books = [dict(isbn=row[1], tag=row[16], count=row[15], title=row[6], authors=row[7], desc=format_desc(row[11])) for row in fetr]
    ss = fig_maxbook if len(books)>fig_maxbook else len(books)
    dataj =[ { 'key': 'keyname', 'values': books[:ss] } ]
    g.db.close()
    catgs = [ x[0] for x in get_categories() ]
    #pdb.set_trace()
    return render_template('index.html', books=books, dataj=dataj, tag='all posts', catgs=catgs)

@application.route('/tag/<tag>')
def tag_view(tag):
    g.db = connect_db()
    cur = g.db.execute('select * from tab_master where tag=:tag order by mentioned desc limit 50;', {'tag': tag}) 
    fetr = cur.fetchall()
    # index     variable    value
    books = [dict(isbn=row[1], tag=row[2], count=row[3], title=row[6], authors=row[7], desc=format_desc(row[11])) for row in fetr]
    ss = fig_maxbook if len(books)>fig_maxbook else len(books)
    dataj =[ { 'key': 'keyname', 'values': books[:ss] } ]
    g.db.close()
    catgs = [ x[0] for x in get_categories() ]
    #pdb.set_trace()
    return render_template('index.html', books=books, dataj=dataj, tag=tag, catgs=catgs)

@application.route('/about')
def about():
    catgs = [ x[0] for x in get_categories() ]
    return render_template('about.html', catgs=catgs)

@application.route('/contact')
def contact():
    catgs = [ x[0] for x in get_categories() ]
    return render_template('contact.html', catgs=catgs)
# testing
# with application.test_request_context():
#     pdb.set_trace()

# connect to database
def connect_db():
    return sqlite3.connect(application.database)

def get_categories():
    g.db = connect_db()
    cur = g.db.execute('select tag from tab_by_tag limit 50;') 
    fetr = cur.fetchall()
    g.db.close()
    return fetr

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)