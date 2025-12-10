import sqlite3

conn = sqlite3.connect(r'C:\Users\rafam\Desktop\IC_GNSS\data\example.db')



cursor = conn.cursor()

cursor.execute('''
        CREATE TABLE stocks (
            date TEXT,
            trans TEXT,
            symbol TEXT,
            qty REAL,
            price REAL
        )
    ''')

cursor.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
dados = cursor.execute("SELECT * FROM stocks")
print(dados.fetchall())
conn.commit()