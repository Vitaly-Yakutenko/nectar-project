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
from cloudant.client import Cloudant

class CouchDB():
    def __init__(self, cfg):
        self._cfg = cfg
        self._client = Cloudant(self._cfg['user'], self._cfg['password'], url=self._cfg['host'])
        self._client.connect()
        self._db = self._get_db()
        
    def _get_db(self):
        databases = self._client.all_dbs()
        db_name = self._cfg[self._name]
        if not db_name in databases:
            self._client.create_database(db_name)
        return self._client[db_name]
    
    def update_document(self, document_id, attributes_dict):
        if attributes_dict is None:
            return False
        
        document = self._db[document_id]
        for key in attributes_dict.keys():
            document[key] = attributes_dict[key]
        document.save()
        return True
    
    def reconnect(self):
        try:
            self._client.disconnect()
            self._client.connect()
        except Exceptions as e:
            print('Eror: {}'.format(e))
    

class TweetsDB(CouchDB):
    def __init__(self, cfg):
        self._name = 'tweets_db'
        super().__init__(cfg)
    
    def save_tweet(self, document):
        if not '_id' in document:
            document['_id'] = document['id_str']
        if 'id' in document:
            document.pop('id')
        self._db.create_document(document)
        
class TwitterUsersDB(CouchDB):
    def __init__(self, cfg):
        self._name = 'twitter_users_db'
        super().__init__(cfg)
        
    def get_user(self, user_id):
        return self._db[user_id]
        
    def save_user(self, document):
        if not '_id' in document:
            document['_id'] = document['id_str']
        if 'id' in document:
            document.pop('id')
        self._db.create_document(document)
    
        