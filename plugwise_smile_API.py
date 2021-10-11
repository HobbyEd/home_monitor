import requests 
from requests.auth import HTTPBasicAuth
import xmltodict  
from enum import Enum
from datetime import datetime
import logging

class meeting_type(Enum): 
    ACTUEEL_VERBRUIKT = 'actueel_verbuikt'
    ACTUEEL_OPGEWEKT = 'actueel_terug_geleverd'
    ACTUEEL = 'actueel'
    CUMULATIEF_OPGEWEKT_LAAG_TARIEF = 'cumulatief_terug_geleverd_laag_tarief'
    CUMULATIEF_OPGEWEKT_HOOG_TARIEF = 'cumulatief_terug_geleverd_tarief'
    CUMULATIEF_VERBRUIKT_LAAG_TARIEF = 'cumulatief_verbuikt_laag_tarief'
    CUMULATIEF_VERBRUIKT_HOOG_TARIEF = 'cumulatief_verbuikt_hoog_tarief'

class Smile: 
    def __init__(
        self,
        host,
        password,
        username="smile",
        port=80,
        ):
        self._endpoint = f"http://{host}:{str(port)}/core/domain_objects"
        self._password = password 
        self._username = username 
        self._actueel_opgewekt = {}
        self._actueel_verbruikt = {}
        self._cumulatief_opgewekt_laag_tarief = {}
        self._cumulatief_opgewekt_hoog_tarief = {}
        self._cumulatief_verbuikt_laag_tarief = {}
        self._cumulatief_verbuikt_hoog_tarief = {}
        self._actueel = {}

    def get_actueel_opgewekt(self): 
        return self._actueel_opgewekt

    def get_actueel_verbruikt(self):
        return self._actueel_verbruikt

    def get_actueel(self): 
        return self._actueel

    def get_cumulatief_verbuikt_hoog_tarief(self): 
        return self._cumulatief_verbuikt_hoog_tarief
    
    def get_cumulatief_verbuikt_laag_tarief(self): 
        return self._cumulatief_verbuikt_laag_tarief

    def get_cumulatief_opgewekt_hoog_tarief(self): 
        return self._cumulatief_opgewekt_hoog_tarief

    def get_cumulatief_opgewekt_laag_tarief(self): 
        return self._cumulatief_opgewekt_laag_tarief

    def update_data(self):
       try:
            resp = requests.get(self._endpoint, auth=HTTPBasicAuth(self._username, self._password) )
            resp_dict = xmltodict.parse(resp.content)

            # Zet alle actuele waarden.  
            point_log  =resp_dict['domain_objects']['location']["logs"]["point_log"]
            for point in point_log:
                if point["type"].upper() == "ELECTRICITY_CONSUMED":
                    ruw_verbruik = point
                elif point["type"].upper() == "ELECTRICITY_PRODUCED":
                    ruw_opgewekt = point

            er_is_verbuik = False
            for verbruik in ruw_verbruik["period"]["measurement"]:
                if float(verbruik['#text']) != float("0"): 
                    er_is_verbuik = True
                    self._actueel_verbruikt = {'meeting_type': meeting_type.ACTUEEL_VERBRUIKT.value, 'waarde': verbruik['#text'], 'time_stamp': verbruik['@log_date'], 'eenheid': 'Watt'}                
            if not er_is_verbuik: 
                self._actueel_verbruikt = {'meeting_type': meeting_type.ACTUEEL_VERBRUIKT.value, 'waarde': str(float('0')), 'time_stamp': ruw_verbruik["period"]["measurement"][0]['@log_date'], 'eenheid': 'Watt'}

            er_is_opgewekt = False
            for opgewekt in ruw_opgewekt["period"]["measurement"]:
                if float(opgewekt['#text']) != float("0"): 
                    er_is_opgewekt = True
                    self._actueel_opgewekt = {'meeting_type': meeting_type.ACTUEEL_OPGEWEKT.value, 'waarde': opgewekt['#text'], 'time_stamp': opgewekt['@log_date'], 'eenheid': 'Watt'}                
            if not er_is_opgewekt: 
                self._actueel_opgewekt = {'meeting_type': meeting_type.ACTUEEL_OPGEWEKT.value, 'waarde': str(float('0')), 'time_stamp': ruw_opgewekt["period"]["measurement"][0]['@log_date'], 'eenheid': 'Watt'}                

            if float(self._actueel_verbruikt['waarde']) == 0: 
                self._actueel = {'meeting_type': meeting_type.ACTUEEL.value, 'waarde': str(0 - float(self._actueel_opgewekt['waarde'])), 'time_stamp': self._actueel_opgewekt['time_stamp'], 'eenheid': self._actueel_opgewekt['eenheid']}            
            else: 
                self._actueel = {'meeting_type': meeting_type.ACTUEEL.value, 'waarde': self._actueel_verbruikt['waarde'], 'time_stamp': self._actueel_verbruikt['time_stamp'], 'eenheid': self._actueel_verbruikt['eenheid']}            
       except: 
            logging.error("%s >> Er is iets fout gegaan met het ophalen van gegevens uit de Smile.", datetime.now())
            

