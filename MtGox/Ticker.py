from MTGox import *
import time
import datetime
import re

m = MTGox()

lastprice = m.getTickerData()['return']['last']['display']
print time.ctime() + ": " + lastprice
time.sleep(30)
while 1:
    tmp = m.getTickerData()
    if tmp['result'] != 'error':
        if tmp['return']['last']['display'] != lastprice:
            print time.ctime() + ": " + tmp['return']['last']['display']
            lastprice = tmp['return']['last']['display'];
    else:
        #print tmp['error']
        time.sleep(5)
        
    time.sleep(30)
