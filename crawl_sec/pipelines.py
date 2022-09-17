# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import logging
import psycopg2
import os
import re
import asyncio

# DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_URL = "host='localhost' dbname='postgres' user='postgres' password='hoang'"

class CrawlSecPipeline:

    def check_url(self, url):
        if not url:
            return False
        self.cursor.execute(
            '''
                SELECT COUNT(url) FROM articles WHERE url = %s
            ''',
            (url,)
        )
        num_row = self.cursor.fetchone()[0]
        if num_row == 0:
            self.cursor.execute(
                '''
                    SELECT COUNT(url) FROM articles
                '''
            )
            num_all_row = self.cursor.fetchone()[0]
            if num_all_row >= 10000:
                # if table have 10000 rows => delete first 5000 rows
                self.cursor.execute(
                    '''
                        DELETE FROM articles ORDER BY ctid LIMIT 5000
                    '''
                )
                logging.info('Table too large, deleted first 5000 rows!!!')
        # return num_row == 0
        return True

    def process_item(self, item, spider):
        # return item
        title = item.get('title', '')
        url = item.get('url', '')
        date = item.get('date', '')
        # Check if this thread alr existed in database
        if self.check_url(url):
            # Save thread in database
            self.cursor.execute(
                '''
                    INSERT INTO articles (
                        title, url, date
                    ) VALUES (%s,%s,%s)
                ''',
                (title, url, date)
            )
            self.connection.commit()

            # Extract relevant lines
            
            # Contruct message
            msg = f"CẢNH BÁO itsecurityguru.org!!!\n\nTiêu đề: {title}\nNgày đăng: {date}\nURL: {url}"
            
            # Send message to client
            logging.info('Saved thread successfully!')
            asyncio.get_event_loop().run_until_complete(spider.bot.send_message(chat_id=spider.chat_id, text=msg))
            logging.info('Sent to telegram successfully!')
        else:
            logging.error('Existed in database!')

    def open_spider(self, spider):
        # Connect to database
        # self.connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.connection = psycopg2.connect(DATABASE_URL)
        self.cursor = self.connection.cursor()
        # Try to create table for articles
        try:
            self.cursor.execute( '''
                CREATE TABLE articles(
                    title varchar,
                    url varchar,
                    date varchar
                )
            ''' )
        except psycopg2.Error:
            pass
        self.connection.commit()
        logging.info('Connected to database!')

    def close_spider(self, spider):
        # Disconnect from database
        self.cursor.close()
        self.connection.close()
        logging.info('Disconnected from database!')