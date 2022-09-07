# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 18:22:26 2021

@author: Bigbo
"""

#!/usr/bin/env python
# encoding: utf-8

# import the module
import python_weather
import asyncio

client = python_weather.Client(format=python_weather.IMPERIAL)
weather = await client.find("Washington DC")
print(weather.current.temperature)