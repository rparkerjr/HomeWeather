import datetime
import time
import pandas as pd
import requests

# Variables
api_key = '06b639d0c99a00d538d0ddee99e33617'
api_key2 = 'bd627fefaef37e87a1709da33a1d8bd1'
city = 'Seattle'
zipcode = '98117'
latlong = (47.6894, -122.4060)     # ballard

class OpenWeather :
    """
    Object wrapper for the OpenWeatherData API.
    """
    def __init__(self, api_key, city, latlong):        
        self.appid = api_key
        self.city = city
        self.latlong = latlong
        self.lat = str(latlong[0])
        self.lon = str(latlong[1])
        
        self.current = pd.DataFrame()
        self.minutely = pd.DataFrame()
        self.hourly = pd.DataFrame()
        self.daily = pd.DataFrame()
        self.alerts = pd.DataFrame()
        
        # make these into their own classes?
        self.airpollution = pd.DataFrame()
        self.airpollution_forecast = pd.DataFrame()
        
        self.aqi_map = {1 : "good", 2 : "fair", 3 : "moderate", 4 : "poor", 5 : "very poor"}
        
        self.debug = False
        
        print('OpenWeather instance created for {}, {}.'.format(self.city, self.latlong))  
        
    @property
    def appid(self) :
        return self._appid
    
    @appid.setter
    def appid(self, value) :
        self._appid = value
        
    @property
    def city(self) :
        return self._city
    
    @city.setter
    def city(self, value) :
        self._city = value
        
    @property
    def latlong(self):
        return self._latlong
    
    @latlong.setter
    def latlong(self, value) :
        self._latlong = value
        
    @property
    def lat(self) :
        return self._latlong[0]
    
    @lat.setter
    def lat(self, value) :
        self._lat = value
    
    @property
    def lon(self):
        return self._latlong[1]
    
    @lon.setter
    def lon(self, value) :
        self._lon = value
        
    @property
    def as_of(self) :
        return self.current.index[0]
    
    @property
    def current_temperature(self) :
        return self.current.temp[0]
    
    @property
    def lo_temp(self) :
        return self.daily.temp[0]['min']
    
    @property
    def hi_temp(self) :
        return self.daily.temp[0]['max']
    
    @property
    def current_conditions_brief(self) :
        return self.current['weather'][0][0]['main']
    
    @property
    def current_conditions(self) :
        return self.current['weather'][0][0]['description']
        
    # functions
    def fmt_unix_date(self, dt) :
        fmt_string = '%Y-%m-%d %I:%M %p'
        timestamp = datetime.datetime.utcfromtimestamp(dt).strftime(fmt_string)
        return timestamp
    
    def get_onecall(self) :
        # api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}
        try :
            url = 'https://api.openweathermap.org/data/2.5/onecall'
            params = {'lat' : self.lat, 'lon' : self.lon, 'appid' : self.appid, 'units' : 'imperial'}
            response = requests.get(url, params = params)
            
            if response.status_code == 200 :
                #print('Successful request, code: {}'.format(response.status_code))
                return response.json()
                #self.data = response.json()
            else :
                print('HTTP error, code: {}'.format(response.status_code))
                return None
        except :
            print('Error contacting remote server.')
            return None

    def initial_load(self) :
    	self.refresh_onecall()
    	self.airpollution = self.get_airpollution()
    	print('data loaded')

    def parse_onecall(self, data) :
    	# This function takes the returned JSON data and breaks the data into
    	# separate dataframes. Datetime fields are cleaned up and adjusted for
    	# time zone differences.
        if data is None :
            print('No data!')
            return None

        tz_offset = data['timezone_offset']

        current = pd.DataFrame.from_dict(data['current'], orient = 'index').T
        minutely = pd.DataFrame.from_dict(data['minutely'], orient = 'columns')
        hourly = pd.DataFrame.from_dict(data['hourly'], orient = 'columns')
        daily = pd.DataFrame.from_dict(data['daily'], orient = 'columns')

        for df in [current, minutely, hourly, daily] :
            df['dt'] += tz_offset
            df['timestamp'] = [self.fmt_unix_date(d) for d in df['dt']]
            df.set_index('timestamp', inplace = True)
            df['month'] = [datetime.datetime.utcfromtimestamp(d).strftime('%b') for d in df['dt']]
            df['day'] = [datetime.datetime.utcfromtimestamp(d).strftime('%d') for d in df['dt']]
            df['weekday'] = [datetime.datetime.utcfromtimestamp(d).strftime('%a') for d in df['dt']]
        #print('parsed')

        #return current, hourly, daily
        self.current = current
        self.minutely = minutely
        self.hourly = hourly
        self.daily = daily
    
    def refresh_onecall(self) :
        self.parse_onecall(self.get_onecall())
        
    # AIR POLLUTION ----------------------------------------------
    @property
    def aqi(self) :
        return airPollution["list"][0]["main"]["aqi"]
    
    @property
    def aq_components(self) :
        return airPollution["list"][0]["components"]
    
    @property
    def carbon_monoxide(self) :
        return airPollution["list"][0]["components"]["co"]
    
    @property
    def ozone(self) :
        return airPollution["list"][0]["components"]["o3"]
    
    @property
    def suphur_dioxide(self) :
        return airPollution["list"][0]["components"]["s02"]
    
    @property
    def fine_particles(self) :
        return airPollution["list"][0]["components"]["pm2_5"]
    
    @property
    def coarse_particles(self) :
        return airPollution["list"][0]["components"]["pm10"]
    
    def get_airpollution(self) :        
        try :
            url = 'https://api.openweathermap.org/data/2.5/air_pollution'
            params = {'lat' : self.lat, 'lon' : self.lon, 'appid' : self.appid}
            response = requests.get(url, params = params)
            
            if response.status_code == 200 :
                #print('Successful request, code: {}'.format(response.status_code))
                return response.json()
            else :
                print('HTTP error, code: {}'.format(response.status_code))
                print(response.text)
                return None
        except :
            print('Error contacting remote server.')
            return None
    
    def get_airpollution_forecast(self) :
        try :
            url = 'https://api.openweathermap.org/data/2.5/airpollution/forecast'
            params = {'lat' : self.lat, 'lon' : self.lon, 'appid' : 'bd627fefaef37e87a1709da33a1d8bd1'}
            response = requests.get(url, params = params)
            
            if response.status_code == 200 :
                #print('Successful request, code: {}'.format(response.status_code))
                return response.json()
            else :
                print('HTTP error, code: {}'.format(response.status_code))
                return None
        except :
            print('Error contacting remote server.')
            return None
    
    def parse_airpollution_forecast(self) :
        if data is None :
            print('No data!')
            return None
        
    # HISTORICAL WEATHER -----------------------------------------
    def get_historical_weather(self) :
        # date from the past 5 days, Unix time, UTC time zone
        dt = ''
        try :
            url = 'https://api.openweathermap.org/data/2.5/onecall/timemachine'
            params = {'lat' : self.lat, 'lon' : self.lon, 'dt' : dt, 'appid' : 'bd627fefaef37e87a1709da33a1d8bd1'}
            response = requests.get(url, params = params)
            
            if response.status_code == 200 :
                #print('Successful request, code: {}'.format(response.status_code))
                return response.json()
            else :
                print('HTTP error, code: {}'.format(response.status_code))
                return None
        except :
            print('Error contacting remote server.')
            return None
    
    def parse_historical_weather(self, data) :
        if data is None :
            print('No data!')
            return None