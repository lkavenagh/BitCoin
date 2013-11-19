import urllib
import urllib2
import json

apikey = 'dea3b122de16ef0e377a94ee58890a3f728b92b119cd0b7609a2cb6399e02891'
url = 'https://coinbase.com/api/v1/'
user_agent = 'Magic Browser'

class Coinbase:
    def requester(self, reqType, qty=0):
        if reqType == 'balanceBTC':
            req = urllib2.Request(url+'account/balance?api_key='+apikey, headers={'User-Agent' : user_agent});
        elif reqType == 'exchange_rates':
            req = urllib2.Request(url+'currencies/exchange_rates?api_key='+apikey, headers={'User-Agent' : user_agent});
        elif reqType == 'buy':
            req = urllib2.Request(url+'buys?api_key='+apikey, urllib.urlencode({'qty' : qty, 'agree_btc_amount_varies' : True}), headers = {'User-Agent' : user_agent});
        elif reqType == 'sell':
            req = urllib2.Request(url+'sells?api_key='+apikey, urllib.urlencode({'qty' : qty}), headers = {'User-Agent' : user_agent});

        con = urllib2.urlopen(req)        
        return json.loads(con.read())
    
    def getBalanceBTC(self):
        
        r = self.requester('balanceBTC')
       
        return r['amount']

    def getUSDBTC(self):

        r = self.requester('exchange_rates')
        
        return r['btc_to_usd']

    def buy(self, btc):
       
        r = self.requester('buy', btc)

        print json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')) 
        
        if not r['success']:
            print 'Transaction failed: ' + str(r['errors'][0])
        else:
            print 'Transaction succeeded!'
            print 'Bought ' + r['transfer']['btc']['amount'] + 'BTC'
            print 'Paid ' + r['transfer']['total']['amount'] + 'USD'
                
        return r['success']

    def sell(self, btc):
       
        r = self.requester('buy', btc)

        print json.dumps(r, sort_keys=True, indent=4, separators=(',', ': ')) 
        
        if not r['success']:
            print 'Transaction failed: ' + str(r['errors'][0])
        else:
            print 'Transaction succeeded!'
            print 'Bought ' + r['transfer']['btc']['amount'] + 'BTC'
            print 'Paid ' + r['transfer']['total']['amount'] + 'USD'
                
        return r['success']
        
        
