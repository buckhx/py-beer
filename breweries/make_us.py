import csv

#Constants
US_STRING = 'United States'
BREWERY_ENDPOINT = 'http://beerme.com/brewery.php?'

#Input
in_header = ['beerme_id','name','city','region','country']
BEERME_FILE = 'breweries.csv'

#Output
out_header = ['name','beerme_link','city','state']
US_FILE = 'us_breweries.csv'

with open(BEERME_FILE, 'rb') as in_file:
	reader = csv.DictReader(in_file)
	us = filter(lambda row: row['country'] == US_STRING, reader)
	with open(US_FILE, 'wb') as out_file:
		writer = csv.DictWriter(out_file, out_header)
		writer.writeheader()
		for row in us:
			out = {}
			out['name'] = row['name']
			out['beerme_link'] = BREWERY_ENDPOINT+row['beerme_id']
			out['city'] = row['city']
			out['state'] = row['region']
			writer.writerow(out)
