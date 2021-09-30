import home_monitor_config as config
import persist_time_series_for_plugwise_smile as plugwise_persistor
import coin_importer as cimporter
import time
import sys
import logging  
from datetime import date
from datetime import datetime
from influxdb import InfluxDBClient

# haal alle configuratie data op!
config_data = config.Home_monitor_config().load_config_data()
influxdb_host = config_data['influxdb']['host']
influxdb_user =  config_data['influxdb']['user']
influxdb_password = config_data['influxdb']['password']
influxdb_database = config_data['influxdb']['database']
plugwise_smile_host = config_data['plugwise_smile']['host']
plugwise_smile_password = config_data['plugwise_smile']['password']
coinmarketcap_api_key = config_data['coin_market_cap']['api_key']

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='./logs/home_monitor.log', level=logging.INFO)
logging.info("%s >>Home monitor gestart.", datetime.now())


influxDB_client = InfluxDBClient(host=influxdb_host, port=8086, database=influxdb_database, username=influxdb_user, password=influxdb_password)
logging.info("%s >> InfluxClient has succesfull been created", datetime.now())

persistor = plugwise_persistor.PersistTimeSeriesForPlugwiseSmile(influxDB_client, plugwise_smile_host,plugwise_smile_password)
cimporter = cimporter.CoinCollector(influxDB_client, coinmarketcap_api_key)
crypto_count = 0

while True:     
    persistor.persist_plugwise_smile_actueel()
    if crypto_count > 300: 
        cimporter.collect()
        crypto_count = 0
    
    crypto_count = crypto_count + 2
    time.sleep(2)
