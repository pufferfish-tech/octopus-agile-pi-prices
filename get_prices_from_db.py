import sqlite3
from datetime import datetime, date
import pytz
import time
from urllib.request import pathname2url
import sys

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_prices_from_db(file, num_entries):
    try:
        # connect to the database in rw mode so we can catch the error if it doesn't exist
        DB_URI = 'file:{}?mode=rw'.format(pathname2url(file))
        conn = sqlite3.connect(DB_URI, uri=True)
        conn.row_factory = dict_factory
        cur = conn.cursor()
        print('Connected to database...')
    except sqlite3.OperationalError as error:
        # handle missing database case
        raise SystemExit('Database not found - you need to run store_prices.py first.') from error


    current_time = time.time()
    current_time -= current_time % (30 * 60) # round down to nearest 30m
    formatted_date = datetime.strftime(datetime.utcfromtimestamp(current_time), "%Y-%m-%d %H:%M:%S")
    
    # select next 24h from db where record >= the above
    cur.execute("SELECT * FROM prices WHERE valid_from>=? ORDER BY valid_from ASC LIMIT ?", (formatted_date, num_entries))

    rows = cur.fetchall()

    return rows

if __name__ == '__main__':
    prices = get_prices_from_db(48)
    print(prices)
else:
    sys.modules[__name__] = get_prices_from_db
