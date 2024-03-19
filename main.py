import streamlit as st

# 页面标题
st.title('简单的Streamlit示例')

# 用户输入框
user_input = st.text_input('请输入您的名字：')

# 显示用户输入的文本
st.write('您输入的名字是：', user_input)

# 显示用户输入的文本（使用Markdown格式）
st.markdown(f'您输入的名字是：**{user_input}**')
