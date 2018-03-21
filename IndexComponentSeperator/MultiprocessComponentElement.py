# -*- coding: utf-8 -*-
"""
Created on Tue Feb 06 16:27:56 2018

@author: xtuser08
"""
import multiprocessing
import time
from ComponentElement import * 

IndexList=['SZ50','HS300','ZZ500','ZZ1000']
if __name__ == "__main__":

    CPU=multiprocessing.cpu_count()
    print("The number of CPU is:" + str(CPU))  
    

    for Index in IndexList:
        p = multiprocessing.Process(target = Component_Element, args = (Index,))         
        p.start() 
        time.sleep(1)
        
    for p in multiprocessing.active_children():
        print("child   p.name:" + p.name + "\tp.id" + str(p.pid)) 
