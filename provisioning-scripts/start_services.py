from create_machine import create_machine
import sys
import subprocess
import time

instance_types = ['jupyter', 'couchdb', 'production']


def start_jupyter():
    stat = create_machine("jupyter", "jupyter3.cloudprojectnectar.co")
    if stat != -1:
        print "Waiting for instances to be ready!"
        time.sleep(30)
        args = ['ansible-playbook', 'playbook.yml', '-l', 'jupyter']
        child = subprocess.Popen(args, cwd='../ansible/')
        data = child.communicate()[0]

def start_production():
    stat1 = create_machine("production", "prod1.cloudprojectnectar.co", "m1.medium", volume=30)
    stat2 = create_machine("production", "prod2.cloudprojectnectar.co", "m1.medium", volume=30)
    if stat1 != -1 and stat2 != -1:
        print "Waiting for instances to be ready!"
        time.sleep(30)
        args = ['ansible-playbook', 'playbook.yml', '-l', 'production']
        child = subprocess.Popen(args, cwd='../ansible/')
        data = child.communicate()[0]

def start_couchdb():
    stat1 = create_machine("couchdb", "couch1.cloudprojectnectar.co", "m1.medium", volume=60)
    stat2 = create_machine("couchdb", "couch2.cloudprojectnectar.co", "m1.medium", volume=60)
    if stat1 != -1 and stat2 != -1:
        print "Waiting for instances to be ready!"
        time.sleep(30)
        args = ['ansible-playbook', 'playbook.yml', '-l', 'couchdb']
        child = subprocess.Popen(args, cwd='../ansible/')
        data = child.communicate()[0]

        print "Setting up Couchdb servers"
        args = ['ansible-playbook', 'InstallCouchDB.yml', '-i', 'hosts', '--private-key', 'Cloud.key']
        child = subprocess.Popen(args, cwd='../ansible/couchdb/')
        data = child.communicate()[0]

        print "Setting up Couchdb cluster"
        args = ['ansible-playbook', 'SetupCluster.yml', '-i', 'hosts', '--private-key', 'Cloud.key']
        child = subprocess.Popen(args, cwd='../ansible/couchdb/')
        data = child.communicate()[0]


if __name__=='__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in instance_types:
        print "Usage: python start_services.py <jupyter|couchdb|production>"
    else:
        service_type = sys.argv[1]
        if service_type == 'production':
            start_production()
        elif service_type == 'jupyter':
            start_jupyter()
        elif service_type == 'couchdb':
            start_couchdb()
        else:
            print "ERROR: Invalid service_type specified: %s" % service_type
