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
from boto import route53
import os

route_conn = route53.connection.Route53Connection(aws_access_key_id=os.environ['AWS_ENV_KEY'],
                                     aws_secret_access_key=os.environ['AWS_ENV_SECRET']
                                     )


