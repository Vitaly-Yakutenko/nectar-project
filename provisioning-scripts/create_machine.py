from connect import ec2_conn
from check_instance import is_ready
from list_machines import list_machines
import time
import sys


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python create_machine.py <machine_name> <volume_size>\nIf no volume_size is given, by default no " \
              "volume will be attached"
        exit(0)
    else:
        name = sys.argv[1]
        vol_size = sys.argv[2] if len(sys.argv) > 2 else None

        reservation = ec2_conn.run_instances('ami-00003837',
                                             key_name='Cloud',
                                             instance_type='m1.small',
                                             security_groups=['default'],
                                             placement='melbourne-qh2')



        instance = reservation.instances[0]
        print('New instance {} has been created.'.format(instance.id))
        print "Machine is Spawning..."

        while not is_ready([instance.id]):
            time.sleep(5)
        print "Machine (%s) is Ready" % instance.id
        print "Naming Instance as :%s" % name
        ec2_conn.create_tags([instance.id], {'Name': name})

        if vol_size:
            vol_req = ec2_conn.create_volume(vol_size, 'melbourne-qh2')
            ec2_conn.create_tags([vol_req.id], {"Name": name + "-volume"})
            curr_vol = ec2_conn.get_all_volumes([vol_req.id])[0]
            while not curr_vol.status=='available':
                time.sleep(5)
                curr_vol = ec2_conn.get_all_volumes([vol_req.id])[0]
            print "Volume created.."

            ec2_conn.attach_volume(vol_req.id, instance.id, '/dev/vdc')
            print "Volume attached at /dev/vdc"

        list_machines([instance.id])
