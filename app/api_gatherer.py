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
from glob import glob
import json
import yaml
import os
import time
import tweepy
os.chdir('../')

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    ymlfile.close()

twitter_cfg = cfg['TWEETER']
queues_cfg = cfg['QUEUES']
users_tasks_path = queues_cfg['user_tweets_tasks']
new_tweets_queue = queues_cfg['new_tweets']

auth = tweepy.OAuthHandler(twitter_cfg['consumer_key'], twitter_cfg['consumer_secret'])
auth.set_access_token(twitter_cfg['access_token'], twitter_cfg['access_token_secret'])
api = tweepy.API(auth)

i = 1
while True:
    unprocessed_users = glob('{}/*.txt'.format(users_tasks_path))[:100]
    for path in unprocessed_users:
        try:
            with open(path, 'r') as fp:
                user_id = json.load(fp)
                response = api.user_timeline(user_id=user_id, count=1000, include_rts = True)
                for item in response:
                    try:
                        tweet_id = item._json['id_str']
                        data = str(item._json)
                        temp_file = '{}/{}.json.tmp'.format(new_tweets_queue, tweet_id)
                        with open(temp_file, 'w') as tweet_fp:
                            json.dump(item._json, tweet_fp)
                        task_file = temp_file[:-4]
                        os.rename(temp_file, task_file)
                        print('Tweet {} was successfully queued to {}'.format(tweet_id, task_file))
                    except Exception as e:
                        print('Tweet from user {} wasn\'t processed due to an error: {}'.format(user_id, e))
                time.sleep(1)
                fp.close()
            os.remove(path)
            print('Task {} was processed successfully.'.format(path))
        except Exception as e:
            print('Enexpected Error: {}'.format(e))
            
    print('Iteration: {}\tFiles processed: {}'.format(i, len(unprocessed_users)))
    i+=1
    time.sleep(1)