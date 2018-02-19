from urllib.request import urlopen
from bs4 import BeautifulSoup
import string
import pandas as pd
import sqlite3
from tqdm import tqdm


url = 'http://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CiaAb/FormBuscaCiaAbOrdAlf.aspx?LetraInicial='

alphanum =string.ascii_lowercase.upper() + ''.join(list(map(str,range(10))))

colors = ['Cornsilk','#FAEFCA']

data = list()
for letra_inicial in tqdm(alphanum, desc='Reading companies...', unit='letters'):
	with urlopen(url+f'{letra_inicial}') as html:
		soup = BeautifulSoup(html, 'html.parser')
	try:
		for row in soup.find_all('tr', bgcolor=True):
			row_tup = tuple()
			
			if row['bgcolor'] in colors:
				for field in row.find_all('td'):
					row_tup += (field.get_text(),)
				data.append(row_tup)
	except:
		continue

columns = ['CNPJ', 'NAME', 'TYPE', 'CVM_CODE', 'SITUATION']

df =  pd.DataFrame(data, columns=columns)
df['CVM_CODE'] = df['CVM_CODE'].apply(int)

conn = sqlite3.connect('cvm.db')
 
df.to_sql('registros', conn, if_exists='replace', index=False)

conn.close()