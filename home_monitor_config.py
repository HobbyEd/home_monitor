import json
import io
import logging
from datetime import datetime

class Home_monitor_config(): 
    # This function read the logfiles in the folder /Logs and return 
    # a dictionary with the JSON data
    
    @classmethod
    def load_config_data(self):
        _importer_config = {}
        try:
            with io.open("./home_monitor.conf", 'r', encoding='utf-8') as f:
                _importer_config = json.load(f)
            return _importer_config
        except Exception:
            logging.error("%s >>The config file could (importer.config) not be read. Is it in the main folder?", datetime.now())
        finally:
            logging.info("%s >>Configuration information hase been read succesfull.", datetime.now())
            f.close()
