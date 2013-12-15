from intervalPrices import IntervalPrices
import trader
from prices import Prices
import time, sched
import sys

def calculateProfit(ip, output=False):
  firstKey = ip.getFirstAvgKey()
  secondKey = ip.getSecondAvgKey()
  btcBought = True
  profit = 0.0
  lastSell = 0.0
  lastBuy = 0.0
  fees = 0.0

  for ts in ip.timestamps:
    if secondKey in ip.timeline[ts]:
      firstAvg = ip.timeline[ts][firstKey]
      secondAvg = ip.timeline[ts][secondKey]

      if not btcBought and firstAvg > secondAvg:
        lastBuy = ip.timeline[ts]['close']
        fees += .002 * lastBuy
        btcBought = True
        profit += lastSell - lastBuy
        if output:
          print 'buy on ', time.strftime('%x %X', time.gmtime(ts - 60*60*6)), ' at ', lastBuy, ' with profit ', profit 
      elif btcBought and firstAvg < secondAvg:
        lastSell = ip.timeline[ts]['close']
        fees += .002 * lastSell
        btcBought = False
        if output:
          print 'sell on ', time.strftime('%x %X', time.gmtime(ts - 60*60*6)), ' at ', lastSell 

  return profit - fees



if __name__ == '__main__':
  # first = 10
  # second = 21

  # bestProfit = -50
  # bestParams = (0,0)
  # ip = IntervalPrices(300)
  # print len(ip.origtimeline)
  # for i in xrange(3,50):
  #   for j in xrange(1, i-1):
  #     ip.setParams(j,i)
  #     currentProfit = calculateProfit(ip)
  #     if currentProfit > bestProfit:
  #       bestProfit = currentProfit
  #       bestParams = (j,i)
  #       print "best profit is : ", currentProfit, " with params: ", bestParams

  # ip.setParams(bestParams[0], bestParams[1])
  # calculateProfit(ip, True)

  try:
    myTrader = trader.Trader()
    coinStr = 'ltc'
    prices = Prices(coinStr + '_usd')
    interval = 1800
    COIN_MIN = 1
    DOLLAR_MIN = 10
    emaPair = (8,17)
    diffPerc = 1.003

    def tradeIfShould(ip):
      timestamp = (int(time.time()) / 60) * 60
      if timestamp in ip.timeline:
        current = ip.timeline[timestamp]
      else:
        current = ip.timeline[ip.getMostRecentTime()]
      firstKey = ip.getFirstAvgKey()
      secondKey = ip.getSecondAvgKey()
      info = myTrader.getInfo()
      coin = info['funds'][coinStr]
      print 'checking trades at ', time.strftime('%x %X', time.gmtime(time.time() - 60*60*6)), ' with first: ', current[firstKey], ' and second: ', current[secondKey]

      if current[firstKey] > current[secondKey] * diffPerc and coin < COIN_MIN:
        dollars = info['funds']['usd']
        price = prices.getBuyPrice(dollars)
        volume = (dollars - .01) / price
        volume *= 100000
        volume = int(volume)
        volume /= 100000.0
        print 'buy btc at ', price
        myTrader.trade(True, price, volume, coinStr + '_usd')
        return True
      elif current[firstKey] * diffPerc < current[secondKey] and coin > COIN_MIN:
        print 'sell btc at ', prices.getSellPrice(coin)
        myTrader.trade(False, prices.getSellPrice(coin), coin, coinStr + '_usd')
        return True

      return False


    def checkTrades():
      ip = IntervalPrices(interval, coinStr)
      while len(ip.origtimeline.keys()) == 0:
        ip = IntervalPrices(interval, coinStr)
        time.sleep(100)

      ip.setParams(emaPair[0], emaPair[1])
      return tradeIfShould(ip)

    while True:
      sleepFor = interval + 10 - (int(time.time()) % interval)
      print 'sleeping for: ', sleepFor
      time.sleep(sleepFor)
      checkTrades()
  except(KeyboardInterrupt, SystemExit):
    sys.exit()
  
  # ip.setParams()
  # print calculateProfit(ip, True)


