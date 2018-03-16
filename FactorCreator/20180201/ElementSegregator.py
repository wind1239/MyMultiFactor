# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 17:23:42 2018

@author: xtuser08
"""

import os
import pandas as pd
import time


#判断路径是否存在，不存在则建立
def Create_Path(Path):
    if not os.path.exists(Path):
        os.makedirs(Path) 

def Segregate_Then_Merge(InputPath,OutputPath):
    Create_Path(OutputPath)
    #获取全部文件数据
    FileList=os.listdir(InputPath)
    Dict={}
    for FileName in FileList:
        Code=FileName[:10]
        print Code
        Data=pd.read_csv(InputPath+FileName,index_col=0,encoding='gbk')
        Dict[Code]=Data
    
    #对文件数据按因子拆分后按股票合并    
    KeyList=sorted(Dict.keys())
    FactorList=Dict.get(KeyList[0]).columns.tolist()[1:]
    if 'Industry' in FactorList:
        FactorList.pop(FactorList.index('Industry'))
        
    for Factor in FactorList:
        FactorDict={}    
        for Key in KeyList:
            print Factor,Key
            FactorDict[Key]=Dict.get(Key)[Factor]   
        df=pd.concat(FactorDict).unstack().T 
        df.to_csv(OutputPath+Factor+'.csv',encoding='gbk')



start=time.clock()
#路径
Dir=os.getcwd()
HigherDir=os.path.dirname(Dir)
DataPath=os.path.dirname(HigherDir)+'\\Data\\'  #数据文件夹
FactorPath=DataPath+'RawFactorData'+Dir[Dir.rfind('\\'):]+'\\' #因子储存路径
ElementPath=DataPath+'FactorLibrary\\'


Segregate_Then_Merge(FactorPath,ElementPath)

end=time.clock()
print end-start
    


