#!/usr/bin/env python3.7

from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium import webdriver

import time
import requests
from bs4 import BeautifulSoup
import cloudscraper

scraper = cloudscraper.create_scraper()

# Load selenium components
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/brave-browser"
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-dev-shm-usage')

# These are the "end builds" for each expansion.
builds = ['1.12.1.5875', '2.4.3.8606', '3.3.5.12340',
          '4.3.4.15595', '5.4.8.18273', '6.2.4.21742',
          '7.3.5.26972', '8.3.7.35662']

# first, we need to get a list of the table names.
url = "https://wow.tools/dbc/?build=4.3.4.15595&hotfixes=true"
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

time.sleep(4)  # allows the javascript to fill in the page data.

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

tables = [str(x.text)
          for x in soup.find(id="fileFilter").find_all('option')]
tables.pop(0)  # Removes the 'Select a table' option.

all_columns = []

# Now that we have a list of tables, let's start going through all of the pages.
for b in builds:
    for t in tables:
        url = "https://wow.tools/dbc/?dbc="+t+"&build="+b+"&hotfixes=true"
        driver.get(url)

        time.sleep(6)  # allows the javascript to fill in the page data.
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        print("["+b+"] Starting: "+t)
        
        # this is a method to ensure that the table exists for this build.
        try:
            if b in soup.find("a", {"id": "downloadCSVButton"})['href']:
                columns = [str(x.text.strip())
                           for x in soup.find(id="dbtable").find_all('th')]
                print("["+b+"] Ending: "+t)
            else:
                print(">> " + t+" is not for " + b)
                print("["+b+"] Ending: "+t)

                continue
        except:
            print(">> Hit an exception, " + t +
                  " does not appear to have a downloadCSVButton.")

        f = open(b+"_column_headers.txt", "a")
        header_list = "('" + t + "', " + str(columns) + "), \n"
        f.write(str(header_list))
        f.close()

driver.close()
driver.quit()
