from intervalPrices import IntervalPrices
import trader
from prices import Prices
import time, sched

def calculateProfit(ip, output=False):
  firstKey = ip.getFirstAvgKey()
  secondKey = ip.getSecondAvgKey()
  btc = 1.0
  dollars = 0.0
  profit = 0.0
  lastSell = 0.0
  lastBuy = 0.0
  mult = .998
  diffPerc = 1.003

  for ts in ip.timestamps:
    if secondKey in ip.timeline[ts]:
      firstAvg = ip.timeline[ts][firstKey]
      secondAvg = ip.timeline[ts][secondKey]

      if btc == 0 and firstAvg > secondAvg * diffPerc:
        lastBuy = ip.timeline[ts]['close']
        btc = dollars / lastBuy * mult
        dollars = 0
        if output:
          print 'buy on ', time.strftime('%x %X', time.gmtime(ts - 60*60*6)), ' at ', lastBuy, ' btc: ', btc
      elif btc != 0 and firstAvg < secondAvg / diffPerc:
        lastSell = ip.timeline[ts]['close']
        dollars = btc * lastSell * mult
        btc = 0
        if output:
          print 'sell on ', time.strftime('%x %X', time.gmtime(ts - 60*60*6)), ' at ', lastSell, 'dollars: ', dollars
  if btc == 0:
    btc = dollars / lastSell / mult
  return btc



if __name__ == '__main__':
  # first = 10
  # second = 21
  ip = IntervalPrices(900, 'ltc')

  bestProfit = -5000
  bestParams = (0,0)
  print len(ip.origtimeline)
  for i in xrange(3,50):
    for j in xrange(1, i-1):
      ip.setParams(j,i)
      currentProfit = calculateProfit(ip)
      if currentProfit > bestProfit:
        bestProfit = currentProfit
        bestParams = (j,i)
        print "best profit is : ", currentProfit, " with params: ", bestParams

  ip.setParams(bestParams[0], bestParams[1])
  calculateProfit(ip, True)

  # ip.setParams(7, 17)
  # calculateProfit(ip, True)
