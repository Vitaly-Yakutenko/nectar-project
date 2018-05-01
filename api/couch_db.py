from cloudant.client import Cloudant

class TweetsDB():
    def __init__(self, cfg):
        self._cfg = cfg
        self._client = Cloudant(self._cfg['user'], self._cfg['password'], url=self._cfg['host'])
        self._client.connect()
        self._db = self._get_db()
        
    def _get_db(self):
        databases = self._client.all_dbs()
        db_name = self._cfg['tweets_db']
        if not db_name in databases:
            client.create_database(db_name)
            #databases = client.all_dbs()
        return self._client[db_name]
        
    def save_tweet(self, document):
        if not '_id' in document:
            document['_id'] = document['id_str']
        if 'id' in document:
            document.pop('id')
        self._db.create_document(document) 
        
    def update_document(self, document_id, attributes_dict):
        document = self._db[document_id]
        for key in attributes_dict.keys():
            document[key] = attributes_dict[key]
        document.save()
        