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
from connect import ec2_conn
from connect_aws import route_conn
from check_instance import is_ready
from list_machines import list_machines
import time
import sys
from platform import system as system_name  # Returns the system/OS name
from subprocess import call as system_call  # Execute a shell command

usages = "Usage: python create_machine.py <jupyter|couchdb|production> > <domain> <flavor> <volume_size>\nIf no volume_size is given, " \
         "by default no volume will be attached"

instance_types = ['jupyter', 'couchdb', 'production']


def domain_exists(domain):
    zone1 = route_conn.get_zone("cloudprojectnectar.co")
    record = zone1.find_records(domain, "A")
    if record:
        return True
    return False


def domain_up(domain):
    # Ping command count option as function of OS
    param = '-n 1' if system_name().lower() == 'windows' else '-c 1'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, domain]

    # Pinging
    return system_call(command) == 0


def create_machine(name, domain, flavor = "m1.small", availability_zone = 'melbourne-np', volume = None):
    if name not in instance_types:
        return -1
    elif domain_exists(domain):
        print "Instance with this domain is already registered."
        if domain_up(domain):
            print "Instance is up and running, not creating any instance"
            return 0
        else:
            print "Instance is not up, exiting!"
            return -1
    else:
        instance = None
        try:
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

        except Exception as ex:
            print ex
            print "Error in creating Instance, nothing to rollback"
            return -1

        try:
            if instance is not None:
                print "Naming Instance as :%s" % name
                ec2_conn.create_tags([instance.id], {'Name': name})
        except Exception as ex:
            print ex.message
            print "Error in naming instance, no worries, moving on"

        try:
            # Creating domain name
            reservations = ec2_conn.get_all_reservations(instance_ids=[instance.id])
            print "Mapping domain: %s to IP: %s" % (domain, reservations[0].instances[0].private_ip_address)
            zone1 = route_conn.get_zone("cloudprojectnectar.co")
            zone1.add_record("A", domain, reservations[0].instances[0].private_ip_address)
        except Exception as ex:
            print ex.message
            print "Error in creating domain name, rolling back!"
            delete_machine(instance)
            return -1

        try:
            if volume:
                vol_req = ec2_conn.create_volume(volume, availability_zone)
                ec2_conn.create_tags([vol_req.id], {"Name": name + "-volume"})
                curr_vol = ec2_conn.get_all_volumes([vol_req.id])[0]
                while not curr_vol.status == 'available':
                    time.sleep(5)
                    curr_vol = ec2_conn.get_all_volumes([vol_req.id])[0]
                print "Volume created.."

                ec2_conn.attach_volume(vol_req.id, instance.id, '/dev/vdc')
                print "Volume attached at /dev/vdc"
        except Exception as ex:
            print ex.message
            print "Error in provisioning Volume, rolling back!"
            delete_domain(domain, "A")
            delete_machine(instance)
            return -1

        return 0

def delete_domain(domain,type):
    zone1 = route_conn.get_zone("cloudprojectnectar.co")
    record = zone1.find_records(domain, type)
    zone1.delete_record(record)
    return

def delete_machine(instance):
    ec2_conn.terminate_instances([instance.id])
    return 0

def restart_machine(instance):
    print "Restarting Instance"
    ec2_conn.stop_instances([instance.id])
    ec2_conn.start_instances([instance.id])
    while not is_ready([instance.id]):
        time.sleep(5)
    print "Instance is Ready"
    return 0

def list_machine(instance):
    list_machines([instance.id])

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

        res = create_machine(name, domain, flavor, availability_zone, vol_size)
        if res == -1:
            print "Machine spawning failed"
