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

# Considerations
- I wrote this myself. Because I was bored, and also because I needed to know when to plug the EV in, or start the laundry. It works but it may not be bug free. 
- The single piece of sensitive data is stored in **plain text** in the file _store_prices.py_. This is in the form of a single API key as a string. If someone were able to access your pi, they could get this. The calls to get the data are done with https:// however. The security audit is up to you. Do the basics - change your pi password, don't open up your firewall to the pi (there's no need) and turn off UPNP in your router, etc. I must stress that I'm sharing this code for you to expand on, and while it is fully operational (I hope!) it doesn't come with the blessing of having been security audited nor is it supported by octopus energy. It is just something I wrote, that people asked me to share. /disclaimer. 
- The code used for the inkyphat uses fairly standard python libraries. I haven't looked into it that much as it's a single line install from pimoroni (see below) but it seems to use PIL (python image library). You should be able to adapt this to fit any display. I haven't tried. 
- The SQLite database currently just stores data every time you update prices. There's no process at this point to ensure you don't duplicate prices (the code doesn't care) or that the database fills up the sd card (I guess it will!). I plan to address this at some point when it becomes a problem. It's important to only run the store_prices.py once a day via cron. Running it more will just duplicate everything more in the db. For now, you can literally just delete the file "octoprice.sqlite" at any time if it gets too big or slow, and rerun store_prices.py. This is why this isn't high priority for me even though it seems like a big deal.

# Future Work
- Support more generic displays
- Enable other metrics to display so you can choose what to see
- Better handling of the sqlite database to avoid duplication and truncate (see above)
