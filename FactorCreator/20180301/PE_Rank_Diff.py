# -*- coding: utf-8 -*-
"""
Created on Fri Mar 09 15:46:05 2018

@author: xtuser08
"""

import os
import pandas as pd

FactorList=['PE_LYR_OPP','PE_TTM_OPP','PB_MRQ_OPP','PS_LYR_OPP','PS_TTM_OPP','CFO_CFP_LYR_OPP','CFO_CFP_TTM_OPP','NCF_CFP_LYR_OPP','NCF_CFP_TTM_OPP']
PeriodList=[90*a for a in range(1,9)]
HigherDir=os.path.dirname(os.path.dirname(os.getcwd()))
FactorPath=HigherDir+'\\Data\\FactorLibrary\\'
StockPath=HigherDir+'\\Data\\StockElement\\'

for Factor in FactorList:
    FactorData=-pd.read_csv(FactorPath+Factor+'.csv',index_col=0).T
    Industry=pd.read_csv(StockPath+'Industry.csv',index_col=1,encoding='gbk')
    del Industry['Unnamed: 0']
    
    df=pd.concat([Industry,FactorData],axis=1)
    FactorIndustry_Rank=df.groupby(['Industry']).rank().T
    
    
    for Period in PeriodList:
        print Factor,Period
        
        FactorIndustry_Rank_Diff=FactorIndustry_Rank-FactorIndustry_Rank.shift(Period)
        FactorIndustry_Rank_Diff_OPP=-FactorIndustry_Rank_Diff.dropna(how='all',axis=0)
        FactorIndustry_Rank_Diff_OPP.to_csv(FactorPath+Factor[:-4]+'_IndustryRank_Diff_OPP_'+str(Period)+'.csv')

    