class DataAggregator():
    def __init__(self, data=''):
        self.data = data

    def appendData(self, data):
        self.data += data

    def setData(self, data):
        self.data = data

    def clearData(self):
        self.data = ''

    def getData(self):
        return self.data

from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from beerme_parser import BeerMeParser
from pymongo import MongoClient

class HTMLParser(Protocol):
    def __init__(self):
        deferred = Deferred()
        deferred.addCallback(BeerMeParser.parse)
        deferred.addCallback(self.writeToMongo)
        self.done = deferred
        self.mongo = MongoClient().entities.breweries

    def connectionMade(self):
        self.parser = DataAggregator()

    def dataReceived(self, bytes):
        self.parser.appendData(str(bytes))

    def connectionLost(self, reason):
        # print 'Finished receiving body:', reason.getErrorMessage()
        self.done.callback(self.parser.getData())

    def writeToMongo(self, info):
        self.mongo.insert(info)
        print "Wrote brewery: %s" % (info['beerme_id'])


from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.defer import DeferredSemaphore, gatherResults 

def cbRequest(response):
    protocol = HTMLParser()
    response.deliverBody(protocol)
    return protocol.done

def cbShutdown(ignored):
    print "Finished, shutting down the reactor..."
    reactor.stop()

def beerme_request(id, agent):
    url = 'http://beerme.com/fixerror.php?'+str(id)
    d = agent.request('GET', url, Headers(), None)
    d.addCallback(cbRequest)
    return d

def getBeermeIds():
    import csv
    path = '/home/buck/py-beer/breweries/us_breweries.csv'
    headers = ['name','beerme_link','city','state']
    with open(path, 'rb') as in_file:
        reader = csv.DictReader(in_file)
        return [line['beerme_link'].split('?')[1] for line in reader]

def main():
    agent = Agent(reactor)
    sem = DeferredSemaphore(5)
    print "Loading IDs"
    ids = getBeermeIds()
    ids = ids[:100]
    print "Done Loading %s IDs" % str(len(ids))
    jobs = []
    for id in ids:
        jobs.append(sem.run(beerme_request,id,agent))
    d = gatherResults(jobs)
    d.addBoth(cbShutdown)

    print "Starting reactor..."
    reactor.run()

if __name__ == '__main__':
    main()
