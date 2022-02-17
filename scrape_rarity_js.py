import pandas as pd
from selenium import webdriver

inp = 'stgeorge' # input("Enter windows username: ")
exe_path = r"C:\Users\{}\Downloads\geckodriver-v0.30.0-win64\geckodriver.exe".format(inp)
html = "https://rarity.tools" # input("Enter HTML address:\n ") 
outpath = "./rarity_df.pickle"

driver = webdriver.Firefox(executable_path=exe_path)
driver.get(html)
print(driver.page_source)
df = pd.read_html(driver.page_source)
df = df[0] if len(df) == 1 else df
df.to_pickle(outpath)

remove = lambda s, rm: s.translate({ord(i): None for i in rm})

market_cap = df['Estimated Market Cap'].apply(lambda x: float(remove(x[:-4], ',')))
vol = df['Volume (7d)'].apply(lambda x: float(remove(x[:-4], ',')))

df.loc[:, ('Estimated Market Cap')] = market_cap
df.loc[:, ('Volume (7d)')] = vol
df.to_pickle(outpath)

mc = df.sort_values('Estimated Market Cap').iloc[-10:]
vl = df.sort_values('Volume (7d)').iloc[-10:]

a = set(mc['Collection'])
b = set(vl['Collection'])

# Highest Volume and Highest Market Cap overlapping projects
olp = a.intersection(b)

print("Projects to investigate:", olp)

high_liq_projects = ['Axie Origins',
 'Bored Ape YC',
 'CLONE X - X TAKASHI MURAKAMI',
 'Cool Cats NFT',
 'CryptoPunks',
 'Mutant Ape Yacht Club',
 'World of Women']