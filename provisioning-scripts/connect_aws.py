from boto import route53
import os

route_conn = route53.connection.Route53Connection(aws_access_key_id=os.environ['AWS_ENV_KEY'],
                                     aws_secret_access_key=os.environ['AWS_ENV_SECRET']
                                     )


