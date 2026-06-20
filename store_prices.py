#!/usr/bin/env python3
# this is the one to run daily just after 4pm ish when the new prices come in
"""Use the public Octopus Energy API to request the half-hourly rates for the Agile tariff
for a particular region, and insert these into an SQLite database, dealing with duplicate
requests and pruning old data so that the DB doesn't grow infinitely."""

import sqlite3
import argparse
import time
from argparse import RawTextHelpFormatter
from reprlib import Repr
from datetime import datetime
from urllib.request import pathname2url

import requests

# Octopus periodically retires the current Agile product and replaces it with a new
# one (e.g. AGILE-FLEX-22-11-25 -> AGILE-24-10-01). A hardcoded date string here goes
# stale whenever that happens - the script then silently stops getting new prices,
# which is exactly what broke this setup. So by default we look the current product
# code up from the API instead, and only use a hardcoded one if --tariff-type is given.
PRODUCTS_URI = 'https://api.octopus.energy/v1/products/?is_variable=true&is_business=false'
AGILE_TARIFF_FORMAT = (
    'https://api.octopus.energy/v1/products/{product}/electricity-tariffs/'
    'E-1R-{product}-{region}/standard-unit-rates/')

MAX_RETRIES = 15  # give up once we've tried this many times to get the prices from the API


def get_prices_from_api(request_uri: str) -> dict:
    """using the provided URI, request data from the Octopus API and return a JSON object.
    Try to handle errors gracefully with retries when appropriate."""
    print('Requesting data from Octopus API: ' + request_uri)
    retry_count = 0
    my_repr = Repr()
    my_repr.maxstring = 80  # let's avoid truncating our error messages too much

    while retry_count <= MAX_RETRIES:
        if retry_count == MAX_RETRIES:
            raise SystemExit('API retry limit exceeded.')
        try:
            success = False
            response = requests.get(request_uri, timeout=5)
            response.raise_for_status()
            if response.status_code // 100 == 2:
                success = True
                return response.json()
        except requests.exceptions.HTTPError as error:
            print('API HTTP error ' + str(response.status_code) +
                  ', retrying in ' + str(2 ** retry_count) + 's')
            time.sleep(2 ** retry_count)
            retry_count += 1
        except requests.exceptions.ConnectionError as error:
            print('API connection error: ' + my_repr.repr(str(error)) +
                  ', retrying in ' + str(2 ** retry_count) + 's')
            time.sleep(2 ** retry_count)
            retry_count += 1
        except requests.exceptions.Timeout:
            print('API request timeout, retrying in ' + str(2 ** retry_count) + 's')
            time.sleep(2 ** retry_count)
            retry_count += 1
        except requests.exceptions.RequestException as error:
            raise SystemExit('API Request error: ' + str(error)) from error

        if success:
            print('API request successful, status ' + str(response.status_code) + '.')
            break


def get_current_agile_product_code() -> str:
    """Find the currently active domestic Agile import product code by asking the API,
    rather than trusting a hardcoded date string that Octopus eventually retires."""
    candidates = []
    url = PRODUCTS_URI
    while url:
        data = get_prices_from_api(url)
        for product in data['results']:
            code = product['code']
            # Domestic Agile import products are named AGILE-<version>, e.g. AGILE-24-10-01.
            # Exclude variants like AGILE-OUTGOING (export tariff) and anything retired
            # (available_to set means it's no longer current).
            if code.startswith('AGILE-') and 'OUTGOING' not in code and product.get('available_to') is None:
                candidates.append(product)
        url = data.get('next')

    if not candidates:
        raise SystemExit(
            'Could not find a currently active Agile product on the Octopus API. '
            'They may have renamed or restructured it again - check '
            'https://api.octopus.energy/v1/products/ manually and pass --tariff-type to override.')

    # If more than one matches, take the most recently published.
    candidates.sort(key=lambda p: p['available_from'], reverse=True)
    chosen = candidates[0]['code']
    print('Auto-detected current Agile product: ' + chosen)
    return chosen


def insert_data(data: dict):
    """Insert our data records one by one, keep track of how many were successfully inserted
    and print the results of the insertion."""
    num_prices_inserted = 0
    num_duplicates = 0
    for result in data['results']:
        # do messy pufferfish data mangling to prevent rewriting the inky display code
        mom_price = result['value_inc_vat']
        raw_from = result['valid_from']

        # work out the buckets
        date = datetime.strptime(raw_from, "%Y-%m-%dT%H:%M:%SZ")
        mom_year = date.year
        mom_month = date.month
        mom_day = date.day
        mom_hour = date.hour
        if date.minute == 0:
            mom_offset = 0
        else:
            mom_offset = 1  # half hour

        if insert_record(mom_year, mom_month, mom_day, mom_hour, mom_offset, mom_price, result['valid_from']):
            num_prices_inserted += 1
        else:
            num_duplicates += 1

    if num_duplicates > 0:
        print('Ignoring ' + str(num_duplicates) + ' duplicate prices...')
    if num_prices_inserted > 0:
        lastslot = datetime.strftime(
            datetime.strptime(data['results'][0]['valid_to'], "%Y-%m-%dT%H:%M:%SZ"), "%H:%M on %A %d %b")
        print(str(num_prices_inserted) + ' prices were inserted, ending at ' + lastslot + '.')
    else:
        print('No prices were inserted - maybe we have them already or octopus are late with their update.')


