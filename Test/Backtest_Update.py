# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 10:35:42 2018

@author: xtuser08
"""

import os 
import pandas as pd
import time

Index='ZZ500_ZZ1000'
Period=5
Amount=100.0
FileName='test_all'


Cost=0.003
LongStockLeverage=1
ShortStockLeverage=0.6
IndexLeverage=0.3
#
#Value=['EP_LYR','EP_TTM','BP_MRQ','PB_MRQ_OPP','SP_LYR','SP_TTM','CFP_CFO_TTM'] 
#Growth=['GR_YOY','OR_YOY','OP_YOY','NPP_YOY']
#Momentum=['Momentum5_OPP','Momentum20_OPP','Momentum30_OPP']
#Value_Growth=['PE_TTM_IndustryRank_Diff_OPP_90']
#FactorList=Value+Growth+Momentum+Value_Growth

#因子列表
def Get_Factor_List():

    Value=['EP_LYR','EP_TTM','BP_MRQ','SP_LYR','SP_TTM','CFP_CFO_TTM','PE_LYR_OPP','PE_TTM_OPP','PB_MRQ_OPP','PS_LYR_OPP','PS_TTM_OPP'] 
    Growth=['GR_YOY','OR_YOY','OP_YOY','NPP_YOY'] 
    Momentum=['Momentum5_OPP','Momentum10_OPP','Momentum20_OPP','Momentum30_OPP','Momentum60_OPP','Momentum90_OPP']
    Volatility=['Vol20_OPP','Vol30_OPP','Vol60_OPP','Vol90_OPP']
    Value_Growth=['PE_TTM_IndustryRank_Diff_OPP_90','PE_TTM_IndustryRank_Diff_OPP_180','PE_TTM_IndustryRank_Diff_OPP_270','PE_TTM_IndustryRank_Diff_OPP_360',
                  'PE_TTM_IndustryRank_Diff_OPP_450','PE_TTM_IndustryRank_Diff_OPP_540','PE_TTM_IndustryRank_Diff_OPP_630','PE_TTM_IndustryRank_Diff_OPP_720']    
    FactorList=Value+Growth+Momentum+Volatility+Value_Growth
    return FactorList

FactorList=Get_Factor_List()



#判断路径是否存在，不存在则建立
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 

#获取数据路径
def Get_Data_Path(Index,FileName):
    BacktestID=Index+'_'+FileName
    DataPath=os.path.dirname(os.getcwd())+'\\Data\\'
    FactorLibPath=DataPath+'FactorLibrary\\' 
    StockPath=DataPath+'StockElement\\'
    

    BacktestPath=DataPath+'BacktestResult\\'+BacktestID+'\\'
    FactorPath=BacktestPath+'Factor\\'
    ScorePath=BacktestPath+'Score\\'
    TopSignalPath=BacktestPath+'Top_Signal'+'_'+str(Period)+'Days\\'
    BottomSignalPath=BacktestPath+'Bottom_Signal'+'_'+str(Period)+'Days\\'
    
    Create_Path(FactorPath)
    Create_Path(ScorePath)
    Create_Path(TopSignalPath)   
    Create_Path(BottomSignalPath) 
    
    IndexPath=DataPath+'Index\\'    
    IndexComponentPath=DataPath+'IndexComponent\\'+Index+'.csv'        

    return FactorLibPath,StockPath,BacktestPath,FactorPath,ScorePath,TopSignalPath,BottomSignalPath,IndexPath,IndexComponentPath


#获取所有的因子数据
def Get_Factor_Data(FactorLibPath,FactorList):
    Dict={}
    for Factor in FactorList:    
        print 'Get factor', Factor
        Dict[Factor]=pd.read_csv(FactorLibPath+Factor+'.csv',index_col=0).T
    return Dict


#提取所有的因子值
def Prepare4Score(Dict,FactorPath,IndexComponentPath):
    IndexComponent=pd.read_csv(IndexComponentPath)
    DateList=sorted(list(set(IndexComponent['date'].values.tolist())&set(Dict[FactorList[0]].columns.tolist())))
    DateList=[a for a in DateList if a>'2007-01-01']
    for Date in DateList:
        print 'Prepare for score',Date
        df=pd.DataFrame()
        Code=IndexComponent[IndexComponent['date']==Date]['code'].values.tolist()
        df['Code']=Code
        for Factor in FactorList:
            if Date in Dict[Factor].columns.tolist():
                df[Factor]=Dict[Factor][Date].loc[Code].values.tolist()

        df.to_csv(FactorPath+Date+'.csv',index=False)

#输出信号
def Output_Signal(Code,Industry,SignalPath):
    df=pd.DataFrame()
    df['Code']=Code
    df['Industry']=Industry
    df['Weight']=[1.0/len(Code)]*len(Code)
    df.to_csv(SignalPath,index=None,encoding='gbk')

def Get_Signal(StockPath,FactorPath,ScorePath,TopSignalPath,BottomSignalPath,Period,Amount):
    IndustryData=pd.read_csv(StockPath+'Industry.csv',index_col=1,encoding='gbk')
    del IndustryData['Unnamed: 0']
    FileList=sorted(os.listdir(FactorPath))
    
    #分行业
    for i in range(0,len(FileList)-1,Period):
        File=FileList[i]
        OutputFile=FileList[i+1]
        
        print 'Find signal',File[:-4]
        Data=pd.read_csv(FactorPath+File,index_col=0)
        Data['Industry']=IndustryData.reindex(Data.index).fillna(value=u'其他')['Industry'].values.tolist()
        Data=Data.sort_values(by=['Industry'])
        Score=Data.groupby(by=['Industry']).rank().fillna(value=0).T.sum()
        df=pd.DataFrame()
        df['Score']=Score
        df['Industry']=Data['Industry'].values.tolist()                
        df=df.sort_values(by=['Industry','Score'],ascending=False)
        df.to_csv(ScorePath+File,encoding='gbk')
        
        df=df[df['Score']!=0]
        df=df[df['Industry']!=u'其他']
        
        Percent=Amount/len(df)
        
        Top=df.groupby('Industry').apply(lambda x: x.head(int(round(len(x)*Percent,0))))
        Code=Top.index.get_level_values(1).tolist()
        Industry=Top['Industry'].values.tolist()
        Output_Signal(Code,Industry,TopSignalPath+OutputFile)
        
        Bottom=df.groupby('Industry').apply(lambda x: x.tail(int(round(len(x)*Percent,0))))
        Code=Bottom.index.get_level_values(1).tolist()
        Industry=Bottom['Industry'].values.tolist()        
        Output_Signal(Code,Industry,BottomSignalPath+OutputFile)
        
        
def Get_Index_Return(IndexPath,Date,Index):
    IndexReturn=pd.read_csv(IndexPath+Index+'.csv',encoding='gbk')
    IndexReturn.index=[str(a)[:10] for a in IndexReturn[u'交易时间']]
    IndexReturn=IndexReturn.loc[Date]
    IndexReturn=[float(a)/100 for a in IndexReturn[u'涨跌幅%'].values.tolist()]
    return IndexReturn 

def Get_Portfolio_Return(AdjOpen,AdjClose,DateList,SignalPath,Flag): 
    
    SignalFileList=sorted(os.listdir(SignalPath))
    CalendarDate=AdjClose.index.tolist()
    
    Return=[]
    OldCode=[]
    TurnOverList=[]
    Open=[]
    Weight=[]
    for Date in DateList:
        print 'Backtest',Date
        FormerDate=CalendarDate[CalendarDate.index(Date)-1]
        File=Date+'.csv'
        if File in SignalFileList:
            DailyReturn=0
            #平仓
            if len(OldCode)>0:
                OldStockReturn=(AdjOpen[OldCode].loc[Date]-AdjClose[OldCode].loc[FormerDate])/Open
                OldStockReturn=OldStockReturn.fillna(0)
                DailyReturn=DailyReturn+sum([OldStockReturn[a]*Weight[a] for a in range(len(Weight))])
            
            #开仓
            Signal=pd.read_csv(SignalPath+File,encoding='gbk')
            Code=Signal['Code'].values.tolist()
            Weight=Signal['Weight'].values.tolist()            
            Open=AdjOpen[Code].loc[Date]
            
            NewStockReturn=(AdjClose[Code].loc[Date]-AdjOpen[Code].loc[Date])/Open
            NewStockReturn=NewStockReturn.fillna(0)
            DailyReturn=DailyReturn+sum([NewStockReturn[a]*Weight[a] for a in range(len(Weight))])             
                       
    
            if len(Code)>len(OldCode):
                TurnOver=len(set(Code)-set(OldCode))*1.0/len(Code)
            else:
                TurnOver=len(set(OldCode)-set(Code))*1.0/len(OldCode)
                
            DailyReturn=Flag*DailyReturn-Cost*TurnOver
        else:
            OldCode=Code
            TurnOver=0
            StockReturn=(AdjClose[Code].loc[Date]-AdjClose[Code].loc[FormerDate])/Open
            StockReturn=StockReturn.fillna(0)
            DailyReturn=Flag*sum([StockReturn[a]*Weight[a] for a in range(len(Weight))])
            
        TurnOverList.append(TurnOver)
        Return.append(DailyReturn)
    return Return    

def Backtest(StockPath,FactorPath,IndexPath,TopSignalPath,BottomSignalPath,BacktestPath):
    
    AdjOpen=pd.read_csv(StockPath+'AdjOpen.csv',index_col=0)
    AdjClose=pd.read_csv(StockPath+'AdjClose.csv',index_col=0)    
    
    Date=[a[:-4] for a in sorted(os.listdir(FactorPath))][1:]

    
    ZZ500=Get_Index_Return(IndexPath,Date,'ZZ500')
    HS300=Get_Index_Return(IndexPath,Date,'HS300')
    Top=Get_Portfolio_Return(AdjOpen,AdjClose,Date,TopSignalPath,1)
    Bottom=Get_Portfolio_Return(AdjOpen,AdjClose,Date,BottomSignalPath,-1)
    
    df=pd.DataFrame()
    df['Top']=Top
    df['Bottom']=Bottom
    df['HS300']=HS300
    df['ZZ500']=ZZ500
    
    df.index=Date
    df['TopMinusHS300']=(df['Top']-df['HS300'])/(LongStockLeverage+IndexLeverage)
    df['TopMinusZZ500']=(df['Top']-df['ZZ500'])/(LongStockLeverage+IndexLeverage)
    
    TopMinusHS300=df['TopMinusHS300'].values.tolist()
    TopMinusZZ500=df['TopMinusZZ500'].values.tolist()
    
    df['HS300MinusBottom']=(df['HS300']+df['Bottom'])/(IndexLeverage+ShortStockLeverage)
    df['ZZ500MinusBottom']=(df['ZZ500']+df['Bottom'])/(IndexLeverage+ShortStockLeverage)
    
    HS300MinusBottom=df['HS300MinusBottom'].values.tolist()
    ZZ500MinusBottom=df['ZZ500MinusBottom'].values.tolist()
    
    df['TopMinusBottom']=(df['Top']+df['Bottom'])/(LongStockLeverage+ShortStockLeverage)
    
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
    

Start=time.clock()  


print Index,FactorList
FactorLibPath,StockPath,BacktestPath,FactorPath,ScorePath,TopSignalPath,BottomSignalPath,IndexPath,IndexComponentPath=Get_Data_Path(Index,FileName)

#Dict=Get_Factor_Data(FactorLibPath,FactorList)
#Prepare4Score(Dict,FactorPath,IndexComponentPath)

Get_Signal(StockPath,FactorPath,ScorePath,TopSignalPath,BottomSignalPath,Period,Amount)

Backtest(StockPath,FactorPath,IndexPath,TopSignalPath,BottomSignalPath,BacktestPath)    

End=time.clock()
print End-Start


    
    



