# -*- coding: utf-8 -*-
"""
Created on Fri Mar 09 15:46:05 2018

@author: xtuser08
"""

import os
import pandas as pd

PeriodList=[90*a for a in range(1,9)]
HigherDir=os.path.dirname(os.path.dirname(os.getcwd()))
FactorPath=HigherDir+'\\Data\\FactorLibrary\\'
StockPath=HigherDir+'\\Data\\StockElement\\'

PE=-pd.read_csv(FactorPath+'PE_TTM_OPP.csv',index_col=0).T
Industry=pd.read_csv(StockPath+'Industry.csv',index_col=1,encoding='gbk')
del Industry['Unnamed: 0']

df=pd.concat([Industry,PE],axis=1)
PE_Industry_Rank=df.groupby(['Industry']).rank().T


for Period in PeriodList:
    print Period
    
    PE_Industry_Rank_Diff=PE_Industry_Rank-PE_Industry_Rank.shift(Period)
    PE_Industry_Rank_Diff_OPP=-PE_Industry_Rank_Diff.dropna(how='all',axis=0)
    PE_Industry_Rank_Diff_OPP.to_csv(FactorPath+'PE_IndustryRank_Diff_OPP_'+str(Period)+'.csv')

    