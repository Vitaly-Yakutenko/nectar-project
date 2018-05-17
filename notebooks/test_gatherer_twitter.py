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


	
	
if sys.version_info > (3,):
    long = int  # pylint: disable=invalid-name,redefined-builtin

CHARACTER_LIMIT = 280

# A singleton representing a lazily instantiated FileCache.
DEFAULT_CACHE = object()

api = twitter.Api(consumer_key= "sZMPWW0zCEVsHnDyO950hWEWN", 
                  consumer_secret= "KfS6UNO3cTCC6j5xHfjQGaNzBFofDRN98pm5aguCvduIr0UQpg", 
                  access_token_key= "1397965644-WVAG6QSXEBCdHtyAeEgBsKYXEKlkoBBtb58oOAN", 
                  access_token_secret= "V6V2aUVFmUwkUcHhFzOn4XnwdkbCJPLOL65ZSEnRe9d7O",)

statuses = api.GetUserTimeline(screen_name="Ali")
print([s.text for s in statuses])



#To fetch your friends (after being authenticated):
users = api.GetFriends(screen_name="Ali")
print([u.name for u in users])

"""
hashtags = ['bitcoin', 'blockchain', 'btc', 'cryptocurrency', 
                         'crypto','ethereum', 'freebitcoin', 'robotcoingame', 'fintech', 'dogecoin']    
stream = api.GetStreamFilter(track=hashtags, locations=[111, -44, 157, -10], languages=['en'])
print([s.text for s in stream])
"""


