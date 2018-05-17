from cloudant.client import CouchDB

client = CouchDB("admin", "group27", url="https://couch1.cloudprojectnectar.co", connect=True)

def get_database(db_name):
    # Context handles connect() and disconnect() for you.
    # Perform library operations within this context.  Such as:
    # client.create_database('testing')
    session = client.session()
    return client.get(key=db_name, remote=True)


def create_document(db, doc):
    return db.create_document(doc)

if __name__=='__main__':
    db = get_database('test-db')
    print type(db)
    doc1 = {
        "testkey":"testvalue"
    }
    print create_document(db, doc1)

