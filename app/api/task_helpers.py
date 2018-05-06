import json
import os
from shapely.geometry import Point, Polygon
from .couch_db import TwitterUsersDB


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
    def australia_check(self, coordinates):
        australia = [[109.94541423022338,-9.67869330662115],[155.03330484714022,-9.67869330662115],
                     [155.03330484714022,-39.93552098705151],[109.94541423022338,-39.93552098705151]]
        australia_box = Polygon(australia)
        if isinstance(coordinates[0], list):              #check if polygon
            coordinate_polygon = Polygon(coordinates[0])
            pnt = Point(coordinate_polygon.centroid)

        else:
            pnt = Point(coordinates)

        if australia_box.contains(pnt):
            return True
        else:
            return False
    
    
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
    def __init__(self, queue_path, cfg):
        self._db = TwitterUsersDB(cfg['COUCHDB'])
        super().__init__(queue_path)
    
    def append_task(self, tweet_id, tweet_data):
        try:   
            user_id = tweet_data['user']['id_str']
            try:
                user = self._db.get_user(user_id)
                print('{} is known user. Skipping them.'.format(user_id))
            except KeyError:
                self._db.save_user(tweet_data['user'])
                task_id = user_id
                print('Sending user {} for processing'.format(user_id))
                return self._append_task(task_id=task_id, content=task_id)
        except Exception as e:
            print(type(e))
            print('Cannot process tweet_id and extract user_id due to an error . {}'.format(tweet_id, e))
            

class TopicsAnalyser(TaskHelper):
    def append_task(self, tweet_id, tweet_data):
        try:
            tweet_id = tweet_data['id_str']
            text = tweet_data['text']
            return self._append_task(task_id=tweet_id, content=text)
        except Exception as e:
            print('Tweet {} wasn\'t wasn\'t sent to topic analyser due to error. {}'.format(tweet_id, e))