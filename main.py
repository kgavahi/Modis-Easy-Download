"""
Created on Sun Jan 26 14:56:35 2020

@author: kayhangavahi@gmail.com
"""
import MODIS as ds

username   = '**********'
password   = '********'
start_date = '2018-01-01'
end_date   = '2018-01-01'
product    = 'MCD12Q1'
version    = '006'

# This might not be nesasd 
ds.dl_MODIS(username , password ,start_date , end_date , product, version)

