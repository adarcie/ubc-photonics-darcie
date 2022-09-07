# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 17:25:13 2021

@author: Bigbo
"""


# importing library
import requests
from bs4 import BeautifulSoup
 
# enter city name
city = "vancouver"
 
# creating url and requests instance
url = "https://www.google.com/search?q="+"weather"+city
html = requests.get(url).content
 
# getting raw data
soup = BeautifulSoup(html, 'html.parser')
# print(soup)
temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
str = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
 
# formatting data
data = str.split('\n')
time = data[0]
sky = data[1]
 
# getting all div tag
listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
strd = listdiv[5].text
print('strd',strd)
 
# getting other required data
pos = strd.find('wind')
other_data = strd[pos:]
 
# printing all data
print(temp)
print("Time: ", time)
print("Sky Description: ", sky)
print(other_data)