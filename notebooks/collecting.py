#######################################################################
# GROUP 23
# CITY: Melbourne
# MEMBERS:
#  - Vitaly Yakutenko - 976504
#  - Shireen Hassan - 972461
#  - Himagna Erla - 975172
#  - Areeb Moin - 899193
#  - Syed Muhammad Dawer - 923859
#######################################################################
#SEARCH API
import ijson
import tweepy
#import TwitterCredentials as twit
import jsonpickle


consumer_key= "sZMPWW0zCEVsHnDyO950hWEWN"
consumer_secret= "KfS6UNO3cTCC6j5xHfjQGaNzBFofDRN98pm5aguCvduIr0UQpg"                  
access_token_key= "1397965644-WVAG6QSXEBCdHtyAeEgBsKYXEKlkoBBtb58oOAN"  
access_token_secret= "V6V2aUVFmUwkUcHhFzOn4XnwdkbCJPLOL65ZSEnRe9d7O"

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

searchQuery = '#bitcoin'
maxTweets = 10000000
tweetsPerQry = 100
fName = 'extra_tweets.json'
sinceId = None
max_id = -1

#australia = [[109.94541423022338,-9.67869330662115],[155.03330484714022,-9.67869330662115],[155.03330484714022,-39.93552098705151],[109.94541423022338,-39.93552098705151]]
#Geobox_australia = Polygon(australia)

tweetCount = 0
print("Downloading max {0} tweets".format(maxTweets))
with open(fName, 'w') as f:
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, lang="en", geocode="-26.0,134.0,1000km", count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery, lang="en", geocode="-26.0,134.0,1000km", count=tweetsPerQry, since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, lang="en", geocode="-26.0,134.0,1000km", count=tweetsPerQry,max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, lang="en", geocode="-26.0,134.0,1000km", count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                f.write(jsonpickle.encode(tweet._json, unpicklable=False) + '\n')
            tweetCount += len(new_tweets)
            print("Downloaded {0} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break

print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))