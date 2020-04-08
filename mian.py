# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 14:56:35 2020

@author: 16785
"""

import MODIS as ds
#import IMERG as ig
#import SMAP as sp


ds.dl_MODIS('kgavahi','491Newyork','2018-01-01','2018-01-01','MCD12Q1')

#ig.dl_IMERG('kgavahi','491Newyork','2016-04-01','2016-04-03','GPM_3IMERGDL')

#sp.dl_SMAP('kgavahi','491Newyork','2015-05-01','2015-05-03','SPL2SMA','003')