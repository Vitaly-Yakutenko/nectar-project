from glob import glob
import json
import re
import yaml
import os
import shutil
import time

from api.couch_db import TweetsDB, TwitterUsersDB
from api.task_helpers import GeoAnalyser, SentimentAnalyser, UsersAnalyser, TopicsAnalyser


def main():
    os.chdir('../')
    with open("config.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        ymlfile.close()

    queues_cfg = cfg['QUEUES']
    tweets_queue_path = queues_cfg['new_tweets']
    processed_tweets_path = queues_cfg['processed_tweets']
    sa_queue_path = queues_cfg['sentiment_tasks']
    geo_queue_path = queues_cfg['geo_tasks']
    users_tasks_path = queues_cfg['user_tweets_tasks']
    topic_tasks_path = queues_cfg['topic_tasks']


    def complete_task(tweet, path):
        filename = path.split('/')[-1]
        #new_path = '{}/{}'.format(processed_tweets_path, filename)
        #shutil.(path, new_path)
        os.remove(path)

    analysers = [
                    GeoAnalyser(geo_queue_path),
                    SentimentAnalyser(sa_queue_path),
                    UsersAnalyser(users_tasks_path, cfg),
                    TopicsAnalyser(topic_tasks_path)
                ]
    geo_analyser = analysers[0]
    couch_db = TweetsDB(cfg['COUCHDB'])
        

    def tweet_within_bounding_box(tweet_data):
        if tweet_data['coordinates'] is not None:
            coordinates = tweet_data['coordinates']
        elif tweet_data['place'] is not None:
            coordinates = tweet_data['place']['bounding_box']
        else:
            return False        
        return geo_analyser.australia_check(coordinates['coordinates'])


    i = 1
    while True:
        unprocessed_tweets = glob('{}/*.json'.format(tweets_queue_path))[:1000]
        for path in unprocessed_tweets:
            try:
                with open(path, 'r') as fp:
                    tweet_json = json.load(fp)
                    tweet_id = tweet_json['id_str']
                    
                    if tweet_within_bounding_box(tweet_json):
                        couch_db.save_tweet(tweet_json)
                        for analyser in analysers:
                            analyser.append_task(tweet_id, tweet_json)
                    else:
                        print('Tweet {} is outside of Australia. Skipping it.'.format(tweet_id))
                    complete_task(tweet_json, path)
            except Exception as e:
                print('Enexpected Error: {}'.format(e))

        print('Iteration: {}\tFiles processed: {}'.format(i, len(unprocessed_tweets)))
        i+=1
        time.sleep(1)

if __name__ == "__main__":
    main()