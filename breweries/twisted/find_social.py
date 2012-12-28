import re
from pymongo import MongoClient

import sys
sys.setrecursionlimit(10000)

class SocialRegexes():
    def __init__(self):
        self.regexes = self.load_re()
        
    def getRegexes(self):
        return self.regexes   
        
    def load_re(self):
        regexes = {}
        regexes['twitter'] = re.compile('(?:http(|s):\/\/)?(:www.)?twitter.com\/(#!\/)?(@?[a-zA-Z0-9_]+)')
        regexes['facebook'] = re.compile('(?:http(|s):\/\/)?(?:www.)?facebook.com\/(?:(?:\w)*#!\/)?(?:pages\/)?(?:[?\w\-]*\/)?(?:profile.php\?id=(?=\d.*))?([\w\-])*')
        return regexes

#SocialProfileDetector
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from bson.objectid import ObjectId

class SocialProfileDetector(Protocol):
    def __init__(self, brewery, mongo):
        deferred = Deferred()
        deferred.addCallback(self.detectProfiles)
        deferred.addErrback(self.fail)
        deferred.addCallback(self.updateBrewery)
        self.done = deferred
        self.brewery = brewery
        self.mongo = mongo

    def fail(self,failure):
        reason = failure.trap(ConnectionLost)
        print "Protocol Error for brewery: " + str(self.brewery)
        print "\t"+str(type(reason))+": "+failure.getErrorMessage()

    def connectionMade(self):
        self.data = ''

    def dataReceived(self,bytes):
        self.data += str(bytes)

    def connectionLost(self, reason):
        self.done.callback(self.data)

    def detectProfiles(self, html):
        regexes = SocialRegexes().getRegexes()
        sources = {}
        for regex in regexes.keys():
            match = regexes[regex].search(html)
            sources[regex] = match.group(0) if match is not None else None
        return sources

    def updateBrewery(self, sources):
        _id = ObjectId(self.brewery['_id'])
        find = {'_id':_id}
        update = {'$set':{'sources':sources}}
        self.mongo.update(find,update)
        

#Main    
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.error import DNSLookupError,ConnectionRefusedError, TimeoutError
from twisted.web._newclient import ResponseFailed
from twisted.internet.defer import DeferredSemaphore, gatherResults

def cbShutdown(ignored):
    reactor.stop()
    print "Reactor has SHUTDOWN"

def cbRequest(response, brewery, mongo):
    protocol = SocialProfileDetector(brewery,mongo)
    response.deliverBody(protocol)
    return protocol.done

'''
    brewery => {_id:1, websites:[]}
'''
def loadBreweries(mongo):
    return mongo.find({'sources':{'$exists':True}},fields=['websites','name','beerme_id'])

def agentErrback(failure,brewery):
    reason = failure.trap(DNSLookupError,ResponseFailed,ConnectionRefusedError,TimeoutError)
    print "Agent Error for brewery: " + str(brewery)
    print "\t"+reason.__class__.__name__+": "+failure.getErrorMessage()

def socialRequest(brewery,agent,mongo):
    brewery['websites'] = [web if web.startswith('http') else 'http://'+web for web in brewery['websites'] if re.search("(facebook|twitter)", web) is None]
    if len(brewery['websites']) > 0:
        url = str(brewery['websites'][0])
        d = agent.request('GET', url, Headers(), None)
        d.addCallback(cbRequest,brewery,mongo)
        d.addErrback(agentErrback,brewery)
        return d
    else:
        return None

def main():
    agent = Agent(reactor)
    sem = DeferredSemaphore(10)
    print "Loading breweries..."
    mongo = MongoClient().entities.breweries
    breweries = loadBreweries(mongo)
    print "Done loading breweries."
    jobs = []
    for brewery in breweries:
        jobs.append(sem.run(socialRequest,brewery,agent,mongo))
    #    if len(jobs) % 50 == 0:
    #        print "Brewery Jobs started: %d" % len(jobs) 
    d = gatherResults(jobs)
    d.addBoth(cbShutdown)
    print "Let the Reactor BEGIN!"
    reactor.run()

if __name__ == '__main__':
    main()
