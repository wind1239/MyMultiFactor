# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 15:49:55 2018

@author: xtuser08
"""
#import thread
#import time
#from GetFactor import *
##start=time.clock()
#try:
#    
#    thread.start_new_thread(Get_Factor,(0,5,))
#    thread.start_new_thread(Get_Factor,(4,10,))
#    print 'try'
#except:
#    print 'wrong'
#while 1:
#    pass
#print 'done'
##end=time.clock()
##print end-start

import multiprocessing
import time
import os
from GetFactor import * 

 
if __name__ == "__main__":

    CPU=multiprocessing.cpu_count()
    print("The number of CPU is:" + str(CPU))
    
    Num=len(os.listdir(os.path.dirname(os.path.dirname(os.getcwd()))+'\\Data\\StockData'))
    Interval=Num/(CPU-1)
    


    for i in range(0,Num,Interval):
        Start=i
        End=i+Interval+2
        print Start,End
        p = multiprocessing.Process(target = Get_Factor, args = (Start,End,))         
        p.start() 
        time.sleep(1)
        
    for p in multiprocessing.active_children():
        print("child   p.name:" + p.name + "\tp.id" + str(p.pid)) 
 

