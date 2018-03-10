# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import pdb
import sqlite3
import os
import pandas as pd
from urllib.parse import urljoin
from time import sleep
from random import randint
import logging
from datetime import datetime

logging.basicConfig(filename='book_info_spider.log', format='%(asctime)s %(levelname)s %(message)s')

#logger = logging.getLogger('logs/book_info_%s.log' %(datetime.now()) )

def isbn_10digit(isbn):
    # 9-digit ISBN not searchable, add x
    if(len(isbn)==9):
        isbn = isbn+'x'
    return isbn

def isbn_remove_x(isbn):
    # for inserting purpose
    return isbn.replace('x', '')

class BookInfoSpider(scrapy.Spider):
    name = 'book_info'
    allowed_domains = ['amazon.com']
    #start_urls = []

    def __init__(self):
        self.urls_seen = set() # urls such as: http://www.xianlvke.com/loc/564/ 
        conn = sqlite3.connect('../../so_production.db')
        df_book_info = pd.read_sql_query("select * from book_info;", conn)
        isbn_pool = df_book_info[df_book_info.Title=='nan'].ISBN
        #pdb.set_trace()
        url_pool = isbn_pool.apply(lambda x: urljoin('https://www.amazon.com/dp/', isbn_10digit(x))).tolist()
        start_urls = url_pool # set start_urls here
        self.cursor = conn
        # set start urls in init
        self.start_urls  = start_urls
        super(BookInfoSpider, self).__init__()
        #pdb.set_trace()
        logging.info('Spider url initialized with N=%d' % (len(start_urls)))

    def parse(self, response):
        sleep(randint(1, 5))
        #pdb.set_trace()
        # f= open('test_scrapy_amazon.html', 'wb')
        # f.write(response.body)
        mysel = Selector(response)
        myisbn = response.url.split('/')[-1]
        try:
            Title = mysel.xpath('//span[@id="productTitle"]/text()').extract()[0]
        except:
            Title = 'nan'
        try:
            Authors = ','.join(mysel.xpath('//a[@class="a-link-normal contributorNameID"]/text()').extract())
        except:
            Authors = 'nan'
        try:
            ISBN13 = mysel.xpath('//span[@class="a-size-base a-color-base"]/text()').extract()[0]
        except:
            ISBN13 = 'nan'
        try:
            Description = mysel.xpath('//noscript/div/text()').extract()[3000]
        except:
            Description = 'nan'
        #pdb.set_trace()
        if Title != 'nan':
            try: 
                self.cursor.execute('update book_info set Title=:title, Authors=:authors, ISBN13=:isbn13, Description=:description where ISBN=:isbn;',
                    {
                        'title': Title,
                        'authors': Authors,
                        'isbn13': ISBN13,                    
                        'description': Description,                    
                        'isbn': isbn_remove_x(myisbn),                    
                    }
                )
                #conn.execute('select * from book_info where ISBN="0131177052"').fetchall()
                self.cursor.commit()
                #pdb.set_trace()
                #print('>>%s meta downloaded!' % (myisbn))
                logging.info('>>%s meta inserted!' % (myisbn))
            except Exception as e:
                print('%s failed insert: %s' %(response.url, e) )
                logging.info('%s failed: %s' %(response.url, e) )
        else:
            logging.info('>>%s empty title extracted, skipping insert!' % (myisbn))