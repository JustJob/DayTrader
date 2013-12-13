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

class Depths:

  def __init__(self, updateCallback, updateInterval = 1000, currency = 'btc_usd'):
    self.lastBid = None
    self.lastAsk = None
    self.running = True
    self.callback = updateCallback
    self.worker = threading.Thread(target=self.__sleepAndUdate,args = [updateInterval, currency])
    self.worker.start()

  def updateDepths(self, currency):
    try:
      response = requests.get("https://btc-e.com/api/2/" + currency + "/depth")
      if response.status_code != 200:
        print 'unable to update depth'
        print response.status_code
      else:
        self.depths = response.json()
        if self.lastBid != self.depths['bids'][0] or self.lastAsk != self.depths['asks'][0]:
          self.lastBid = self.depths['bids'][0]
          self.lastAsk = self.depths['asks'][0]
          self.callback(self.lastBid, self.lastAsk)
    except httplib.BadStatusLine:
      print "bad status line"
    except socket.gaierror, e:
      if e.errno == 10054:
        self.conn.close()
        self.conn = httplib.HTTPSConnection('btc-e.com')

  def __sleepAndUdate(self, sleepTime, currency):
    while self.running:
      self.updateDepths(currency)
      time.sleep(sleepTime/1000.0)

  def close(self):
    self.running = False

if __name__ == '__main__':
  def printLastPrice(bid, ask):
    print 'last bid:',bid
    print 'last ask:',ask
  depths = Depths(printLastPrice)
  time.sleep(30)
  depths.close()