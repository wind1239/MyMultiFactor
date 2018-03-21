# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 14:41:40 2018

@author: xtuser08
"""

import os
import pandas as pd

Index='ZZ500_ZZ1000'
Period=5
Signal='Top'
BacktestID=Index+'_BestVersion'

HigherDir=os.path.dirname(os.getcwd())
DataPath=HigherDir+'\\Data\\BacktestResult\\'+BacktestID+'\\'
SignalPath=DataPath+Signal+'_Signal_'+str(Period)+'Days\\'
OutputPath=DataPath+Signal+'_Signal_'+str(Period)+'Days_Merged.csv'

FileList=sorted(os.listdir(SignalPath))
Dict={}
for File in FileList:
    df=pd.read_csv(SignalPath+File)
    del df['Industry']
    df.columns=['code','weight']
    df.insert(1,'date',[File[:-4]]*len(df))
    df.insert(2,'Direction',[1]*len(df))
    Dict[File]=df
    
dfSignal=pd.concat(Dict)
dfSignal.to_csv(OutputPath,index=False)