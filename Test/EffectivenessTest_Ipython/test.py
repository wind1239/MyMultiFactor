# -*- coding: utf-8 -*-
"""
Created on Thu Mar 08 12:38:19 2018

@author: xtuser08
"""

import EffectivenessTest as ET

Factor='EPS_LYR'
Index='ZZ500'
Year=0 #单独看某一年的话，year=某一年，全部回测时间的话，year=0
Quantile=10

ET.Effectiveness_Test(Factor,Index,Year,Quantile)
