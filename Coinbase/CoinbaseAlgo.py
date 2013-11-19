from Coinbase import *
import time

cutoff = 100.0
cutoffExtreme = 50.0

cutoff1 = False
cutoff2 = False

c = Coinbase()

lastprice = c.getUSDBTC()
print time.ctime() + ": " + lastprice

time.sleep(5)

while 1:
    tmp = c.getUSDBTC()
    if tmp != lastprice:
        print time.ctime() + ": " + tmp
        lastprice = tmp;
    else:
        time.sleep(5)
        
    if not cutoff1 and (lastprice < cutoff):
        print 'Price below first cutoff, buying...'
        if c.buy(1):
            cutoff1 = True
        else:
            print 'Buy failed. Continuing...'
        

    if not cutoff2 and (lastprice < cutoffExtreme):
        print 'Price below second cutoff, buying...'
        if c.buy(2):
            cutoff2 = True

    if cutoff1 and lastprice > cutoff*2:
        cutoff2 = True
        
    time.sleep(5)
    
    if cutoff1 and cutoff2:
        print 'Both cutoffs breached, exiting buy stage...'
        break

cutoff = 500.0
cutoffExtreme = 750.0

cutoff1 = False
cutoff2 = False
while 1:
    tmp = c.getUSDBTC()
    if tmp != lastprice:
        print time.ctime() + ": " + tmp
        lastprice = tmp;
    else:
        time.sleep(5)
        
    if not cutoff1 and (lastprice > cutoff):
        print 'Price below first cutoff, selling...'
        if c.sell(1):
            cutoff1 = True
        else:
            print 'Sell failed. Continuing...'

    if not cutoff2 and (lastprice > cutoffExtreme):
        print 'Price below second cutoff, selling...'
        if c.sell(2):
            cutoff2 = True
        else:
            print 'Sell failed. Continuing...'

    time.sleep(5)
    
    if cutoff1 and cutoff2:
        print 'Both cutoffs breached, exiting program...'
        break
   
