from connect import ec2_conn
from connect_aws import route_conn
from check_instance import is_ready
from list_machines import list_machines
import time
import sys

usages = "Usage: python create_machine.py <machine_name> <domain> <flavor> <volume_size>\nIf no volume_size is given, " \
         "by default no volume will be attached"
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print usages
        exit(0)
    else:
        name = sys.argv[1]
        domain = sys.argv[2]
        flavor = sys.argv[3]
        availability_zone = 'melbourne-np'
        # validating domain name
        if "cloudprojectnectar.co" not in domain:
            print "The given domain name should be complete."
            print usages
            exit(-1)

        vol_size = sys.argv[4] if len(sys.argv) > 3 else None

        # Spawning Instance
        reservation = ec2_conn.run_instances('ami-00003837',
                                             key_name='Cloud',
                                             instance_type=flavor,
                                             security_groups=['default'],
                                             placement=availability_zone)


        # Getting the actual created instance
        instance = reservation.instances[0]

        print('New instance {} has been created.'.format(instance.id))
        print "Machine is Spawning..."

        while not is_ready([instance.id]):
            time.sleep(5)
        print "Machine (%s) is Ready" % instance.id
        print "Naming Instance as :%s" % name
        ec2_conn.create_tags([instance.id], {'Name': name})

        # Creating domain name
        reservations = ec2_conn.get_all_reservations(instance_ids=[instance.id])
        print "Mapping domain: %s to IP: %s" % (domain, reservations[0].instances[0].private_ip_address)
        zone1 = route_conn.get_zone("cloudprojectnectar.co")
        zone1.add_record("A", domain, reservations[0].instances[0].private_ip_address)

        # Creating and attaching volume
        if vol_size:
            vol_req = ec2_conn.create_volume(vol_size, availability_zone)
            ec2_conn.create_tags([vol_req.id], {"Name": name + "-volume"})
            curr_vol = ec2_conn.get_all_volumes([vol_req.id])[0]
            while not curr_vol.status=='available':
                time.sleep(5)
                curr_vol = ec2_conn.get_all_volumes([vol_req.id])[0]
            print "Volume created.."

            ec2_conn.attach_volume(vol_req.id, instance.id, '/dev/vdc')
            print "Volume attached at /dev/vdc"

        list_machines([instance.id])

        print "Restarting Instance"
        ec2_conn.stop_instances([instance.id])
        ec2_conn.start_instances([instance.id])
        while not is_ready([instance.id]):
            time.sleep(5)
        print "Instance is Ready"
