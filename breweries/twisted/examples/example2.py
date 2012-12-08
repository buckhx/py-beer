from bs4 import BeautifulSoup

class BeerMeParser():

    @staticmethod
    def parseData(data):
	soup = BeautifulSoup(data)
	table = soup.find('form',attrs={'name':'breweryinformation'}).table 
	name = table.find('input',attrs={'name':'brewname'}).attrs['value']
	status = table.find('select',attrs={'name':'brewstatus'}).find('option',attrs={'selected':'selected'}).attrs['value']
	info = {'name': name, 'status': status}
	return info

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

class HTMLParser(Protocol):
    def __init__(self):
        deferred = Deferred()
        deferred.addCallback(BeerMeParser.parseData)
	deferred.addCallback(self.cbPrint)
	self.done = deferred

    def connectionMade(self):
	self.parser = DataAggregator()

    def dataReceived(self, bytes):
	self.parser.appendData(str(bytes))

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
	self.done.callback(self.parser.getData())

    def cbPrint(self, d):
	print d


from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

agent = Agent(reactor)
url = 'http://beerme.com/fixerror.php?168'

d = agent.request('GET', url, Headers(), None)
def cbRequest(response):
    protocol = HTMLParser()
    response.deliverBody(protocol)
    return protocol.done
d.addCallback(cbRequest)

def cbShutdown(ignored):
    reactor.stop()
d.addBoth(cbShutdown)

reactor.run()
