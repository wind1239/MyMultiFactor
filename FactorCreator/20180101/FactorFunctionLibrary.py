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
        self.DataFrame=pd.concat([self.PerShare,self.Value,self.Profit,self.Quality,self.Cash,self.Capital,self.Debt,self.Operation,self.Growth],axis=1)   
        self.DataFrame.insert(0,'Code',[Code]*len(self.DataFrame))
        return self.DataFrame
        
    def Get_Data(self):
        self.Close,AdjClose,FreeFloatA,self.TotalShare,Industry=Get_Stock_Info(self.Stock) 
        self.Get_BS_Data()
        self.Get_IS_Data()
        self.Get_CFS_Data()
        
    def Get_Factor_Type(self):
        self.Get_Per_Share()
        self.Get_Value()
        self.Get_Profit()
        self.Get_Quality()
        self.Get_Cash()
        self.Get_Capital()
        self.Get_Debt()
        self.Get_Operation()
        self.Get_Growth()        
        
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
    
          
        
        self.PerShare=pd.concat([self.EPS_LYR,self.EPS_TTM,self.BPS_MRQ,self.ORPS_LYR,self.ORPS_TTM,self.CFOPS_LYR,self.CFOPS_TTM,self.CFPS_LYR,self.CFPS_TTM],axis=1)
    
    
    #------------------------------------------------------------------------------------------#
    def Get_Value(self):
        #估值
