import urllib2,unicodecsv 
from bs4 import BeautifulSoup

BREWERY_URL = 'http://beerme.com/brewerylist.php'
OUT_FILE = 'breweries.csv'
SOUP_PARSER = "lxml"

html = urllib2.urlopen(BREWERY_URL).read()
soup = BeautifulSoup(html, SOUP_PARSER)
brews = soup.find('div',id='main').find_all('li')
out = unicodecsv.writer(open(OUT_FILE,'wb'))
out.writerow(['beerme_id','name','city','region','country'])
for brew in brews:
	id = brew.a['href'].split('?')[1]
	name = brew.a.contents[0]
	loc = [bit.strip() for bit in brew.contents[1][2:].split(',')]
	city = loc[0]
	region = loc[1] if len(loc) is 3 else ''
	country = loc[len(loc)-1]
	row = [id, name, city, region, country]
	out.writerow(row)


