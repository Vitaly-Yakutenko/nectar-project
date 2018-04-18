from connect import ec2_conn
import sys

def is_ready(instance_ids = []):
    instances = ec2_conn.get_all_reservations(instance_ids=instance_ids)
    for inst in instances:
        if inst.instances[0].state == 'running':
            return True
        else:
            return False


if __name__=='__main__':
    ids = []
    if len(sys.argv) > 2:
        ids = sys.argv[1].split(',')

    print is_ready(ids)