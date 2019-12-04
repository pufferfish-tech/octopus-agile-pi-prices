# this is the script you run every half hour by cron, best done about 20-30 seconds after the half hour to ensure
# that the right datetime is read in.
# For example --->   */30 * * * * sleep 20; /usr/bin/python3 octoprice_main_inky.py > /home/pi/cron.log

# NOTE - this version is designed for the pimoroni "display-o-tron" hat. You need to install all the libraries as per
# pimoroni's one line script.

import dothat.lcd as lcd
import dothat.backlight as backlight

import sqlite3
conn = sqlite3.connect('octoprice.sqlite')
cur = conn.cursor()
import datetime
import requests


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



# select from db where record = ^
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))

rows = cur.fetchall()

for row in rows:
	print(row[5])



# get price
current_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE


# display price on LCD
# Clear the LCD and display Hello World
lcd.clear()
lcd.write("Now:")
lcd.write(str(current_price))

lcd.set_cursor_position(1, 0)

lcd.set_contrast(52)


# change colour to match the badness of the price.
backlight.off()
# doing nothing with the graph so far
backlight.set_graph(0)


if current_price < 9.8: #greens
	g=255
	if current_price < 6:
		r = 0
		b = 0
	elif current_price < 7:
		r = 30
		b = 30
	elif current_price < 8:
		r = 60
		b = 60
	else:
		r = 90
		b = 90
elif current_price < 14.8: # blues
	b = 255
	if current_price < 11:
		r = 30
		g = 30
	else:
		r = 60
		g = 60
else: #expensive! 
	r = 255
	if current_price < 20:
		b = 100
		g = 100
		backlight.set_graph(0.3)
	elif current_price < 30:
		b = 30
		g = 30
		backlight.set_graph(0.5)
	else:
		b = 0
		g = 0
		backlight.set_graph(1)




#backlight.rgb(r,g,b)
#backlight.rgb(0,0,0)
if the_hour < 9:
	backlight.rgb(0,0,0)
else:
	backlight.rgb(int(r/2),int(g/2),int(b/2))

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

print ('segment:')
print (the_segment)



# select from db where record = ^
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))

rows = cur.fetchall()

for row in rows:
	print(row[5])



# get price
next_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE

# put that on the lcd
lcd.set_cursor_position(0, 1)
lcd.write("Soon:")
lcd.write(str(next_price))



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
next_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE

# put that on the lcd
lcd.set_cursor_position(0, 2)
lcd.write("Then:")
lcd.write(str(next_price))
