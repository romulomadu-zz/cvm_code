from urllib.request import urlopen
from bs4 import BeautifulSoup
import string
import pandas as pd
import sqlite3
from tqdm import tqdm

# url base
url = 'http://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CiaAb/FormBuscaCiaAbOrdAlf.aspx?LetraInicial='
# alphanum uppercase set to use in page index
alphanum =string.ascii_lowercase.upper() + ''.join(list(map(str,range(10))))
# attributes values to identify table lines of interest
colors = ['Cornsilk','#FAEFCA']

# loop through index pages
data = list()
for letra_inicial in tqdm(alphanum, desc='Reading companies...', unit='letters'):
	# get html
	with urlopen(url+f'{letra_inicial}') as html:
		soup = BeautifulSoup(html, 'html.parser')
	try:
		# loop through table lines retrieving fields values
		for row in soup.find_all('tr', bgcolor=True):
			row_tup = tuple()
			# check the attribute matching
			if row['bgcolor'] in colors:
				for field in row.find_all('td'):
					row_tup += (field.get_text(),)
				data.append(row_tup)
	except:
		continue

# store data in dataframe
columns = ['CNPJ', 'NAME', 'TYPE', 'CVM_CODE', 'SITUATION']
df =  pd.DataFrame(data, columns=columns)
df['CVM_CODE'] = df['CVM_CODE'].apply(int)

# store data in db
conn = sqlite3.connect('cvm.db') 
df.to_sql('registros', conn, if_exists='replace', index=False)
conn.close()
