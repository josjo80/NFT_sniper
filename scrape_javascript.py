exe_path = '/Users/joshuajohnson/Drive/Documents/Projects/NFT/NFT_sniper/geckodriver'
html = input("Enter HTML address:\n ") # "https://rarity.tools"

import pandas as pd
from selenium import webdriver

webdriver.Firefox(executable_path=exe_path)
driver.get(html)

df = pd.read_html(driver.page_source)