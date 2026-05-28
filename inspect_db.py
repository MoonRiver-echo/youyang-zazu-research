import sqlite3
conn = sqlite3.connect('C:/Users/lx/Desktop/前期准备/清洗数据/youyang_zazu.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])
for table in tables:
    tname = table[0]
    cursor.execute(f'PRAGMA table_info({tname})')
    cols = cursor.fetchall()
    print(f'\nTable: {tname}')
    for col in cols:
        print(f'  {col[1]} ({col[2]})')
    cursor.execute(f'SELECT COUNT(*) FROM {tname}')
    count = cursor.fetchone()[0]
    print(f'  Rows: {count}')
conn.close()
