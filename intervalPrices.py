import httplib
import urllib
import json
import hashlib
import hmac
import threading
import time
import socket
import copy
import requests

class IntervalPrices:

  def __init__(self, interval = 300, currency = 'btc'):
    self.origtimeline = {}
    self.interval = interval
    params = {
      'sid':'de8150f9',
      'symbol':'btce' + currency + 'usd',
      'nonce':IntervalPrices.NONCE,
      'step':interval
    }

    response = requests.get("http://s2.bitcoinwisdom.com:8080/period", params = params, headers={'Cache-Control': 'max-age=0', 'Pragma':'no-cache', 'User-Agent':'Mozilla/5.0'})
    IntervalPrices.NONCE += 1
    if response.status_code == 200:
      responseJson = response.json()
      for line in responseJson:
        ts = int(line[0])
        self.origtimeline[ts] = {
          'open':float(line[3]),
          'close':float(line[4]),
          'low':float(line[5]),
          'high':float(line[6])
        }
    else:
      print "can't get response"

    response.close()

  def setParams(self, firstEMA = 10, secondEMA = 21):
    self.timeline = copy.deepcopy(self.origtimeline)
    self.firstEMA = firstEMA
    self.secondEMA = secondEMA

    self.timestamps = sorted(self.timeline.keys())
    prevTs = 0
    firstLine = True 
    for ts in self.timestamps:
      if firstLine:
        firstLine = False
        diff = self.timeline[ts]['close'] - self.timeline[ts]['open']
      else:
        diff = self.timeline[ts]['close'] - self.timeline[prevTs]['close']

      if diff > 0:
        self.timeline[ts]['gain'] = diff
        self.timeline[ts]['loss'] = 0
      else:
        self.timeline[ts]['gain'] = 0
        self.timeline[ts]['loss'] = -1 * diff
      prevTs = ts

    self.addExpMovingAverage('close', firstEMA)
    self.addExpMovingAverage('close', secondEMA)

  def addExpMovingAverage(self, key, length, start = 0):
    avgKey = 'avg' + str(length) + key
    k = 2.0/(length+1)

    average = 0.0
    for i in xrange(start, length + start):
      average += self.timeline[self.timestamps[i]][key]
    average /= length
    self.timeline[self.timestamps[length + start - 1]][avgKey] = average
    
    for i in xrange(length + start, len(self.timestamps)):
      current = self.timeline[self.timestamps[i]]
      prev = self.timeline[self.timestamps[i - 1]]
      current[avgKey] = current[key] * k + prev[avgKey] * (1 - k)

  def addMovingAverage(self, key, length, start = 0):
    avgKey = 'avg' + str(length) + key
    for i in xrange(length + start - 1, len(self.timestamps)):
      average = 0.0
      for j in xrange(length):
        current = self.timeline[self.timestamps[i-j]]
        average += current[key]
      self.timeline[self.timestamps[i]][avgKey] = average / length

  def addRSI(self, length):
    gainKey = 'avg' + str(length) + 'gain'
    lossKey = 'avg' + str(length) + 'loss'
    rsiKey = 'rsi' + str(length)

    for i in xrange(length - 1, len(self.timestamps)):
      current = self.timeline[self.timestamps[i]]
      current[rsiKey] = 100.0 - 100.0 / (1 + current[gainKey]/current[lossKey])

  def addStoch(self, key, start, length):
    stochKey = 'stoch' + str(length) + key
    for i in xrange(start + length - 1, len(self.timestamps)):
      current = self.timeline[self.timestamps[i]]
      minVal = maxVal = current[key]
      for j in xrange(i + 1 - length, i+1):
        prior = self.timeline[self.timestamps[j]]
        if prior[key] > maxVal:
          maxVal = prior[key]
        if prior[key] < minVal:
          minVal = prior[key]

      current[stochKey] = (current[key] - minVal) / (maxVal - minVal)

  def getAvgStochRSIKey(self):
    return 'avg' + str(self.stochAvg) + 'stoch' + str(self.stochLength) + 'rsi' + str(self.rsiLength)

  def getFirstAvgKey(self):
    return 'avg' + str(self.firstEMA) + 'close'

  def getSecondAvgKey(self):
    return 'avg' + str(self.secondEMA) + 'close'

  def getMostRecentTime(self):
    return self.timestamps[-1]

IntervalPrices.NONCE = 10000

if __name__ == '__main__':
  intervals = IntervalPrices()
  intervals.setParams()
  for ts in intervals.timestamps:
    if 'avg21close' in intervals.timeline[ts]:
      print time.strftime('%X', time.gmtime(ts)), ' avg10:',intervals.timeline[ts]['avg10close'], ' avg21:', intervals.timeline[ts]['avg21close']
    else:
      print time.strftime('%X', time.gmtime(ts))
