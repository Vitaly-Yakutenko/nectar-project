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
import boto
import os
from boto.ec2.regioninfo import RegionInfo

region = RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')

ec2_conn = boto.connect_ec2(aws_access_key_id=os.environ['ENV_KEY'],
                            aws_secret_access_key=os.environ['ENV_SECRET'],
                            is_secure=True,
                            region=region,
                            port=8773,
                            path='/services/Cloud',
                            validate_certs=False
                            )

