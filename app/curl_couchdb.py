import couchdb
import requests
from datetime import datetime
from datetime import timedelta


COUCHDB_HOST = 'https://admin:group27@couch1.cloudprojectnectar.co/'
TWEETS_DBNAME = 'tweets_raw'

couch = couchdb.Server()
couch = couchdb.Server(COUCHDB_HOST)
if TWEETS_DBNAME in couch:
    db = couch[TWEETS_DBNAME]
else:
    db = couch.create(TWEETS_DBNAME)


def GeoCoordinates(feature, json_data):
  if feature['geometry']['coordinates'] != None:
    json_data['coordinates'] = {}
    json_data['coordinates']['long'] = feature['geometry']['coordinates'][0]
    json_data['coordinates']['lat'] = feature['geometry']['coordinates'][1]
  return json_data


def tweets_from_couchdb_source(geohash):
  count = 0
  start_geohash = geohash + '0'
  end_geohash = geohash + 'z'
  while True:
    url = 'http://readonly:ween7ighai9gahR6@45.113.232.90/couchdbro/twitter/_design/twitter/_view/geoindex?include_docs=true&reduce=false&start_key=["' + start_geohash + '",2017,1,1]&end_key=["' + end_geohash + '",2017,12,31]&skip='+ str(100*count) +'&limit=100'
    print(url)
    r = requests.get(url)
    json_data = r.json()
    rows = json_data['rows']
    if len(rows) == 0:
      break
    for row in rows:
      tweet = {}
      tweet_id = row['id']
      print(tweet_id)
      doc = row['doc']
      if doc['lang'] == 'en':
        tweet['text'] = doc["text"]
        tweet['user'] = {}
        tweet['user']['name'] = doc["user"]["name"]
        tweet['user']['location'] = doc["user"]["location"]
        if doc['place'] != None:
          tweet['place'] = {}
          tweet['place']['name'] = str(doc['place']['full_name'])
          tweet['place']['coordinates'] = str(doc['place']['bounding_box']['coordinates'])
        try:
          tweet['created_at'] = str(datetime.strptime(doc["created_at"],'%a %b %d %H:%M:%S +0000 %Y') + timedelta(hours=10))
          # print(json.dumps(tweet))
        except Exception as e:
          print(e)
        if doc["geo"] != None:
          tweet['geo'] = {}
          tweet['geo']['lat'] = doc["geo"]['coordinates'][0]
          tweet['geo']['long'] = doc["geo"]['coordinates'][1]
        if doc['coordinates'] != None:
          tweet['coordinates'] = {}
          tweet['coordinates']['lat'] = doc["coordinates"]['coordinates'][1]
          tweet['coordinates']['long'] = doc["coordinates"]['coordinates'][0]
        try:
          db[str(tweet_id)] = tweet
        except Exception as e:
          tweet['id'] = tweet_id
          print(tweet)
    count += 1

if __name__ == '__main__':
  geohash_list = ['r1qf', 'r1qc', 'r1qb', 'r1nz', 'r1r5', 'r1r4', 'r1r1', 'r1r0', 'r1r7','r1r6', 'r1r3', 'r1r2', 'r1r9', 'r1r8', 'r1pp', 'r1pn', 'r1pj', 'r1pr', 'r1pq', 'r1ny', 'r1nv']
  for geohash in geohash_list:
    tweets_from_couchdb_source(geohash)
