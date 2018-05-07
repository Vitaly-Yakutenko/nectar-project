import json
import os
import time
import yaml
import pandas as pd
from glob import glob
from shapely.geometry import Point, Polygon
from api.couch_db import TweetsDB


def australia_check(coordinates):
    australia = [[109.94541423022338,-9.67869330662115],[155.03330484714022,-9.67869330662115],[155.03330484714022,-39.93552098705151],[109.94541423022338,-39.93552098705151]]
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
        
        



def geo_check(coordinates):
    if isinstance(coordinates[0], list):              #check if polygon
        coordinate_polygon = Polygon(coordinates[0])
        pnt = Point(coordinate_polygon.centroid)

    else:
        pnt = Point(coordinates)
         
    for i in range(len(features)):
        for j in range(len(features[i]['geometry']['coordinates'])):
     
            poly = Polygon(features[i]['geometry']['coordinates'][j][0])
            idx = int(features[i]['properties']['sa4_code16'])
            
            if pnt.within(poly):
                return {'SA4_name':features[i]['properties']['feature_name'],
                        'SA4_code':idx,
                        'GCCSA_name':mappings_df.loc[idx]['GCCSA_NAME_2016'],
                        'GCCSA_code':mappings_df.loc[idx]['GCCSA_CODE_2016'],
                        'State_name':mappings_df.loc[idx]['STATE_NAME_2016']}
                break
            
            elif pnt.touches(poly):
                return {'SA4_name':features[i]['properties']['feature_name'],
                        'SA4_code':idx,
                        'GCCSA_name':mappings_df.loc[idx]['GCCSA_NAME_2016'],
                        'GCCSA_code':mappings_df.loc[idx]['GCCSA_CODE_2016'],
                        'State_name':mappings_df.loc[idx]['STATE_NAME_2016']}
                break
            

def none_geo_check(coordinates):
    dist_from_point = []
    dist_point_id = []
    if isinstance(coordinates[0], list):              #check if polygon
        coordinate_polygon = Polygon(coordinates[0])
        pnt = Point(coordinate_polygon.centroid)

    else:
        pnt = Point(coordinates)
         
    for i in range(len(features)):
        for j in range(len(features[i]['geometry']['coordinates'])):
     
            poly = Polygon(features[i]['geometry']['coordinates'][j][0])
            
            dist_from_point.append(poly.exterior.distance(pnt))
            dist_point_id.append(i)
            

    min_index = dist_point_id[dist_from_point.index(min(dist_from_point))]   
    idx = int(features[min_index]['properties']['sa4_code16'])
    return {'SA4_name':features[i]['properties']['feature_name'],
                        'SA4_code':idx,
                        'GCCSA_name':mappings_df.loc[idx]['GCCSA_NAME_2016'],
                        'GCCSA_code':mappings_df.loc[idx]['GCCSA_CODE_2016'],
                        'State_name':mappings_df.loc[idx]['STATE_NAME_2016']}

print('Starting application...')

os.chdir('../')

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    ymlfile.close()


#db connections
couch_db_conf = cfg['COUCHDB']
#create an instance of TWEETSDB and pass the connection details
couch_db = TweetsDB(couch_db_conf)


sa2_australia = cfg['AURIN_DATA']['sa2_australia']
df = pd.read_csv(sa2_australia)

columns = ['SA4_CODE_2016', 'SA4_NAME_2016', 'GCCSA_NAME_2016', 'STATE_NAME_2016','GCCSA_CODE_2016']

mappings_df = df[columns].drop_duplicates().set_index('SA4_CODE_2016')
mappings_df.head()

sa4_geo_tag = cfg['AURIN_DATA']['sa4_data_for_geo']
with open(sa4_geo_tag, 'r') as fp:
    data = json.load(fp)
    fp.close()

features = data['features']

geo_tasks_path= cfg['QUEUES']['geo_tasks']

print('Initialisation finished.')
print('Starting processing queue ...')
i = 1
while True:
    geo_tweets = glob('{}/*.txt'.format(geo_tasks_path))[:1000]
 
    for path in geo_tweets:
        try:
            couch_db = TweetsDB(couch_db_conf)
            tweet_id = path.split('/')[-1].split('.')[0]
            with open(path, 'r') as fp:
                geo = json.load(fp)
                fp.close()
            geo_doc =geo_check(geo['coordinates'])
            if australia_check(geo['coordinates']):         #geotag only if in Australia               
                if geo_doc== None:
                    none_geo = none_geo_check(geo['coordinates'])
                    couch_db.update_document(tweet_id,none_geo)
                    print('Task {} was processed.'.format(path))
                    try:
                        os.remove(path)
                    except OSError as e:
                        ## if failed, report it back to the user ##
                        print ("Error: {} - {},".format(e.filename,e.strerror))            
                else:
                    couch_db.update_document(tweet_id,geo_doc)
                    print('Task {} was processed.'.format(path))
                    try:
                        os.remove(path)
                    except OSError as e:
                        ## if failed, report it back to the user ##
                        print ("Error: {} - {},".format(e.filename,e.strerror))         
            else: 
                                             #if point not in Australia just add an attibute not in aus to the document
                none_aus = {'geo_analyser_tag':'tweet not in Australia'}
                couch_db.update_document(tweet_id,none_aus)
                print('Task {} was processed.'.format(path))
                try:
                    os.remove(path)
                except OSError as e:
                        ## if failed, report it back to the user ##
                    print ("Error: {} - {},".format(e.filename,e.strerror))         
    
        except Exception as e:
            print('Tweet {} wasn\'t geotagged and updated on DB due to error. {}'.format(tweet_id, e))
         
    print('Iteration: {}\tFiles processed: {}'.format(i, len(geo_tweets)))
    i+=1
    time.sleep(1)



