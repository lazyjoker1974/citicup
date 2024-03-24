import torch.nn as nn
import torch
import matplotlib.pyplot as plt
import openpyxl
import pandas as pd
import numpy as np
import torch.utils.data as Data 
from torch.autograd import Variable
import torch.nn.functional as F
class MLP(nn.Module):
    def __init__(self,input_dim,output_dim):
        super(MLP,self).__init__()
        self.hidden=nn.Sequential(
            nn.Linear(input_dim,10),
            nn.ReLU(),
            nn.Linear(10,20),
            nn.ReLU(),
            nn.Linear(20,10),
            nn.ReLU(),
            nn.Linear(10,output_dim),
        )
    def forward(self,x):
        return self.hidden(x)
class FocalLoss(nn.Module):
    '''Multi-class Focal loss implementation'''
    def __init__(self, gamma=5, weight=None):
        super(FocalLoss, self).__init__()
        self.gamma = gamma
        self.weight = weight

    def forward(self, input, target):
        """
        input: [N, C]
        target: [N, ]
        """
        logpt = F.log_softmax(input, dim=1)
        pt = torch.exp(logpt)
        logpt = (1-pt)**self.gamma * logpt
        loss = F.nll_loss(logpt, target, self.weight)
        return loss
learning_rate=0.01
#mlp=MLP(3,4)
mlp=torch.load("mlp_params.pth")
optim=torch.optim.SGD(mlp.parameters(),lr=learning_rate)
loss_func=FocalLoss()
train_losses=[]
data=pd.read_excel("D:\\huaqi_data\\guquan.xlsx")
x=data[["赋分0.6...4","赋分0.25...10","赋分0.15...13"]].values.astype(np.float32)
y=data[["股权架构等级"]].values
label_array=[]
for i in range(len(y)):
    if y[i]=="A":
        label_array.append(np.array([1,0,0,0]))
    if y[i]=="B":
        label_array.append(np.array([0,1,0,0]))
    if y[i]=="C":
        label_array.append(np.array([0,0,1,0]))
    if y[i]=="D":
        label_array.append(np.array([0,0,0,1]))
label_array=np.array(label_array).astype(float)
x=torch.tensor(x)
y=torch.LongTensor(label_array)
dataset=Data.TensorDataset(x,y)
train_data=Data.DataLoader(dataset,batch_size=64,shuffle=True)
accuarys=[]
for i in range(50):
    train_loss=0
    accuary=0
    for x_train,y_train in train_data:
        optim.zero_grad()
        y_hat=mlp(x_train)
        accuary=(torch.sum(torch.argmax(y_hat,dim=1)==torch.argmax(y_train,dim=1)).item())+accuary
        loss=loss_func(y_hat,torch.argmax(y_train,dim=1))
        loss.backward()
        optim.step()
        train_loss=(train_loss+loss.item())
    accuarys.append(accuary/(len(y)))
    train_losses.append(train_loss)
torch.save(mlp,"mlp_params.pth")
plt.plot(accuarys)
plt.show()
plt.plot(train_losses)
plt.show()
         

"""def load_model(path):
    return torch.load(path)
model=torch.load("D:\coding\huaqi_project\mlp_params.pth")
data=pd.read_excel("D:\\huaqi_data\\guquan.xlsx")
x=data[["股权制衡指数","换手率%","关联方得分...11"]].values.astype(np.float32)
y=data[["股权架构等级"]].values
x=torch.tensor(x)
y_hat=model(x)
for y in y_hat:
    print(y)"""