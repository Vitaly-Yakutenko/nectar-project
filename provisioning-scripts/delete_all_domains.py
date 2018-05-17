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
from connect_aws import route_conn
import sys

def delete_domain(domain,type):
    zone1 = route_conn.get_zone("cloudprojectnectar.co")
    record = zone1.find_records(domain, type)
    zone1.delete_record(record)
    return

domains = ["jupyter2.cloudprojectnectar.co", "prod1.cloudprojectnectar.co", "prod2.cloudprojectnectar.co"]

couch_domains = ["couch1.cloudprojectnectar.co", "couch2.cloudprojectnectar.co"]

if __name__=='__main__':
    delete_domains = False
    delete_db_domains = False
    input = raw_input("You are about to delete all sub-domains within cloudprojectnectar.co. Are you really sure you "
                      "want to torch it all?? (Y/N)")

    if input.lower() == 'yes' or input.lower() == 'y':
        delete_domains = True
        input2 = raw_input("Okay, we understand. But let us at least keep our data :(. Are you really that harsh? (Y/N)")
        if input.lower() == 'yes' or input.lower() == 'y':
            print "It didn't have to be this way!\n Destroying everything"
            delete_db_domains = True

    if delete_domains:
        for item in domains:
            delete_domain(item, "A")
        print "Deleted Jupyter and Prod domains"

    if delete_db_domains:
        for item in couch_domains:
            delete_domain(item, "A")
        print "Deleted All CouchDB domains."


