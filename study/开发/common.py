import sqlite3
import os

(日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8) = range(16)

# 创建或打开数据库
def create_or_open_db(db_file):
    print(db_file)
    print(os.getcwd())
    db_is_new = not os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    if db_is_new:
        print('Creating schema')
        sql = '''create table if not exists 深渊统计(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        日期 DATE,
        图 TEXT,
        角色 TEXT,
        深渊次数 INTEGER,
        爆货次数 INTEGER,
        灵魂爆数 INTEGER,
        加百利次数 INTEGER,
        晶石 INTEGER,
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
