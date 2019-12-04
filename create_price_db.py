# sets up the db; run this script once. ever.

import sqlite3

conn = sqlite3.connect('octoprice.sqlite')

cursor = conn.cursor()
# price data is split into half hour buckets;  so 5am is hour = 5, segment = 0, 
# and 5:30 would be hour = 5, segment = 1

cursor.execute('CREATE TABLE prices (year INTEGER, month INTEGER, day INTEGER, hour INTEGER, segment INTEGER, price REAL)')
conn.commit()
conn.close()

