# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 13:02:44 2017

@author: hasee
"""

import pandas as pd
import numpy as np
import scipy.optimize as sco
import time as tt
import os
from WindPy import w
import matplotlib.pyplot as plt

AllCode=pd.read_csv('Code\HS300Code.csv')
TradeCode=pd.read_csv('Code\TradeCodes.csv',low_memory=False)
AllPrice=pd.read_csv('StockData\HS300CloseHFQ.csv', index_col=0)
IndexPrice=pd.read_csv('StockData\HS300Index.csv', index_col=0)
tdate = AllPrice.index.tolist() 

def Statistics(Weights):

    Weights = np.array(Weights)    
    PReturns = np.sum(Returns.mean()*Weights)*252    
    PVariance = np.dot(Weights.T, np.dot(Returns.cov()*252,Weights))

    return np.array([PReturns, PVariance, PReturns/PVariance])

def Maximum_Sharpe_Ratio(Weights):

    return -Statistics(Weights)[2]

def Minimum_Variance(Weights):
    return Statistics(Weights)[1]



def Get_Returns(Code,EndDate,ndays):
    Index = tdate.index(EndDate)
    StartDate=tdate[Index-ndays]
    
    Price=AllPrice[Code].loc[StartDate:EndDate]
    Price['HS300']=IndexPrice['HS300'].loc[StartDate:EndDate]
    LagPrice=Price.shift(1)
    Returns=(Price/LagPrice-1)
    return Returns
    

def Optimize_Sharpe_Ratio(Code,Returns,StockLB,StockUB,IndexLB,IndexUB):
    Num=len(Code)
    
    cons = ({'type':'eq', 'fun':lambda x: np.sum(abs(x))-1})
    bnds = tuple([(StockLB,StockUB) for x in range(Num-1)]+[(IndexLB,IndexUB)])
    
    print 'optimization start'
    st=tt.clock()
    opts = sco.minimize(Maximum_Sharpe_Ratio, Num*[1./Num,], method = 'SLSQP', bounds = bnds, constraints = cons)
    print 'cost',tt.clock()-st,'seconds'
    print 'optimization finished'
    
    Weight=opts['x']
    Stat=Statistics(opts['x'])
    return Weight,Stat

def Optimize_Variance(Code,Returns,StockLB,StockUB,IndexLB,IndexUB):
    Num=len(Code)
    
    cons = ({'type':'eq', 'fun':lambda x: np.sum(abs(x))-1})
    bnds = tuple([(StockLB,StockUB) for x in range(Num-1)]+[(IndexLB,IndexUB)])
    
    print 'optimization start'
    st=tt.clock()
    opts = sco.minimize(Minimum_Variance, Num*[1./Num,], method = 'SLSQP', bounds = bnds, constraints = cons)
    print 'cost',tt.clock()-st,'seconds'
    print 'optimization finished'
    
    Weight=opts['x']
    Stat=Statistics(opts['x'])
    return Weight,Stat

def WeightList_Output(Code,Weight,FileName):
    WeightList=pd.DataFrame()
    WeightList['Code']=Code
    WeightList['Weight']=Weight
    WeightList.to_csv(FileName)
    
ndays=5
UpdateFrequency=5
StartDate='2011-01-10'
EndDate='2011-02-01'
#EndDate='2017-04-17'
#EndDate='2015-01-23'

StockLB=0
StockUB=1
IndexLB=-1
IndexUB=0
homedir=os.getcwd()

StorePosition=homedir+'\WeightWithIndexMinimumVariance\\'  
if not os.path.exists(StorePosition):
    os.makedirs(StorePosition) 
    
Capital=[1000000]
#
BacktestDate=[tdate[a] for a in range(tdate.index(StartDate),tdate.index(EndDate)+1)]
w.start()
wData=w.tdays(tdate[tdate.index(StartDate)-10], EndDate, "Period=W")
Update=[a.strftime('%Y-%m-%d') for a in wData.Times]
Update=[tdate[tdate.index(a)] for a in Update]

for i in range(len(BacktestDate)):
    TradeDate=BacktestDate[i]
    FormerDate=tdate[tdate.index(TradeDate)-1]
    
    print TradeDate

    if FormerDate in Update:
        
        Code=AllCode[FormerDate].values.tolist()
        CodeList=[]
        TradeList=TradeCode[FormerDate].values.tolist()
        for j in Code:
            if j in TradeList:
                CodeList.append(j)
                
        Returns=Get_Returns(CodeList,FormerDate,ndays)
        CodeList.append('HS300')
        
        # if Returns['HS300'].mean()>0:
        #     Weight,Stat=Optimize_Sharpe_Ratio(CodeList,Returns,StockLB,StockUB,IndexLB,IndexUB)
        # else:
        Weight,Stat=Optimize_Variance(CodeList,Returns,StockLB,StockUB,IndexLB,IndexUB)
               
  
        TradeCodeList=[CodeList[a] for a in range(len(Weight)) if abs(Weight[a])>0.0001]        
        TradeWeightList=[Weight[a] for a in range(len(Weight)) if abs(Weight[a])>0.0001]
        print TradeCodeList
        print TradeWeightList
        
        if len(TradeWeightList)==0:
            Weight=[0]*len(CodeList)
#
#
        WeightList_Output(CodeList,Weight,StorePosition+'Weight'+FormerDate+'.csv')   
        
#        df1=pd.read_csv(StorePosition+'Weight'+FormerDate+'.csv',index_col=0)   
#        Code=df1['Code'].values.tolist()
#        Weight=df1['Weight'].values
#        df2=pd.read_csv('StockData\HS300Index.csv',index_col=0)

        Price=AllPrice[CodeList[0:-1]].loc[FormerDate]
        Price['HS300']=IndexPrice['HS300'].loc[FormerDate]
        FormerIndexPrice=IndexPrice['HS300'].loc[FormerDate]
        
#        TradeCodeList=[CodeList[a] for a in range(len(Weight)) if abs(Weight[a])>0.0001] 

        WeightStandard=sum([abs(a) for a in Weight])
        
        Percent=1
        Share=Capital[-1]*Percent*Weight/WeightStandard/Price
        StockShare=[int(abs(a)/100)*100 for a in Share[0:-1]]
        IndexShare=int(abs(Share[-1]))
        Margin=IndexShare*Price['HS300']
        Cash=Capital[-1]-sum(StockShare*Price[0:-1])-Margin
#        print IndexShare
        
#        IndexPrice=df2['HS300'].loc[FormerDate]
#        IndexShare=int(Cash/IndexPrice/100)*100
#        Margin=IndexPrice*IndexShare
#        Cash=Cash-Margin
        
#    IndexPrice1=df2['HS300'].loc[FormerDate]
#    IndexPrice2=df2['HS300'].loc[TradeDate]
#    NewCapital=sum(StockShare*Price)+Cash+Margin+(IndexPrice1-IndexPrice2)*IndexShare
        
    Price=AllPrice[CodeList[0:-1]].loc[TradeDate]

    Price2=IndexPrice['HS300'].loc[TradeDate]
    NewCapital=sum(StockShare*Price)+Cash+Margin+(FormerIndexPrice-Price2)*IndexShare
    
    print sum(StockShare*Price),Cash,Margin,(FormerIndexPrice-Price2)*IndexShare

    
    
    print NewCapital
    Capital.append(NewCapital)        
#    if i==1214:
#        break
Capital.pop(0)
CapitalReturn=[i/Capital[0] for i in Capital]

HS300Data=IndexPrice['HS300'].loc[BacktestDate[0]:BacktestDate[-1]]

HS300=[i/HS300Data[0] for i in HS300Data]

plt.plot(HS300,'r')
plt.plot(CapitalReturn,'b')
plt.show()

df=pd.DataFrame()
df['Date']=BacktestDate
df['Strategy']=CapitalReturn
df['HS300']=HS300
df.to_csv('Strategy.csv')
   






