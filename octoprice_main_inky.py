# this is the script you run every half hour by cron, best done about 20-30 seconds after the half hour to ensure
# that the right datetime is read in.
# For example --->   */30 * * * * sleep 20; /usr/bin/python3 octoprice_main_inky.py > /home/pi/cron.log

# NOTE - USAGE
# This script *won't work* unless you have run (python3 store_prices.py) at least once in the last 'n' hours (n is variable, it updates 4pm every day)
# You also need to update store_prices.py to include your own DNO region.

from inky.auto import auto
#from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium  # should you choose to switch to gross fonts
#from font_intuitive import Intuitive
from font_fredoka_one import FredokaOne  # this is the font we're currently using
from PIL import Image, ImageFont, ImageDraw

import sqlite3
from datetime import datetime, timezone
import pytz
import time
from urllib.request import pathname2url
import get_prices_from_db

low_price = 14.8

##  -- Detect display type automatically
try:
    inky_display = auto(ask_user=False, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

inky_display.set_border(inky_display.WHITE)
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# array of up to 48 dicts, sorted by time
prices = get_prices_from_db(48)

if len(prices) == 0:
	print('No prices found!')
	exit(1)

min_price = {'price': 999}
min_price_index = 0
total_price = 0

for idx, price in enumerate(prices):
	if price['price'] < min_price['price']:
		min_price = price
		min_price_index = idx

	total_price += price['price']

avg_price = total_price / len(prices)
time_to_min_price = min_price_index / 2

min_price_str = "{0:.1f}p".format(min_price['price'])
min_price_duration_str = "{0:.1f}hrs".format(min_price_index/2)
min_price_time = datetime.strptime(min_price['valid_from'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).astimezone(pytz.timezone('Europe/London')).strftime("%H:%M")
print("Lowest price {0} in {1} at {2}".format(min_price_str, min_price_duration_str, min_price_time))


def colour_for_price(price):
	return inky_display.RED if price > low_price else inky_display.BLACK


def draw_current_price(price, current_font_size, current_y_offset):
	font = ImageFont.truetype(FredokaOne, current_font_size)
	message = "{0:.1f}".format(price) + "p"
	w, h = font.getsize(message)
	#x = (inky_display.WIDTH / 2) - (w / 2)
	#y = (inky_display.HEIGHT / 2) - (h / 2)
	x = 0
	y = current_y_offset
	draw.text((x, y), message, colour_for_price(price), font)


def draw_next_price(index, size, x_offset):
	if(len(prices) < index + 1):
		return

	# NEXT
	message = "{0}:{1:.1f}p".format(index + 2, prices[index+1]['price'])
	font = ImageFont.truetype(FredokaOne, size)
	w2, h2 = font.getsize(message)
	x = x_offset
	y = size * index
	colour = colour_for_price(prices[index + 1]['price'])
	draw.text((x,y), message, colour, font)


def draw_graph(bar_width, bar_height_per_p, bar_base_offset):
	if(min_price['price'] < 0):
		bar_base_offset += min_price['price'] * bar_height_per_p

	for i, price in enumerate(prices):
		scaled_price = price['price'] * bar_height_per_p
		ink_color = colour_for_price(price['price'])
		# takes a bit of thought this next bit, draw a rectangle from say x =  2i to 2(i-1) for each plot value
		# pixels_per_w defines the horizontal scaling factor (2 seems to work)
		draw.rectangle((bar_width*i,bar_base_offset,bar_width*(i-1),(bar_base_offset-scaled_price)),ink_color)


def draw_lowest_price_text(right_column_offset, lowest_price_y_offset, lowest_price_font_size, index, msg):
	font = ImageFont.truetype(FredokaOne, lowest_price_font_size)
	draw.text((right_column_offset,lowest_price_y_offset + lowest_price_font_size * index), msg, inky_display.BLACK, font)


def draw_all(current_font_size, current_y_offset, right_column_offset, right_column_text_size, bar_width, bar_height_per_p, bar_base_offset, lowest_price_font_size):
	# Current price
	draw_current_price(prices[0]['price'], current_font_size, current_y_offset)


	# Next prices
	draw_next_price(0, right_column_text_size, right_column_offset)
	draw_next_price(1, right_column_text_size, right_column_offset)
	draw_next_price(2, right_column_text_size, right_column_offset)


	# Graph
	draw_graph(bar_width, bar_height_per_p, bar_base_offset)


	# Lowest price
	# draw the bottom right min price and how many hours that is away
	lowest_price_y_offset = right_column_text_size * 3
	draw_lowest_price_text(right_column_offset, lowest_price_y_offset, lowest_price_font_size, 0, "min:"+min_price_str)
	draw_lowest_price_text(right_column_offset, lowest_price_y_offset, lowest_price_font_size, 1, "in:"+min_price_duration_str)
	draw_lowest_price_text(right_column_offset, lowest_price_y_offset, lowest_price_font_size, 2, "at:"+min_price_time)


if (inky_display.WIDTH == 212): #low res display
	draw_all(
		current_font_size=60,
		current_y_offset=-5,
		right_column_offset=145,
		right_column_text_size=20,
		bar_width=3,
		bar_height_per_p=2,
		bar_base_offset=104,
		lowest_price_font_size=15
		)


else: #high res display
	draw_all(
		current_font_size=72,
		current_y_offset=-10,
		right_column_offset=172,
		right_column_text_size=23,
		bar_width=3.5,
		bar_height_per_p=2.3,
		bar_base_offset=121,
		lowest_price_font_size=16
		)


# render the actual image onto the display
inky_display.set_image(img)
inky_display.show()
