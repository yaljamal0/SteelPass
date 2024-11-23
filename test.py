import sqlite3
def createDB():
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            username TEXT,
            password TEXT,
            color TEXT
        )
    ''')
    conn.commit()
    conn.close()

# get all entries from table
def getEntries():
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('SELECT * FROM entries')
    entries = c.fetchall()
    conn.close()
    return entries

#print(getEntries())

# add entry to table
def addEntry(title, username, password, color):
    conn = sqlite3.connect('entries.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO entries (title, username, password, color)
        VALUES (?, ?, ?, ?)
    ''', (title, username, password, color))
    conn.commit()
    conn.close()

createDB()
addEntry('Facebook', 'cmu_student', 'goodpassword', 'blue')