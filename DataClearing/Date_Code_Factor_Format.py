# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 11:20:22 2018

@author: xtuser08
"""

import os
import pandas as pd
import multiprocessing
import time

#判断路径是否存在，不存在则建立
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 
def Get_Fator_List():
    Value=['EP_LYR','EP_TTM','BP_MRQ','SP_LYR','SP_TTM','CFP_CFO_TTM','PE_LYR_OPP','PE_TTM_OPP','PB_MRQ_OPP','PS_LYR_OPP','PS_TTM_OPP'] 
    Growth=['GR_YOY','OR_YOY','OP_YOY','NPP_YOY'] 
    Momentum=['Momentum5_OPP','Momentum10_OPP','Momentum20_OPP','Momentum30_OPP','Momentum60_OPP','Momentum90_OPP']
    Volatility=['Vol20_OPP','Vol30_OPP','Vol60_OPP','Vol90_OPP']
    Value_Growth=['PE_IndustryRank_Diff_OPP_90','PE_IndustryRank_Diff_OPP_180','PE_IndustryRank_Diff_OPP_270','PE_IndustryRank_Diff_OPP_360',
                  'PE_IndustryRank_Diff_OPP_450','PE_IndustryRank_Diff_OPP_540','PE_IndustryRank_Diff_OPP_630','PE_IndustryRank_Diff_OPP_720']    
    FactorList=Value+Growth+Momentum+Volatility+Value_Growth
    return FactorList

FactorList=Get_Fator_List()
        
HigherDir=os.path.dirname(os.getcwd())
FactorPath=HigherDir+'\\Data\\FactorLibrary\\'
OutputPath=HigherDir+'\\Data\\Date_Code_Factor_Format\\'
Create_Path(OutputPath)


def Main(Start,End):
    for Factor in FactorList[Start:End]:
        print Factor
        Data=pd.read_csv(FactorPath+Factor+'.csv',index_col=0)
        df=pd.DataFrame(Data.stack())
        df.columns=[Factor]
        df.to_csv(OutputPath+Factor+'.csv',index_label=['Date','Code'])
        
#CPU=multiprocessing.cpu_count()
#print("The number of CPU is:" + str(CPU))  
#
#Interval=len(FactorList)/(CPU-1)
#if len(FactorList)/Interval>CPU-1:
#    Interval=Interval+1
#    
#
#for Loc in range(0,len(FactorList),Interval):
#    Start=Loc
#    End=Loc+Interval
#    print FactorList[Start:End]
#    p = multiprocessing.Process(target = Component_Element, args = (Index,))         
#    p.start() 
#    time.sleep(1)
#    
#for p in multiprocessing.active_children():
#    print("child   p.name:" + p.name + "\tp.id" + str(p.pid)) 