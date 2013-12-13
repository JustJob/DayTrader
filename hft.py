import priceDepths
import trader
import time
import sys

FEE = .002
BTC_QUANT = .05
USD_DIFF = .005
SPREAD_DIFF = .0015
myTrader = None

def newPrice(bid, ask):
  buyUsd = bid[0] + USD_DIFF
  sellUsd = ask[0] - USD_DIFF
  profit = (sellUsd - buyUsd) - FEE * (buyUsd + sellUsd)
  print "you can make $", profit, "on the current spread"
  print 'bid is: ', bid
  print 'ask is: ', ask
  info = myTrader.getInfo()
  if  profit > SPREAD_DIFF * buyUsd and info['funds']['btc'] > BTC_QUANT and info['funds']['usd'] > buyUsd * BTC_QUANT:
    myTrader.trade(True, buyUsd, BTC_QUANT)
    myTrader.trade(False, sellUsd, BTC_QUANT)
    print "made trades"

if __name__ == '__main__':
  try:
    myTrader = trader.Trader()
    depths = priceDepths.Depths(newPrice)
    while True:
      time.sleep(10)
  except(KeyboardInterrupt, SystemExit):
    depths.close()
    sys.exit()

