# this is the script you run every half hour by cron, best done about 20-30 seconds after the half hour to ensure
# that the right datetime is read in.
# For example --->   */30 * * * * sleep 20; /usr/bin/python3 octoprice_main_inky.py > /home/pi/cron.log

# NOTE - USAGE
# This script *won't work* unless you have created a db (python3 create_price_db.py)
# And run (python3 store_prices.py) at least once in the last 'n' hours (n is variable, it updates 4pm every day)
# You also need to update store_prices.py to include your own API access credentials and tariff.


from inky import InkyPHAT
#from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium  # should you choose to switch to gross fonts
#from font_intuitive import Intuitive
from font_fredoka_one import FredokaOne  # this is the font we're currently using
from PIL import Image, ImageFont, ImageDraw

import sqlite3
conn = sqlite3.connect('octoprice.sqlite')
cur = conn.cursor()
import datetime

##  -- Display type = red. Change below if you have the yellow
inky_display = InkyPHAT("red")
## --   ----------------------------------------------------

inky_display.set_border(inky_display.WHITE)
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# find current time and convert to year month day etc
the_now = datetime.datetime.now()
the_year = the_now.year
the_month = the_now.month
the_hour = the_now.hour
the_day = the_now.day
if the_now.minute < 30:
	the_segment = 0
else:
	the_segment = 1

print ('segment:')
print (the_segment)

# select from db where record == the above
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))

rows = cur.fetchall()

for row in rows:
	print(row[5])

# get price
current_price = row[5] # literally this is hardcoded tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE on the sqlite db or you'll get something that isn't price.

# Find Next Price
# find current time and convert to year month day etc
the_now = datetime.datetime.now()
now_plus_10 = the_now + datetime.timedelta(minutes = 30)
the_year = now_plus_10.year
the_month = now_plus_10.month
the_hour = now_plus_10.hour
the_day = now_plus_10.day
if now_plus_10.minute < 30:
	the_segment = 0
else:
	the_segment = 1

print ('segment+1:')
print (the_segment)

# select from db where record == the above
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))

rows = cur.fetchall()

for row in rows:
	print(row[5])

# get price
next_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE



# Find Next+1 Price
# find current time and convert to year month day etc
the_now = datetime.datetime.now()
now_plus_10 = the_now + datetime.timedelta(minutes = 60)
the_year = now_plus_10.year
the_month = now_plus_10.month
the_hour = now_plus_10.hour
the_day = now_plus_10.day
if now_plus_10.minute < 30:
	the_segment = 0
else:
	the_segment = 1

print ('segment:')
print (the_segment)

# select from db where record = ^
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))

rows = cur.fetchall()

for row in rows:
	print(row[5])



# get price
nextp1_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE



# Find Next+2 Price
# find current time and convert to year month day etc
the_now = datetime.datetime.now()
now_plus_10 = the_now + datetime.timedelta(minutes = 90)
the_year = now_plus_10.year
the_month = now_plus_10.month
the_hour = now_plus_10.hour
the_day = now_plus_10.day
if now_plus_10.minute < 30:
	the_segment = 0
else:
	the_segment = 1

print ('segment:')
print (the_segment)

# select from db where record == the above
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))
rows = cur.fetchall()
for row in rows:
	print(row[5])
# get price
nextp2_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE



# attempt to make an list of the next 42 hours of values
prices = []
for offset in range(0, 48):  ##24h = 48 segments
	min_offset = 30 * offset
	the_now = datetime.datetime.now()
	now_plus_offset = the_now + datetime.timedelta(minutes=min_offset)
	the_year = now_plus_offset.year
	the_month = now_plus_offset.month
	the_hour = now_plus_offset.hour
	the_day = now_plus_offset.day
	if now_plus_offset.minute < 30:
		the_segment = 0
	else:
		the_segment = 1
	cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
				(the_year, the_month, the_day, the_hour, the_segment))
	# rows = cur.fetchall()
	# get price
	row = cur.fetchone()
	if row is None:
		prices.append(0) # we don't have that price yet!
	else:
		prices.append(row[5])





font = ImageFont.truetype(FredokaOne, 60)
message = "{0:.1f}".format(current_price) + "p"
w, h = font.getsize(message)
#x = (inky_display.WIDTH / 2) - (w / 2)
#y = (inky_display.HEIGHT / 2) - (h / 2)
x = 0
y = -5

