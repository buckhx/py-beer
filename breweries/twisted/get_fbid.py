import urllib2,pymongo,json
from bson.objectid import ObjectId

mongo = pymongo.MongoClient().entities.breweries
breweries = mongo.find({'sources.facebook':{'$ne':None}},{'name':1,'sources':1,'websites':1})

def makeGraphUrl(url):
    graph_url = fb_url.replace("www.","graph.")
    graph_url = graph_url.replace("http://","https://")
    graph_url += "?access_token=AAAHOssyebnMBAEOOteXKBWHuwefgm766XiiBW1mO8woj2oVEgQ5aEZAkyAlvJoef4exmkqVZB498ifZAZBTBZB7xVrZBso3tMOdMBSE6B4MwZDZD"
    return graph_url

total = 0
success_count = 0
for brewery in breweries:
    total += 1
    fb_url = brewery['sources']['facebook']
    if "pages" in fb_url:
        fbid = fb_url.split("/")[-1]
    else:
        graph_url = makeGraphUrl(fb_url)
        try:
            info = urllib2.urlopen(graph_url)
            info = info.read()
            info = json.loads(info)
            if 'id' not in info: raise urllib2.URLError("no id")
            fbid = info['id']
        except urllib2.URLError:
            print "URL Error on graph lookup: "+str(brewery)
            continue
        except ValueError, e:
            print e.message
            continue
    success_count += 1
    print fbid
    mongo.update({'_id':ObjectId(brewery['_id'])},{'$set':{'social.facebook.id':fbid}})

print "\n\nDONE!"
print "Facebook Profile IDs found %d/%d %d%%" % (success_count,total,float(success_count)/total*100)
    
    
