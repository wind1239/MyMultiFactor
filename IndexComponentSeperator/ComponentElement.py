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
    def __init__(self,Index):  
    	self.Index=Index
    	self.Define_Path()
        self.main()

    def Define_Path(self):
        HigherDir=os.path.dirname(os.getcwd())
        self.IndexComponentPath=HigherDir+'\\Data\\IndexComponent\\'
        self.FactorPath=HigherDir+'\\Data\\FactorLibrary\\'
        self.StockPath=HigherDir+'\\Data\\StockElement\\'
        self.OutputPath=HigherDir+'\\Data\\Factor4IndexComponent\\'+self.Index+'\\'

    def Get_Index_Component(self,IndexComponentPath,TargetIndex):
        IndexComponent=pd.read_csv(IndexComponentPath+TargetIndex)
        Date=IndexComponent['date'].values.tolist()
        Code=IndexComponent['code'].values.tolist()
        ComponentList=[(Date[a],Code[a]) for a in range(len(Date))]
        return ComponentList
    
    def Get_Index_Component_Data(self,InputPath,OutputPath,ComponentList):
        Create_Path(OutputPath)
        FileList=list(set(os.listdir(InputPath))-set(os.listdir(OutputPath)))
        for FileName in FileList:
            print self.Index,FileName
            if FileName!='Industry.csv':
                df=pd.read_csv(InputPath+FileName,index_col=0,encoding='gbk')
                df=df.stack()
                df=df[ComponentList]
                df=df.unstack()
                df.to_csv(OutputPath+FileName,encoding='gbk')
            else:
                df=pd.read_csv(InputPath+FileName,index_col=0,encoding='gbk')
                df.to_csv(OutputPath+FileName,encoding='gbk')
                           
        
    def main(self):

        ComponentList=self.Get_Index_Component(self.IndexComponentPath,self.Index+'.csv')

        self.Get_Index_Component_Data(self.FactorPath,self.OutputPath,ComponentList)
        self.Get_Index_Component_Data(self.StockPath,self.OutputPath,ComponentList)
                