if (current_price > 14.8):
	draw.text((x, y), message, inky_display.RED, font)
else:
	draw.text((x, y), message, inky_display.BLACK, font)


right_column = 145


# NEXT
message = "2:" + "{0:.1f}".format(next_price) + "p"
font = ImageFont.truetype(FredokaOne, 20)
w2, h2 = font.getsize(message)
x = right_column
y = 0
if (next_price > 14.8):
	draw.text((x,y), message, inky_display.RED, font)
else:
	draw.text((x, y), message, inky_display.BLACK, font)

# NEXT
message = "3:" + "{0:.1f}".format(nextp1_price) + "p"
font = ImageFont.truetype(FredokaOne, 20)
w3, h3 = font.getsize(message)
x = right_column
y = 20

if (nextp1_price > 14.8):
	draw.text((x,y), message, inky_display.RED, font)
else:
	draw.text((x, y), message, inky_display.BLACK, font)


# NEXT
message = "4:" + "{0:.1f}".format(nextp2_price) + "p"
font = ImageFont.truetype(FredokaOne, 20)
w3, h3 = font.getsize(message)
x = right_column
y = 40

if (nextp2_price > 14.8):
	draw.text((x,y), message, inky_display.RED, font)
else:
	draw.text((x, y), message, inky_display.BLACK, font)


#draw.text((10,70),"It fits in the case!", inky_display.RED, font)


pixels_per_h = 2  # how many pixels 1p is worth
pixels_per_w = 2  # how many pixels 1/2 hour is worth
chart_height = 104  # total height of the chart in pixels
number_of_vals_to_display = 36 # 36 half hours = 18 hours

# plot the graph
lowest_price_next_24h = min(i for i in prices if i > 0)

print("lowest price Position:", prices.index(lowest_price_next_24h))
print("low Value:", lowest_price_next_24h)

# go through each hour and get the value

for i in range(0,number_of_vals_to_display):
	scaled_price = prices[i] * pixels_per_h # we're scaling it by the value above innit

	if prices[i] <= (lowest_price_next_24h + 1):   # if within 1p of the lowest price, display in black
		ink_color = inky_display.BLACK
	else:
		ink_color = inky_display.RED

	# takes a bit of thought this next bit, draw a rectangle from say x =  2i to 2(i-1) for each plot value
	# pixels_per_w defines the horizontal scaling factor (2 seems to work)
	draw.rectangle((pixels_per_w*i,chart_height,4*(i-pixels_per_w),chart_height-scaled_price),ink_color)

#draw minimum value on chart  <- this doesn't seem to work yet
# font = ImageFont.truetype(FredokaOne, 15)
# msg = "{0:.1f}".format(lowest_price_next_24h) + "p"
# draw.text((4*(minterval-1),110),msg, inky_display.BLACK, font)

# draw the bottom right min price and how many hours that is away
font = ImageFont.truetype(FredokaOne, 20)
msg = "min:"+"{0:.1f}".format(lowest_price_next_24h) + "p"
draw.text((right_column,60), msg, inky_display.BLACK, font)
# we know how many half hours to min price, now figure it out in hours.
minterval = (round(prices.index(lowest_price_next_24h)/2))
print ("minterval:"+str(minterval))
msg = "in:"+str(minterval)+"hrs"
draw.text((right_column,75), msg, inky_display.BLACK, font)

# and convert that to an actual time
# note that this next time will not give you an exact half hour if you don't run this at an exact half hour eg cron
# because it's literally just adding n * 30 mins!
# could in future add some code to round to 30 mins increments but it works for now.
min_offset = prices.index(lowest_price_next_24h) * 30
time_of_cheapest = the_now + datetime.timedelta(minutes=min_offset)
print("cheapest at " + str(time_of_cheapest))
print("which is: "+ str(time_of_cheapest.time())[0:5])
time_of_cheapest_formatted = "at " + (str(time_of_cheapest.time())[0:5])
font = ImageFont.truetype(FredokaOne, 15)
draw.text((right_column,90), time_of_cheapest_formatted, inky_display.BLACK, font)

# render the actual image onto the display
inky_display.set_image(img)
inky_display.show()