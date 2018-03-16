# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 17:21:59 2018

@author: xtuser08
"""

import os
import pandas as pd
import datetime
import time

#判断路径是否存在，不存在则建立
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 

#获取总股本每份数据的文件     
def Get_File_DataFrame(Path,FileName):
    df=pd.read_csv(Path+FileName,header=None)
    df.columns=['Date','Code','TotalShare']
    return df    

#获取总股本的数据   
def Get_Total_Capital(Path):
    FileNameList=os.listdir(Path)
    df=Get_File_DataFrame(Path,FileNameList[0])
    for FileName in FileNameList[1:]:
        df=df.append(Get_File_DataFrame(Path,FileName))
        print FileName,'is done'
    df['Date']=[datetime.datetime.strptime(a,'%Y/%m/%d').strftime('%Y-%m-%d') for a in df['Date'].values.tolist()]
    return df

#获取所有股票的数据
def Get_Stock_Data(TotalSharePath,StockInfoPath,StockPath):
    Create_Path(StockPath)    
    #总股本
    TotalShare=Get_Total_Capital(TotalSharePath)
    print 'Get Total Share'
    
    #股票信息
    Stock=pd.read_csv(StockInfoPath,encoding='gbk')
    Stock.columns=['Date','Code','AdjOpen','AdjHigh','AdjLow','AdjClose','Close','Volume','Amount','ST','FreeFloatA','Industry']
    print 'Get Stock Info'
    
    #股票与总股本的数据，删除2007年以前数据
    StockData=Stock.merge(TotalShare,on=['Date','Code'],how='outer')
    StockData=StockData[StockData['Date']>'2006-01-01']
    print 'Merged'
    
    #
    CodeList=sorted(list(set(StockData['Code'].values.tolist())))
    for Code in CodeList:
        SingleStock=StockData[StockData['Code']==Code]
        SingleStock=SingleStock.sort_values(by=['Date'])
        SingleStock.to_csv(StockPath+Code+'.csv',index=None,encoding='gbk')
        print Code,len(SingleStock)

#获取所有股票对应元素的数据        
def Segregate_Then_Merge(InputPath,OutputPath):
    Create_Path(OutputPath)
    #获取全部文件数据
    FileList=os.listdir(InputPath)
    Dict={}
    for FileName in FileList:
        Code=FileName[:10]
        print Code
        Data=pd.read_csv(InputPath+FileName,index_col=0,encoding='gbk')
        Dict[Code]=Data
    
    #对文件数据按因子拆分后按股票合并    
    KeyList=sorted(Dict.keys())
    FactorList=Dict.get(KeyList[0]).columns.tolist()[1:]
    if 'Industry' in FactorList:
        FactorList.pop(FactorList.index('Industry'))
        
    for Factor in FactorList:
        FactorDict={}    
        for Key in KeyList:
            print Factor,Key
            FactorDict[Key]=Dict.get(Key)[Factor]   
        df=pd.concat(FactorDict).unstack().T 
        df.to_csv(OutputPath+Factor+'.csv',encoding='gbk')  
        
#获取股票的行业        
def Get_Industry(InputPath,OutputPath):
    Data=pd.read_csv(InputPath,encoding='gbk').dropna(how='all')
    Industry=pd.DataFrame()
    CodeList=[str(int(a)) for a in Data[u'股票代码'].values.tolist()]
    CodeList=['0'*(6-len(a))+a if len(a)<6 else a for a in CodeList]
    CodeList=[('SSE_' if a[0]=='6' else 'SZE_')+a for a in CodeList]
    Industry['Code']=CodeList
    Industry['Industry']=Data[u'行业名称'].values.tolist()
    Industry.index=[time.strftime('%Y-%m-%d',time.strptime(str(a),'%Y-%m-%d %H:%M')) for a in Data[u'起始日期'].values.tolist()]
    Industry.to_csv(OutputPath+'Industry.csv',encoding='gbk')

#输入路径
HigherDir=os.path.dirname(os.getcwd())
TotalSharePath=os.path.dirname(HigherDir)+'\\Data\\zgb\\'
StockInfoPath=os.path.dirname(HigherDir)+'\\Data\\stock_info\\day.csv'
IndustryPath=os.path.dirname(HigherDir)+'\\Data\\stock_info\\SwClass.csv'

#输出路径
StockPath=HigherDir+'\\Data\\StockData\\'
StockElementPath=HigherDir+'\\Data\\StockElement\\'


Get_Stock_Data(TotalSharePath,StockInfoPath,StockPath)
Segregate_Then_Merge(StockPath,StockElementPath)
Get_Industry(IndustryPath,StockElementPath)