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
from twitter import (__version__,
                     _FileCache, 
                     Category, 
                     DirectMessage, 
                     List, 
                     Status, 
                     Trend, 
                     User, 
                     UserStatus,
                    )
from twitter.ratelimit import RateLimit
from twitter.twitter_utils import (
    calc_expected_status_length,
    is_url,
    parse_media_file,
    enf_type,
    parse_arg_list)
from twitter.error import (
    TwitterError,
    PythonTwitterDeprecationWarning330,
)

logger = logging.getLogger(__name__)

class Api(object):


    DEFAULT_CACHE_TIMEOUT = 60  # cache for 1 minute
    _API_REALM = 'Twitter API'

    def __init__(self,
                 consumer_key=None,
                 consumer_secret=None,
                 access_token_key=None,
                 access_token_secret=None,
                 application_only_auth=False,
                 input_encoding=None,
                 request_headers=None,
                 cache=DEFAULT_CACHE,
                 base_url=None,
                 stream_url=None,
                 upload_url=None,
                 chunk_size=1024 * 1024,
                 use_gzip_compression=False,
                 debugHTTP=False,
                 timeout=None,
                 sleep_on_rate_limit=False,
                 tweet_mode='compat',
                 proxies=None):
        
        # check to see if the library is running on a Google App Engine instance
        # see GAE.rst for more information
        if os.environ:
            if 'APPENGINE_RUNTIME' in os.environ.keys():
                # Adapter ensures requests use app engine's urlfetch
                import requests_toolbelt.adapters.appengine
                requests_toolbelt.adapters.appengine.monkeypatch()
                # App Engine does not like this caching strategy, disable caching
                cache = None

        self.SetCache(cache)
        self._cache_timeout = Api.DEFAULT_CACHE_TIMEOUT
        self._input_encoding = input_encoding
        self._use_gzip = use_gzip_compression
        self._debugHTTP = debugHTTP
        self._shortlink_size = 19
        if timeout and timeout < 30:
            warnings.warn("Warning: The Twitter streaming API sends 30s keepalives, the given timeout is shorter!")
        self._timeout = timeout
        self.__auth = None

        self._InitializeRequestHeaders(request_headers)
        self._InitializeUserAgent()
        self._InitializeDefaultParameters()

        self.rate_limit = RateLimit()
        self.sleep_on_rate_limit = sleep_on_rate_limit
        self.tweet_mode = tweet_mode
        self.proxies = proxies

        if base_url is None:
            self.base_url = 'https://api.twitter.com/1.1'
        else:
            self.base_url = base_url

        if stream_url is None:
            self.stream_url = 'https://stream.twitter.com/1.1'
        else:
            self.stream_url = stream_url

        if upload_url is None:
            self.upload_url = 'https://upload.twitter.com/1.1'
        else:
            self.upload_url = upload_url

        self.chunk_size = chunk_size

        if self.chunk_size < 1024 * 16:
            warnings.warn((
                "A chunk size lower than 16384 may result in too many "
                "requests to the Twitter API when uploading videos. You are "
                "strongly advised to increase it above 16384"))

        if (consumer_key and not
           (application_only_auth or all([access_token_key, access_token_secret]))):
            raise TwitterError({'message': "Missing oAuth Consumer Key or Access Token"})

        self.SetCredentials(consumer_key, consumer_secret, access_token_key, access_token_secret,
                            application_only_auth)

        if debugHTTP:
            try:
                import http.client as http_client  # python3
            except ImportError:
                import httplib as http_client  # python2

            http_client.HTTPConnection.debuglevel = 1

            logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    def GetAppOnlyAuthToken(consumer_key, consumer_secret):
        
        key = quote_plus(consumer_key)
        secret = quote_plus(consumer_secret)
        bearer_token = base64.b64encode('{}:{}'.format(key, secret).encode('utf8'))

        post_headers = {
            'Authorization': 'Basic {0}'.format(bearer_token.decode('utf8')),
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

        res = requests.post(url='https://api.twitter.com/oauth2/token',
                            data={'grant_type': 'client_credentials'},
                            headers=post_headers)
        bearer_creds = res.json()
        return bearer_creds

	def SetCredentials(self,
                       consumer_key:"sZMPWW0zCEVsHnDyO950hWEWN",
					   consumer_secret: "KfS6UNO3cTCC6j5xHfjQGaNzBFofDRN98pm5aguCvduIr0UQpg", 
                       access_token_key:"1397965644-WVAG6QSXEBCdHtyAeEgBsKYXEKlkoBBtb58oOAN",
                       access_token_secret: "V6V2aUVFmUwkUcHhFzOn4XnwdkbCJPLOL65ZSEnRe9d7O",
                       application_only_auth=False):
        
		  
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_token_key = access_token_key
        self._access_token_secret = access_token_secret

        if application_only_auth:
            self._bearer_token = self.GetAppOnlyAuthToken(consumer_key, consumer_secret)
            self.__auth = OAuth2(token=self._bearer_token)
        else:
            auth_list = [consumer_key, consumer_secret,
                         access_token_key, access_token_secret]
            if all(auth_list):
                self.__auth = OAuth1(consumer_key, consumer_secret,
                                     access_token_key, access_token_secret)

        self._config = None

	def GetHelpConfiguration(self):

        if self._config is None:
            url = '%s/help/configuration.json' % self.base_url
            resp = self._RequestUrl(url, 'GET')
            data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))
            self._config = data
        return self._config

	def GetShortUrlLength(self, https=False):

        config = self.GetHelpConfiguration()
        if https:
            return config['short_url_length_https']
        else:
            return config['short_url_length']

	def ClearCredentials(self):
        """Clear any credentials for this instance
        """
        self._consumer_key = None
        self._consumer_secret = None
        self._access_token_key = None
        self._access_token_secret = None
        self._bearer_token = None
        self.__auth = None  # for request upgrade

	def GetSearch(self,
                  term=None,
                  raw_query=None,
                  geocode=None,
                  since_id=None,
                  max_id=None,
                  until=None,
                  since=None,
                  count=15,
                  lang='en',
                  locale=None,
                  result_type="mixed",
                  include_entities=None,
                  return_json=False):

        url= '%s/search/tweets.json' % self.base_url
        parameters = {}

        if since_id:
            parameters['since_id'] = enf_type('since_id', int, since_id)

        if max_id:
            parameters['max_id'] = enf_type('max_id', int, max_id)

        if until:
            parameters['until'] = enf_type('until', str, until)

        if since:
            parameters['since'] = enf_type('since', str, since)

        if lang:
            parameters['lang'] = enf_type('lang', str, lang)

        if locale:
            parameters['locale'] = enf_type('locale', str, locale)

        if term is None and geocode is None and raw_query is None:
            return []

        if term is not None:
            parameters['q'] = term

        if geocode is not None:
            if isinstance(geocode, list) or isinstance(geocode, tuple):
                parameters['geocode'] = ','.join([str(geo) for geo in geocode])
            else:
                parameters['geocode'] = enf_type('geocode', str, geocode)

        if include_entities:
            parameters['include_entities'] = enf_type('include_entities',
                                                      bool,
                                                      include_entities)

        parameters['count'] = enf_type('count', int, count)

        if result_type in ["mixed", "popular", "recent"]:
            parameters['result_type'] = result_type

        if raw_query is not None:
            url = "{url}?{raw_query}".format(
                url=url,
                raw_query=raw_query)
            resp = self._RequestUrl(url, 'GET')
        else:
            resp = self._RequestUrl(url, 'GET', data=parameters)

        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))
        if return_json:
            return data
        else:
            return [Status.NewFromJsonDict(x) for x in data.get('statuses', '')]

	def GetUsersSearch(self,
                       term='#bitcoin',
                       page=10,
                       count=200,
                       include_entities=None):

        parameters = {}

        if term is not None:
            parameters['q'] = term

        if page != 1:
            parameters['page'] = page

        if include_entities:
            parameters['include_entities'] = 1

        try:
            parameters['count'] = int(count)
        except ValueError:
            raise TwitterError({'message': "count must be an integer"})

        # Make and send requests
        url = '%s/users/search.json' % self.base_url
        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))
        return [User.NewFromJsonDict(x) for x in data]

	def GetUserSuggestionCategories(self):
        url = '%s/users/suggestions.json' % (self.base_url)
        resp = self._RequestUrl(url, verb='GET')
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        categories = []

        for category in data:
            categories.append(Category.NewFromJsonDict(category))
        return categories

    def GetUserSuggestion(self, category):
        url = '%s/users/suggestions/%s.json' % (self.base_url, category.slug)

        resp = self._RequestUrl(url, verb='GET')
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        users = []
        for user in data['users']:
            users.append(User.NewFromJsonDict(user))
        return users

	def GetHomeTimeline(self,
                        count=100,
                        since_id=None,
                        max_id=None,
                        trim_user=False,
                        exclude_replies=False,
                        contributor_details=False,
                        include_entities=True):
        
        url = '%s/statuses/home_timeline.json' % self.base_url

        parameters = {}
        if count is not None:
            try:
                if int(count) > 200:
                    raise TwitterError({'message': "'count' may not be greater than 200"})
            except ValueError:
                raise TwitterError({'message': "'count' must be an integer"})
            parameters['count'] = count
        if since_id:
            try:
                parameters['since_id'] = int(since_id)
            except ValueError:
                raise TwitterError({'message': "'since_id' must be an integer"})
        if max_id:
            try:
                parameters['max_id'] = int(max_id)
            except ValueError:
                raise TwitterError({'message': "'max_id' must be an integer"})
        if trim_user:
            parameters['trim_user'] = 1
        if exclude_replies:
            parameters['exclude_replies'] = 1
        if contributor_details:
            parameters['contributor_details'] = 1
        if not include_entities:
            parameters['include_entities'] = 'false'
        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return [Status.NewFromJsonDict(x) for x in data]

	def GetUserTimeline(self,
                        user_id=None,
                        screen_name=None,
                        since_id=None,
                        max_id=None,
                        count=None,
                        include_rts=True,
                        trim_user=False,
                        exclude_replies=False):

        url = '%s/statuses/user_timeline.json' % (self.base_url)
        parameters = {}

        if user_id:
            parameters['user_id'] = enf_type('user_id', int, user_id)
        elif screen_name:
            parameters['screen_name'] = screen_name
        if since_id:
            parameters['since_id'] = enf_type('since_id', int, since_id)
        if max_id:
            parameters['max_id'] = enf_type('max_id', int, max_id)
        if count:
            parameters['count'] = enf_type('count', int, count)

        parameters['include_rts'] = enf_type('include_rts', bool, include_rts)
        parameters['trim_user'] = enf_type('trim_user', bool, trim_user)
        parameters['exclude_replies'] = enf_type('exclude_replies', bool, exclude_replies)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return [Status.NewFromJsonDict(x) for x in data]

	def GetStatus(self,
                  status_id,
                  trim_user=False,
                  include_my_retweet=True,
                  include_entities=True,
                  include_ext_alt_text=True):

        url = '%s/statuses/show.json' % (self.base_url)

        parameters = {
            'id': enf_type('status_id', int, status_id),
            'trim_user': enf_type('trim_user', bool, trim_user),
            'include_my_retweet': enf_type('include_my_retweet', bool, include_my_retweet),
            'include_entities': enf_type('include_entities', bool, include_entities),
            'include_ext_alt_text': enf_type('include_ext_alt_text', bool, include_ext_alt_text)
        }

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return Status.NewFromJsonDict(data)

	def GetStatuses(self,
                    status_ids,
                    trim_user=False,
                    include_entities=True,
                    map=False):

        url = '%s/statuses/lookup.json' % (self.base_url)

        map = enf_type('map', bool, map)

        if map:
            result = {}
        else:
            result = []
        offset = 0
        parameters = {
            'trim_user': enf_type('trim_user', bool, trim_user),
            'include_entities': enf_type('include_entities', bool, include_entities),
            'map': map
        }
        while offset < len(status_ids):
            parameters['id'] = ','.join([str(enf_type('status_id', int, status_id)) for status_id in status_ids[offset:offset + 100]])

            resp = self._RequestUrl(url, 'GET', data=parameters)
            data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))
            if map:
                result.update({int(key): (Status.NewFromJsonDict(value) if value else None) for key, value in data['id'].items()})
            else:
                result += [Status.NewFromJsonDict(dataitem) for dataitem in data]

            offset += 100

        return result

	def GetStatusOembed(self,
                        status_id=None,
                        url=None,
                        maxwidth=None,
                        hide_media=False,
                        hide_thread=False,
                        omit_script=False,
                        align=None,
                        related=None,
                        lang=None):

        request_url = '%s/statuses/oembed.json' % (self.base_url)

        parameters = {}

        if status_id is not None:
            try:
                parameters['id'] = int(status_id)
            except ValueError:
                raise TwitterError({'message': "'status_id' must be an integer."})
        elif url is not None:
            parameters['url'] = url
        else:
            raise TwitterError({'message': "Must specify either 'status_id' or 'url'"})

        if maxwidth is not None:
            parameters['maxwidth'] = maxwidth
        if hide_media is True:
            parameters['hide_media'] = 'true'
        if hide_thread is True:
            parameters['hide_thread'] = 'true'
        if omit_script is True:
            parameters['omit_script'] = 'true'
        if align is not None:
            if align not in ('left', 'center', 'right', 'none'):
                raise TwitterError({'message': "'align' must be 'left', 'center', 'right', or 'none'"})
            parameters['align'] = align
        if related:
            if not isinstance(related, str):
                raise TwitterError({'message': "'related' should be a string of comma separated screen names"})
            parameters['related'] = related
        if lang is not None:
            if not isinstance(lang, str):
                raise TwitterError({'message': "'lang' should be string instance"})
            parameters['lang'] = lang

        resp = self._RequestUrl(request_url, 'GET', data=parameters, enforce_auth=False)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return data

	def DestroyStatus(self, status_id, trim_user=False):

        url = '%s/statuses/destroy/%s.json' % (self.base_url, status_id)

        post_data = {
            'id': enf_type('status_id', int, status_id),
            'trim_user': enf_type('trim_user', bool, trim_user)
        }

        resp = self._RequestUrl(url, 'POST', data=post_data)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return Status.NewFromJsonDict(data)

    def _TweetTextWrap(self,
                       status,
                       char_lim=CHARACTER_LIMIT):

        if not self._config:
            self.GetHelpConfiguration()

        tweets = []
        line = []
        line_length = 0
        words = re.split(r'\s', status)

        if len(words) == 1 and not is_url(words[0]):
            if len(words[0]) > CHARACTER_LIMIT:
                raise TwitterError("Unable to split status into tweetable parts. Word was: {0}/{1}".format(len(words[0]), char_lim))
            else:
                tweets.append(words[0])
                return tweets

        for word in words:
            if len(word) > char_lim:
                raise TwitterError("Unable to split status into tweetable parts. Word was: {0}/{1}".format(len(word), char_lim))
            new_len = line_length

            if is_url(word):
                new_len = line_length + self._config['short_url_length_https'] + 1
            else:
                new_len += len(word) + 1

            if new_len > CHARACTER_LIMIT:
                tweets.append(' '.join(line))
                line = [word]
                line_length = new_len - line_length
            else:
                line.append(word)
                line_length = new_len

        tweets.append(' '.join(line))
        return tweets

	def PostUpdates(self,
                    status,
                    continuation=None,
                    **kwargs):

        results = list()

        if continuation is None:
            continuation = ''
        char_limit = CHARACTER_LIMIT - len(continuation)

        tweets = self._TweetTextWrap(status=status, char_lim=char_limit)

        if len(tweets) == 1:
            results.append(self.PostUpdate(status=tweets[0], **kwargs))
            return results

        for tweet in tweets[0:-1]:
            results.append(self.PostUpdate(status=tweet + continuation, **kwargs))
        results.append(self.PostUpdate(status=tweets[-1], **kwargs))

        return results

	def PostRetweet(self, status_id, trim_user=False):

        try:
            if int(status_id) <= 0:
                raise TwitterError({'message': "'status_id' must be a positive number"})
        except ValueError:
            raise TwitterError({'message': "'status_id' must be an integer"})

        url = '%s/statuses/retweet/%s.json' % (self.base_url, status_id)
        data = {'id': status_id}
        if trim_user:
            data['trim_user'] = 'true'
        resp = self._RequestUrl(url, 'POST', data=data)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return Status.NewFromJsonDict(data)

	def GetUserRetweets(self,
                        count=None,
                        since_id=None,
                        max_id=None,
                        trim_user=False):

        return self.GetUserTimeline(
            since_id=since_id,
            count=count,
            max_id=max_id,
            trim_user=trim_user,
            exclude_replies=True,
            include_rts=True)

	def GetReplies(self,
                   since_id=None,
                   count=None,
                   max_id=None,
                   trim_user=False):

        return self.GetUserTimeline(since_id=since_id, count=count, max_id=max_id, trim_user=trim_user,
                                    exclude_replies=False, include_rts=False)

	def GetRetweets(self,
                    statusid,
                    count=None,
                    trim_user=False):

        url = '%s/statuses/retweets/%s.json' % (self.base_url, statusid)
        parameters = {
            'trim_user': enf_type('trim_user', bool, trim_user),
        }

        if count:
            parameters['count'] = enf_type('count', int, count)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return [Status.NewFromJsonDict(s) for s in data]

	def GetRetweeters(self,
                      status_id,
                      cursor=None,
                      count=100,
                      stringify_ids=False):

        url = '%s/statuses/retweeters/ids.json' % (self.base_url)
        parameters = {
            'id': enf_type('id', int, status_id),
            'stringify_ids': enf_type('stringify_ids', bool, stringify_ids),
            'count': count,
        }

        result = []

        total_count = 0
        while True:
            if cursor:
                try:
                    parameters['cursor'] = int(cursor)
                except ValueError:
                    raise TwitterError({'message': "cursor must be an integer"})
            resp = self._RequestUrl(url, 'GET', data=parameters)
            data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))
            result += [x for x in data['ids']]
            if 'next_cursor' in data:
                if data['next_cursor'] == 0 or data['next_cursor'] == data['previous_cursor']:
                    break
                else:
                    cursor = data['next_cursor']
                    total_count -= len(data['ids'])
                    if total_count < 1:
                        break
            else:
                break

        return result

	def GetRetweetsOfMe(self,
                        count=None,
                        since_id=None,
                        max_id=None,
                        trim_user=False,
                        include_entities=True,
                        include_user_entities=True):
       
        url = '%s/statuses/retweets_of_me.json' % self.base_url
        if count is not None:
            try:
                if int(count) > 100:
                    raise TwitterError({'message': "'count' may not be greater than 100"})
            except ValueError:
                raise TwitterError({'message': "'count' must be an integer"})
        parameters = {
            'count': count,
            'since_id': since_id,
            'max_id': max_id,
            'trim_user': bool(trim_user),
            'include_entities': bool(include_entities),
            'include_user_entities': bool(include_user_entities),
        }

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return [Status.NewFromJsonDict(s) for s in data]

    def _GetBlocksMutesPaged(self,
                             endpoint,
                             action,
                             cursor=-1,
                             skip_status=False,
                             include_entities=True,
                             stringify_ids=False):

        urls = {
            'mute': {
                'list': '%s/mutes/users/list.json' % self.base_url,
                'ids': '%s/mutes/users/ids.json' % self.base_url
            },
            'block': {
                'list': '%s/blocks/list.json' % self.base_url,
                'ids': '%s/blocks/ids.json' % self.base_url
            }
        }

        url = urls[endpoint][action]

        result = []
        parameters = {
            'skip_status': bool(skip_status),
            'include_entities': bool(include_entities),
            'stringify_ids': bool(stringify_ids),
            'cursor': cursor,
        }

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if action == 'ids':
            result += data.get('ids')
        else:
            result += [User.NewFromJsonDict(x) for x in data['users']]
        next_cursor = data.get('next_cursor', 0)
        previous_cursor = data.get('previous_cursor', 0)

        return next_cursor, previous_cursor, result

	def GetBlocks(self,
                  skip_status=False,
                  include_entities=False):
        result = []
        cursor = -1

        while True:
            next_cursor, previous_cursor, users = self.GetBlocksPaged(
                cursor=cursor,
                skip_status=skip_status,
                include_entities=include_entities)
            result += users
            if next_cursor == 0 or next_cursor == previous_cursor:
                break
            else:
                cursor = next_cursor

        return result

	def GetBlocksPaged(self,
                       cursor=-1,
                       skip_status=False,
                       include_entities=False):
        return self._GetBlocksMutesPaged(endpoint='block',
                                         action='list',
                                         cursor=cursor,
                                         skip_status=skip_status,
                                         include_entities=include_entities)

	def GetBlocksIDs(self,
                     stringify_ids=False):
        result = []
        cursor = -1

        while True:
            next_cursor, previous_cursor, user_ids = self.GetBlocksIDsPaged(
                cursor=cursor,
                stringify_ids=stringify_ids)
            result += user_ids
            if next_cursor == 0 or next_cursor == previous_cursor:
                break
            else:
                cursor = next_cursor

        return result


	def GetBlocksIDsPaged(self,
                          cursor=-1,
                          stringify_ids=False):
        return self._GetBlocksMutesPaged(endpoint='block',
                                         action='ids',
                                         cursor=cursor,
                                         stringify_ids=stringify_ids)

    def _GetIDsPaged(self,
                     url,
                     user_id,
                     screen_name,
                     cursor,
                     stringify_ids,
                     count):

        result = []

        parameters = {}
        if user_id is not None:
            parameters['user_id'] = user_id
        if screen_name is not None:
            parameters['screen_name'] = screen_name
        if count is not None:
            parameters['count'] = count
        parameters['stringify_ids'] = stringify_ids
        parameters['cursor'] = cursor

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if 'ids' in data:
            result.extend([x for x in data['ids']])

        next_cursor = data.get('next_cursor', 0)
        previous_cursor = data.get('previous_cursor', 0)

        return next_cursor, previous_cursor, result

	def GetFollowerIDsPaged(self,
                            user_id=None,
                            screen_name=None,
                            cursor=-1,
                            stringify_ids=False,
                            count=5000):

        url = '%s/followers/ids.json' % self.base_url
        return self._GetIDsPaged(url=url,
                                 user_id=user_id,
                                 screen_name=screen_name,
                                 cursor=cursor,
                                 stringify_ids=stringify_ids,
                                 count=count)

	def GetFriendIDsPaged(self,
                          user_id=None,
                          screen_name=None,
                          cursor=-1,
                          stringify_ids=False,
                          count=5000):

        url = '%s/friends/ids.json' % self.base_url
        return self._GetIDsPaged(url,
                                 user_id,
                                 screen_name,
                                 cursor,
                                 stringify_ids,
                                 count)

    def _GetFriendFollowerIDs(self,
                              url=None,
                              user_id=None,
                              screen_name=None,
                              cursor=None,
                              count=None,
                              stringify_ids=False,
                              total_count=None):
        """ Common method for GetFriendIDs and GetFollowerIDs """

        count = 5000
        cursor = -1
        result = []

        if total_count:
            total_count = enf_type('total_count', int, total_count)

        if total_count and total_count < count:
            count = total_count

        while True:
            if total_count is not None and len(result) + count > total_count:
                break

            next_cursor, previous_cursor, data = self._GetIDsPaged(
                url=url,
                user_id=user_id,
                screen_name=screen_name,
                cursor=cursor,
                stringify_ids=stringify_ids,
                count=count)

            result.extend([x for x in data])

            if next_cursor == 0 or next_cursor == previous_cursor:
                break
            else:
                cursor = next_cursor

        return result

	def GetFollowerIDs(self,
                       user_id=None,
                       screen_name=None,
                       cursor=None,
                       stringify_ids=False,
                       count=None,
                       total_count=None):
       
        url = '%s/followers/ids.json' % self.base_url
        return self._GetFriendFollowerIDs(url=url,
                                          user_id=user_id,
                                          screen_name=screen_name,
                                          cursor=cursor,
                                          stringify_ids=stringify_ids,
                                          count=count,
                                          total_count=total_count)

	def GetFriendIDs(self,
                     user_id=None,
                     screen_name=None,
                     cursor=None,
                     count=None,
                     stringify_ids=False,
                     total_count=None):
        
        url = '%s/friends/ids.json' % self.base_url
        return self._GetFriendFollowerIDs(url,
                                          user_id,
                                          screen_name,
                                          cursor,
                                          count,
                                          stringify_ids,
                                          total_count)

    def _GetFriendsFollowersPaged(self,
                                  url=None,
                                  user_id=None,
                                  screen_name=None,
                                  cursor=-1,
                                  count=200,
                                  skip_status=False,
                                  include_user_entities=True):

       
        if user_id and screen_name:
            warnings.warn(
                "If both user_id and screen_name are specified, Twitter will "
                "return the followers of the user specified by screen_name, "
                "however this behavior is undocumented by Twitter and might "
                "change without warning.", stacklevel=2)

        parameters = {}

        if user_id is not None:
            parameters['user_id'] = user_id
        if screen_name is not None:
            parameters['screen_name'] = screen_name

        try:
            parameters['count'] = int(count)
        except ValueError:
            raise TwitterError({'message': "count must be an integer"})

        parameters['skip_status'] = skip_status
        parameters['include_user_entities'] = include_user_entities
        parameters['cursor'] = cursor

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if 'users' in data:
            users = [User.NewFromJsonDict(user) for user in data['users']]
        else:
            users = []

        if 'next_cursor' in data:
            next_cursor = data['next_cursor']
        else:
            next_cursor = 0
        if 'previous_cursor' in data:
            previous_cursor = data['previous_cursor']
        else:
            previous_cursor = 0

        return next_cursor, previous_cursor, users

	def GetFollowersPaged(self,
                          user_id=None,
                          screen_name=None,
                          cursor=-1,
                          count=200,
                          skip_status=False,
                          include_user_entities=True):

        url = '%s/followers/list.json' % self.base_url
        return self._GetFriendsFollowersPaged(url,
                                              user_id,
                                              screen_name,
                                              cursor,
                                              count,
                                              skip_status,
                                              include_user_entities)

	def GetFriendsPaged(self,
                        user_id=None,
                        screen_name=None,
                        cursor=-1,
                        count=200,
                        skip_status=False,
                        include_user_entities=True):

        url = '%s/friends/list.json' % self.base_url
        return self._GetFriendsFollowersPaged(url,
                                              user_id,
                                              screen_name,
                                              cursor,
                                              count,
                                              skip_status,
                                              include_user_entities)

    def _GetFriendsFollowers(self,
                             url=None,
                             user_id=None,
                             screen_name=None,
                             cursor=None,
                             count=None,
                             total_count=None,
                             skip_status=False,
                             include_user_entities=True):

       
        if cursor is not None or count is not None:
            warnings.warn(
                "Use of 'cursor' and 'count' parameters are deprecated as of "
                "python-twitter 3.0. Please use GetFriendsPaged or "
                "GetFollowersPaged instead.",
                PythonTwitterDeprecationWarning330)

        count = 200
        cursor = -1
        result = []

        if total_count:
            try:
                total_count = int(total_count)
            except ValueError:
                raise TwitterError({'message': "total_count must be an integer"})

            if total_count <= 200:
                count = total_count

        while True:
            if total_count is not None and len(result) + count > total_count:
                break

            next_cursor, previous_cursor, data = self._GetFriendsFollowersPaged(
                url,
                user_id,
                screen_name,
                cursor,
                count,
                skip_status,
                include_user_entities)

            if next_cursor:
                cursor = next_cursor

            result.extend(data)

            if next_cursor == 0 or next_cursor == previous_cursor:
                break

        return result
    

	def GetFollowers(self,
                     user_id=None,
                     screen_name=None,
                     cursor=None,
                     count=None,
                     total_count=None,
                     skip_status=False,
                     include_user_entities=True):
        
        url = '%s/followers/list.json' % self.base_url
        return self._GetFriendsFollowers(url,
                                         user_id,
                                         screen_name,
                                         cursor,
                                         count,
                                         total_count,
                                         skip_status,
                                         include_user_entities)

	def GetFriends(self,
                   user_id=None,
                   screen_name=None,
                   cursor=None,
                   count=None,
                   total_count=None,
                   skip_status=False,
                   include_user_entities=True):
       
        url = '%s/friends/list.json' % self.base_url
        return self._GetFriendsFollowers(url,
                                         user_id,
                                         screen_name,
                                         cursor,
                                         count,
                                         total_count,
                                         skip_status,
                                         include_user_entities)

	def UsersLookup(self,
                    user_id=None,
                    screen_name=None,
                    users=None,
                    include_entities=True,
                    return_json=False):
        
        if not any([user_id, screen_name, users]):
            raise TwitterError("Specify at least one of user_id, screen_name, or users.")

        url = '%s/users/lookup.json' % self.base_url
        parameters = {
            'include_entities': include_entities
        }
        uids = list()
        if user_id:
            uids.extend(user_id)
        if users:
            uids.extend([u.id for u in users])
        if len(uids):
            parameters['user_id'] = ','.join([str(u) for u in uids])
        if screen_name:
            parameters['screen_name'] = parse_arg_list(screen_name, 'screen_name')

        if len(uids) > 100:
            raise TwitterError("No more than 100 users may be requested per request.")

        print(parameters)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return [User.NewFromJsonDict(u) for u in data]

	def GetUser(self,
                user_id=None,
                screen_name=None,
                include_entities=True,
                return_json=False):
        
        url = '%s/users/show.json' % (self.base_url)
        parameters = {
            'include_entities': include_entities
        }
        if user_id:
            parameters['user_id'] = user_id
        elif screen_name:
            parameters['screen_name'] = screen_name
        else:
            raise TwitterError("Specify at least one of user_id or screen_name.")

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return User.NewFromJsonDict(data)

	def GetDirectMessages(self,
                          since_id=None,
                          max_id=None,
                          count=None,
                          include_entities=True,
                          skip_status=False,
                          full_text=False,
                          page=None,
                          return_json=False):
       
        url = '%s/direct_messages.json' % self.base_url
        parameters = {
            'full_text': bool(full_text),
            'include_entities': bool(include_entities),
            'max_id': max_id,
            'since_id': since_id,
            'skip_status': bool(skip_status),
        }

        if count:
            parameters['count'] = enf_type('count', int, count)
        if page:
            parameters['page'] = enf_type('page', int, page)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return [DirectMessage.NewFromJsonDict(x) for x in data]

	def GetSentDirectMessages(self,
                              since_id=None,
                              max_id=None,
                              count=None,
                              page=None,
                              include_entities=True,
                              return_json=False):
        url = '%s/direct_messages/sent.json' % self.base_url

        parameters = {
            'include_entities': bool(include_entities),
            'max_id': max_id,
            'since_id': since_id,
        }

        if count:
            parameters['count'] = enf_type('count', int, count)
        if page:
            parameters['page'] = enf_type('page', int, page)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return [DirectMessage.NewFromJsonDict(x) for x in data]


	def PostDirectMessage(self,
                          text,
                          user_id=None,
                          screen_name=None,
                          return_json=False):
       
        url = '%s/direct_messages/new.json' % self.base_url
        data = {'text': text}
        if user_id:
            data['user_id'] = user_id
        elif screen_name:
            data['screen_name'] = screen_name
        else:
            raise TwitterError({'message': "Specify at least one of user_id or screen_name."})

        resp = self._RequestUrl(url, 'POST', data=data)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return DirectMessage.NewFromJsonDict(data)

	def GetFavorites(self,
                     user_id=None,
                     screen_name=None,
                     count=None,
                     since_id=None,
                     max_id=None,
                     include_entities=True,
                     return_json=False):
        
        parameters = {}
        url = '%s/favorites/list.json' % self.base_url
        if user_id:
            parameters['user_id'] = enf_type('user_id', int, user_id)
        elif screen_name:
            parameters['screen_name'] = screen_name
        if since_id:
            parameters['since_id'] = enf_type('since_id', int, since_id)
        if max_id:
            parameters['max_id'] = enf_type('max_id', int, max_id)
        if count:
            parameters['count'] = enf_type('count', int, count)
        parameters['include_entities'] = enf_type('include_entities', bool, include_entities)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return [Status.NewFromJsonDict(x) for x in data]

	def GetMentions(self,
                    count=None,
                    since_id=None,
                    max_id=None,
                    trim_user=False,
                    contributor_details=False,
                    include_entities=True,
                    return_json=False):
        
        url = '%s/statuses/mentions_timeline.json' % self.base_url

        parameters = {
            'contributor_details': bool(contributor_details),
            'include_entities': bool(include_entities),
            'max_id': max_id,
            'since_id': since_id,
            'trim_user': bool(trim_user),
        }

        if count:
            parameters['count'] = enf_type('count', int, count)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return [Status.NewFromJsonDict(x) for x in data]

    def _IDList(list_id, slug, owner_id, owner_screen_name):
        parameters = {}
        if list_id is not None:
            parameters['list_id'] = enf_type('list_id', int, list_id)
        elif slug is not None:
            parameters['slug'] = slug
            if owner_id is not None:
                parameters['owner_id'] = enf_type('owner_id', int, owner_id)
            elif owner_screen_name is not None:
                parameters['owner_screen_name'] = owner_screen_name
            else:
                raise TwitterError({'message': (
                    'If specifying a list by slug, an owner_id or '
                    'owner_screen_name must also be given.')})
        else:
            raise TwitterError({'message': (
                'Either list_id or slug and one of owner_id and '
                'owner_screen_name must be passed.')})

        return parameters

	def CreateList(self, name, mode=None, description=None):
        """Creates a new list with the give name for the authenticated user.

          twitter.list.List: A twitter.List instance representing the new list
        """
        url = '%s/lists/create.json' % self.base_url
        parameters = {'name': name}
        if mode is not None:
            parameters['mode'] = mode
        if description is not None:
            parameters['description'] = description

        resp = self._RequestUrl(url, 'POST', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return List.NewFromJsonDict(data)

	def DestroyList(self,
                    owner_screen_name=None,
                    owner_id=None,
                    list_id=None,
                    slug=None):
        """Destroys the list identified by list_id or slug and one of
        owner_screen_name or owner_id.

       
          twitter.list.List: A twitter.List instance representing the
          removed list.
        """
        url = '%s/lists/destroy.json' % self.base_url
        parameters = {}

        parameters.update(self._IDList(list_id=list_id,
                                       slug=slug,
                                       owner_id=owner_id,
                                       owner_screen_name=owner_screen_name))

        resp = self._RequestUrl(url, 'POST', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return List.NewFromJsonDict(data)

	def CreateSubscription(self,
                           owner_screen_name=None,
                           owner_id=None,
                           list_id=None,
                           slug=None):
        """Creates a subscription to a list by the authenticated user.

          twitter.user.User: A twitter.User instance representing the user subscribed
        """
        url = '%s/lists/subscribers/create.json' % self.base_url
        parameters = {}

        parameters.update(self._IDList(list_id=list_id,
                                       slug=slug,
                                       owner_id=owner_id,
                                       owner_screen_name=owner_screen_name))

        resp = self._RequestUrl(url, 'POST', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return User.NewFromJsonDict(data)

    
	def GetMemberships(self,
                       user_id=None,
                       screen_name=None,
                       count=20,
                       cursor=-1,
                       filter_to_owned_lists=False,
                       return_json=False):
        """Obtain the lists the specified user is a member of. If no user_id or
        screen_name is specified, the data returned will be for the
        authenticated user.

        
          list: A list of twitter.List instances, one for each list in which
          the user specified by user_id or screen_name is a member
        """
        url = '%s/lists/memberships.json' % (self.base_url)
        parameters = {}
        if cursor is not None:
            parameters['cursor'] = enf_type('cursor', int, cursor)
        if count is not None:
            parameters['count'] = enf_type('count', int, count)
        if filter_to_owned_lists:
            parameters['filter_to_owned_lists'] = enf_type(
                'filter_to_owned_lists', bool, filter_to_owned_lists)

        if user_id is not None:
            parameters['user_id'] = enf_type('user_id', int, user_id)
        elif screen_name is not None:
            parameters['screen_name'] = screen_name

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return [List.NewFromJsonDict(x) for x in data['lists']]

	def GetListsList(self,
                     screen_name=None,
                     user_id=None,
                     reverse=False,
                     return_json=False):
       
        url = '%s/lists/list.json' % (self.base_url)
        parameters = {}
        if user_id:
            parameters['user_id'] = enf_type('user_id', int, user_id)
        elif screen_name:
            parameters['screen_name'] = screen_name
        if reverse:
            parameters['reverse'] = enf_type('reverse', bool, reverse)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return [List.NewFromJsonDict(x) for x in data]

	def GetListTimeline(self,
                        list_id=None,
                        slug=None,
                        owner_id=None,
                        owner_screen_name=None,
                        since_id=None,
                        max_id=None,
                        count=None,
                        include_rts=True,
                        include_entities=True,
                        return_json=False):
        
        url = '%s/lists/statuses.json' % self.base_url
        parameters = {}

        parameters.update(self._IDList(list_id=list_id,
                                       slug=slug,
                                       owner_id=owner_id,
                                       owner_screen_name=owner_screen_name))

        if since_id:
            parameters['since_id'] = enf_type('since_id', int, since_id)
        if max_id:
            parameters['max_id'] = enf_type('max_id', int, max_id)
        if count:
            parameters['count'] = enf_type('count', int, count)
        if not include_rts:
            parameters['include_rts'] = enf_type('include_rts', bool, include_rts)
        if not include_entities:
            parameters['include_entities'] = enf_type('include_entities', bool, include_entities)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        if return_json:
            return data
        else:
            return [Status.NewFromJsonDict(x) for x in data]

	def GetListMembersPaged(self,
                            list_id=None,
                            slug=None,
                            owner_id=None,
                            owner_screen_name=None,
                            cursor=-1,
                            count=100,
                            skip_status=False,
                            include_entities=True):
        
        url = '%s/lists/members.json' % self.base_url
        parameters = {}

        parameters.update(self._IDList(list_id=list_id,
                                       slug=slug,
                                       owner_id=owner_id,
                                       owner_screen_name=owner_screen_name))

        if count:
            parameters['count'] = enf_type('count', int, count)
        if cursor:
            parameters['cursor'] = enf_type('cursor', int, cursor)

        parameters['skip_status'] = enf_type('skip_status', bool, skip_status)
        parameters['include_entities'] = enf_type('include_entities', bool, include_entities)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))
        next_cursor = data.get('next_cursor', 0)
        previous_cursor = data.get('previous_cursor', 0)
        users = [User.NewFromJsonDict(user) for user in data.get('users', [])]

        return next_cursor, previous_cursor, users

	def GetListMembers(self,
                       list_id=None,
                       slug=None,
                       owner_id=None,
                       owner_screen_name=None,
                       skip_status=False,
                       include_entities=False):
        cursor = -1
        result = []
        while True:
            next_cursor, previous_cursor, users = self.GetListMembersPaged(
                list_id=list_id,
                slug=slug,
                owner_id=owner_id,
                owner_screen_name=owner_screen_name,
                cursor=cursor,
                skip_status=skip_status,
                include_entities=include_entities)
            result += users

            if next_cursor == 0 or next_cursor == previous_cursor:
                break
            else:
                cursor = next_cursor

        return result


	def CreateListsMember(self,
                          list_id=None,
                          slug=None,
                          user_id=None,
                          screen_name=None,
                          owner_screen_name=None,
                          owner_id=None):
        is_list = False
        parameters = {}

        parameters.update(self._IDList(list_id=list_id,
                                       slug=slug,
                                       owner_id=owner_id,
                                       owner_screen_name=owner_screen_name))

        if user_id:
            if isinstance(user_id, list) or isinstance(user_id, tuple):
                is_list = True
                uids = [str(enf_type('user_id', int, uid)) for uid in user_id]
                parameters['user_id'] = ','.join(uids)
            else:
                parameters['user_id'] = enf_type('user_id', int, user_id)

        elif screen_name:
            if isinstance(screen_name, list) or isinstance(screen_name, tuple):
                is_list = True
                parameters['screen_name'] = ','.join(screen_name)
            else:
                parameters['screen_name'] = screen_name
        if is_list:
            url = '%s/lists/members/create_all.json' % self.base_url
        else:
            url = '%s/lists/members/create.json' % self.base_url

        resp = self._RequestUrl(url, 'POST', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return List.NewFromJsonDict(data)

	def DestroyListsMember(self,
                           list_id=None,
                           slug=None,
                           owner_screen_name=None,
                           owner_id=None,
                           user_id=None,
                           screen_name=None):
        
        is_list = False
        parameters = {}

        parameters.update(self._IDList(list_id=list_id,
                                       slug=slug,
                                       owner_id=owner_id,
                                       owner_screen_name=owner_screen_name))

        if user_id:
            if isinstance(user_id, list) or isinstance(user_id, tuple):
                is_list = True
                uids = [str(enf_type('user_id', int, uid)) for uid in user_id]
                parameters['user_id'] = ','.join(uids)
            else:
                parameters['user_id'] = int(user_id)
        elif screen_name:
            if isinstance(screen_name, list) or isinstance(screen_name, tuple):
                is_list = True
                parameters['screen_name'] = ','.join(screen_name)
            else:
                parameters['screen_name'] = screen_name

        if is_list:
            url = '%s/lists/members/destroy_all.json' % self.base_url
        else:
            url = '%s/lists/members/destroy.json' % self.base_url

        resp = self._RequestUrl(url, 'POST', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return List.NewFromJsonDict(data)

	def GetListsPaged(self,
                      user_id=None,
                      screen_name=None,
                      cursor=-1,
                      count=20):
       
        url = '%s/lists/ownerships.json' % self.base_url
        parameters = {}
        if user_id is not None:
            parameters['user_id'] = enf_type('user_id', int, user_id)
        elif screen_name is not None:
            parameters['screen_name'] = screen_name

        if count is not None:
            parameters['count'] = enf_type('count', int, count)

        parameters['cursor'] = enf_type('cursor', int, cursor)

        resp = self._RequestUrl(url, 'GET', data=parameters)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        next_cursor = data.get('next_cursor', 0)
        previous_cursor = data.get('previous_cursor', 0)
        lists = [List.NewFromJsonDict(x) for x in data.get('lists', [])]

        return next_cursor, previous_cursor, lists

	def GetLists(self,
                 user_id=None,
                 screen_name=None):
        
        result = []
        cursor = -1

        while True:
            next_cursor, prev_cursor, lists = self.GetListsPaged(
                user_id=user_id,
                screen_name=screen_name,
                cursor=cursor)
            result += lists
            if next_cursor == 0 or next_cursor == prev_cursor:
                break
            else:
                cursor = next_cursor

        return result

	def UpdateProfile(self,
                      name=None,
                      profileURL=None,
                      location=None,
                      description=None,
                      profile_link_color=None,
                      include_entities=False,
                      skip_status=False):
        
        url = '%s/account/update_profile.json' % (self.base_url)
        data = {
            'name': name,
            'url': profileURL,
            'location': location,
            'description': description,
            'profile_link_color': profile_link_color,
            'include_entities': include_entities,
            'skip_status': skip_status,
        }

        resp = self._RequestUrl(url, 'POST', data=data)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return User.NewFromJsonDict(data)

	def UpdateImage(self,
                    image,
                    include_entities=False,
                    skip_status=False):
        url = '%s/account/update_profile_image.json' % (self.base_url)
        with open(image, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read())
        data = {
            'image': encoded_image
        }
        if include_entities:
            data['include_entities'] = 1
        if skip_status:
            data['skip_status'] = 1

        resp = self._RequestUrl(url, 'POST', data=data)

        if resp.status_code in [200, 201, 202]:
            return True
        if resp.status_code == 400:
            raise TwitterError({'message': "Image data could not be processed"})
        if resp.status_code == 422:
            raise TwitterError({'message': "The image could not be resized or is too large."})

	def UpdateBanner(self,
                     image,
                     include_entities=False,
                     skip_status=False):
        
        url = '%s/account/update_profile_banner.json' % (self.base_url)
        with open(image, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read())
        data = {
            # When updated for API v1.1 use image, not banner
            # https://dev.twitter.com/docs/api/1.1/post/account/update_profile_banner
            # 'image': encoded_image
            'banner': encoded_image
        }
        if include_entities:
            data['include_entities'] = 1
        if skip_status:
            data['skip_status'] = 1

        resp = self._RequestUrl(url, 'POST', data=data)

        if resp.status_code in [200, 201, 202]:
            return True
        if resp.status_code == 400:
            raise TwitterError({'message': "Image data could not be processed"})
        if resp.status_code == 422:
            raise TwitterError({'message': "The image could not be resized or is too large."})

        raise TwitterError({'message': "Unkown banner image upload issue"})

    def GetStreamSample(self, delimited=False, stall_warnings=True):
        url = '%s/statuses/sample.json' % self.stream_url
        parameters = {
            'delimited': bool(delimited),
            'stall_warnings': bool(stall_warnings)
        }
        resp = self._RequestStream(url, 'GET', data=parameters)
        for line in resp.iter_lines():
            if line:
                data = self._ParseAndCheckTwitter(line.decode('utf-8'))
                yield data

	def GetStreamFilter(self,
                        follow=None,
                        track=None,
                        locations=None,
                        languages=None,
                        delimited=None,
                        stall_warnings=None,
                        filter_level=None):
        
        if all((follow is None, track is None, locations is None)):
            raise ValueError({'message': "No filter parameters specified."})
        url = '%s/statuses/filter.json' % self.stream_url
        data = {}
        if follow is not None:
            data['follow'] = ','.join(follow)
        if track is not None:
            data['track'] = ','.join(track)
        if locations is not None:
            data['locations'] = ','.join(locations)
        if delimited is not None:
            data['delimited'] = str(delimited)
        if stall_warnings is not None:
            data['stall_warnings'] = str(stall_warnings)
        if languages is not None:
            data['language'] = ','.join(languages)
        if filter_level is not None:
            data['filter_level'] = filter_level

        resp = self._RequestStream(url, 'POST', data=data)
        for line in resp.iter_lines():
            if line:
                data = self._ParseAndCheckTwitter(line.decode('utf-8'))
                yield data

	def GetUserStream(self,
                      replies='all',
                      withuser='user',
                      track=None,
                      locations=None,
                      delimited=None,
                      stall_warnings=None,
                      stringify_friend_ids=False,
                      filter_level=None,
                      session=None,
                      include_keepalive=False):
        
        url = 'https://userstream.twitter.com/1.1/user.json'
        data = {}
        if stringify_friend_ids:
            data['stringify_friend_ids'] = 'true'
        if replies is not None:
            data['replies'] = replies
        if withuser is not None:
            data['with'] = withuser
        if track is not None:
            data['track'] = ','.join(track)
        if locations is not None:
            data['locations'] = ','.join(locations)
        if delimited is not None:
            data['delimited'] = str(delimited)
        if stall_warnings is not None:
            data['stall_warnings'] = str(stall_warnings)
        if filter_level is not None:
            data['filter_level'] = filter_level

        resp = self._RequestStream(url, 'POST', data=data, session=session)
        # The Twitter streaming API sends keep-alive newlines every 30s if there has not been other
        # traffic, and specifies that streams should only be reset after three keep-alive ticks.
        #
        # The original implementation of this API didn't expose keep-alive signals to the user,
        # making it difficult to determine whether the connection should be hung up or not.
        #
        # https://dev.twitter.com/streaming/overview/connecting
        for line in resp.iter_lines():
            if line:
                data = self._ParseAndCheckTwitter(line.decode('utf-8'))
                yield data
            elif include_keepalive:
                yield None

	def VerifyCredentials(self, include_entities=None, skip_status=None, include_email=None):
        
        url = '%s/account/verify_credentials.json' % self.base_url
        data = {
            'include_entities': enf_type('include_entities', bool, include_entities),
            'skip_status': enf_type('skip_status', bool, skip_status),
            'include_email': 'true' if enf_type('include_email', bool, include_email) else 'false',
        }

        resp = self._RequestUrl(url, 'GET', data)
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        return User.NewFromJsonDict(data)

	def SetCache(self, cache):
        
        if cache == DEFAULT_CACHE:
            self._cache = _FileCache()
        else:
            self._cache = cache

	def SetUrllib(self, urllib):
        self._urllib = urllib

	def SetCacheTimeout(self, cache_timeout):
        self._cache_timeout = cache_timeout

	def SetUserAgent(self, user_agent):
        self._request_headers['User-Agent'] = user_agent

	def SetXTwitterHeaders(self, client, url, version):
        self._request_headers['X-Twitter-Client'] = client
        self._request_headers['X-Twitter-Client-URL'] = url
        self._request_headers['X-Twitter-Client-Version'] = version

	def SetSource(self, source):
        self._default_params['source'] = source

	def InitializeRateLimit(self):
        _sleep = self.sleep_on_rate_limit
        if self.sleep_on_rate_limit:
            self.sleep_on_rate_limit = False

        url = '%s/application/rate_limit_status.json' % self.base_url

        resp = self._RequestUrl(url, 'GET')  # No-Cache
        data = self._ParseAndCheckTwitter(resp.content.decode('utf-8'))

        self.sleep_on_rate_limit = _sleep
        self.rate_limit = RateLimit(**data)

	def CheckRateLimit(self, url):
        if not self.rate_limit.__dict__.get('resources', None):
            self.InitializeRateLimit()

        if url:
            limit = self.rate_limit.get_limit(url)

        return limit

    def _BuildUrl(self, url, path_elements=None, extra_params=None):
        # Break url into constituent parts
        (scheme, netloc, path, params, query, fragment) = urlparse(url)

        # Add any additional path elements to the path
        if path_elements:
            # Filter out the path elements that have a value of None
            filtered_elements = [i for i in path_elements if i]
            if not path.endswith('/'):
                path += '/'
            path += '/'.join(filtered_elements)

        # Add any additional query parameters to the query string
        if extra_params and len(extra_params) > 0:
            extra_query = self._EncodeParameters(extra_params)
            # Add it to the existing query
            if query:
                query += '&' + extra_query
            else:
                query = extra_query

        # Return the rebuilt URL
        return urlunparse((scheme, netloc, path, params, query, fragment))

    def _InitializeRequestHeaders(self, request_headers):
        if request_headers:
            self._request_headers = request_headers
        else:
            self._request_headers = {}

    def _InitializeUserAgent(self):
        user_agent = 'Python-urllib/%s (python-twitter/%s)' % \
                     (urllib_version, __version__)
        self.SetUserAgent(user_agent)

    def _InitializeDefaultParameters(self):
        self._default_params = {}

    def _DecompressGzippedResponse(response):
        raw_data = response.read()
        if response.headers.get('content-encoding', None) == 'gzip':
            url_data = gzip.GzipFile(fileobj=io.StringIO(raw_data)).read()
        else:
            url_data = raw_data
        return url_data

    def _EncodeParameters(parameters):
        
        if parameters is None:
            return None
        if not isinstance(parameters, dict):
            raise TwitterError("`parameters` must be a dict.")
        else:
            params = dict()
            for k, v in parameters.items():
                if v is not None:
                    if getattr(v, 'encode', None):
                        v = v.encode('utf8')
                    params.update({k: v})
            return urlencode(params)

    def _ParseAndCheckTwitter(self, json_data):
        """Try and parse the JSON returned from Twitter and return
        an empty dictionary if there is any error.

        This is a purely defensive check because during some Twitter
        network outages it will return an HTML failwhale page.
        """
        try:
            data = json.loads(json_data)
        except ValueError:
            if "<title>Twitter / Over capacity</title>" in json_data:
                raise TwitterError({'message': "Capacity Error"})
            if "<title>Twitter / Error</title>" in json_data:
                raise TwitterError({'message': "Technical Error"})
            if "Exceeded connection limit for user" in json_data:
                raise TwitterError({'message': "Exceeded connection limit for user"})
            if "Error 401 Unauthorized" in json_data:
                raise TwitterError({'message': "Unauthorized"})
            raise TwitterError({'Unknown error: {0}'.format(json_data)})
        self._CheckForTwitterError(data)
        return data

    def _CheckForTwitterError(data):
        """Raises a TwitterError if twitter returns an error message.

        Args:
            data (dict):
                A python dict created from the Twitter json response

        Raises:
            (twitter.TwitterError): TwitterError wrapping the twitter error
            message if one exists.
        """
        # Twitter errors are relatively unlikely, so it is faster
        # to check first, rather than try and catch the exception
        if 'error' in data:
            raise TwitterError(data['error'])
        if 'errors' in data:
            raise TwitterError(data['errors'])

    def _RequestChunkedUpload(self, url, headers, data):
        try:
            return requests.post(
                url,
                headers=headers,
                data=data,
                auth=self.__auth,
                timeout=self._timeout,
                proxies=self.proxies
            )
        except requests.RequestException as e:
            raise TwitterError(str(e))

    def _RequestUrl(self, url, verb, data=None, json=None, enforce_auth=True):
        
        if enforce_auth:
            if not self.__auth:
                raise TwitterError("The twitter.Api instance must be authenticated.")

            if url and self.sleep_on_rate_limit:
                limit = self.CheckRateLimit(url)

                if limit.remaining == 0:
                    try:
                        stime = max(int(limit.reset - time.time()) + 10, 0)
                        logger.debug('Rate limited requesting [%s], sleeping for [%s]', url, stime)
                        time.sleep(stime)
                    except ValueError:
                        pass

        if not data:
            data = {}

        if verb == 'POST':
            if data:
                if 'media_ids' in data:
                    url = self._BuildUrl(url, extra_params={'media_ids': data['media_ids']})
                    resp = requests.post(url, data=data, auth=self.__auth, timeout=self._timeout, proxies=self.proxies)
                elif 'media' in data:
                    resp = requests.post(url, files=data, auth=self.__auth, timeout=self._timeout, proxies=self.proxies)
                else:
                    resp = requests.post(url, data=data, auth=self.__auth, timeout=self._timeout, proxies=self.proxies)
            elif json:
                resp = requests.post(url, json=json, auth=self.__auth, timeout=self._timeout, proxies=self.proxies)
            else:
                resp = 0  # POST request, but without data or json

        elif verb == 'GET':
            data['tweet_mode'] = self.tweet_mode
            url = self._BuildUrl(url, extra_params=data)
            resp = requests.get(url, auth=self.__auth, timeout=self._timeout, proxies=self.proxies)

        else:
            resp = 0  # if not a POST or GET request

        if url and self.rate_limit:
            limit = resp.headers.get('x-rate-limit-limit', 0)
            remaining = resp.headers.get('x-rate-limit-remaining', 0)
            reset = resp.headers.get('x-rate-limit-reset', 0)

            self.rate_limit.set_limit(url, limit, remaining, reset)

        return resp

    def _RequestStream(self, url, verb, data=None, session=None):
        """Request a stream of data.

           Args:
             url:
               The web location we want to retrieve.
             verb:
               Either POST or GET.
             data:
               A dict of (str, unicode) key/value pairs.

           Returns:
             A twitter stream.
        """
        session = session or requests.Session()

        if verb == 'POST':
            try:
                return session.post(url, data=data, stream=True,
                                    auth=self.__auth,
                                    timeout=self._timeout,
                                    proxies=self.proxies)
            except requests.RequestException as e:
                raise TwitterError(str(e))
        if verb == 'GET':
            url = self._BuildUrl(url, extra_params=data)
            try:
                return session.get(url, stream=True, auth=self.__auth,
                                   timeout=self._timeout, proxies=self.proxies)
            except requests.RequestException as e:
                raise TwitterError(str(e))
        return 0  # if not a POST or GET request