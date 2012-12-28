import urllib2,urllib,pymongo,json,time
from bson.objectid import ObjectId

mongo = pymongo.MongoClient().entities.ba
search = {'type':'regional','location':{'$exists':False}}

GOOGLE_GEO_URL = "http://maps.googleapis.com/maps/api/geocode/json?"

for brewery in mongo.find(search):
    params = {'address':brewery['address'], 'sensor':'false'}
    url = GOOGLE_GEO_URL+urllib.urlencode(params)
    res = json.loads(urllib2.urlopen(url).read())
    if res['status'] == 'OK':
        res = res['results'][0]
        loc = {}
        geo = res['geometry']['location']
        loc['geo'] = geo
        loc['address'] = res['formatted_address']
        loc['gran'] = res['geometry']['location_type']
        for comp in res['address_components']:
            if "locality" in comp['types']:
                loc['city'] = comp['long_name']
            if "administrative_area_level_2" in comp["types"]:
                loc['county'] = comp['long_name']
            if "administrative_area_level_1" in comp["types"]:
                loc['state'] = comp['short_name']
            if "country" in comp["types"]:
                loc['country'] = comp["short_name"]
            if "postal_code" in comp["types"]:
                loc['zip'] = comp["long_name"]
        brewery['location'] = loc
        mongo.update({'_id':ObjectId(brewery['_id'])},brewery)
        print "UPDATED: " + brewery['name']
    else:
        print "GOOG API STATUS FAIL: "+json.dumps(res)
        print brewery
    time.sleep(0.15)

print "FINISHED!"