#        FreeFloatTMV=pd.DataFrame(Close['Close']*TotalShare['TotalShare'],columns=['FreeFloatTMV'])
        #市盈率的倒数
        EP_LYR=Divide(self.EPS_LYR,self.Close,'EP_LYR')
        EP_TTM=Divide(self.EPS_TTM,self.Close,'EP_TTM')
        
        #市净率的倒数
        BP_MRQ=Divide(self.BPS_MRQ,self.Close,'BP_MRQ')
        
        #市销率的倒数
        SP_LYR=Divide(self.ORPS_LYR,self.Close,'SP_LYR')
        SP_TTM=Divide(self.ORPS_TTM,self.Close,'SP_TTM')
        
        #市现率的倒数
        CFP_CFO_LYR=Divide(self.CFOPS_LYR,self.Close,'CFP_CFO_LYR')
        CFP_CFO_TTM=Divide(self.CFOPS_TTM,self.Close,'CFP_CFO_TTM')      
        CFP_NCF_LYR=Divide(self.CFPS_LYR,self.Close,'CFP_NCF_LYR')
        CFP_NCF_TTM=Divide(self.CFPS_TTM,self.Close,'CFP_NCF_TTM')
        
     
        self.Value=pd.concat([EP_LYR,EP_TTM,BP_MRQ,SP_LYR,SP_TTM,CFP_CFO_LYR,CFP_CFO_TTM,CFP_NCF_LYR,CFP_NCF_TTM],axis=1)
    #
    #------------------------------------------------------------------------------------------#
    def Get_Profit(self):
        #盈利
        #ROE净资产收益率
        ROE_LYR=Merge_and_Divide(self.TotalShare,self.NPP_LYR,self.OEP_MRQ,'ROE_LYR')
        ROE_TTM=Merge_and_Divide(self.TotalShare,self.NPP_TTM,self.OEP_MRQ,'ROE_TTM')
        
        #ROA资产收益率
        ROA_LYR=Merge_and_Divide(self.TotalShare,self.NPP_LYR,self.Asset_MRQ,'ROA_LYR')
        ROA_TTM=Merge_and_Divide(self.TotalShare,self.NPP_TTM,self.Asset_MRQ,'ROA_TTM')
        
        #销售净利率
        NPM_LYR=Merge_and_Divide(self.TotalShare,self.NP_LYR,self.OpRvn_LYR,'NPM_LYR')
        NPM_TTM=Merge_and_Divide(self.TotalShare,self.NP_TTM,self.OpRvn_TTM,'NPM_TTM')
        
        #销售毛利率
        GPM_LYR=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.OpRvn_LYR['OpRvn_LYR']-self.OpExp_LYR['OpExp_LYR']),self.OpRvn_LYR,'GPM_LYR')
        GPM_TTM=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.OpRvn_TTM['OpRvn_TTM']-self.OpExp_TTM['OpExp_TTM']),self.OpRvn_TTM,'GPM_TTM')
        
        #销售成本率
        S2C_LYR=Merge_and_Divide(self.TotalShare,self.OpRvn_LYR,self.OpExp_LYR,'S2C_LYR')
        S2C_TTM=Merge_and_Divide(self.TotalShare,self.OpRvn_TTM,self.OpExp_TTM,'S2C_TTM')
               
        self.Profit=pd.concat([ROE_LYR,ROE_TTM,ROA_LYR,ROA_TTM,NPM_LYR,NPM_TTM,GPM_LYR,GPM_TTM,S2C_LYR,S2C_TTM],axis=1)      
        
    #------------------------------------------------------------------------------------------#
    def Get_Quality(self):
        #质量
        #毛利润占净利润的比值
        OI2NP_LYR=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.OpRvn_LYR['OpRvn_LYR']-self.OpExp_LYR['OpExp_LYR']),self.NP_LYR,'OI2NP_LYR')
        OI2NP_TTM=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.OpRvn_TTM['OpRvn_TTM']-self.OpExp_TTM['OpExp_TTM']),self.NP_TTM,'OI2NP_TTM')
        
        #BerryRatio
        BerryRatio=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.OpRvn_TTM['OpRvn_TTM']-self.OpExp_TTM['OpExp_TTM']),self.ME_TTM,'BerryRatio')
        
        #资产周转率
        AssetTurnover=Merge_and_Divide(self.TotalShare,self.OpRvn_TTM,self.Asset_MRQ,'AssetTurnover')
        
        
        self.Quality=pd.concat([OI2NP_LYR,OI2NP_TTM,BerryRatio,AssetTurnover],axis=1)
    #------------------------------------------------------------------------------------------#   
    def Get_Cash(self):
        #现金
        #经营活动产生的现金流净额占营业收入的比
        CFO2OR_LYR=Merge_and_Divide(self.TotalShare,self.CFO_LYR,self.OpRvn_LYR,'CFO2OR_LYR')
        CFO2OR_TTM=Merge_and_Divide(self.TotalShare,self.CFO_TTM,self.OpRvn_TTM,'CFO2OR_TTM')
        
        #经营活动产生的现金流量净额占营业利润的比
        CFO2OI_LYR=Merge_and_Divide(self.TotalShare,self.CFO_LYR,pd.DataFrame(self.OpRvn_LYR['OpRvn_LYR']-self.OpExp_LYR['OpExp_LYR']),'CFO2OI_LYR')
        CFO2OI_TTM=Merge_and_Divide(self.TotalShare,self.CFO_TTM,pd.DataFrame(self.OpRvn_TTM['OpRvn_TTM']-self.OpExp_TTM['OpExp_TTM']),'CFO2OI_TTM')    
        
        #经营活动产生的现金流量净额占净利润的比
        CFO2NP_LYR=Merge_and_Divide(self.TotalShare,self.CFO_LYR,self.NP_LYR,'CFO2NP_LYR')
        CFO2NP_TTM=Merge_and_Divide(self.TotalShare,self.CFO_TTM,self.NP_TTM,'CFO2NP_TTM')   
        
        self.Cash=pd.concat([CFO2OR_LYR,CFO2OR_TTM,CFO2OI_LYR,CFO2OI_TTM,CFO2NP_LYR,CFO2NP_TTM],axis=1)
        
    #------------------------------------------------------------------------------------------#        
    def Get_Capital(self):
        #资本
        #资产负债率
        Liability2Asset=Merge_and_Divide(self.TotalShare,self.Liability_MRQ,self.Asset_MRQ,'Liability2Asset')
        #权益乘数
        Asset2Equity=1/(1-Liability2Asset)
        Asset2Equity.columns=['Asset2Equity']
        
        #流动资产占总资产的比
        CA2Asset=Merge_and_Divide(self.TotalShare,self.CA_MRQ,self.Asset_MRQ,'CA2Asset')
        #非流动资产占总资产的比
        NCA2Asset=Merge_and_Divide(self.TotalShare,self.NCA_MRQ,self.Asset_MRQ,'NCA2Asset')
        #流动负债占负债的比
        CL2Liability=Merge_and_Divide(self.TotalShare,self.CL_MRQ,self.Liability_MRQ,'CL2Liability')
        #非流动负债占负债的比
        NCL2Liability=Merge_and_Divide(self.TotalShare,self.NCL_MRQ,self.Liability_MRQ,'NCL2Liability')       
        
        self.Capital=pd.concat([Liability2Asset,Asset2Equity,CA2Asset,NCA2Asset,CL2Liability,NCL2Liability],axis=1)
    #------------------------------------------------------------------------------------------#        
    def Get_Debt(self):
        #偿债
        #流动比率
        CurrentRatio=Merge_and_Divide(self.TotalShare,self.CA_MRQ,self.CL_MRQ,'CurrentRatio')
        #速动比率
        QuickRatio=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.CA_MRQ['CA_MRQ']-self.Inventory_MRQ['Inventory_MRQ']),self.CL_MRQ,'QuickRatio')
        #产权比率的倒数
        OEP2Liability=Merge_and_Divide(self.TotalShare,self.OEP_MRQ,self.Liability_MRQ,'OEP2Liability')
        #归属于母公司的股东权益占非流动负债的比
        OEP2NCL=Merge_and_Divide(self.TotalShare,self.OEP_MRQ,self.NCL_MRQ,'OEP2NCL')
        #经营活动产生的现金流量净额与负债的比
        CFO2Liability_TTM=Merge_and_Divide(self.TotalShare,self.CFO_TTM,self.Liability_MRQ,'CFO2Liability_TTM')
        #经营活动产生的现金流量净额与负债的比
        CFO2CL_TTM=Merge_and_Divide(self.TotalShare,self.CFO_TTM,self.CL_MRQ,'CFO2CL_TTM')
        
        self.Debt=pd.concat([CurrentRatio,QuickRatio,OEP2Liability,OEP2NCL,CFO2Liability_TTM,CFO2CL_TTM],axis=1)
        
    #------------------------------------------------------------------------------------------#   
    def Get_Operation(self):
        #营运
        #存货周转率
        InvTurnRatio=Merge_and_Divide(self.TotalShare,self.OpExp_SQ,(self.Inventory_MRQ+self.Inventory_MRQ.shift(1))/2,'InvTurnRatio')
        #应收账款周转率
        ARTurnRatio=Merge_and_Divide(self.TotalShare,self.OpRvn_SQ,(self.AR_MRQ+self.AR_MRQ.shift(1))/2,'ARTurnRatio')
        #应付账款周转率
        APTurnRatio=Merge_and_Divide(self.TotalShare,self.OpExp_SQ,(self.AP_MRQ+self.AP_MRQ.shift(1))/2,'APTurnRatio')
        #流动资产周转率
        CATurnRatio=Merge_and_Divide(self.TotalShare,self.GRvn_SQ,(self.CA_MRQ+self.CA_MRQ.shift(1))/2,'CATurnRatio')    
        #固定资产周转率
        FATurnRatio=Merge_and_Divide(self.TotalShare,self.GRvn_SQ,(self.FA_MRQ+self.FA_MRQ.shift(1))/2,'FATurnRatio')   
        #总资产周转率
        AssetTurnRatio=Merge_and_Divide(self.TotalShare,self.GRvn_SQ,(self.Asset_MRQ+self.Asset_MRQ.shift(1))/2,'AssetTurnRatio')  
        #营运资本周转率
        WC=pd.DataFrame(((self.CA_MRQ+self.CA_MRQ.shift(1))['CA_MRQ']-(self.CL_MRQ+self.CL_MRQ.shift(1))['CL_MRQ'])/2)
        WCTurnRatio=Merge_and_Divide(self.TotalShare,self.GRvn_SQ,WC,'WCTurnRatio')      
        #非流动资产周转率
        NCATurnRatio=Merge_and_Divide(self.TotalShare,self.GRvn_SQ,(self.NCA_MRQ+self.NCA_MRQ.shift(1))/2,'NCATurnRatio')        
    
        self.Operation=pd.concat([InvTurnRatio,ARTurnRatio,APTurnRatio,CATurnRatio,FATurnRatio,AssetTurnRatio,WCTurnRatio,NCATurnRatio],axis=1)    
    #------------------------------------------------------------------------------------------#        
        
    def Get_Growth(self):
        #成长
        #总营业收入同比增长率
        GR_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.GRvn_SQ-self.GRvn_SQ.shift(3)),abs(self.GRvn_SQ.shift(3)),'GR_YOY')
        #营业收入同比增长率
        OR_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.OpRvn_SQ-self.OpRvn_SQ.shift(3)),abs(self.OpRvn_SQ.shift(3)),'OR_YOY')    
        #营业利润同比增长率
        OP_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.OP_SQ-self.OP_SQ.shift(3)),abs(self.OP_SQ.shift(3)),'OP_YOY')
        #归属于母公司股东的净利润的同比增长率
        NPP_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.NPP_SQ-self.NPP_SQ.shift(3)),abs(self.NPP_SQ.shift(3)),'NPP_YOY')
        #经营活动产生的现金流净额同比增长率
        CFO_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.CFO_SQ-self.CFO_SQ.shift(3)),abs(self.CFO_SQ.shift(3)),'CFO_YOY')
        #现金净流量同比增长率
        CF_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.CF_SQ-self.CF_SQ.shift(3)),abs(self.CF_SQ.shift(3)),'CF_YOY')
    
        #净资产同比增长率
        Equity_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.Equity_MRQ-self.Equity_MRQ.shift(3)),abs(self.Equity_MRQ.shift(3)),'Equity_YOY')
        #总负债同比增长率
        Liability_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.Liability_MRQ-self.Liability_MRQ.shift(3)),abs(self.Liability_MRQ.shift(3)),'Liability_YOY')
        #总资产同比增长率
        Asset_YOY=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.Asset_MRQ-self.Asset_MRQ.shift(3)),abs(self.Asset_MRQ.shift(3)),'Asset_YOY')
        
        #归属于母公司股东的净利润长期（5年）历史增长率
        NPP_LTG=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.NPP_SQ-self.NPP_SQ.shift(19)),abs(self.NPP_SQ.shift(19)),'NPP_LTG')
        #营业收入长期（5年）历史增长率
        OP_LTG=Merge_and_Divide(self.TotalShare,pd.DataFrame(self.OP_SQ-self.OP_SQ.shift(19)),abs(self.OP_SQ.shift(19)),'OP_LTG')        
        
        
        self.Growth=pd.concat([GR_YOY,OR_YOY,OP_YOY,NPP_YOY,CFO_YOY,CF_YOY,Equity_YOY,Liability_YOY,Asset_YOY,NPP_LTG,OP_LTG],axis=1)
        
    #------------------------------------------------------------------------------------------#    
