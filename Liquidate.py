from MTGox import *

# Waits until a given 'stopPrice' and when it gets there, sells all
# BTC that you currently hold

m = MTGox()

stopPrice = 150

bidPrice = m.getBid()

while bidPrice < stopPrice:
    print '%s: stopPrice not reached, bid=%2.2f, stop=%2.2f'%(time.strftime('%c'), bidPrice, stopPrice)
    time.sleep(30)

fee = m.getFee()
btc,usd = m.getBalance()

liquidateAmount = btc/(1+fee)

m.cancelAllOrders()

m.sell(liquidateAmount, stopPrice)

print '%s: Liquidation finished'%(time.strftime('%c'))
