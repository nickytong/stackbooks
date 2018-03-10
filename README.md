# StackBooks
What books are mostly discussed by Stack Overflow users? What are the most frequently recommended books in C, Java, Python or R? This project answers these questions by analyzing the entire Stack Overflow data and extracts all books discussed in different tags. The end product is a web site now availabe at: http://stackbooks.us-west-2.elasticbeanstalk.com/.

# Technical Aspecs
## The Stack Overflow Data
All posts (more than 38 million) and tags hosted on Stack Overflow have been downloaded from Stack Overflow data dump at: https://archive.org/details/stackexchange. The data is around 60Gb in xml format. Apparently, files of this size cannot be loaded into memory for most machines. Storing and querying this data in a SQL database will greatly facilitate analysis. SQLite is used here to store and index the data which takes disk space ~100Gb. The script can be found at: https://github.com/nickytong/stackbooks/blob/master/misc/load.py 

## Find Book Mentions
Presumably, named-entity recognition (NER) is needed to extract all books mentioned in the posts. However, we are not just interested in the book names. We also want exact book title, authors, ISBN, cover image and summary to be displayed on the web so that users may have an urge to buy the books. There are tools to find book information given ISBN number such as the Google Books API or we can directly crawl the data from Amazon website. The core is to find book ISBN as the unique book ID. Conveniently enough, Stack Overflow has structured web link encoding ISBN for the books such as http://rads.stackoverflow.com/amzn/click/1598631128 where 1598631128 is the ISBN number. So we can easily extract posts containing books and ISBN value using following SQL command: 
```
CREATE TABLE book_posts AS SELECT * FROM Posts WHERE Body LIKE '%http://rads.stackoverflow.com%';
```
This gives us around 16k posts easily handled in memory which greatly facilitate further analysis.

## A Book-By-Tag Count Matrix
I use Python Pandas to extract a Book-By-Tag count matrix storing how many posts are there given a book and a Stack Overflow tag. It turns out this matrix is very sparse with lots of zeros. I convert it into the long format (rows representing book, tag, and number of mentions) and remove the zero counts. It is then stored into SQLite serving as the core table enpowering the StackBooks website.

## Extract Book Information
At this stage, we are able to extrac





