# StackBooks
What books are mostly discussed by Stack Overflow users? What are the most frequently recommended books in C, Java, Python or R? This project answers these questions by analyzing the entire Stack Overflow data and extracts all books discussed in different tags. The end product is a web site now availabe at: http://stackbooks.us-west-2.elasticbeanstalk.com/.

# Technical Aspecs
## The Stack Overflow Data
All posts (more than 38 million) and tags hosted on Stack Overflow have been downloaded from Stack Overflow data dump at: https://archive.org/details/stackexchange. The data is around 60Gb in xml format. Apparently, files of this size cannot be loaded into memory for most machines. Storing and querying this data in a **SQL database** will greatly facilitate analysis. **SQLite** is used here to store and index the data which takes disk space ~100Gb. The script can be found at: https://github.com/nickytong/stackbooks/blob/master/misc/load.py 

## Find Book Mentions
Presumably, named-entity recognition (NER) is needed to extract all books mentioned in the posts. However, we are not just interested in the book names. We also want exact book title, authors, ISBN, cover image and summary to be displayed on the web so that users may have an urge to buy the books. There are tools to find book information given ISBN number such as the Google Books API or we can directly crawl the data from Amazon website. The core is to find book ISBN as the unique book ID. Conveniently enough, Stack Overflow has structured web link encoding ISBN for the books such as http://rads.stackoverflow.com/amzn/click/1598631128 where 1598631128 is the ISBN number. So we can easily extract posts containing books and ISBN value using following **SQL** command: 
```
CREATE TABLE book_posts AS SELECT * FROM Posts WHERE Body LIKE '%http://rads.stackoverflow.com%';
```
This gives us around 16k posts easily handled in memory which greatly facilitate further analysis.

## A Book-By-Tag Count Matrix
I use **Python Pandas** to extract a Book-By-Tag count matrix storing how many posts are there given a book and a Stack Overflow tag. It turns out this matrix is very sparse with lots of zeros. I convert it into the long format (rows representing book, tag, and number of mentions) and remove the zero counts. It is then stored into SQLite serving as the core table enpowering the StackBooks website. Data exploration using Jupyter notebooks can be found at:  
http://htmlpreview.github.com/?https://github.com/nickytong/stackbooks/blob/master/misc/DataQuery.html 

## Extract Book Information
At this stage, we are able to show users how many posts a books is mentioned overall or in a given tag. But it is pretty abstract without detailed book information. I first try to use the **Google Books API** (wrapped into the isbntools module) to download the book information (code at: https://github.com/nickytong/stackbooks/blob/master/misc/book_misc.py). The script first makes a SQL query about whether the book title is already extracted. If not, it make a Google API requests and insert the book information into SQLite database on the fly. I use the Google API cautiously without making too many requests based on my prior experience on Google GPS api which enforces strict rate limiting rules. Still, after a whole night, I only obtain less than 200 records before receiving request failure. 

I have to resort to a formal web crawling procedure to extract book information from Amazon.com. I choose **Scrapy** since it is rather flexible. Amazon is also very aggressive in protecting itself from data crawling. So I have planned to use rotating proxies and the selenium webdriver mimicking real user behavior rather a cold robot. Things turns out easier than I expected. After setting the browser agent, I quickly scraped the book information I need. Code can be found at: https://github.com/nickytong/stackbooks/tree/master/misc/amazon_book

## Build the Website
This time I use the **Flask framework** to build the website due to its lightweight and easy to use. **Bootstrap** is used as the front end framework. **NVD3/D3** is used to generate a bar chart showing number of posts mentioning a given book. For the server side, I make SQL queries to extract information and send to the Jinja templates for rendering. 

## Deploy Website
After satisfied with the local view of the StackBooks website, I use the **Elastic Beanstalk** to deploy the site on a free tier Amazon machine. 

## Special Thanks
This project is motivated by Vlad Wetzel who has developed http://dev-books.com/ which for the first time presents recommended books on Stack Overflow. After reading his posts that his analysis of the Stack Overflow book mentioning data received very positive feedback from users and even generated thousands of dollars in the first month it was published, I told myself I can do this myself. Although the StackBooks is deployed for the world to view, I have no attention to compete with Vlad Wetzel's site and only use this project to learn and showcase my skills.

Further, this project is impossible without Stack Overflow providing its data in such an open manner.



 



