# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 17:08:43 2021

@author: Bigbo
"""

import pywapi 
import string

# weather_com_result = pywapi.get_weather_from_weather_com('10001') 
# yahoo_result = pywapi.get_weather_from_yahoo('10001') 
noaa_result = pywapi.get_weather_from_noaa('KJFK')
yahoo_result = pywapi.get_weather_from_yahoo('10001')

result=yahoo_result
print(result)
# weather=result['weather']
# windspeed=float(result['wind_mph'])*1.60934#km/h

# print(weather,windspeed)


