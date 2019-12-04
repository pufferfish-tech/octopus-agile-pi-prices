# octopus-agile-pi-prices
Display the upcoming prices on the Octopus Energy "Agile" tariff. 

# What does it do? 
Octopus is an energy provider in the uk. Agile is a package they provide with half hourly energy prices. https://octopus.energy/agile/
Amazingly they offer an API to allow us nerds to code things. 

# Yeah but...what does it do? 
It's for displaying current prices. It runs in python on a raspberry pi. 
This is great because it means you don't need to install anything*: The current version of Raspbian has the two things it needs: python and 
There's 2 versions right now. The first one I wrote was for the pimoroni "display-o-tron" hat, which is a three line LCD with RGB frontlighting. It's good, but it's not graphical, and it made a whine noise (a fault in my unit). 
So I wrote a second version for the pimoroni inkyphat. This is silent, doesn't self light, consumes no extra power, and oh, it looks awesome! 

(* other than the libraries for whatever display device you want...)

# What do I need?
currently: 
- A raspberry pi. The zero W works fine. The pi needs network one way or another. 
- A display adapter. If you use an inkyphat, it should work out of the box. Same with the DOThat assuming I didn't accidentally break that code.
- An sd card (obviously) - 4GB works fine. Raspbian buster LITE version uses only about half of that. No need for any more. 
- Octopus Agile API key. 

# Preparing the pi
This is actually more of a tutorial on what I've found to be the best way to just set up a pi to run arbitrary code without the hassle of a mouse keyboard and monitor. It's the path of least resistance!

- Download raspbian buster **lite** from the raspberry pi page https://www.raspberrypi.org/downloads/raspbian/ and flash the .img file onto the sd card using balenaetcher https://www.balena.io/etcher/
- Add the necessary bits in to make your pi "headless" (a file named just "ssh" and a "wpa_supplicant.conf" with your wifi credentials) https://www.raspberrypi.org/documentation/configuration/wireless/headless.md
- Boot the pi and _find it somehow_. Most routers have a page that tells you what IP address everything is using, otherwise there's an app on ios and android called "fing". SSH into it using putty or terminal and set it up. I suggest you run the terminal command "passwd" to change the pi password from the default of 'raspberry' to something else. You can also change stuff in "sudo raspi-config". 
- I recently discovered that the easiest way to transfer files is by SSH file transfer using something like filezilla. Get filezilla and upload the files for this project just into the home directory /home/pi. Connecting in filezilla is easy so long as you remember it's port 22 (standard FTP is 23 so filezilla tries to default to this!). 

-You now need to install the libraries using the one line script from pimoroni if you are using one of their displays. At time of writing this page is for inkyphat: https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-inky-phat and the line to run (in an SSH shell on the pi obviously) is 
```
curl https://get.pimoroni.com/inky | bash
```
This step installs loads of stuff including the PIL libraries and the inkyphat libraries. Nice one pimoroni. It should be noted that it does throw up some errors during and at the end and these seem fine to ignore. 

- The pi is ready for our code (and anything else you want to do with it!)

# How to use the code

We're ready for the bits specific to this project now! 

In an SSH terminal (putty etc): 
- open store_prices.py (using nano or whatever) and edit the top lines where you need to change the tariff code and API key. You will find these on your agile dashboard. 
- run **crontab -e** on the pi and add _something like this_ : 

```
@reboot sleep 10; /usr/bin/python3 octoprice_main_inky.py
*/30 * * * * sleep 20; /usr/bin/python3 octoprice_main_inky.py > /home/pi/cron.log
05 16 * * * /usr/bin/python3 store_prices.py > /home/pi/cron.log
```

First line says run the script if you reboot, second line says run every half hour (but delay by 20s to avoid time based issues!), third line is quite important, runs every day at 4:05pm to get the next set of prices. Nothing unusual here. 

- Done! Fix it to the wall! 

NOTE: If you are using the DOThat, you need to edit the above to use octoprice_main_dot.py instead of octoprice_main_inky.py. You will also need to run pimoroni's one line curl install script for the DOThat instead of inkyphat. You can go find that yourself, it exists :) 

Another NOTE: Don't be afraid to read my code. I made it as simple as possible, I subscribe to the theory that code doesn't have to be elegant or smart or even fast (in this application anyway!), it has to be maintainable above all else. If you can't understand it, what good is it? Read my code. If you don't understand it, ask me to explain it. We might find some bugs! 

# Considerations
- I wrote this myself. Because I was bored, and also because I needed to know when to plug the EV in, or start the laundry. It works but it may not be bug free. 
- The single piece of sensitive data is stored in **plain text** in the file _store_prices.py_. This is in the form of a single API key as a string. If someone were able to access your pi, they could get this. The calls to get the data are done with https:// however. The security audit is up to you. Do the basics - change your pi password, don't open up your firewall to the pi (there's no need) and turn off UPNP in your router, etc. I must stress that I'm sharing this code for you to expand on, and while it is fully operational (I hope!) it doesn't come with the blessing of having been security audited nor is it supported by octopus energy. It is just something I wrote, that people asked me to share. /disclaimer. 
- The code used for the inkyphat uses fairly standard python libraries. I haven't looked into it that much as it's a single line install from pimoroni (see below) but it seems to use PIL (python image library). You should be able to adapt this to fit any display. I haven't tried. 
- The SQLite database currently just stores data every time you update prices. There's no process at this point to ensure you don't duplicate prices (the code doesn't care) or that the database fills up the sd card (I guess it will!). I plan to address this at some point when it becomes a problem. It's important to only run the store_prices.py once a day via cron. Running it more will just duplicate everything more in the db. For now, you can literally just delete the file "octoprice.sqlite" at any time if it gets too big or slow, and rerun store_prices.py. This is why this isn't high priority for me even though it seems like a big deal.

# Future Work
- Support more generic displays
- Enable other metrics to display so you can choose what to see
- Better handling of the sqlite database to avoid duplication and truncate (see above)
