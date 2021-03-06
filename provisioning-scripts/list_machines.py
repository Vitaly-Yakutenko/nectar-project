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
import sys

def list_machines(instance_ids = None):
    reservations = ec2_conn.get_all_reservations(instance_ids=instance_ids)
    for idx, res in enumerate(reservations):
        print('\nID: {}\nIP: {}\nPlacement: {}\n-----------'.format(res.id,
                                                       res.instances[0].private_ip_address,
                                                       res.instances[0].placement))


if __name__=='__main__':
    ids = None
    if len(sys.argv) > 2:
        ids = sys.argv[1].split(',')

    list_machines(ids)