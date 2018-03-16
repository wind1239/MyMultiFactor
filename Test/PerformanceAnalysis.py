# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 13:01:49 2017

@author: hasee
"""

#Performance Analysis
#Delete fama_french anaylisis in pyfolio library
import pyfolio as pf
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

PortfolioName='TopMinusZZ500'
BenchmarkIndex='ZZ500'

Index='ZZ500'
BacktestID=Index+'_haha'
FileName='Return_5Days'
#FileName='1'

def Get_Drawdown_Table(Portfolio,OutputPath):
    drawdown_df=pf.timeseries.gen_drawdown_table(Portfolio, top=len(Portfolio)/10)
    drawdown_df=drawdown_df[drawdown_df['Net drawdown in %']>1]
    drawdown_df.to_csv(OutputPath+FileName+'_Drawdown.csv',index=None)
    
def Get_Return_Analysis(Portfolio,Index,OutputPath):
    perf_stats=pd.DataFrame(pf.timeseries.perf_stats(Portfolio,Index),columns=['Backtest'])
    perf_stats.to_csv(OutputPath+FileName+'_PerformanceStats.csv')
    
def Change_Return_Format(Date,Return):  
    DailyReturn=pd.Series(Return)
    DailyReturn.columns='Return'
    DailyReturn.index=pd.DatetimeIndex(Date,tz='Asia/Shanghai')
    return DailyReturn



DataPath=os.path.dirname(os.getcwd())+'\\Data\\'
BacktestPath=DataPath+'BacktestResult\\'+BacktestID+'\\'

Data=pd.read_csv(BacktestPath+FileName+'.csv',index_col=0)
Date=Data.index.tolist()
Portfolio=Data[PortfolioName].values.tolist()
Index=Data[BenchmarkIndex].values.tolist()


Portfolio=Change_Return_Format(Date,Portfolio)
Index=Change_Return_Format(Date,Index)


pf.create_full_tear_sheet(Portfolio,benchmark_rets=Index)
Get_Drawdown_Table(Portfolio,BacktestPath)
Get_Return_Analysis(Portfolio,Index,BacktestPath)




