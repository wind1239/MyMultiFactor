# -*- coding: utf-8 -*-
"""
Created on Tue Feb 06 13:53:42 2018

@author: xtuser08
"""

import os
import pandas as pd

#判断路径是否存在，不存在则建立
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 
class Component_Element():
    def __init__(self,Start,End):  
        self.main(Start,End)
    def Get_Index_Component(self,IndexComponentPath,TargetIndex):
        IndexComponent=pd.read_csv(IndexComponentPath+TargetIndex)
        Date=IndexComponent['Date'].values.tolist()
        Code=IndexComponent['Code'].values.tolist()
        ComponentList=[(Date[a],Code[a]) for a in range(len(Date))]
        return ComponentList
    
    def Get_Index_Component_Data(self,InputPath,OutputPath,ComponentList):
        Create_Path(OutputPath)
        FileList=list(set(os.listdir(InputPath))-set(os.listdir(OutputPath)))
        for FileName in FileList:
            print self.TargetIndexName,FileName
            if FileName!='Industry.csv':
                df=pd.read_csv(InputPath+FileName,index_col=0,encoding='gbk')
                df=df.stack()
                df=df[ComponentList]
#                a=df.duplicated()
                df=df.unstack()
                df.to_csv(OutputPath+FileName,encoding='gbk')
            else:
                df=pd.read_csv(InputPath+FileName,index_col=0,encoding='gbk')
                df.to_csv(OutputPath+FileName,encoding='gbk')
                           
        
    def main(self,Start,End):
        HigherDir=os.path.dirname(os.getcwd())
        IndexComponentPath=HigherDir+'\\Data\\IndexComponent\\'
        FileList=os.listdir(IndexComponentPath)
        Index=[a[:-4] for a in FileList]
        for Num in range(Start,End):
            if Num<len(Index) and Num>=0:
                TargetIndex=FileList[Num]
                self.TargetIndexName=Index[Num]
                ComponentList=self.Get_Index_Component(IndexComponentPath,TargetIndex)
                FactorPath=HigherDir+'\\Data\\FactorLibrary\\'
                StockPath=HigherDir+'\\Data\\StockElement\\'
                OutputPath=HigherDir+'\\Data\\Factor4IndexComponent\\'+self.TargetIndexName+'\\'
                self.Get_Index_Component_Data(FactorPath,OutputPath,ComponentList)
                self.Get_Index_Component_Data(StockPath,OutputPath,ComponentList)
                
