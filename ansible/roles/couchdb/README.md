

To run deploy CouchDB on the cloud:
	
	1. Run the install playbook to install couchdb and initialize the server
		ansible-playbook InstallCouchDB.yml  -i hosts --private-key Cloud.key
	
	2. Run another playbook to form a cluster.
		ansible-playbook SetupCluster.yml  -i hosts --private-key Cloud.key

	3. Now ssh into one of the server, you should found the source code and when you run
		curl http://admin:group27@127.0.0.1:5984/_membership
		You should see that all the node are now a cluster.