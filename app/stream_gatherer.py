from tweepy import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import time
import yaml
import os
import numpy as np

class TwitterListener(StreamListener):
    def __init__(self, dump_folder):
        if not os.path.exists(dump_folder):
            os.makedirs(dump_folder)
        self._dump_folder = dump_folder
        
    def _save_tweet(self, tweet_id, json_data):
        temp_filename = '{}/{}.json.tmp'.format(self._dump_folder, tweet_id)
        filename = temp_filename[:-4]
        with open(temp_filename, 'w') as fp:
            fp.write(json_data)
            fp.close()
        os.rename(temp_filename, filename)
        print("Tweet {} was queued to {}".format(tweet_id, filename))
    
    def on_data(self, data):
        try:
            s = str(data)
            json_data = json.loads(s)
            if not 'id_str' in json_data:
                print('Invalid tweet:\n{}'.format(data))
                return False

            tweet_id = json_data['id_str']                
            self._save_tweet(tweet_id, data)
        except Exception as e:
            print('Failed to process stream of data: {}'.format(data))
            print('Error: {}'.format(e))
            
        return True

    def on_error(self, status):
        print(status)

os.chdir('../')

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    ymlfile.close()
    
twitter_cfg = cfg['TWEETER']
access_token = twitter_cfg['access_token']
access_token_secret = twitter_cfg['access_token_secret']
consumer_key = twitter_cfg['consumer_key']
consumer_secret = twitter_cfg['consumer_secret']
tweets_folder = cfg['QUEUES']['new_tweets']

bounding_boxes = np.array(twitter_cfg['bounding_boxes'])
size = twitter_cfg['number_of_instances']
rank = twitter_cfg['rank']
target_boxes_mask = np.divmod(range(bounding_boxes.shape[0]), size)[1] == rank

#list(bounding_boxes[target_boxes_mask].ravel())

wait_time = 1
while True:
    try:
        listener = TwitterListener(tweets_folder)
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        stream = Stream(auth, listener)
        wait_time = 1
        #stream.filter(locations=[111,-44,157,-10], languages=['en'])
        stream.filter(locations=list(bounding_boxes[target_boxes_mask].ravel()), languages=['en'])
        
    except Exception as e:
        print('Error: {}'.format(e))
        print('Restarting Stream Gatherer in {} seconds'.format(wait_time))
        time.sleep(wait_time)
        wait_time = min(wait_time * 2, 30)