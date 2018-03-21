# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 17:56:43 2018

@author: xtuser08
"""

import multiprocessing
import time
import os
from Backtest_Best import * 

HigherDir=os.path.dirname(os.getcwd())
IndexComponentPath=HigherDir+'\\Data\\IndexComponent'
FileList=os.listdir(IndexComponentPath)
IndexList=[a[:-4] for a in FileList]
if __name__ == "__main__":

    CPU=multiprocessing.cpu_count()
    print("The number of CPU is:" + str(CPU))  
    
    Interval=len(IndexList)/(CPU-3)
    for i in range(0,len(IndexList),Interval):
        print IndexList[i:i+Interval]
        p = multiprocessing.Process(target = main, args = (IndexList[i:i+Interval],))         
        p.start() 
        time.sleep(1)
        
    for p in multiprocessing.active_children():
        print("child   p.name:" + p.name + "\tp.id" + str(p.pid)) 