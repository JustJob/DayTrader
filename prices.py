# If you find this sample useful, please feel free to donate :)
# LTC: LePiC6JKohb7w6PdFL2KDV1VoZJPFwqXgY
# BTC: 1BzHpzqEVKjDQNCqV67Ju4dYL68aR8jTEe
 
import httplib
import urllib
import json
import hashlib
import hmac
import threading
import time
import socket
import requests

class Prices:

  def __init__(self, currency = 'btc_usd'):
    self.lastBid = None
    self.lastAsk = None
    self.currency = currency

  def __getDepths(self):
    try:
      response = requests.get("https://btc-e.com/api/2/" + self.currency + "/depth")
      if response.status_code != 200:
        print 'unable to update depth'
      else:
        return response.json()
    except httplib.BadStatusLine:
      print "bad status line"
    except socket.gaierror, e:
      if e.errno == 10054:
        self.conn.close()
        self.conn = httplib.HTTPSConnection('btc-e.com')

    return None

  def getBuyPrice(self, dollars):
    depths = self.__getDepths()
    if depths is not None:
      currentDollars = 0
      for bid in depths['asks']:
        currentDollars += bid[1] * bid[0]
        if currentDollars > dollars:
          return bid[0]

  def getSellPrice(self, volume):
    depths = self.__getDepths()
    if depths is not None:
      currentVol = 0
      for bid in depths['bids']:
        currentVol += bid[1]
        if currentVol > volume:
          return bid[0]

if __name__ == '__main__':
  def printLastPrice(bid, ask):
    print 'last bid:',bid
    print 'last ask:',ask
  depths = Depths(printLastPrice)
  time.sleep(30)
  depths.close()