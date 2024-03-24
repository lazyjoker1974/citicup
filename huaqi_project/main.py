import os

import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd
import suanfa
import torch
import torch.nn as nn
import torch.utils.data as Data
from graph import gupiaoGraph

'''file = r'D:\\huaqi_data\\subsidiary'
for root, dirs, files in os.walk(file):
    print(files)
proportion=80
for i,file in enumerate(files):
    file="D:\\huaqi_data\\subsidiary\\"+file
    company_name,entity=suanfa.get_entity(file,proportion)
    print(i+1,company_name,"持股比例超过",proportion,"%的实体有",entity,'\n','\n')'''
"""graph="D:\\huaqi_data\\subsidiary\\000005subsidiary.xlsx"
company_name,list_1,list_2=suanfa.get_class(graph)
proportion=80
company_name,list_3=suanfa.get_entity(graph,proportion)
for i,j in list_2:
    print(company_name,"的",i,"为\n",j)
for i,j in list_1:
    print(company_name,"的",i,"为\n",j)
print(company_name,"持股比例超过",proportion,"%","实体为",list_3)"""


"""gupiaograp=gupiaoGraph("http://localhost:7474/","neo4j","lhy135831")
gupiaograp.create_graph("D:\\huaqi_data\\1-000069\\000004subsidiary.xlsx",path_up="D:\\huaqi_data\\1-000069\\000004shareholder.xlsx")
gupiaograp.get_entity(60)
print("\n")
gupiaograp.get_class_entity("控股子公司")
print("\n")
gupiaograp.get_gudong_person()
print("\n")
gupiaograp.get_gudong_company()"""
 
 
model=torch.load("mlp_params.pth")
data=pd.read_excel("深度学习训练数据集合.xlsx")
x=data[["股权制衡指数","换手率%","关联方得分...11"]].values.astype(np.float32)
y=data[["股权架构等级"]].values
x=torch.tensor(x)
y_hat=model(x)
for y in y_hat:
    print(y)