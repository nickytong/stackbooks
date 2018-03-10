# py36
# this needs to run at home PC, otherwise, VPN will give different http response and try/except will not work
# 
import sqlite3
import pandas as pd
from urllib.request import urlretrieve, urlopen
from time import sleep
from random import randint
import os

conn_production = sqlite3.connect('../so_production.db')
tab_by_book = pd.read_sql_query("select * from tab_by_book;", conn_production)


isbns = tab_by_book.ISBN.tolist()


for i in range(len(isbns)):
	myisbn = isbns[i]
	progr = '%d/%d: ' % (i, len(isbns))
	cover_url = "http://dev-books.com/img/ol/jpeg/%s.jpeg" % (myisbn)
	cover_path = '../static/images/%s.jpg' % (myisbn)
	if not os.path.isfile(cover_path):
		try:
		    response_open = urlopen(cover_url) # error may occur if cover not present, so we will not get empty figure
		    outpath, resp = urlretrieve(cover_url, cover_path)
		    print('>>%s%s downloaded!' % (progr, outpath))
		    sleep(randint(0, 100)/50)
		except Exception as e:
		    print('\t%s<--%s failed-->!' % (progr, myisbn))
	else:
		print('>>>>%s%s exist, skipping!' % (progr, myisbn))


