# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 10:35:42 2018

@author: xtuser08
"""

import os 
import pandas as pd
import math


Index='ZZ500'
Period=5
Percent=1/5.0
Cost=0.003
BacktestID=Index+'_BestVersion'

Value=['EP_LYR','EP_TTM','BP_MRQ','SP_LYR','SP_TTM','CFP_CFO_LYR','CFP_CFO_TTM'] 
Growth=['GR_YOY','OR_YOY','OP_YOY','NPP_YOY']
Momentum=['Momentum5_OPP','Momentum20_OPP','Momentum30_OPP']
FactorList=Value+Growth+Momentum


#判断路径是否存在，不存在则建立
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 


def Get_DataPath(Index,BacktestID):
    DataPath=os.path.dirname(os.getcwd())+'\\Data\\'
    if Index=='All':
        FactorPath=DataPath+'FactorLibrary\\' 
        StockPath=DataPath+'StockElement\\'
    else:
        FactorPath=DataPath+'Factor4IndexComponent\\'+Index+'\\'
        StockPath=FactorPath
    BacktestPath=DataPath+'BacktestResult\\'+BacktestID+'\\'
    PreScorePath=BacktestPath+'PreScore\\'
    TopSignalPath=BacktestPath+'Top_Signal'+'_'+str(Period)+'Days\\'
    BottomSignalPath=BacktestPath+'Bottom_Signal'+'_'+str(Period)+'Days\\'
    Create_Path(PreScorePath)
    Create_Path(TopSignalPath)   
    Create_Path(BottomSignalPath) 
    IndexPath=DataPath+'Index\\'
    return FactorPath,StockPath,BacktestPath,PreScorePath,TopSignalPath,BottomSignalPath,IndexPath

def Get_Stock_Return(StockPath):
    AdjClose=pd.read_csv(StockPath+'AdjClose.csv',index_col=0)
    Return=AdjClose/AdjClose.shift(1)-1
    Return=Return.T.dropna(axis=1,how='all')
    return Return

def Get_Factor_Data(FactorPath,FactorList):
    Dict={}
    for Factor in FactorList:    
        Dict[Factor]=pd.read_csv(FactorPath+Factor+'.csv',index_col=0).T
    return Dict


def Prepare4Score(Return,Dict,PreScorePath):
    DateList=Return.columns.tolist()
    for Date in DateList:
        print 'Prepare for score',Date
        df=pd.DataFrame()
        CurrentReturn=Return[Date].dropna()
        df['Return']=CurrentReturn    
        StockList=df.index.tolist()
        for Factor in FactorList:
            df[Factor]=Dict[Factor][Date].loc[StockList].values.tolist()
        df.to_csv(PreScorePath+Date+'.csv')

def Output_Signal(Code,SignalPath):
    df=pd.DataFrame()
    df['Code']=Code
    df['Weight']=[1.0/len(Code)]*len(Code)
    df.to_csv(SignalPath,index=None)

def Get_Signal(StockPath,PreScorePath,TopSignalPath,BottomSignalPath,Period,Percent):
    IndustryData=pd.read_csv(StockPath+'Industry.csv',index_col=1,encoding='gbk')
    del IndustryData['Unnamed: 0']   
    FileList=sorted(os.listdir(PreScorePath))
    
    #分行业
    for i in range(0,len(FileList),Period):
        File=FileList[i]
        print 'Find signal',File[:-4]
        Data=pd.read_csv(PreScorePath+File,index_col=0)
        Industry=IndustryData.loc[Data.index].fillna(value=u'其他')['Industry'].values.tolist()
        Data['Industry']=Industry
        Data=Data.sort_values(by=['Industry'])
#        Data=Data[Data['Industry']!=u'其他']
        del Data['Return']
        Score=Data.groupby(by=['Industry']).rank().fillna(value=0).T.sum()
        df=pd.DataFrame()
        df['Score']=Score
        df['Industry']=Data['Industry'].values.tolist()
        df=df.sort_values(by=['Industry','Score'],ascending=False)
        
        Code=df.groupby('Industry').apply(lambda x: x.head(int(round(len(x)*Percent,0)))).index.levels[1].tolist()
        Output_Signal(Code,TopSignalPath+File)
        
        Code=df.groupby('Industry').apply(lambda x: x.tail(int(round(len(x)*Percent,0)))).index.levels[1].tolist()
        Output_Signal(Code,BottomSignalPath+File)
        
        
def Get_Index_Return(IndexPath,Date,Index):
    IndexReturn=pd.read_csv(IndexPath+Index+'.csv',encoding='gbk')
    IndexReturn.index=[str(a)[:10] for a in IndexReturn[u'交易时间']]
    IndexReturn=IndexReturn.loc[Date]
    IndexReturn=[float(a)/100 for a in IndexReturn[u'涨跌幅%'].values.tolist()]
    return IndexReturn 

def Get_Portfolio_Return(FactorFileList,SignalPath):   
    SignalFileList=sorted(os.listdir(SignalPath))
    Return=[]
    OldCode=[]
    TurnOverList=[]
    for File in FactorFileList[1:]:
        print 'Backtest',File[:-4]
        FormerFile=FactorFileList[FactorFileList.index(File)-1]
        if FormerFile in SignalFileList:
            Signal=pd.read_csv(SignalPath+FormerFile)
            Code=Signal['Code'].values.tolist()
            Weight=Signal['Weight'].values.tolist()
    
            if len(Code)>len(OldCode):
                TurnOver=len(set(Code)-set(OldCode))*1.0/len(Code)
            else:
                TurnOver=len(set(OldCode)-set(Code))*1.0/len(OldCode)
        else:
            OldCode=Code
            TurnOver=0
        Data=pd.read_csv(PreScorePath+File,index_col=0)
        StockReturn=[0 if math.isnan(a) else a for a in Data['Return'].T[Code].values.tolist() ]
        DailyReturn=sum([StockReturn[a]*Weight[a] for a in range(len(Weight))])-Cost*TurnOver
        TurnOverList.append(TurnOver)
        Return.append(DailyReturn)
    return Return    

def Backtest(PreScorePath,IndexPath,TopSignalPath,BottomSignalPath):
    FactorFileList=sorted(os.listdir(PreScorePath))
    Date=[a[:10] for a in FactorFileList][1:]
    ZZ500=Get_Index_Return(IndexPath,Date,'ZZ500')
    HS300=Get_Index_Return(IndexPath,Date,'HS300')
    Top=Get_Portfolio_Return(FactorFileList,TopSignalPath)
    Bottom=Get_Portfolio_Return(FactorFileList,BottomSignalPath)
    
    df=pd.DataFrame()
    df['Top']=Top
    df['Bottom']=[-a for a in Bottom]
    df['HS300']=HS300
    df['ZZ500']=ZZ500
    
    df.index=Date
    df['TopMinusHS300']=df['Top']-df['HS300']
    df['TopMinusZZ500']=df['Top']-df['ZZ500']
    
    TopMinusHS300=df['TopMinusHS300'].values.tolist()
    TopMinusZZ500=df['TopMinusZZ500'].values.tolist()
    
    df['HS300MinusBottom']=df['HS300']+df['Bottom']
    df['ZZ500MinusBottom']=df['ZZ500']+df['Bottom']
    
    HS300MinusBottom=df['HS300MinusBottom'].values.tolist()
    ZZ500MinusBottom=df['ZZ500MinusBottom'].values.tolist()
    
    df['TopMinusBottom']=df['Top']+df['Bottom']
    
    TopMinusBottom=df['TopMinusBottom'].values.tolist()
    
    df['CumTop']=[1+sum(Top[:i])for i in range(len(Top))]
    df['CumBottom']=[1+sum(Bottom[:i])for i in range(len(Top))]
    df['CumHS300']=[1+sum(HS300[:i])for i in range(len(Top))]
    df['CumZZ500']=[1+sum(ZZ500[:i])for i in range(len(Top))]
    
    df['CumTopMinusHS300']=[1+sum(TopMinusHS300[:i])for i in range(len(Top))]
    df['CumTopMinusZZ500']=[1+sum(TopMinusZZ500[:i])for i in range(len(Top))]
    
    df['CumHS300MinusBottom']=[1+sum(HS300MinusBottom[:i])for i in range(len(Top))]
    df['CumZZ500MinusBottom']=[1+sum(ZZ500MinusBottom[:i])for i in range(len(Top))]
    
    df['CumTopMinusBottom']=[1+sum(TopMinusBottom[:i])for i in range(len(Top))]
    df.to_csv(BacktestPath+'Return_'+str(Period)+'Days.csv')
    
    
FactorPath,StockPath,BacktestPath,PreScorePath,TopSignalPath,BottomSignalPath,IndexPath=Get_DataPath(Index,BacktestID)


Return=Get_Stock_Return(StockPath)
Dict=Get_Factor_Data(FactorPath,FactorList)

#Prepare4Score(Get_Stock_Return(StockPath),Get_Factor_Data(FactorPath,FactorList),PreScorePath)

print 'Find Signal'
#Get_Signal(StockPath,PreScorePath,TopSignalPath,BottomSignalPath,Period,Percent)

print 'Backtest'
#Backtest(PreScorePath,IndexPath,TopSignalPath,BottomSignalPath)




    
    



