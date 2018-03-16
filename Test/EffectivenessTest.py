# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 18:46:32 2018

@author: xtuser08
"""
import os
import alphalens
import time
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

#测试数据
FactorName='PE_IndustryRank_Diff_OPP_90'
Index='All'
Year=0 #单独看某一年的话，year=某一年，全部回测时间的话，year=0
Quantile=10



HigherDir=os.path.dirname(os.getcwd())
def Get_DataPath(Index):

    if Index=='All':
        FactorPath=HigherDir+'\\Data\\FactorLibrary\\' 
        StockPath=HigherDir+'\\Data\\StockElement\\'
    else:
        FactorPath=HigherDir+'\\Data\\Factor4IndexComponent\\'+Index+'\\'
        StockPath=FactorPath
    return FactorPath,StockPath

def Format4Alphalen(df,Name):
    df.index=pd.to_datetime(df.index).tz_localize('UTC')
    df=df.stack()
    df.index=df.index.set_names(['Date',Name])
    return df

def Get_Factor_AdjClose_Sector(FactorPath,StockPath,FactorName,Year):
    Factor=pd.read_csv(FactorPath+FactorName+'.csv',index_col=0,encoding='gbk')
    
    AdjClose=pd.read_csv(StockPath+'AdjClose.csv',index_col=0,encoding='gbk')
    
    if Year!=0:    
        Date=[a for a in AdjClose.index.tolist() if a>str(Year)+'-01-01' and a<str(Year+1)+'-01-01']

    else:
        Date=[a for a in AdjClose.index.tolist() if '2007-01-01']
    AdjClose=AdjClose.loc[Date]
    Factor=Factor.loc[Date]

        
    AdjClose.index=pd.to_datetime(AdjClose.index).tz_localize('UTC')
    AdjCloseCodeList=AdjClose.columns.tolist()
    
    Industry=pd.read_csv(StockPath+'Industry.csv',index_col=0,encoding='gbk')
    IndustryShortName=pd.read_csv(HigherDir+'\\Data\\IndustryWithEnglishName.csv',encoding='gbk')
    IndustryCN=IndustryShortName['Industry'].values.tolist()
    IndustryEN=IndustryShortName['Name'].values.tolist()
    IndustryList=[IndustryEN[IndustryCN.index(a)] for a in Industry['Industry'].values.tolist()]
    CodeList=Industry['Code'].values.tolist()
    SectorNames=pd.Series(IndustryEN).to_dict()
    
    OtherCode=list(set(AdjCloseCodeList)-set(CodeList))
    CodeSector=dict(zip(CodeList+OtherCode,[IndustryEN.index(a) for a in IndustryList]+[len(IndustryEN)-1]*len(OtherCode)))
        
    Factor=Format4Alphalen(Factor,FactorName)
    if len(Factor)<365:
        Period=(5,10,20,30)
    else:
        Period=(5,10,20,30,60,90)
        
    return Factor,AdjClose,Period,SectorNames,CodeSector

def Get_Analysis_For_Single_Industry(SectorNames,CodeSector,Factor,Symbol,AdjClose,Quantile):
    Group=[str(CodeSector.keys()[a]) for a in range(len(CodeSector.values())) if CodeSector.values()[a]==SectorNames.values().index(Symbol)]
    Factor=Factor.unstack()
    Group=[a for a in Group if a in Factor.columns.tolist()]
    Factor=Factor[Group]
    Factor=Factor.stack()
    FactorData = alphalens.utils.get_clean_factor_and_forward_returns(Factor,
                                                                       AdjClose,                                                                   
                                                                       periods=(5,10,20,30,60,90),
                                                                       quantiles=Quantile,
                                                                       bins=None)
    alphalens.tears.create_full_tear_sheet(FactorData,long_short=True)

def Effectiveness_Test(FactorName,Index,Year,Quantile):
    print FactorName,Index
    Start=time.clock()
    
    FactorPath,StockPath=Get_DataPath(Index)
    
    Factor,AdjClose,Period,SectorNames,CodeSector=Get_Factor_AdjClose_Sector(FactorPath,StockPath,FactorName,Year)
    
    FactorData = alphalens.utils.get_clean_factor_and_forward_returns(Factor,
                                                                       AdjClose,                                                                   
                                                                       periods=Period,
                                                                       quantiles=Quantile,
                                                                       groupby=CodeSector,
                                                                       groupby_labels=SectorNames,
                                                                       bins=None)
    
    alphalens.tears.create_full_tear_sheet(FactorData,long_short=True,group_neutral=True,by_group=False)
    #Get_Analysis_For_Single_Industry(SectorNames,CodeSector,Factor,u'Bank',AdjClose,Quantile)
    
    #alphalens.tears.plotting.plot_quantile_statistics_table(FactorData)
    #alphalens.tears.create_returns_tear_sheet(FactorData,long_short=True,group_neutral=True,by_group=False,set_context=False)
    #alphalens.tears.create_information_tear_sheet(FactorData,group_neutral=True,by_group=False,set_context=False)
    #alphalens.tears.create_turnover_tear_sheet(FactorData, set_context=False)
    
    End=time.clock()
    print End-Start
#Effectiveness_Test(FactorName,Index,Year,Quantile)

