import sqlite3
conn = sqlite3.connect('C:/Users/lx/Desktop/前期准备/清洗数据/youyang_zazu.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for row in cursor.fetchall():
    print(row[0])
conn.close()
