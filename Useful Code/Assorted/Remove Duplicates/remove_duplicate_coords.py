# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 15:53:01 2021

Use this on a coordinate file that has diplicates of names and coordinates
 - for example a bad cell structure that has the same coordinates written multiple times to the same place

@author: Adam
"""

fname='E:\\NEXTCLOUD_NEW\\Lab data\\Adam\\ZEP_Density_2021\\Oct2021_Ring_Density_v1\\UBC_ZEP_DENSITY_goodGCs_inverted_20211008_coords.txt'

with open(fname) as f:
    lines = f.readlines()
    
lines_no_dupes = list(dict.fromkeys(lines))
for i in range(len(lines_no_dupes)):
    print(lines_no_dupes[i])
    
print("From ",str(len(lines))," coords to ",str(len(lines_no_dupes)))