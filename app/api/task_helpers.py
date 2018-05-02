import json
import os


class TaskHelper():
    def __init__(self, queue_path):
        self._queue_path = queue_path
        if not os.path.exists(queue_path):
            os.makedirs(queue_path)
        #print(queue_path)
    
    def _append_task(self, task_id, content):
        temp_file = '{}/{}.task.txt.tmp'.format(self._queue_path, task_id) 
        with open(temp_file, 'w') as fp:
            fp.write(json.dumps(content))
            fp.close()
        task_file = temp_file[:-4]
        os.rename(temp_file, task_file)
        print('New task was queued to {}'.format(task_file))
        return task_file
    

class GeoAnalyser(TaskHelper):
    def append_task(self, tweet_id, tweet_data):
        try:
            if tweet_data['coordinates'] is not None:
                return self._append_task(task_id=tweet_id,
                                         content=tweet_data['coordinates'])
            elif tweet_data['place'] is not None:
                return self._append_task(task_id=tweet_id,
                                         content=tweet_data['place']['bounding_box'])
            else:
                print('Tweet {} doesn\'t contain coordinates.\nFile {} was skipped.'.format(tweet_id, path))
                return None
        except Exception as e:
            print('Tweet {} wasn\'t sent to geoanalyser due to error. {}'.format(tweet_id, e))
            #raise e
            
class SentimentAnalyser(TaskHelper):
    def append_task(self, tweet_id, tweet_data):
        try:
            if tweet_data['text'] is not None:
                text = tweet_data['text']
                return self._append_task(task_id=tweet_id,
                                         content=text)
            else:
                print('Tweet {} doesn\'t contain text.\nFile {} was skipped.'.format(tweet_id, path))
                return None
        except Exception as e:
            print('Tweet {} wasn\'t sent to sentiment analyser due to error. {}'.format(tweet_id, e))
            
            
class UsersAnalyser(TaskHelper):
    def append_task(self, tweet_id, tweet_data):
        try:
            task_id = tweet_data['user']['id_str']
            return self._append_task(task_id=task_id, content=task_id)
        except Exception as e:
            print('Cannot process tweet_id and extract user_id due to an error . {}'.format(tweet_id, e))
            

class TopicsAnalyser(TaskHelper):
    def append_task(self, tweet_id, tweet_data):
        try:
            tweet_id = tweet_data['id_str']
            text = tweet_data['text']
            return self._append_task(task_id=tweet_id, content=text)
        except Exception as e:
            print('Tweet {} wasn\'t wasn\'t sent to topic analyser due to error. {}'.format(tweet_id, e))