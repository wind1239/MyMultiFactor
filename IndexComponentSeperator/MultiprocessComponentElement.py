# -*- coding: utf-8 -*-
"""
Created on Tue Feb 06 16:27:56 2018

@author: xtuser08
"""
import multiprocessing
import time
import os
import numpy as np
from ComponentElement import * 

 
if __name__ == "__main__":

    CPU=multiprocessing.cpu_count()
    print("The number of CPU is:" + str(CPU))  
    
    HigherDir=os.path.dirname(os.getcwd())
    IndexComponentPath=HigherDir+'\\Data\\IndexComponent\\'
    Num=len(os.listdir(IndexComponentPath))
    Interval=Num/(CPU-1)
    if Interval<=0:
        Interval=Interval+1
    elif len(range(0,Num,Interval))>=7 or Interval<=0:
        Interval=Interval+1
    for i in range(0,Num,Interval):
        Start=i
        End=i+Interval+2   
        p = multiprocessing.Process(target = Component_Element, args = (Start,End,))         
        p.start() 
        time.sleep(1)
        
    for p in multiprocessing.active_children():
        print("child   p.name:" + p.name + "\tp.id" + str(p.pid)) 
