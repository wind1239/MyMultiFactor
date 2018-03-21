# -*- coding: utf-8 -*-
import pandas as pd
import os
from itertools import combinations

#判断是否存在路径
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 

HigherDir=os.path.dirname(os.getcwd())
InputPath=os.path.dirname(HigherDir)+'\\Data\\IndexComponent\\'
OutputPath=HigherDir+'\\Data\\IndexComponent\\'
Create_Path(OutputPath)

Index=[u'沪深300',u'上证50',u'中证500',u'中证1000']
IndexName=['HS300','SZ50','ZZ500','ZZ1000']
FileList=[a+u'成分股历史列表.csv' for a in Index]

def Get_Index_Component_Combination():
    Dict={}
    for Loc in range(len(Index)):
        df=pd.read_csv(InputPath+FileList[Loc],encoding='gbk')
        df['index']=[IndexName[Loc]]*len(df)
        Dict[IndexName[Loc]]=df
    
       
    for Loc in range(len(Index)):    
        Combine=[a for a in combinations(IndexName,Loc+1)]
        print Combine
        for ComLoc in range(len(Combine)):
            ComElement=Combine[ComLoc]
            df=pd.DataFrame() 
            FileName='' 
            for Element in ComElement:
                df=pd.concat([df,Dict[Element]],ignore_index=True)
                FileName=FileName+Element+'_'
            FileName=FileName[:-1]
            df['Sign']=df.duplicated(subset=['code','date'],keep='last')
            df=df[df['Sign']==False]
            del df['Sign'] 
            print FileName,len(df)
            df.to_csv(OutputPath+FileName+'.csv',index=False)
        
def Get_All_Component():
    StockPath=HigherDir+'\\Data\\StockData\\'
    FileList=[a for a in os.listdir(StockPath) if a[:5]!='SSE_0']
    Code=[]
    Date=[]
    for File in FileList:
        print 'Get all',File
        df=pd.read_csv(StockPath+File)
        Code=Code+df['Code'].values.tolist()
        Date=Date+df['Date'].values.tolist()
    All=pd.DataFrame()
    All['code']=Code
    All['date']=Date
    All.to_csv(OutputPath+'All.csv',index=False)
    
    
Get_Index_Component_Combination()
#Get_All_Component()
