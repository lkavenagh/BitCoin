from requester import *
import re
import time

simulation = 0
waitTime = 5
leaveTime = 3
epsilon = 0.0001

class MTGox:

    def getGenericData(self):
        return requester().perform(requester().generic, {})

    def getTickerData(self):
        return requester().perform(requester().ticker, {})

    def getTradeData(self, args={}):
        return requester().perform(requester().trades, args)

    def getLagData(self):
        return requester().perform(requester().lag, {})

    def getOpenOrders(self):
        return requester().perform(requester().openorders, {})

    def getFinishedOrder(self, thistype, oid):
        args = {}
        args['type'] = thistype
        args['order'] = oid
        return requester().perform(requester().orderresults, args)

    def getDepth(self):
        return requester().perform(requester().depth, {})

    def getBTCHistory(self, type={}):
        args = {}
        args['currency'] = 'BTC'
        args['type'] = type
        return requester().perform(requester().history, args)

    def getUSDHistory(self, type={}):
        args = {}
        args['currency'] = 'USD'
        args['type'] = type
 
        return requester().perform(requester().history, args)
    
    def getUser(self):
        user = self.getGenericData()['return']['Login']
        print 'Logged in as %s'%(user)
        
    def getBalance(self):
        data = self.getGenericData()

        if simulation == 1:
            return (10,100)
        else:    
            btcbalance = float(self.getGenericData()['return']['Wallets']['BTC']['Balance']['value'])
            usdbalance = float(self.getGenericData()['return']['Wallets']['USD']['Balance']['value'])
            return (btcbalance,usdbalance)

    def displayJSON(self, jsondata):
        print json.dumps(jsondata, sort_keys=True, indent=4, separators=(',', ': '))
        
    def displayTicker(self):
        print self.displayJSON(self.getTickerData())

    def getLastTradePrice(self):
        ret = -1
        while ret == -1:
            try:
                ret = float(self.getTickerData()['return']['last']['value'])
            except KeyError:
                ret = -1
                print 'Problem getting last price, retrying...'
                time.sleep(10)

        return ret

    def getOrderTradePrice(self, thistype, oid):
        data = self.getFinishedOrder(thistype, oid)
        if data['result'] == 'error':
            return -1
        else:
            return float(data['return']['avg_cost']['value'])

    def getLastTradesTimespan(self, timespan):
        args = {}
        args['since'] = self.getTimeOfLastTrade()-(timespan*1000000)
        data = self.getTradeData(args)
        return data

    def getBid(self):
        ret = -1
        while ret == -1:
            try:
                ret = float(self.getTickerData()['return']['buy']['value'])
            except KeyError:
                ret = -1
                print 'Problem getting bid price, retrying...'
                time.sleep(10)

        return ret

    def getAsk(self):
        ret = -1
        while ret == -1:
            try:
                ret = float(self.getTickerData()['return']['sell']['value'])
            except KeyError:
                ret = -1
                print 'Problem getting ask price, retrying...'
                time.sleep(5)

        return ret

    def getTimeOfLastTrade(self):
        return int(self.getTickerData()['return']['now'])

    def getLagMS(self):
        return int(self.getLagData()['return']['lag'])

    def getLagS(self):
        return int(self.getLagData()['return']['lag_secs'])

    def getFee(self):
        return (float(self.getGenericData()['return']['Trade_Fee'])/100)

    def buy(self, btcamount, limit):
        args = {}
        args['type'] = 'bid'
        args['amount_int'] = btcamount*1e8
        args['price_int'] = limit*1e5

        #if limit > self.getLastTradePrice():
        #    print 'Limit is above current price, market orders not allowed'
        #    return -1

        if simulation == 1:
            print time.ctime() + ': Order submitted: BUY %2.2f BTC at $%2.2f'%(btcamount,limit)
            return 'test_oid_buy'
        else:
            data = requester().perform(requester().submitorder, args)
            
        if data['result'] == 'success':
            print time.ctime() + ': Order submitted: BUY %2.2f BTC at $%2.2f'%(btcamount,limit)
            return data['return']
        else:
            print 'Order failed'
            return -1

    def buyAtBid(self, btcamount, price):
        # Wait until the bid reaches our desired price (this won't trigger on the first iteration)
        tooHighFails = 0;
        bidPrice = self.getBid()
        print '%s: Bid is (%2.4f), waiting to post order at %2.4f'%(time.strftime('%c'), bidPrice, price)
        while bidPrice > (price):
            time.sleep(waitTime)
            bidPrice = self.getBid()

        # send in BUY order, replace every 3 seconds to avoid front-running
        buyPrice = bidPrice+epsilon
        oid = self.buy(btcamount,buyPrice)
        time.sleep(leaveTime)
        orderFinished = 0;
        while orderFinished == 0:
            r = self.getOrderResult(oid)
            if r == 1:
                print 'BUY Order filled!'
                orderFinished = 1
                return 1
            elif r == -1:
                print 'No orders found! Exiting...'
                return -1
            elif r['amount']['value'] < btcamount:
                # Perhaps add a replace here, for the remaining shares. Will need to grab the average price to work out sellPrice
                print '%s: %2.2f BTC remaining. Current price is %2.2f, buying at %2.2f'%(time.strftime('%c'),float(r['amount']['value']),self.getLastTradePrice(),price)
                time.sleep(waitTime)
            else:
                print '%s: No fills, replacing'%(time.strftime('%c'))
                bidPrice = self.getBid()
                cxloid = self.cancel(oid)
                if cxloid != -1:
                    while bidPrice > (price):
                        print '%s: Bid is (%2.4f), waiting to post order at %2.4f'%(time.strftime('%c'), bidPrice, price)
                        time.sleep(waitTime)
                        bidPrice = self.getBid()
                        tooHighFails = tooHighFails + 1
                        if tooHighFails >= 100:
                            print "Bid was too low 100 times, returning without trading."
                            return -2
                        
                    buyPrice = bidPrice+epsilon
                    oid = self.buy(btcamount,buyPrice)

                time.sleep(leaveTime)

    def sell(self, btcamount, limit):
        args = {}
        args['type'] = 'ask'
        args['amount_int'] = btcamount*1e8
        args['price_int'] = limit*1e5

        #if limit < self.getLastTradePrice():
        #    print 'Limit is below current price, market orders not allowed'
        #    return -1

        if simulation == 1:
            print time.ctime() + ': Order submitted: SELL %2.2f BTC at $%2.2f'%(btcamount,limit)
            return 'test_oid_sell'
        else:
            data = requester().perform(requester().submitorder, args)
            
        if data['result'] == 'success':
            print time.ctime() + ': Order submitted: SELL %2.2f BTC at $%2.2f'%(btcamount,limit)
            return data['return']
        else:
            print 'Order failed'
            print data['error']
            return -1

    def sellAtAsk(self, btcamount, price):
        # Wait until the bid reaches our desired price (this won't trigger on the first iteration)
        tooLowFails = 0;
        askPrice = self.getAsk()
        print '%s: Ask is (%2.2f), waiting to post order at %2.2f'%(time.strftime('%c'), askPrice, price)
        while askPrice < (price):
            time.sleep(waitTime)
            askPrice = self.getAsk()

        # send in SELL order, replace every 3 seconds to avoid front-running
        sellPrice = askPrice-epsilon
        oid = self.sell(btcamount,sellPrice)
        time.sleep(leaveTime)
        orderFinished = 0;
        while orderFinished == 0:
            r = self.getOrderResult(oid)
            if r == 1:
                print 'SELL Order filled!'
                orderFinished = 1
                return 1
            elif r == -1:
                print 'No orders found! Exiting...'
                return -1
            elif r['amount']['value'] < btcamount:
                # Perhaps add a replace here, for the remaining shares. Will need to grab the average price to work out sellPrice
                print '%s: %2.2f BTC remaining. Current price is %2.2f, selling at %2.2f'%(time.strftime('%c'),float(r['amount']['value']),self.getLastTradePrice(),price)
                time.sleep(waitTime)
            else:
                print '%s: No fills, replacing'%(time.strftime('%c'))
                askPrice = self.getAsk()
                cxloid = self.cancel(oid)
                if cxloid != -1:
                    while askPrice < (price):
                        print '%s: Ask is (%2.2f), waiting to post order at %2.2f'%(time.strftime('%c'), askPrice, price)
                        time.sleep(waitTime)
                        askPrice = self.getAsk()
                        tooLowFails = tooLowFails + 1
                        if tooLowFails >= 100:
                            print "Ask was too high 100 times, returning without trading."
                            return -2
                        
                    sellPrice = askPrice-epsilon
                    oid = self.sell(btcamount,sellPrice)

                time.sleep(leaveTime)
                
    def cancel(self, oid):
        args = {}
        args['oid'] = oid
        
        data = requester().perform(requester().cancelorder, args)
        
        if data['result'] == 'success':
            print 'Order cancelled successfully: %s'%(data['return']['qid'])
            return (data['return']['qid'], data['return']['oid'])
        else:
            print 'Cancel failed'
            print data['error']
            return -1

    def cancelAllOrders(self):
        data = self.getAllOrders()
        for i in range(0, len(data)):
            self.cancel(data[i]['oid'])

    def getAllOrders(self):
        data = requester().perform(requester().openorders, {})
        return data['return']
        
    def getOrderResult(self, oid):
        args = {}
        args['order'] = oid
        
        data = requester().perform(requester().openorders, args)

        idx = -1
        for i in range(0, len(data['return'])):
            if data['return'][i]['oid'] == oid:
                idx = i
        if len(data['return']) == 0:
            return -1
        elif idx == -1:
            return 1
        else:
            return data['return'][idx]

    def getUSDFeesPaid(self):
        feeUSD = self.getUSDHistory('fee')
        feeBTC = self.getBTCHistory('fee')

        totalfee = 0

        for i in range(0,len(feeUSD['return']['result'])):
            totalfee = totalfee + float(feeUSD['return']['result'][i]['Value']['value'])
            btcfee = float(feeBTC['return']['result'][i]['Value']['value'])
            info = (feeBTC['return']['result'][i]['Info'])
            price = re.search('(?<=\$)\d*\.\d* ', info)
            if price:
                price = float(price.group())
            else:
                price = 0
                
            totalfee = totalfee + (btcfee * price)

        return totalfee

    def getUSDSpent(self):
        spentUSD = self.getUSDHistory('spent')

        totalspent = 0

        for i in range(0,len(spentUSD['return']['result'])):
            totalspent = totalspent + float(spentUSD['return']['result'][i]['Value']['value'])

        return totalspent

    def getUSDEarned(self):
        earnedUSD = self.getUSDHistory('earned')

        totalearned = 0

        for i in range(0,len(earnedUSD['return']['result'])):
            totalearned = totalearned + float(earnedUSD['return']['result'][i]['Value']['value'])

        return totalearned

    def getUSDDeposited(self):
        depositedUSD = self.getUSDHistory('deposit')

        totaldeposited = 0

        for i in range(0,len(depositedUSD['return']['result'])):
            totaldeposited = totaldeposited + float(depositedUSD['return']['result'][i]['Value']['value'])

        return 1000

    def getUSDWithdrawn(self):
        withdrawnUSD = self.getUSDHistory('withdraw')

        totalwithdrawn = 0

        for i in range(0,len(withdrawnUSD['return']['result'])):
            totalwithdrawn = totalwithdrawn + float(withdrawnUSD['return']['result'][i]['Value']['value'])

        return totalwithdrawn

    def printSummary(self):
        btc,usd = self.getBalance()
        print 'Balance is %4.fBTC/$%2.2f'%(btc,usd)
        fees = self.getUSDFeesPaid()
        print 'Fees paid: $%4.2fUSD'%(fees)
        spent = self.getUSDSpent()
        print 'USD spent: $%4.2f'%(spent)
        earn = self.getUSDEarned()
        print 'USD earned: $%4.2f'%(earn)
        dep = self.getUSDDeposited()
        print 'USD deposited: $%4.2f'%(dep)
        wit = self.getUSDWithdrawn()
        print 'USD withdrawn: $%4.2f'%(wit)
        last = self.getLastTradePrice()
        print 'Last trade price: $%4.2f'%(last)

        val = btc*last
        print 'USD value of BTC held: $%4.2f'%(val)

        pnl = val + usd - dep + wit

        print 'Total PnL: $%4.2f'%(pnl)

        return pnl

    def getPNL(self):
        last = self.getLastTradePrice()
        btc,usd = self.getBalance()
        dep = self.getUSDDeposited()
        val = btc*last
        
        return val + usd - dep
