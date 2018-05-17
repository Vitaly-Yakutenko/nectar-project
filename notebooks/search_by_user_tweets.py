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
#twitter _ harvester
#from tweet_api import Api 

from __future__ import division
from __future__ import print_function
import json
import sys
import gzip
import time
import base64
import re
import logging
import requests
from requests_oauthlib import OAuth1, OAuth2
import io
import warnings
from uuid import uuid4
import os
import twitter
try:
    from urllib.parse import urlparse, urlunparse, urlencode, quote_plus
    from urllib.request import __version__ as urllib_version
except ImportError:
    from urlparse import urlparse, urlunparse
    from urllib import urlencode, quote_plus
    from urllib import __version__ as urllib_version
import glob

if sys.version_info > (3,):
    long = int  # pylint: disable=invalid-name,redefined-builtin

CHARACTER_LIMIT = 280

# A singleton representing a lazily instantiated FileCache.
DEFAULT_CACHE = object()

api = twitter.Api(consumer_key= "sZMPWW0zCEVsHnDyO950hWEWN", 
                  consumer_secret= "KfS6UNO3cTCC6j5xHfjQGaNzBFofDRN98pm5aguCvduIr0UQpg", 
                  access_token_key= "1397965644-WVAG6QSXEBCdHtyAeEgBsKYXEKlkoBBtb58oOAN", 
                  access_token_secret= "V6V2aUVFmUwkUcHhFzOn4XnwdkbCJPLOL65ZSEnRe9d7O",)

path = 'shared_folder/user_tweets_tasks/'
filepath_read = glob.glob(os.path.join(path, '*.txt'))
path1 = 'shared_folder/shireens_tweets'
#filepath_write = glob.glob(os.path.join(path, '*.json'))


for filename in filepath_read:
    with open(filename, 'r') as f:
       # Read the first line of the file
        user = f.readline()
        statuses = api.GetUserTimeline(user_id = user[1:-1])
        
        f = open(path1+user[1:-1]+".txt", "a")
        f.write([statuses])
        break