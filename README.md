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
- Octopus Agile API key. 

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

You'll need to obtain some information from Octopus for the next step. Go to the [octopus developer page](https://octopus.energy/dashboard/new/accounts/personal-details/api-access) and scroll to "Unit rates". There you will see a URL, for example "https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-M/standard-unit-rates/". Look at this part: "E-1R-AGILE-FLEX-22-11-25-M". This is in the format `E-1R-AGILE-<tariff>-<region>`. The tariff is the part following "AGILE-", e.g. "FLEX-22-11-25". The region is the letter at the end, e.g. "M".

Now its time to test our scripts:

- Get prices

  ```
  python3 store_prices.py -r <your region> -t <your tariff>
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
  */30 * * * * sleep 20; cd /home/$USER/octopus-agile-pi-prices; /usr/bin/python3 octoprice_main_inky.py > /home/$USER/cron.log
  05 * * * * cd /home/$USER/octopus-agile-pi-prices; /usr/bin/python3 octoprice_main_inky.py -r <your region> -t <your tariff> > /home/$USER/cron.log
  ```
  Substituting the tariff and region as before.

  The first line runs the script if you reboot, the second line runs every half hour (but delay by 20s to avoid time based issues!), the third line runs every hour at :05pm to get the next set of prices (it only fetches from the API if there are less than 3 hours cached prices left).

- Done! Fix it to the wall! 

NOTE: If you are using the DOThat, you need to edit the above to use octoprice_main_dot.py instead of octoprice_main_inky.py. You will also need to run pimoroni's one line curl install script for the DOThat instead of inkyphat. You can go find that yourself, it exists :) 

Another NOTE: I tried to make this code **simple** and readable. If you see any issues let me know. 

# Considerations
- I wrote this myself. Because I was bored, and also because I needed to know when to plug the EV in, or start the laundry. It works but it may not be bug free. 
- The code used for the inkyphat uses fairly standard python libraries. I haven't looked into it that much as it's a single line install from pimoroni (see below) but it seems to use PIL (python image library). You should be able to adapt this to fit any display. I haven't tried. 
- The SQLite database currently just stores data every time you update prices. There's no process at this point to ensure you don't duplicate prices (the code doesn't care) or that the database fills up the sd card (I guess it will!). I plan to address this at some point when it becomes a problem. It's important to only run the store_prices.py once a day via cron. Running it more will just duplicate everything more in the db. For now, you can literally just delete the file "octoprice.sqlite" at any time if it gets too big or slow, and rerun store_prices.py. This is why this isn't high priority for me even though it seems like a big deal.

# Future Work
- Support more generic displays
- Enable other metrics to display so you can choose what to see
- Better handling of the sqlite database to avoid duplication and truncate (see above)

# Final note
If you do appreciate this code and are thinking about joining octopus, I'll leave my referral link here https://share.octopus.energy/rust-heron-863 - We both get £50 which is pretty spectacular. 

Also if you're into home automation or random tinkering then subscribe to my youtube stuff here -> https://www.youtube.com/channel/UCl_uGYJe9KW9fJWBMq1A9kw
