# octopus-agile-pi-prices
Display the upcoming prices on the Octopus Energy "Agile" tariff. 

# What does it do? 
Octopus is an energy provider in the uk. Agile is a package they provide with half hourly energy prices. https://octopus.energy/agile/
Amazingly they offer an API to allow us nerds to code things. 

# Yeah but...what does it do? 
It's for displaying current prices. It runs in python on a raspberry pi. 
This is great because it means you don't need to install anything*. The current version of Raspbian has the two things it needs: python and SQLite. 

image of it working here -> https://imgur.com/hymxfbq

There's 2 versions right now. The first one I wrote was for the pimoroni "display-o-tron" hat, which is a three line LCD with RGB frontlighting. It's good, but it's not graphical, and it made a whine noise (a fault in my unit). 

So I wrote a second version for the **pimoroni inkyphat** https://shop.pimoroni.com/?q=inkyphat. This is silent, doesn't self light, consumes no extra power, and oh, it looks awesome! 

(* other than the libraries for whatever display device you want...)

# What do I need?
currently: 
- A raspberry pi. The zero W works fine. The pi needs network one way or another. 
- A display adapter. If you use an inkyphat, it should work out of the box. Same with the DOThat assuming I didn't accidentally break that code.
- An sd card (obviously) - 4GB works fine. Raspbian buster LITE version uses only about half of that. No need for any more. 

# Preparing the pi
This is actually more of a tutorial on what I've found to be the best way to just set up a pi to run arbitrary code without the hassle of a mouse keyboard and monitor. It's the path of least resistance!

- Download Respberry Pi Imager from the raspberry pi page https://www.raspberrypi.org/downloads/raspbian/
- Press "Operating system" then select  "Raspberry Pi OS (Other)" > "Raspberry Pi OS Lite (32 bit)"
- Choose your storage
- Click the advanced cog icon, then fill out the info to enable headless boot
  - You could enter "octoprice" as the hostname
  - Enable SSH, and enter your public key or a password
  - Set a username and password
  - Configure Wireless LAN
  - Set your locale
  - Save
- Press write

Once imaged, put the SD card in your Pi and wait a while for it to boot (it can take 5-10 minutes). It should connect to your wifi, then you can ssh to it using `ssh <username>@<hostname>.local` replacing the username and hostname for those entered when imaging

Once you have an ssh terminal, you can get started with setting up our project

# Installing

- Install the libraries for inky phat using the [one line script from pimoroni](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat)

  ```
  curl https://get.pimoroni.com/inky | bash
  ```

- Install git:

  ```
  sudo apt install git
  ```

- Clone our project

  ```
  git clone https://github.com/pufferfish-tech/octopus-agile-pi-prices.git
  cd octopus-agile-pi-prices
  ```

- Install requirements

  ```
  pip install -r requirements.txt
  ```

- Setup the database

  ```
  python3 create_price_db.py
  ```

You'll need to know your region letter for the next step. Run `python3 store_prices.py --help` to see the full list, or use this table:

| Letter | Region |
|--------|--------|
| A | East England |
| B | East Midlands |
| C | London |
| D | North Wales, Merseyside and Cheshire |
| E | West Midlands |
| F | North East England |
| G | North West England |
| H | Southern England |
| J | South East England |
| K | South Wales |
| L | South West England |
| M | Yorkshire |
| N | South and Central Scotland |
| P | North Scotland |

The current Agile product code is detected automatically from the Octopus API, so you do not need to look it up or pass it as an argument. This means the script will continue working when Octopus retire and replace the Agile product (which they do periodically).

Now its time to test our scripts:

- Get prices

  ```
  python3 store_prices.py -r <your region>
  ```

- Update the display

  ```
  python3 octoprice_main_inky.py
  ```

You should see your display update with the current price!

# Set up cron to update regularly

- Run `crontab -e` on the pi and add: 

  ```
  @reboot sleep 10; cd /home/$USER/octopus-agile-pi-prices; /usr/bin/python3 octoprice_main_inky.py > /home/$USER/cron.log
  0,30 * * * * sleep 20; cd /home/$USER/octopus-agile-pi-prices; /usr/bin/python3 octoprice_main_inky.py > /home/$USER/cron.log
  05 * * * * cd /home/$USER/octopus-agile-pi-prices; /usr/bin/python3 store_prices.py -r <your region> > /home/$USER/store_prices.log
  ```

  The first line runs the display script on reboot. The second line refreshes the display at the top and bottom of every hour, aligned with Agile slot changes. The third line fetches fresh prices from Octopus at 5 past every hour — the product code is detected automatically, so no tariff flag is needed. If Octopus publish tomorrow's prices late, the Pi will pick them up within the hour.

- Done! Fix it to the wall! 

NOTE: If you are using the DOThat, you need to edit the above to use octoprice_main_dot.py instead of octoprice_main_inky.py. You will also need to run pimoroni's one line curl install script for the DOThat instead of inkyphat. You can go find that yourself, it exists :) 

Another NOTE: I tried to make this code **simple** and readable. If you see any issues let me know. 

# Considerations
- I wrote this myself. Because I was bored, and also because I needed to know when to plug the EV in, or start the laundry. It works but it may not be bug free. 
- The code used for the inkyphat uses fairly standard python libraries. I haven't looked into it that much as it's a single line install from pimoroni (see below) but it seems to use PIL (python image library). You should be able to adapt this to fit any display. I haven't tried. 
- The SQLite database deduplicates prices automatically and prunes entries older than 2 days, so the database will not grow unboundedly.

# Future Work
- Support more generic displays
- Enable other metrics to display so you can choose what to see

# Final note
If you do appreciate this code and are thinking about joining octopus, I'll leave my referral link here https://share.octopus.energy/rust-heron-863 - We both get £50 which is pretty spectacular. 

Also if you're into home automation or random tinkering then subscribe to my youtube stuff here -> https://www.youtube.com/channel/UCl_uGYJe9KW9fJWBMq1A9kw