def insert_record(year: int, month: int, day: int, hour: int, segment: int, price: float, valid_from: str) -> bool:
    """Assuming we still have a cursor, take a tuple and stick it into the database.
    Return False if it was a duplicate record (not inserted) and True if a record
    was successfully inserted."""
    if not cursor:
        raise SystemExit('Database connection lost!')

    valid_from_formatted = datetime.strftime(
        datetime.strptime(valid_from, "%Y-%m-%dT%H:%M:%SZ"), "%Y-%m-%d %H:%M:%S")
    data_tuple = (year, month, day, hour, segment, price, valid_from_formatted)
    try:
        cursor.execute("INSERT INTO 'prices' "
                       "('year', 'month', 'day', 'hour', 'segment', 'price', 'valid_from')"
                       "VALUES (?, ?, ?, ?, ?, ?, ?);", data_tuple)
    except sqlite3.Error as error:
        # ignore expected UNIQUE constraint errors when trying to duplicate prices
        if str.find(str(error), 'UNIQUE') == -1:
            raise SystemExit('Database error: ' + str(error)) from error
        return False  # it was a duplicate record and wasn't inserted
    else:
        return True  # the record was inserted


def remove_old_prices(age: str):
    """Delete old prices from the database, we don't want to display those and we don't want it
    to grow too big. 'age' must be a string that SQLite understands"""
    if not cursor:
        raise SystemExit('Database connection lost before pruning prices!')
    try:
        cursor.execute("SELECT COUNT(*) FROM prices "
                       "WHERE valid_from < datetime('now', '-" + age + "')")
        selected_rows = cursor.fetchall()
        num_old_rows = selected_rows[0][0]
        if num_old_rows > 0:
            cursor.execute("DELETE FROM prices WHERE valid_from < datetime('now', '-" + age + "')")
            print(str(num_old_rows) + ' unneeded prices from the past were deleted.')
        else:
            print('There were no old prices to delete.')
    except sqlite3.Error as error:
        print('Failed while trying to remove old prices from database: ', error)


# let's get the region from the command line and make sure it's allowed!
parser = argparse.ArgumentParser(description=('Retrieve Octopus Agile prices'
                                               'and store in a SQLite database'),
                                  formatter_class=RawTextHelpFormatter)
parser.add_argument('--region', '-r', nargs=1, type=str, metavar='X', action='store', required=True,
                     help="""
https://en.wikipedia.org/wiki/Distribution_network_operator
A = East England
B = East Midlands
C = London
D = North Wales, Merseyside and Cheshire
E = West Midlands
F = North East England
G = North West England
P = North Scotland
N = South and Central Scotland
J = South East England
H = Southern England
K = South Wales
L = South West England
M = Yorkshire""",
                     choices=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'P', 'N', 'J', 'H', 'K', 'L', 'M'])
parser.add_argument('--tariff-type', '-t', nargs=1, type=str, dest='tariff', action='store', required=False,
                     help="""
Optional manual override, e.g. "24-10-01". If omitted (recommended), the current
Agile product code is looked up automatically from the Octopus API, since Octopus
periodically retires old product codes and a hardcoded value here will silently
stop returning new prices when that happens - which is what broke this setup.
""")
args = parser.parse_args()

print('Selected region ' + args.region[0])

if args.tariff:
    product_code = 'AGILE-' + args.tariff[0]
    print('Using manually specified tariff: ' + product_code)
else:
    product_code = get_current_agile_product_code()

# Build the API for the request - public API so no authentication required
AGILE_TARIFF_URI = AGILE_TARIFF_FORMAT.format(product=product_code, region=args.region[0])
data_rows = get_prices_from_api(AGILE_TARIFF_URI)

try:
    # connect to the database in rw mode so we can catch the error if it doesn't exist
    DB_URI = 'file:{}?mode=rw'.format(pathname2url('agileprices.sqlite'))
    conn = sqlite3.connect(DB_URI, uri=True)
    cursor = conn.cursor()
    print('Connected to database...')
except sqlite3.OperationalError:
    # handle missing database case
    print('No database found. Creating a new one...')
    conn = sqlite3.connect('agileprices.sqlite')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE prices (year INTEGER, month INTEGER, day INTEGER, hour INTEGER, "
                   "segment INTEGER, price REAL, valid_from STRING UNIQUE ON CONFLICT FAIL)")
    conn.commit()
    print('Database created... ')

insert_data(data_rows)
remove_old_prices('2 days')

# finish up the database operation
if conn:
    conn.commit()
    conn.close()
