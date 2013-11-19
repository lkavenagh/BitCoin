from MTGox import *

# Waits until the spread is wide enough to make a certain profit
# buys just above bid and sells just above ask to try to take the spread

m = MTGox()

spendPercent = 0.01
epsilon = 0.0001
waitTime = 15
profit = 0.25

fee = m.getFee()
bid = m.getBid()
ask = m.getAsk()

requiredSpread = fee*bid
print 'Require a spread of at least %2.2f'%(requiredSpread)
print 'Adding profit margin, require a spread of at least %2.2f'%(requiredSpread+profit)

while (ask-bid) < requiredSpread+profit:
    time.sleep(waitTime)
    bid = m.getBid()
    ask = m.getAsk()
    print 'Spread is %2.2f, require %2.2f'%(ask-bid, requiredSpread+profit)

btc,usd = m.getBalance
toBuy = (usd*spendPercent)/bid
oid = m.buyAtBid(toBuy, bid)

price1 = m.getOrderTradePrice('bid', oid)
print 'Bought %2.2f BTC at %2.2f USD'%(toBuy, price1)

if oid == 1:
    oid = m.sellAtAsk(toBuy, ask)

if oid == 1:
    price2 = m.getOrderTradePrice('ask', oid)
    print 'Sold %2.2f BTC at %2.2f USD'%(toBuy, price2)

profitAfterFee = (toBuy-(toBuy*fee))*(price2-price1)
print 'Profit after fees = $%2.2f'%(profitAfterFee)
