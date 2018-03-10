# cd /projects/ptong1/Data/SO
# use py27; py3 gives error for UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe2 in position
# module load python/2.7.2
## bash
## source activate nnet


import sqlite3
import os
import xml.etree.cElementTree as etree
import logging
import pdb

# failed: Error: database or disk is full
# CREATE INDEX ixPostBody on Posts (Body);
# within sqlite CLI, PRAGMA temp_store_directory = '/projects/ptong1/Data/SO'; this fixed it and db goes from 50G to 102G
# CREATE TABLE rads_posts AS SELECT * FROM Posts WHERE Body LIKE '%http://rads.stackoverflow.com%';
# http://covers.openlibrary.org/b/isbn/0131177052-L.jpg
# 
# copy table to production db
# sqlite3 so_dump_posts_tags.db ".dump tab_book_tag_long" | sqlite3 new.db

SCHEME_DICTS = {
    'Tags': {
        'Id':'INTEGER',
        'TagName':'TEXT',
        'Count':'INTEGER',
        'ExcerptPostId':'INTEGER',
        'WikiPostId':'INTEGER',
    },
    'Posts': {
        'Id':'INTEGER', 
        'PostTypeId':'INTEGER', # 1: Question, 2: Answer
        'AcceptedAnswerId':'INTEGER', # (only present if PostTypeId is 1)
        'ParentID':'INTEGER', # (only present if PostTypeId is 2)
        'CreationDate':'DATETIME',
        'DeletionDate':'DATETIME',
        'Score':'INTEGER',
        'ViewCount':'INTEGER',
        'Body':'TEXT',
        'OwnerUserId':'INTEGER', # (present only if user has not been deleted) 
        'OwnerDisplayName':'TEXT', # (present only if user has not been deleted) 
        'LastEditorUserId':'INTEGER',
        'LastEditorDisplayName':'TEXT', #="Rich B" 
        'LastEditDate':'DATETIME', #="2009-03-05T22:28:34.823" 
        'LastActivityDate':'DATETIME', #="2009-03-11T12:51:01.480" 
        'Title':'TEXT',
        'Tags':'TEXT',
        'AnswerCount':'INTEGER',
        'CommentCount':'INTEGER',
        'FavoriteCount':'INTEGER',
        'ClosedDate':'DATETIME',
        'CommunityOwnedDate':'DATETIME', #(present only if post is community wikied)
    },
}

def dump_files(file_names, anathomy, 
                dump_path='/projects/ptong1/Data/SO', 
                dump_database_name = 'so_dump_posts_tags.db',
                create_query='CREATE TABLE IF NOT EXISTS [{table}]({fields})',
                insert_query='INSERT INTO {table} ({columns}) VALUES ({values})',
                log_filename='so_parser.log'):

    logging.basicConfig(filename=os.path.join(dump_path, log_filename),level=logging.INFO)
    db = sqlite3.connect(os.path.join(dump_path, dump_database_name))

    for file in file_names:
        print("Opening {0}.xml".format(file))
        with open(os.path.join(dump_path, file + '.xml'), 'r') as xml_file:
            tree = etree.iterparse(xml_file)
            table_name = file
            # anathomy key order may be different from the actual xml; this is ok since insert is by key, not by order;
            sql_create = create_query.format(
                                table=table_name, 
                                fields=", ".join(['{0} {1}'.format(name, type) for name, type in anathomy[table_name].items()]))
            print('Creating table {0}'.format(table_name))

            try:
                logging.info(sql_create)
                db.execute(sql_create)
            except Exception as e:
                logging.warning(e)

            for events, row in tree:
                #pdb.set_trace()
                try:
                    logging.debug(row.attrib.keys())
                    cmd = insert_query.format(
                                table=table_name, 
                                columns=', '.join(row.attrib.keys()), 
                                values=('?, ' * len(row.attrib.keys()))[:-2])
                    #pdb.set_trace()
                    if(len(row.attrib.values())>0):
                        db.execute(cmd, tuple(row.attrib.values()))
                    #print(".")
                except Exception as e:
                    logging.warning(e)
                    print('Exception %s for: %s' %(e, str(row.attrib.values())) )
                finally:
                    row.clear()
            print("Committing change into table %s\n" %(table_name))
            db.commit()
            del(tree)

dump_files(SCHEME_DICTS.keys(), SCHEME_DICTS)