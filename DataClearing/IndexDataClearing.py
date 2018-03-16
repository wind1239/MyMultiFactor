# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 15:43:35 2018

@author: xtuser08
"""

import os
import pandas as pd

IndexList=['ZZ500','HS300']

#判断是否存在路径
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 
        
HigherDir=os.path.dirname(os.getcwd())
InputPath=os.path.dirname(HigherDir)+'\\Data\\Index\\'
OutputPath=HigherDir+'\\Data\\Index\\'
Create_Path(OutputPath)
for Index in IndexList:
    df=pd.read_excel(InputPath+Index+'.xls',encoding='gbk')
    df.to_csv(OutputPath+Index+'.csv',index=False,encoding='gbk')
