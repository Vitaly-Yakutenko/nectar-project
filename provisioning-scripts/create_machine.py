from connect import ec2_conn
from check_instance import is_ready
from list_machines import list_machines
import time
import sys



if __name__=='__main__':
    if len(sys.argv) < 2:
        print "Usage: python create_machine.py <machine_name>"
        exit(0)
    else:
        name = sys.argv[1]
        reservation = ec2_conn.run_instances('ami-00003837',
                                             key_name='Cloud',
                                             instance_type='m1.small',
                                             security_groups=['default'])



        instance = reservation.instances[0]
        print('New instance {} has been created.'.format(instance.id))
        print "Machine is Spawning..."

        while not is_ready([instance.id]):
            time.sleep(5)
        print "Machine (%s) is Ready" % instance.id
        print "Naming Instance as :%s" % name
        ec2_conn.create_tags([instance.id], {'Name': name})
        list_machines([instance.id])
