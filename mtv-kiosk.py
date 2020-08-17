#!/usr/bin/env python

"""
READ ME!
This script will start chromium in kiosk mode.
You should be able to use this script for a raspberry-pi kiosk. You could make a systemd service or a .desktop file in ~/.config/autostart to autostart the script.

This script will automatically
* start chromium in kiosk mode
* open mtv (for /a/)
* wait until a new video plays and auto-fullscreen it

Auto-fullscreen now works (with a workaround).

INSTALL

* chromium
* python (>= 2.7, I have the 3.8)
* selenium library (pip install --user --upgrade selenium)

Don't forget to keep your software updated (pip install --upgrade pip).

RUN

* chmod 750 mtv-kiosk.py
* python mtv-kiosk.py

DAISUKI!
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time

option = Options()

option.add_argument("--disable-infobars")
option.add_argument("--disable-extensions")
option.add_argument("--kiosk") # otherwise .requestFullscreen works only once
option.add_argument("--fullscreen")


# Pass the argument 1 to allow and 2 to block
option.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 2
})

browser = webdriver.Chrome(options=option)

# browser = webdriver.Firefox() # wont work well, needs webkitRequestFullscreen() replaced with requestFullscreen() and other options
browser.get('https://shamik.ooo/a/catalog') # /a/ catalog

# get rid of alert (gaia redirect)
try:
    WebDriverWait(browser, 3).until(EC.alert_is_present(), 'Timed out waiting for PA creation confirmation popup to appear.')
    alert = browser.switch_to.alert
    alert.accept()
    print("alert accepted")
except TimeoutException:
    print("no alert")

browser.find_element_by_link_text("Last 100").click()
print("thread open")
browser.execute_script("document.getElementById('options').style.display='block'");
print("options open")
browser.find_element_by_link_text("Fun").click()
print("fun open")
browser.find_element_by_name("meguTV").click()
print("mtv open")

# temp fix
print("let's wait (2 sec) for mtv to preload...")
time.sleep(2)

browser.execute_script("document.getElementById('megu-tv').children[0].requestFullscreen()")
print("fullscreened video")

lastHash = browser.execute_script("return document.getElementById('megu-tv').children[0].getAttribute('data-sha1')")
print(lastHash)

# change to fullscreen on new video automatically
try:
    while True:
        time.sleep(1)
        nextHash = browser.execute_script("return document.getElementById('megu-tv').children[0].getAttribute('data-sha1')")
        print(nextHash)
        if lastHash != nextHash:
            print("video hash changed! fullscreening again...")
            lastHash = nextHash  
            # this is an arbritraty click() event, which serves as a "workaround" for mandatory user-input on requestFullscreen()
            browser.find_element_by_link_text("Fun").click()
            browser.execute_script("document.getElementById('megu-tv').children[0].requestFullscreen()")

except KeyboardInterrupt:
    print("KeyboardInterrupt. Script wont auto-fullscreen anymore, chromium still running.")
    exit(0)
