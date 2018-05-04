#importing and downloading revelant modules from NLTK
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


import json
import os
import time
import yaml
from glob import glob
from api.couch_db import TweetsDB
os.chdir('../')


#open the config file for Db connections and folder paths
with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


#db connections
couch_db_conf = cfg['COUCHDB']
#create an instance of TWEETSDB and pass the connection details
couch_db = TweetsDB(couch_db_conf)
#path to senti_folder
senti_tasks_path= cfg['QUEUES']['sentiment_tasks']



def senti_analyse(input_doc):
    senti = SentimentIntensityAnalyzer()
    points = senti.polarity_scores(input_doc)
    if points['compound']<0.0:
        points['sentiment']= "Negative"
        if points['compound']<= -0.5:
            points['Intensity']="Strong"
        if -0.5 <points['compound']< 0.0:
            points['Intensity']="Moderate"
    if points['compound']>0.0:
        points['sentiment']= "Positive"
        if points['compound']>= 0.5:
            points['Intensity']="Strong"
        if 0.0<points['compound']<0.5:
            points['Intensity']="Moderate"
    if points['neu']==1:
        points['sentiment']="Neutral"       

    return points
            
    
    

i = 1
while True:
    senti_tweets = glob('{}/*.txt'.format(senti_tasks_path))[:1000]
 
    for path in senti_tweets:
        try:
            tweet_id = path.split('/')[-1].split('.')[0]
            with open(path, 'r') as fp:
                senti = fp.read()
            senti_doc = senti_analyse(senti)
            couch_db.update_document(tweet_id,senti_doc)
            try:
                os.remove(path)
                print('Task {} was processed.'.format(path))
            except Exception as e:
                           # if failed, report it back to the user 
                print("Error: {} .".format(e))
        except Exception as e:
            print('Tweet {} wasn\'t Senti Analysed and updated on DB due to error. {}'.format(tweet_id, e))
         
    print('Iteration: {}\tFiles processed: {}'.format(i, len(senti_tweets)))
    i+=1
    time.sleep(18)








