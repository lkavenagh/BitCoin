from MTGox import *
import sys

m = MTGox()

dropPercent = 0.015 #percent
timeWindow = 300 #seconds
spendPercent = 0.50
epsilon = 0.0001
waitTime = 15

myVolume = 0
totalVolume = 5.0

while myVolume < totalVolume:
    fee = m.getFee()

    drop = 0
    while drop < dropPercent:
        data = m.getLastTradesTimespan(timeWindow)

        last = float(data['return'][len(data['return'])-1]['price'])
        first = float(data['return'][0]['price'])
        drop = -1*(last-first)/first
        print '%s: Price has dropped %2.1f%% in %d minutes...'%(time.strftime('%c'), drop*100, timeWindow/60)
        time.sleep(waitTime)

    print '%s: Limit breached, buying with %2.0f%% of available funds'%(time.strftime('%c'), spendPercent*100)
    first = last

    btc,usd = m.getBalance()
    buyAmount = usd * spendPercent;
    bidPrice = m.getBid()

    m.cancelAllOrders()

    ret = m.buy(buyAmount, bidPrice+epsilon)
    if ret == -1:
        print 'Exiting...'
        sys.exit()

    # Now wait for same reversal and sell
    gain = 0
    while gain < dropPercent:
        last = m.getLastTradePrice()
        gain = (last-first)/first
        print '%s: Price has gained %2.1f%% since buy...'%(time.strftime('%c'), drop*100)
        time.sleep(waitTime)

    print '%s: Limit breached, selling same amount...'%(time.strftime('%c'), spendPercent*100)

    askPrice = m.getAsk()

    m.sell(buyAmount, askPrice-epsilon)
    myVolume = myVolume + buyAmount
    pnl = m.getPNL()
    print 'Total PNL: $2.2f'%(pnl)
    print 'Total traded: %2.2f BTC'%(myVolume)
