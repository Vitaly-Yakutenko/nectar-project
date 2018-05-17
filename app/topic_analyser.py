import json
import os
import time
import yaml
import re
from glob import glob
from api.couch_db import TweetsDB
os.chdir('../')

#open the config file for Db connections and folder paths
with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

print('Script Initialised and connected to DB')
#db connections
couch_db_conf = cfg['COUCHDB']
#create an instance of TWEETSDB and pass the connection details
couch_db = TweetsDB(couch_db_conf)
#path to topic_folder
topic_tasks_path= cfg['QUEUES']['topic_tasks']


hashtags = ['bitcoin', 'blockchain', 'btc', 'cryptocurrency',
            'crypto','ethereum', 'fintech', 'doge', 'ethereum', 'litecoin', 
            'monero', 'TRON', 'zcash', 'jaxx', 'copay', 'bitpay', 
            'mycelium', 'trezor', 'darknet\smarket', 
            'dogecoin','Central\sLedger','ICO']


'|'.join(hashtags)


def topic_check(text):
    if re.search('|'.join(hashtags), text):
        return True
    else:
        return False

print('strating processing queue')
i = 1
while True:
    topic_tweets = glob('{}/*.txt'.format(topic_tasks_path))
 
    for path in topic_tweets:
        try:
            tweet_id = path.split('/')[-1].split('.')[0]
            with open(path, 'r') as fp:
                topic_text = fp.read()
            if topic_check(topic_text):
                topic = {'topic':'crypto'}
                couch_db.update_document(tweet_id,topic)
                os.remove(path)
                print("file:{} is about crypto, and is updated",format(path))
            else:
                os.remove(path)
                continue
            
        except Exception as e:
            print('Tweet {} wasn\'t topic and updated on DB due to error. {}'.format(tweet_id, e))
            #print(e.StackTrace())
         
    print('Iteration: {}\tFiles processed: {}'.format(i, len(topic_tweets)))
    i+=1
    time.sleep(3)

