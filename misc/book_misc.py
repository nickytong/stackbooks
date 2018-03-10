# py27 on home PC since isbntools not work with py36-win
# extract description and meta of the books using isbntools

from isbntools.app import meta, desc, to_isbn13, cover
import pandas as pd
import numpy as np
import sqlite3
import pdb
from time import sleep
from random import randint
import os

conn = sqlite3.connect('../so_production.db')
tab_by_book = pd.read_sql_query("select * from tab_by_book;", conn)

book_info = pd.DataFrame(index=tab_by_book.ISBN, columns=[ 'Title', 'Authors', 'Year', 'ISBN13', 'Publisher', 'Description', 'Cover'], dtype=object)
book_info = book_info.astype('str')
book_info.reset_index(inplace=True)
try:
    book_info.to_sql("book_info", conn, if_exists="fail")
except:
    print('book_info table already exist in db!')

mytime = 3
for index, row in book_info.iterrows():
    progr = '%d/%d: ' % (index, book_info.shape[0])
    myisbn = row['ISBN']
    # 9-digit is invalid: how SO get these?
    if(len(myisbn)==9):
        myisbn1 = myisbn+'x'
        print('>>invalid ISBN: %s shifted to: %s' % (myisbn, myisbn1))
    else:
        myisbn1 = myisbn
    cur = conn.execute("select Title from book_info where ISBN='%s';" %(myisbn) )
    tpr = cur.fetchall()
    #pdb.set_trace()
    if tpr[0][0]!='nan':
        print('>>%s%s already in DB, skipping!' % (progr, myisbn))
    else:
        try:
            # if index==3:
            #     pdb.set_trace()
            bookinfo = meta(myisbn1)
            descp = desc(myisbn1)
            aut = ', '.join(bookinfo['Authors'])
            #pdb.set_trace()
            conn.execute('update book_info set Title=:title, Authors=:authors, Year=:year, ISBN13=:isbn13, Publisher=:publisher, Description=:description where ISBN=:isbn;',
                {
                    'title': bookinfo['Title'],
                    'authors': aut,
                    'year': bookinfo['Year'],
                    'isbn13': bookinfo['ISBN-13'],                    
                    'publisher': bookinfo['Publisher'],                    
                    'description': descp,                    
                    'isbn': myisbn,                    
                }
            )
            #conn.execute('select * from book_info where ISBN="0131177052"').fetchall()
            conn.commit()
            print('>>%s%s meta downloaded!' % (progr, myisbn))
            sleep(randint(30, 60))
            #pdb.set_trace()
        except Exception as e:
            mytime += randint(30, 60)
            if mytime>90:
                mytime=10
            print('\t%s<--%s failed: %s-->! Sleep %d secs...' % (progr, myisbn, e, mytime))
            sleep(mytime)
#
# create left join table in sqlite:
# create table tab_book_tag_long_wtinfo as select * from tab_book_tag_long left join book_info where tab_book_tag_long.ISBN=book_info.ISBN;
#
### debug
index = 0
row = book_info.iloc[index, :]
myisbn = row['ISBN']
myisbn = "020161622"
myisbn = "0321344758"
bookinfo = meta(myisbn)
descp = desc(myisbn)
aut = ', '.join(bookinfo['Authors'])
#http://rads.stackoverflow.com/amzn/click/020161622x

## request on amazon works with header!
# https://www.scrapehero.com/tutorial-how-to-scrape-amazon-product-details-using-python/
# headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
# r  = requests.get("https://www.amazon.com/dp/0131177052", headers=headers)

# with open('test_request_amazon.html', 'wb') as f:
#     f.write(r.content)
# scrapy shell "https://www.amazon.com/dp/0131177052"