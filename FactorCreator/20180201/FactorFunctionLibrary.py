# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 13:37:30 2018

@author: xtuser08
"""

import pandas as pd

#获取收盘价、后复权收盘价、自由流通A股股本，总股本，行业
def Get_Stock_Info(Stock):
    Date=Stock['Date'].values.tolist()
    Close=pd.DataFrame((Stock['Close']).values.tolist(),index=Date,columns=['Close'])
    AdjClose=pd.DataFrame((Stock['AdjClose']).values.tolist(),index=Date,columns=['Close'])    
    FreeFloatA=pd.DataFrame((Stock['FreeFloatA']*10000).values.tolist(),index=Date,columns=['FreeFloatA'])
    TotalShare=pd.DataFrame((Stock['TotalShare']*10000).values.tolist(),index=Date,columns=['TotalShare'])
    Industry=pd.DataFrame((Stock['Industry']).values.tolist(),index=Date,columns=['Industry'])
    return Close,AdjClose,FreeFloatA,TotalShare,Industry

#第3种类型，当期报告公告日期与下期公告日期重合
def Remove_Duplicated_Data(df):
    df['Sign']=~df.index.duplicated(keep='last') #重复时，保留后面出现的日期的数据
    df=df[df['Sign']==True]
    del df['Sign']  
    return df  

#计算SQ（单季度）
def Get_SQ(df,Name,Symbol):
    df_PublicDate=pd.DataFrame(df[Name].values.tolist(),index=df[u'公告日期'].values.tolist()) 

    ReportDate=df[u'报告年度'].values.tolist()
    FirstSeasonIndex=[a for a in range(len(ReportDate)) if ReportDate[a][-5:]=='03-31'] #第一季度的数据位置索引
    
    SQ=df_PublicDate-df_PublicDate.shift(1)
    SQ[0][FirstSeasonIndex]=df[Name][FirstSeasonIndex]#第一季度不变
    SQ.columns=[Symbol+'_SQ']
    return SQ

#计算LYR（最近一期年报）
def Get_LYR(df,Name,Symbol):
    ReportDate=df[u'报告年度'].values.tolist()
    Index=[a for a in range(len(ReportDate)) if ReportDate[a][-5:]=='12-31']#年报数据位置索引
    df_Year=df.iloc[Index] 
    LYR=pd.DataFrame(df_Year[Name].values.tolist(),index=df_Year[u'公告日期'].values.tolist())
    LYR.columns=[Symbol+'_LYR']
    return LYR

  
#计算TTM（滚动计算4个季度）
def Get_TTM(df,Name,Symbol):
    SQ=Get_SQ(df,Name,Symbol)
    TTM=(SQ+SQ.shift(1)+SQ.shift(2)+SQ.shift(3)).dropna()  
    TTM=pd.DataFrame(TTM)
    TTM.columns=[Symbol+'_TTM']
    
    #第3种类型，当期报告公告日期与下期公告日期重合
    TTM=Remove_Duplicated_Data(TTM) 
    return TTM


#计算MRQ（最近一期季报）
def Get_MRQ(df,Name,Symbol):        
    MRQ=pd.DataFrame(df[Name].values.tolist(),index=df[u'公告日期'].values.tolist())
    MRQ.columns=[Symbol+'_MRQ'] 
    return MRQ

def Replace_INF(df,Symbol):
    Index=df[df[Symbol]==float('inf')].index.tolist()
    df[Symbol].loc[Index]=[10000000]*len(Index)       
    Index=df[df[Symbol]==float('-inf')].index.tolist()
    df[Symbol].loc[Index]=[-10000000]*len(Index)  
    return df    
#df1,df2中含全时间序列，计算df1/df2
def Divide(df1,df2,Symbol):

    df=df1.merge(df2,left_index=True,right_index=True,how='outer').fillna(method='ffill')
    Numerator=df.columns[0]
    Denominator=df.columns[1]
    if len(df1)>len(df2):
        df=df.loc[df1.index,:]  
    else:
        df=df.loc[df2.index,:]
    df=Remove_Duplicated_Data(df)
    df=pd.DataFrame(df[Numerator]/df[Denominator],columns=[Symbol])
    #删除Inf
    df=Replace_INF(df,Symbol)
  
    return df

#df1,df2中不含全时间序列，合并全时间序列后计算df1/df2
def Merge_and_Divide(TimeSeries,df1,df2,Symbol):
 
    df=df1.merge(df2,left_index=True,right_index=True,how='outer')
    Numerator=df.columns[0]
    Denominator=df.columns[1]    
    df=df.merge(TimeSeries,left_index=True,right_index=True,how='outer').fillna(method='ffill')
    df=df.loc[TimeSeries.index,:]  
    df=Remove_Duplicated_Data(df) 
    df=pd.DataFrame(df[Numerator]/df[Denominator],columns=[Symbol])
    #删除Inf
    df=Replace_INF(df,Symbol)
    return df

class Calculate_Factor():
    def __init__(self,Code,Stock,BS,IS,CFS):
        self.Stock=Stock
        self.BS=BS
        self.IS=IS
        self.CFS=CFS
        self.main(Code)
        
    def main(self,Code):
        #获取收盘价、后复权收盘价、自由流通A股股本，总股本，行业
        self.Get_Data()
        self.Get_Factor_Type()
#        print 'Size',self.Value.shape,self.Growth.shape,self.Momentum.shape,self.Volatility.shape
        self.DataFrame=pd.concat([self.Value,self.Momentum,self.Volatility],axis=1)   
        self.DataFrame.insert(0,'Code',[Code]*len(self.DataFrame))
        return self.DataFrame
        
    def Get_Data(self):
        self.Close,self.AdjClose,FreeFloatA,self.TotalShare,Industry=Get_Stock_Info(self.Stock) 
        self.Get_BS_Data()
        self.Get_IS_Data()
        self.Get_CFS_Data()
        
    def Get_Factor_Type(self):
        self.Get_Per_Share()
        self.Get_Value() 
        self.Get_Momentum()
        self.Get_Volatility()
        
    #-----------------------------------------------------------------------------------------#             
    def Get_BS_Data(self):
        #资产负债表上数据
        
        self.Equity_MRQ=Get_MRQ(self.BS,u'所有者权益（或股东权益）合计','Equity')#所有者权益(或股东权益)合计
        self.OEP_MRQ=Get_MRQ(self.BS,u'归属于母公司所有者权益','OEP')
        
        self.CL_MRQ=Get_MRQ(self.BS,u'流动负债合计','CL')
        self.NCL_MRQ=Get_MRQ(self.BS,u'非流动负债合计','NCL')
        self.Liability_MRQ=Get_MRQ(self.BS,u'负债合计','Liability')
        
        self.CA_MRQ=Get_MRQ(self.BS,u'流动资产合计','CA')
        self.NCA_MRQ=Get_MRQ(self.BS,u'非流动资产合计','NCA')
        self.FA_MRQ=Get_MRQ(self.BS,u'固定资产','FA')
        self.Asset_MRQ=Get_MRQ(self.BS,u'资产总计','Asset')
        
        self.Inventory_MRQ=Get_MRQ(self.BS,u'存货','Inventory')      
        self.AR_MRQ=Get_MRQ(self.BS,u'应收账款','AR')
        self.AP_MRQ=Get_MRQ(self.BS,u'应收账款','AP')
    
    
    #-----------------------------------------------------------------------------------------#             
    def Get_IS_Data(self):
        #利润表上数据
        
        self.ME_TTM=Get_TTM(self.IS,u'销售费用','ME') 
        
        self.NP_LYR=Get_LYR(self.IS,u'五、净利润','NP')
        self.NP_TTM=Get_TTM(self.IS,u'五、净利润','NP')

        self.NPP_LYR=Get_LYR(self.IS,u'归属于母公司所有者的净利润','NPP') 
        self.NPP_TTM=Get_TTM(self.IS,u'归属于母公司所有者的净利润','NPP')    
        self.NPP_SQ=Get_SQ(self.IS,u'归属于母公司所有者的净利润','NPP') 

        self.OpRvn_LYR=Get_LYR(self.IS,u'其中：营业收入（元）','OpRvn')
        self.OpRvn_TTM=Get_TTM(self.IS,u'其中：营业收入（元）','OpRvn')

        self.OpExp_LYR=Get_LYR(self.IS,u'其中：营业成本','OpExp')
        self.OpExp_TTM=Get_TTM(self.IS,u'其中：营业成本','OpExp')
        
        
        self.OpRvn_SQ=Get_SQ(self.IS,u'其中：营业收入（元）','OpRvn')
        self.OpExp_SQ=Get_SQ(self.IS,u'其中：营业成本','OpExp')
        self.GRvn_SQ=Get_SQ(self.IS,u'一、营业总收入','GRvn')        
        self.OP_SQ=pd.DataFrame(self.OpRvn_SQ['OpRvn_SQ']-self.OpExp_SQ['OpExp_SQ']) #营业利润=营业收入-营业成本
        
        
    
    #-----------------------------------------------------------------------------------------#             
    def Get_CFS_Data(self):    
        #现金流量表              
        
        #经营活动产生的现金流量净额
        self.CFO_LYR=Get_LYR(self.CFS, u'经营活动产生的现金流量净额','CFO')
        self.CFO_TTM=Get_TTM(self.CFS, u'经营活动产生的现金流量净额','CFO')
        self.CFO_SQ=Get_SQ(self.CFS, u'经营活动产生的现金流量净额','CFO')
        #现金及现金等价物净增加额       
        self.CF_LYR=Get_LYR(self.CFS, u'五、现金及现金等价物净增加额','CF')
        self.CF_TTM=Get_TTM(self.CFS, u'五、现金及现金等价物净增加额','CF') 
        self.CF_SQ=Get_SQ(self.CFS, u'五、现金及现金等价物净增加额','CF')      
    #-----------------------------------------------------------------------------------------#             
    def Get_Per_Share(self):   
        #每股
        #EPS每股盈余
        self.EPS_LYR=Divide(self.NPP_LYR,self.TotalShare,'EPS_LYR')     
        self.EPS_TTM=Divide(self.NPP_TTM,self.TotalShare,'EPS_TTM')
     
        #BPS每股净资产
        self.BPS_MRQ=Divide(self.Equity_MRQ,self.TotalShare,'BPS_MRQ')
        
        #ORPS每股营业收入
        self.ORPS_LYR=Divide(self.OpRvn_LYR,self.TotalShare,'ORPS_LYR')
        self.ORPS_TTM=Divide(self.OpRvn_TTM,self.TotalShare,'ORPS_TTM')
        
        #CFOPS每股经营现金流
        self.CFOPS_LYR=Divide(self.CFO_LYR,self.TotalShare,'CFOPS_LYR')
        self.CFOPS_TTM=Divide(self.CFO_TTM,self.TotalShare,'CFOPS_TTM')     
        
        #CFPS每股现金流
        self.CFPS_LYR=Divide(self.CF_LYR,self.TotalShare,'CFPS_LYR')
        self.CFPS_TTM=Divide(self.CF_TTM,self.TotalShare,'CFPS_TTM')  

    
    
    #------------------------------------------------------------------------------------------#
    def Get_Value(self):
        #估值
#        FreeFloatTMV=pd.DataFrame(Close['Close']*TotalShare['TotalShare'],columns=['FreeFloatTMV'])
        #市盈率的相反数
        PE_LYR_OPP=-Divide(self.Close,self.EPS_LYR,'PE_LYR_OPP')
        PE_TTM_OPP=-Divide(self.Close,self.EPS_TTM,'PE_TTM_OPP')
        
        #市净率的相反数
        PB_MRQ_OPP=-Divide(self.Close,self.BPS_MRQ,'PB_MRQ_OPP')
        
        #市销率的相反数
        PS_LYR_OPP=-Divide(self.Close,self.ORPS_LYR,'PS_LYR_OPP')
        PS_TTM_OPP=-Divide(self.Close,self.ORPS_TTM,'PS_TTM_OPP')
        
        #市现率的相反数
        CFO_CFP_LYR_OPP=-Divide(self.Close,self.CFOPS_LYR,'CFO_CFP_LYR_OPP')
        CFO_CFP_TTM_OPP=-Divide(self.Close,self.CFOPS_TTM,'CFO_CFP_TTM_OPP')      

        #市现率的相反数
        NCF_CFP_LYR_OPP=-Divide(self.Close,self.CFPS_LYR,'NCF_CFP_LYR_OPP')
        NCF_CFP_TTM_OPP=-Divide(self.Close,self.CFPS_TTM,'NCF_CFP_TTM_OPP')        
     
        self.Value=pd.concat([PE_LYR_OPP,PE_TTM_OPP,PB_MRQ_OPP,PS_LYR_OPP,PS_TTM_OPP,CFO_CFP_LYR_OPP,CFO_CFP_TTM_OPP,NCF_CFP_LYR_OPP,NCF_CFP_TTM_OPP],axis=1)
        

        
    
    def Get_Momentum(self):
        
        def Calculate_Momentum(Day):
            Momentum=-(self.AdjClose/self.AdjClose.shift(Day)-1)
            Momentum.columns=['Momentum'+str(Day)+'_OPP']
            return Momentum
        Momentum5_OPP=Calculate_Momentum(5)
        Momentum10_OPP=Calculate_Momentum(10)
        Momentum20_OPP=Calculate_Momentum(20)
        Momentum30_OPP=Calculate_Momentum(30)
        Momentum60_OPP=Calculate_Momentum(60)
        Momentum90_OPP=Calculate_Momentum(90)
        Momentum120_OPP=Calculate_Momentum(120)
        self.Momentum=pd.concat([Momentum5_OPP,Momentum10_OPP,Momentum20_OPP,Momentum30_OPP,Momentum60_OPP,Momentum90_OPP,Momentum120_OPP],axis=1)
        
    def Get_Volatility(self):
        
        Momentum1=self.AdjClose/self.AdjClose.shift(1)-1
        def Calculate_Volatility(Day):
            Vol=-Momentum1.rolling(window=Day,center=False).std()
            Vol.columns=['Vol'+str(Day)+'_OPP']
            return Vol
        Vol5_OPP=Calculate_Volatility(5)
        Vol10_OPP=Calculate_Volatility(10)
        Vol20_OPP=Calculate_Volatility(20)
        Vol30_OPP=Calculate_Volatility(30)
        Vol60_OPP=Calculate_Volatility(60)
        Vol90_OPP=Calculate_Volatility(90)
        Vol120_OPP=Calculate_Volatility(120)
        self.Volatility=pd.concat([Vol5_OPP,Vol10_OPP,Vol20_OPP,Vol30_OPP,Vol60_OPP,Vol90_OPP,Vol120_OPP],axis=1)
        

        
        
    #------------------------------------------------------------------------------------------#    
