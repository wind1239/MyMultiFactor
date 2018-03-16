# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 10:33:08 2018

@author: xtuser08
"""
"""
变量名

"""
import os
import pandas as pd
from FactorFunctionLibrary import *
#from FunctionLibrary import *



class Get_Factor():
    def __init__(self,Start,End):
#        Start=time.clock()
        self.Get_Data_Path()
        self.main(Start,End)
#        End=time.clock()
#        print End-Start
        
    def Get_Data_Path(self):
        #获取数据路径
        Dir=os.getcwd()
        HigherDir=os.path.dirname(Dir)
        DataPath=os.path.dirname(HigherDir)+'\\Data\\'  #数据文件夹
        self.StockPath=DataPath+'StockData\\'  #股票基本数据路径
        self.BSPath=DataPath+'FinancialData\\BalanceSheet\\' #资产负债表路径
        self.ISPath=DataPath+'FinancialData\\IncomeStatement\\' #利润表路径
        self.CFSPath=DataPath+'FinancialData\\CashFlowStatement\\' #现金流路径
        
        self.FactorPath=DataPath+'RawFactorData'+Dir[Dir.rfind('\\'):]+'\\' #因子储存路径
        self.Create_Path(self.FactorPath) #判断因子储存路径是否存在
        
        StockInfoFileList=[a for a in os.listdir(self.StockPath) if a[:5]!='SSE_0'] #文件夹中所有股票的文件名
        self.CodeList=[a[:10] for a in StockInfoFileList if os.path.exists(self.BSPath+a)] #有财务数据的代码列表        
        
    #获取Code的报告（支持资产负债表、利润表以及现金流量表）
    def Get_Statement(self,Path,Code):
        df=pd.read_csv(Path+Code+'.csv',encoding='gbk')
        
        #第1种类型，报告缺失
        ReportDate=df[u'报告年度'].values.tolist() #获取财务报表中的报告日期
        #实际上报告日期
        RealReportDate=[str(a)+b for a in range(int(ReportDate[0][:4]),int(ReportDate[-1][:4])+1) for b in ['-03-31','-06-30','-09-30','-12-31']]
        #判断是否有报告缺失，若缺失则用后面最近的一期数据补全
        for Date in RealReportDate:
            if Date not in ReportDate and Date<ReportDate[-1]: 
                Correction=[a for a in range(len(ReportDate)) if ReportDate[a]>Date][0]
                df.loc[len(df)]=df.loc[Correction] 
                df[u'报告年度'].iloc[len(df)-1]=Date
        df=df.sort_values([u'报告年度'])
            
    
        #第2种类型，当前公告日期大于下期公告日期，即当前公告报告不可用
        PublicDate=df[u'公告日期'].values.tolist() #获取财务报表中的公告日期
        AbnormalDateIndex=[a for a in range(len(PublicDate)-1) if PublicDate[a]>=PublicDate[a+1]] #查找未按顺序排列的日期
        df.loc[AbnormalDateIndex,[u'公告日期']]=[PublicDate[a+1] for a in AbnormalDateIndex] #用后面最近的日期替换
    
        return df   
    
    #判断路径是否存在，不存在则建立
    def Create_Path(self,Path):
        if not os.path.exists(Path):
            os.makedirs(Path) 
   
    #获取股票的基本数据以及财务报表    
    def Get_Stock_BS_IS_CFS(self,Code):

        #获取代码的价量数据
        Stock=pd.read_csv(self.StockPath+Code+'.csv',encoding='gbk')
            
        #获取资产负债表、利润表以及现金流量表
        BS=self.Get_Statement(self.BSPath,Code)
        IS=self.Get_Statement(self.ISPath,Code)
        CFS=self.Get_Statement(self.CFSPath,Code)
        return Stock,BS,IS,CFS
    
    def Get_DataFrame(self,Code):
        print Code

        Stock,BS,IS,CFS=self.Get_Stock_BS_IS_CFS(Code)
        
        if len(BS)>=4:
            self.DataFrame=Calculate_Factor(Code,Stock,BS,IS,CFS).DataFrame 
                        
            self.DataFrame.to_csv(self.FactorPath+Code+'.csv') 
            
    def main(self,Start,End):
        #按股票计算各个因子
        for Code in self.CodeList[Start:min(End,len(self.CodeList)+1)]: 
            self.Get_DataFrame(Code)

    