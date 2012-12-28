import urllib2,csv
from beerme_parser import BeerMeParser
from pymongo import MongoClient

def getBeermeIds():
    path = '/home/buck/py-beer/breweries/us_breweries.csv'
    headers = ['name','beerme_link','city','state']
    with open(path, 'rb') as in_file:
        reader = csv.DictReader(in_file)
        return [line['beerme_link'].split('?')[1] for line in reader]

def main():
    print "Loadings IDs"
    ids = getBeermeIds()
    ids = ids[2100:]
    print "Done Loading %i IDs" % len(ids)
    mongo = MongoClient().entities.breweries
    brew_count = len(ids)
    count = 0
    breweries = []
    for id in ids:
        count += 1
        url = 'http://beerme.com/fixerror.php?'+str(id)
        data = urllib2.urlopen(url).read()
        try:
            breweries.append(BeerMeParser.parse(data))
        except:
            "FAILED: "+id
        if count % 50 == 0:
            mongo.insert(breweries)
            breweries = []
            print "Inserted MongoBatch: %i, %d%%" % (count,float(count)/brew_count*100)
    if len(breweries) > 0:
        mongo.insert(breweries)
    print "Finished!"

if __name__ == '__main__':
    main()
