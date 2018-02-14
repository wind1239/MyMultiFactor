# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 16:59:38 2018

@author: xtuser08
"""

import os 
import pandas as pd

#判断是否存在路径
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 

#对合并报表进行合并        
def Get_Append_Sheet(Type,Code,FileNameList,TagList,InputPath,OutputPath):
    Tag=Type+'_'+Code
    StockFiles=[FileNameList[a] for a in range(len(TagList)) if TagList[a]==Tag and FileNameList[a][14:18]>'2004']
    df=pd.read_csv(InputPath+StockFiles[0],encoding='gbk')
    for File in StockFiles[1:]:
        df=df.append(pd.read_csv(InputPath+File,encoding='gbk'))
    df.to_csv(OutputPath+'\\'+('SSE_' if Code[0]=='6' else 'SZE_')+Code+'.csv',index=False,encoding='gbk')
    return df

#循环将报表以资产负债表、利润表、现金流量表三类分开，以股票代码储存
def main(InputPath,OutputPath):
    SheetType=['BalanceSheet','IncomeStatement','CashFlowStatement']
    for Type in SheetType:
        Create_Path(OutputPath+Type)    
    FileNameList=os.listdir(InputPath)
    TagList=[a[3:13] for a in FileNameList]
    CodeList=sorted(list(set([a[7:13] for a in FileNameList])))
    Error=[]
    for Code in CodeList:
        BS=Get_Append_Sheet('fzb',Code,FileNameList,TagList,InputPath,OutputPath+SheetType[0])
        IS=Get_Append_Sheet('lrb',Code,FileNameList,TagList,InputPath,OutputPath+SheetType[1])
        CFS=Get_Append_Sheet('llb',Code,FileNameList,TagList,InputPath,OutputPath+SheetType[2])
        print Code,len(BS),len(IS),len(CFS)
        if len(BS)!=len(IS) or len(BS)!=len(CFS):
            Error.append(Code)
            print 'The lengths of Statements of ',Code, 'are not equal'

HigherDir=os.path.dirname(os.getcwd())
InputPath=os.path.dirname(HigherDir)+'\\Data\\FinancialData\\' 
OutputPath=HigherDir+'\\Data\\FinancialData\\'
main(InputPath,OutputPath)
