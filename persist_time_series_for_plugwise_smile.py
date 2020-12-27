import plugwise_smile_API
import time
import json
import logging
from datetime import datetime

class PersistTimeSeriesForPlugwiseSmile(): 
    def __init__(self, influxDB_client, plugwise_smile_host, plugwise_smile_password): 
        self.influx_client = influxDB_client
        self.p1 = plugwise_smile_API.Smile(plugwise_smile_host, plugwise_smile_password)

    def persist_plugwise_smile_actueel(self): 
        self.p1.update_data()
        self.__persist_point(self.p1.get_actueel_verbruikt())
        self.__persist_point(self.p1.get_actueel_opgewekt())
        self.__persist_point(self.p1.get_actueel())
                    
    def persist_plugwise_smile_cumulatief(self): 
        self.p1.update_data()
        self.__persist_point(self.p1.get_cumulatief_opgewekt_hoog_tarief())
        self.__persist_point(self.p1.get_cumulatief_opgewekt_laag_tarief())
        self.__persist_point(self.p1.get_cumulatief_verbuikt_hoog_tarief())
        self.__persist_point(self.p1.get_cumulatief_verbuikt_laag_tarief())

    def __persist_point(self, meetwaarde): 
        json_body = self.__get_point(meetwaarde)
        try: 
            self.influx_client.write_points(json_body)
        except: 
            logging.error("%s >>Influxdb is down", datetime.now())

    def __get_point(self, meetwaarde): 
        json_body = [
            {
                "measurement": meetwaarde['meeting_type'],
                "time": meetwaarde['time_stamp'],
                "fields": {
                    "waarde": meetwaarde['waarde'],
                    "eenheid": meetwaarde['eenheid']
                }
            }
        ]
        return json_body
