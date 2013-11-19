from MTGox import *
import sys
import time
import random
import smtplib

m = MTGox()
volumeLimit = 50
volLeft = volumeLimit
myVolume = 0
myProfit = 0.0
restartTime = 300

abandon = False

offset = 0.002 # percentage profit desired
minTradeSize = 0.75
maxTradeSize = 1.25
desiredTradeSize = float(random.randrange(minTradeSize*1000,maxTradeSize*1000))/1000
resetoffset = 1.2
leaveTime = 3
waitTime = 15
epsilon = 0.0
initialOffset = 0.1

sender = 'MTGoxAlgo'
receivers = 'lkavenagh@gmail.com'
headers = ["from: " + sender,
           "subject: MTGox algo trade",
           "to: " + receivers,
           "mime-version: 1.0",
           "content-type: text/html"]
headers = "\r\n".join(headers)

btc,usd = m.getBalance()
buyPrice = m.getBid()-initialOffset

while usd < desiredTradeSize*buyPrice:
    print time.ctime() + ': Not enough funds, waiting 5 minutes for more funds'
    time.sleep(300)
    desiredTradeSize = float(random.randrange(minTradeSize*1000,maxTradeSize*1000))/1000
    btc,usd = m.getBalance()
    buyPrice = m.getBid()-initialOffset

tradeSize = desiredTradeSize
print time.ctime() + ': Have funds, starting algo'

buyPrice = 0

while myVolume < volumeLimit and usd > tradeSize*buyPrice:
    print time.ctime() + ': Volume limit is %2.2f BTC, we''ve traded %2.2f BTC so far'%(volumeLimit, myVolume)

    fee = m.getFee()

    if buyPrice == 0:
        buyPrice = m.getBid()-initialOffset
        
    initialOffset = 0

    oid = m.buy(tradeSize, buyPrice+epsilon)
    r = m.getOrderResult(oid)
    while r != 1:
        if m.getBid() > buyPrice+1:
            buyPrice = m.getBid()-initialOffset
            m.cancel(oid)
            oid = m.buy(tradeSize, buyPrice+epsilon)
            
        time.sleep(waitTime)
        r = m.getOrderResult(oid)
        if r == -1:
            print 'Exiting...'
            sys.exit()

    print time.ctime() + ': BUY order filled!'
    msg = time.ctime() + ': BOUGHT %2.2f BTC at $%2.2f.'%(tradeSize, buyPrice+epsilon)
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()
    s.login('lkavenagh', 'eightcows')
    try:
        s.sendmail(sender, receivers, headers + "\r\n\r\n" + msg)
        s.quit()
    except:
        print 'Email failed'
        s.quit()

    tp = m.getOrderTradePrice('bid', oid)
    if tp != -1:
        buyPrice = tp
    # sellPrice should obtain desired offset after fees
    buyFee = (fee*buyPrice*tradeSize)
    spentSoFar = ((buyPrice+epsilon)*tradeSize) + buyFee
    needFromSell = spentSoFar + (offset*spentSoFar)
    needFromSell = needFromSell / (1-fee)
    
    sellPrice = needFromSell / tradeSize
    oid = m.sell(tradeSize, sellPrice-epsilon)
    r = m.getOrderResult(oid)
    while r != 1:
        time.sleep(waitTime)
        r = m.getOrderResult(oid)
        if r == -1:
            print 'Exiting...'
            sys.exit()
        if m.getAsk() < sellPrice-3:
            # Abandon this order in the book for later, wait, and start again with buy order
            abandon = True
            r = 1

    if not abandon:
        print time.ctime() + ': SELL order filled!'
        msg = time.ctime() + ': SOLD %2.2f BTC at $%2.2f. Buy price was $%2.2f.'%(tradeSize, sellPrice-epsilon, buyPrice+epsilon)
        
        tp = m.getOrderTradePrice('ask', oid)
        if tp != -1:
            sellPrice = tp
        sellFee = (fee*sellPrice*tradeSize)
        totalFee = buyFee + sellFee

        # Finish up - report details
        desiredTradeSize = float(random.randrange(minTradeSize*1000,maxTradeSize*1000))/1000
        btc,usd = m.getBalance()
        myVolume = myVolume + tradeSize
        myProfit = myProfit + ((sellPrice-buyPrice)*tradeSize) - totalFee
        volLeft = volumeLimit - myVolume
        buyPrice = sellPrice-resetoffset;
        
        while usd < desiredTradeSize*buyPrice:
            print time.ctime() + ': Not enough funds, waiting 5 minutes for more funds'
            time.sleep(300)
            desiredTradeSize = float(random.randrange(minTradeSize*1000,maxTradeSize*1000))/1000
            btc,usd = m.getBalance()
            buyPrice = m.getBid()-initialOffset

        tradeSize = desiredTradeSize
        print time.ctime() + ': Have funds, starting algo'
        
        if tradeSize > volLeft:
            print 'tradeSize would exceed limit, capping next trade to %2.2f BTC'%(volLeft)
            tradeSize = volLeft

        print time.ctime()
        print 'Traded %2.2f BTC so far'%(myVolume)
        print 'Profit (after fees) is %2.5f USD so far'%(myProfit)
        msg = msg + '\r\LTD PnL (after fees) is %2.5f USD'%(m.getPNL())
        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        s.login('lkavenagh', 'eightcows')
        try:
            s.sendmail(sender, receivers, headers + "\r\n\r\n" + msg)
            s.quit()
        except:
            print 'Email failed'
            s.quit()
            
        if myVolume < volumeLimit:
            print 'Waiting %d seconds to restart'%(restartTime)
            time.sleep(restartTime)
            print 'New anchor is %2.2f'%(buyPrice)
    else:
        print 'Price has dropped too far, leaving SELL on book and restarting.'
        print 'Will wait 30 minutes for restart'
        time.sleep(30*60)
        desiredTradeSize = float(random.randrange(minTradeSize*1000,maxTradeSize*1000))/1000
        btc,usd = m.getBalance()
        myProfit = 0
        volLeft = volumeLimit - myVolume
        buyPrice = m.getBid()
        
        while usd < desiredTradeSize*buyPrice:
            print time.ctime() + ': Not enough funds, waiting 5 minutes for more funds'
            time.sleep(300)
            desiredTradeSize = float(random.randrange(minTradeSize*1000,maxTradeSize*1000))/1000
            btc,usd = m.getBalance()
            buyPrice = m.getBid()-initialOffset

        tradeSize = desiredTradeSize
        print time.ctime() + ': Have funds, starting algo'
        if tradeSize > volLeft:
            print 'tradeSize would exceed limit, capping next trade to %2.2f BTC'%(volLeft)
            tradeSize = volLeft

        abandon = False
        

print '%s: Algo finished'%(time.strftime('%c'))
print '%s: Balance is %2.2f BTC/%2.2f USD'%(time.strftime('%c'), btc, usd)
s.quit()
