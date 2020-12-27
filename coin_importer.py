from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from datetime import datetime
import argparse
import json
import logging
import os
import sys
import time

class CoinClient():
  def __init__(self, coinmarketcap_api_key):

    self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    self.headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': coinmarketcap_api_key}
    self.parameters = {'start': '1', 'limit': '5000', 'convert': 'EUR'}

  def tickers(self):
    session = Session()
    session.headers.update(self.headers)
    r = session.get(self.url, params=self.parameters)
    data = json.loads(r.text)
    if 'data' not in data:
      logging.error('No data in response. Is your API key set?')
    return data

class CoinCollector():
  def __init__(self,  influxDB_client, coinmarketcap_api_key):
    self.influxdb_client = influxDB_client
    self.coin_client = CoinClient(coinmarketcap_api_key)
    logging.info("%s >> CoinCollector has succesfull been created", datetime.now())

  def collect(self):
    try:
      response = self.coin_client.tickers()
      if 'data' not in response:
        logging.error('%s >>No data in response. Is your API key set?', datetime.now())
      else:
        for value in response['data']:
          for price in ['EUR']:
            if value['symbol'] == 'BTC' or value['symbol'] == 'ETH': 
              self.__persist_point(value)
    except: 
      logging.error("%s >>something went wrong this requesting Coin Market Cap API", datetime.now())

  def __persist_point(self, meetwaarde): 
      json_body = self.__get_point(meetwaarde)
      try: 
          self.influxdb_client.write_points(json_body)
      except: 
          logging.error("%s >>Influxdb is down", datetime.now())

  def __get_point(self, meetwaarde): 
      json_body = [
          {
              "measurement": meetwaarde['symbol'],
              "time": meetwaarde['last_updated'],
              "fields": {
                  "waarde": meetwaarde['quote']['EUR']['price'],
                  "eenheid": 'Euro'
              }
          }
      ]
      return json_body
