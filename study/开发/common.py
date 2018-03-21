import sqlite3
import os
TIME = 1
NAME = 2  # mingzi
DITU = 3  #
PIAOSHU = 4
CISHU = 5
SS1 = 6
SS2 = 7
SS3 = 8
SS4 = 9
SS5 = 10
SS6 = 11
SS7 = 12
SS8 = 13
JIANBAILI = 14
GOUYAN = 15
JINGSHI = 16

FILEPATH = "./record.db"


# 创建或打开数据库
def create_or_open_db(db_file):
    db_is_new = not os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    if db_is_new:
        print('Creating schema')
        sql = '''create table if not exists record(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TIME DATE,
        NAME TEXT,
        DITU TEXT,
        PIAOSHU INTEGER,
        CISHU INTEGER,
        SS1 TEXT,
        SS2 TEXT,
        SS3 TEXT,
        SS4 TEXT,
        SS5 TEXT,
        SS6 TEXT,
        SS7 TEXT,
        SS8 TEXT);'''
        conn.execute(sql) # shortcut for conn.cursor().execute(sql)

        sql_d = """
         create table if not exists pic(
         ID INTEGER PRIMARY KEY AUTOINCREMENT,
         NAME TEXT,
         DID INTEGER,
         PIC BLOB
         );
        """
    else:
        print('Schema exists\n')
    return conn
