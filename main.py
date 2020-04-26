# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 14:56:35 2020

@author: 16785
"""
import MODIS as ds
start_date = '2018-01-01'
end_date   = '2019-01-01'
product    = 'MCD12Q1'

ds.dl_MODIS('<earthdata_username>','<earthdata_pass>', start_date, end_date, product)

