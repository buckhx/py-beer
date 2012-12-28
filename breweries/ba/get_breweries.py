import urllib,urllib2,cookielib
from bs4 import BeautifulSoup as BS
from pymongo import MongoClient

BA_URL = "http://www.brewersassociation.org/pages/directories/find-us-brewery"

def format_brewery(soup):
    doc = {}
    # Get Name
    doc['name'] = soup.h1.text
    # Address on page contains location and other keys like phone and type
    addr_bits = [bit for bit in [line.strip() for line in soup.p.text.split('\n')] if bit is not u'']
    # Get website and remove from addr
    webs = [ bit for bit in addr_bits if 'www.' in bit ]
    doc['website'] = webs[0] if len(webs) > 0 else None
    addr_bits = [bit for bit in addr_bits if 'www.' not in bit]
    # This get the rest of the non location info
    keys = [tuple( [str(k.strip().lower()) for k in bit.split(':') ]) for bit in addr_bits if ':' in bit]
    doc.update(dict(keys))
    # Assume the rest is a part of the address
    doc['address'] = "--".join([bit for bit in addr_bits if ':' not in bit])
    # TODO Use this to see if member of BA
    #attr = b.p.find_next_sibling('p')
    return doc

def get_states(soup):
    return [state.attrs['value'] for state in soup.find(id='dir_states').find_all('option')]

mongo = MongoClient().entities.ba
cookieJar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
_root = opener.open(BA_URL)
soup = BS(_root)
tok = soup.find("input",attrs={'name':'authenticity_token'}).attrs['value']
form = {'_method':'put','dir_search':'','postback':'postback','authenticity_token':tok}

states = get_states(soup)
for state in states:
    form['dir_states'] = state
    soup = BS(opener.open(BA_URL,urllib.urlencode(form)))
    breweries = soup.find_all("div",'listing-item')
    docs = []
    for brew_soup in breweries:
        brew_doc = format_brewery(brew_soup)
        docs.append(brew_doc)
    mongo.insert(docs)
        
