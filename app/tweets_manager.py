from glob import glob
import json
import re
import yaml
import os
import shutil
import time

from api.couch_db import TweetsDB
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
        new_path = '{}/{}'.format(processed_tweets_path, filename)
        shutil.move(path, new_path)


    analysers = [GeoAnalyser(geo_queue_path), SentimentAnalyser(sa_queue_path),
                 UsersAnalyser(users_tasks_path), TopicsAnalyser(topic_tasks_path)]
    couch_db = TweetsDB(cfg['COUCHDB'])



    i = 1
    while True:
        unprocessed_tweets = glob('{}/*.json'.format(tweets_queue_path))
        for path in unprocessed_tweets:
            try:
                with open(path, 'r') as fp:
                    tweet_json = json.load(fp)
                    couch_db.save_tweet(tweet_json)
                    tweet_id = tweet_json['id_str']
                    for analyser in analysers:
                        analyser.append_task(tweet_id, tweet_json)
                    complete_task(tweet_json, path)
            except Exception as e:
                print('Enexpected Error: {}'.format(e))

        print('Iteration: {}\tFiles processed: {}'.format(i, len(unprocessed_tweets)))
        i+=1
        time.sleep(20)

if __name__ == "__main__":
    main()