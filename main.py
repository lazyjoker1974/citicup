import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.title('复杂的Streamlit示例')

st.sidebar.header('用户输入')
user_input = st.sidebar.text_input('请输入您的名字：')

# 数据输入
st.subheader('数据输入')
data_size = st.slider('选择数据集大小：', min_value=100, max_value=1000, step=100)
condition = st.selectbox('选择条件：', ['条件1', '条件2', '条件3'])

# 模拟数据
np.random.seed(42)
data = pd.DataFrame({
    'A': np.random.randn(data_size),
    'B': np.random.randint(0, 10, size=data_size),
    'C': np.random.choice(['X', 'Y', 'Z'], size=data_size)
})

# 显示数据
st.write('模拟数据集：')
st.write(data)

# 数据可视化
st.subheader('数据可视化')
if st.checkbox('显示数据摘要'):
    st.write(data.describe())

if st.checkbox('显示数据散点图'):
    sns.pairplot(data)
    st.pyplot()

# 用户反馈
st.subheader('用户反馈')
feedback = st.text_area('您对我们的应用有什么建议或反馈？')

# 显示用户输入和反馈信息
st.write('您输入的名字是：', user_input)
st.write('您的反馈是：', feedback)
