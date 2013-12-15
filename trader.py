import httplib
import urllib
import json
import hashlib
import hmac
import requests

class Trader:
  nonceFile = open('nonce', 'r')
  nonce = int(nonceFile.readline())
  nonceFile.close()

  def __init__(self):
    secrets = open('secrets.txt')
    self.BTC_api_key = secrets.readline()[:-1]
    self.BTC_api_secret = secrets.readline()[:-1]
    print self.BTC_api_key
    print self.BTC_api_secret
  
  def __getHeaders(self, params):
    # Hash the params string to produce the Sign header value    
    H = hmac.new(self.BTC_api_secret, digestmod=hashlib.sha512)
    H.update(params)
    sign = H.hexdigest()
     
    return {"Content-type": "application/x-www-form-urlencoded",
           "Key":self.BTC_api_key,
           "Sign":sign}

  def __getResponse(self, params, headers, retries = 3):
    for x in xrange(retries):
      try:
        response = requests.post("https://btc-e.com/tapi", data=params, headers=headers)
        if response.status_code != 200:
          print 'BAD request'
          print response.status_code
        else:
          response = response.json()
          if response['success'] != 1:
            print 'unsuccessful',params
            print response
            return None
          else:
            return response['return']
      except Exception as e:
        print "Bad request to trader"
        print e

  def __updateNonce(self):
    self.nonce += 1
    nonceFile = open('nonce','w')
    nonceFile.write(str(self.nonce))
    nonceFile.close()

  def __exeResponse(self, params):
    self.__updateNonce()
    params["nonce"] = self.nonce
    params = urllib.urlencode(params)
    headers = self.__getHeaders(params)
    return self.__getResponse(params, headers)

  def trade(self, isBuy, price, quantity, coin):
    transType = 'buy' if isBuy else 'sell'
    params = {
        "method":'Trade', 
        'pair':coin,
        'type':transType,
        'rate':price,
        'amount':quantity
      }
    return self.__exeResponse(params)

  def activeOrders(self):
    params = {
        "method":'ActiveOrders', 
        'pair':'btc_usd'
      }
    return self.__exeResponse(params)

  def cancelOrders(self, oid):
    params = {
        "method":'CancelOrder',
        'order_id': oid
      }
    return self.__exeResponse(params)

  def getInfo(self):
    params = {
        "method":'getInfo'
      }
    return self.__exeResponse(params)

if __name__ == '__main__':
  trader = Trader()
  print trader.activeOrders()
  print trader.getInfo()