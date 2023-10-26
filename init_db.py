import sqlite3
connection = sqlite3.connect('visitka.db')

with open('schema.sql') as f:
    connection.executescript(f.read())
cur = connection.cursor()
cur.execute("INSERT INTO services (title, txt) VALUES (?,?)", ("Услуги по гражданскому праву", 'Описание 1'))
cur.execute("INSERT INTO services (title, txt) VALUES (?,?)", ("Услуги по уголовному праву", 'Описание 2'))
connection.commit()
connection.close()