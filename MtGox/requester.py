from hashlib import sha512
from hmac import HMAC
from base64 import b64decode, b64encode
from urllib import urlencode
import urllib2

import time

import json

def get_nonce():
   return int(time.time()*100000)

def sign_data(secret, data):
   return b64encode(str(HMAC(secret, data, sha512).digest()))
   
class requester:
   def __init__(self):

      self.key = '15416792-f48a-464c-8684-887cc14d2713'
      self.secret = b64decode('jVfZZ6sUaAH++7cxXGTurgKZzyhX/aDXgEk5LhaS1U2tLxbTQ+BQneMV+V7zh6ks2UQotQlxT3G20mESMcRTQA==')

      self.base_url = "https://data.mtgox.com/api/1/"
      self.generic = 'generic/info'
      self.ticker = '/BTCUSD/ticker_fast'
      self.trades = '/BTCUSD/trades'
      self.depth = '/BTCUSD/depth/full'
      self.lag = '/generic/order/lag'
      self.history = '/generic/private/wallet/history'

      self.submitorder = '/BTCUSD/private/order/add'
      self.cancelorder = '/BTCUSD/private/order/cancel'
      self.openorders = '/generic/private/orders'
      self.orderresults = '/generic/private/order/result'
      
      self.time = {'init': time.time(), 'req': time.time()}
      self.reqs = {'max': 1, 'window': 10, 'curr': 0}
               
   def build_query(self, req={}):

      req['nonce'] = get_nonce()
      post_data = urlencode(req)

      headers = {
         'User-Agent': 'GoxApi',
         'Rest-Key': self.key,
         'Rest-Sign': sign_data(self.secret, post_data)
      }
      return (post_data, headers)

   def perform(self, path, args):
      data, headers = self.build_query(args)
      req = urllib2.Request(self.base_url+path, data, headers)
      success = 0
      while success == 0:
         try:
            res = urllib2.urlopen(req, data)
            success = 1
         except urllib2.HTTPError as e:
            print time.ctime() + ': HTTPError'
            time.sleep(30)
         except urllib2.URLError:
            print time.ctime() + ': URLError'
            time.sleep(5)
         
      return json.load(res)
      
      
