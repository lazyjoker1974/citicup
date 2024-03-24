### Requirements Analysis

#### Objective

Develop a software for querying the equity structure diagram, where users can view the equity structure diagram of a corresponding listed company by entering the stock code and the number of companies with the highest shareholding ratio.

#### 功能需求

- 用户输入股票代码，系统显示该公司的股权穿透图。
- 显示股权穿透图的各层级关系，包括上市公司、子公司、控制人等。
- 对股权穿透图进行分类标注，例如海外实体、国内实体的区分，股东公司和股东控制人的区分。
- 显示每个公司的名称、持股比例（子公司只留下持股比例大于30%的）等信息。
- 提供风险等级说明，根据风险等级对不同公司进行标注。
- 显示子公司的所属行业分类，并用直观的颜色标注。

#### 非功能需求

* 用户界面友好直观 : 界面设计应简洁明了，操作流畅，使用户能够轻松理解和使用软件。
* 查询结果实时显示 : 查询结果应当快速显示，不应有明显的延迟，提供良好的用户体验。
* 系统稳定可靠 : 系统应具备良好的稳定性和可靠性，避免出现崩溃或异常情况。
* 数据安全性 : 用户输入信息应得到有效保护，不会被未经授权的人员访问或篡改。
* 兼容性 : 软件应具备良好的兼容性，能够在不同操作系统和浏览器上正常运行。
* 易维护性 : 代码应具备良好的结构和注释，方便后续维护和修改。

### 设计

#### 技术选型

* 前端技术选择 : 前端界面采用Streamlit框架，该框架基于Python，具有简单易用的特点，可快速搭建交互式Web应用。
* 后端处理 : 后端使用Python进行数据处理和图形展示，Python作为一种高级编程语言，具有丰富的数据处理库和可视化工具，并且借助Streamlit的图形组件展示股权穿透图，能够满足复杂数据处理和图形展示的需求。
* 数据存储方式 : 数据存储使用CSV文件格式，CSV文件具有简单、通用的特点，易于存储和处理结构化数据，同时也便于与其他系统进行数据交换和共享。
* 用户界面设计 : 用户界面设计应简洁明了，符合用户习惯，提供良好的用户体验。可以考虑使用图表、图形等方式直观展示数据，同时提供查询和筛选功能，方便用户快速获取所需信息。

#### 数据流程

- 用户输入股票代码。
- 后端根据股票代码查询相关股权信息。
- 根据股权信息生成股权穿透图数据。
- 将股权穿透图数据传输给前端进行展示。

### 测试

#### 单元测试

针对各个模块编写单元测试，检查功能是否按预期工作。

#### 集成测试

测试系统各部分之间的交互和协作，确保系统整体功能正常。

#### 用户测试

邀请用户使用系统，收集反馈意见，优化用户体验和功能。

### 用户手册

#### 界面介绍

- 输入框：用于输入股票代码与number of companies with the highest shareholding ratio。
- 界面左侧图例：解释股权穿透图中各种标记和颜色的含义，包括不同实体框的区分，风险等级说明，业务分类说明。

#### 操作步骤

1. 输入股票代码与number of companies with the highest shareholding ratio（可选，默认为5）。
2. 回车键确认搜索
3. 查看股权穿透图及相关信息。

#### 注意事项

- 输入正确的股票代码。
- 确保网络连接正常。
- 如有疑问或问题，请联系开发团队。

### 源代码

```python
from collections import defaultdict
from itertools import groupby

import pandas as pd
# import pygraphviz as pgv
import streamlit as st
# from graphviz import Digraph, Source
# from streamlit_agraph import Config, Edge, Node, agraph
from streamlit_react_flow import react_flow

st.markdown("### 股权视界 ShareVision")

def get_top_n_subsidiaries(edges2, n=5): # 取每个公司前 n 个子公司
    subsidiaries_dict = defaultdict(list)
    for edge in edges2:
        company_name = edge[0]
        holding_ratio = edge[2]
        if holding_ratio:
            subsidiaries_dict[company_name].append(edge[1:])
    top_n_subsidiaries = {}
    for company, subsidiaries in subsidiaries_dict.items():
        sorted_subsidiaries = sorted(subsidiaries, key=lambda x: x[1], reverse=True)
        top_n_subsidiaries[company] = sorted_subsidiaries[:n]
    final_edges = [(company, *sub_company) for company, sub_companies in top_n_subsidiaries.items() for sub_company in sub_companies]
    return final_edges

def get_stock_name(data, ticker):
    return data[data['Symbol'] == ticker]['Name'].values[0]

def sub_company(df, not_first_layer): # 给定dataframe，返回edges，以及子公司的(company, ticker)对
    if df.shape[0]:
        if not_first_layer:
            edges = list(zip([not_first_layer] * df.shape[0], df['RalatedParty'], df['DirectHoldingRatio'].astype(float), df['big_ind'], df['is_foreign'], df['Relationship'], df['is_subsidiary_listed']))
        else:
            edges = list(zip(df['Name'], df['RalatedParty'], df['DirectHoldingRatio'].astype(float), df['big_ind'], df['is_foreign'], df['Relationship'], df['is_subsidiary_listed']))
        descendant = df[~df['Sub_Symbol'].isna()]
        return edges, list(zip(descendant['RalatedParty'], descendant['Sub_Symbol']))
    else:
        return [], []

def search(data, input_ticker):
    level = 0
    edges = []
    new_edges, subsidiary = sub_company(data[data['Symbol'] == input_ticker], not_first_layer=False)
    while True:
        edges = edges + [i + (level,) for i in new_edges]
        level += 1
        gen = list((sub_company(data[data['Symbol'] == ticker], not_first_layer=company) for company, ticker in subsidiary))
        new_edges, subsidiary = [edge + (level,) for edges, _ in gen for edge in edges], [temp for _, temps in gen for temp in temps]
        if len(subsidiary) == 0 or level == 3:
            break
    edges = [edge for edge in edges if edge[6] == '1' or (not pd.isnull(edge[2]) and edge[2] > 30)] # excess 30%
    return edges

def Shareholder(df, not_first_layer): # 给定dataframe，返回edges，以及子公司的(company, ticker)对
    if df.shape[0]:
        if not_first_layer:
            edges = list(zip([not_first_layer] * df.shape[0], df['Shareholder_Name'], df['Shareholding_Ratio'].astype(float), df['Shares_Number'], df['is_foreign'], df['Shareholder_Nature'], df['is_subsidiary_listed']))
        else:
            edges = list(zip(df['Name'], df['Shareholder_Name'], df['Shareholding_Ratio'].astype(float), df['Shares_Number'], df['is_foreign'], df['Shareholder_Nature'], df['is_subsidiary_listed']))
        descendant = df[~df['Sub_Symbol'].isna()]
        return edges, list(zip(descendant['Shareholder_Name'], descendant['Sub_Symbol']))
    else:
        return [], []

def search_shareholder(data, input_ticker):
    level = -1
    edges = []
    new_edges, shareholders = Shareholder(data[data['Symbol'] == input_ticker], not_first_layer=False)
    while True:
        edges = edges + [i + (level,) for i in new_edges]
        level -= 1
        gen = list((Shareholder(data[data['Symbol'] == ticker], not_first_layer=company) for company, ticker in shareholders))
        new_edges, shareholders = [edge + (level,) for edges, _ in gen for edge in edges], [temp for _, temps in gen for temp in temps]
        if len(shareholders) == 0 or level == -3:
            break
    edges = [edge for edge in edges if edge[6] == '1' or not pd.isnull(edge[2])]
    return edges

data = pd.read_csv('data/data.csv', dtype=str)
df = pd.read_csv('data/十大股东.csv', dtype=str)
map_risk = pd.read_csv('data/风险等级.csv', dtype=str)
map_dict = dict(zip(map_risk['证券代码.x'], map_risk['股权架构等级']))
user_input = st.text_input("Enter stock code (e.g.: 000009)")

try:
    top_n = int(st.text_input("Enter the number of companies with the highest shareholding ratio (e.g.: 5):"))
except:
    top_n = 5
  
          


with st.sidebar:
    st.markdown("# 股权穿刺图查询软件")
    st.markdown("通过搜索股票代码可以展示对应上市公司的股权穿刺图：")
    st.markdown("<style> .red-dashed-box { border: 2px dashed red; padding: 5px; margin-bottom: 10px; } .black-solid-box { border: 2px solid black; padding: 5px; margin-bottom: 10px; } </style>", unsafe_allow_html=True)
    st.markdown("<div class='red-dashed-box'>红色虚线框：海外实体</div>", unsafe_allow_html=True)
    st.markdown("<div class='black-solid-box'>黑色实线框：国内实体</div>", unsafe_allow_html=True)
    st.markdown("黑色字体：公司名称</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: blue;'>蓝色字体：控制人</div>", unsafe_allow_html=True)
    st.markdown("# 风险等级说明：")
  
  
    st.markdown("共有A, B, C, D四个档次，风险等级从A到D依次升高")
    st.markdown("<font color='#5f9ea0'>这是风险等级 A</font>", unsafe_allow_html=True)
    st.markdown("<font color='#7b68ee'>这是风险等级 B</font>", unsafe_allow_html=True)
    st.markdown("<font color='orange'>这是风险等级 C</font>", unsafe_allow_html=True)
    st.markdown("<font color='red'>这是风险等级 D</font>", unsafe_allow_html=True)


    st.markdown("# 按照业务分类")
    # st.markdown("<div style='background-color: pink; padding: 5px;'>业务1</div>", unsafe_allow_html=True)
    st.markdown("<div style='background-color: #99ffcc; color: #000000; padding: 5px;'>研发类</div>", unsafe_allow_html=True)
    st.markdown("<div style='background-color: #ffcc99; color: #000000; padding: 5px;'>生产类</div>", unsafe_allow_html=True)
    st.markdown("<div style='background-color: #e6ffcc; color: #000000; padding: 5px;'>业务类</div>", unsafe_allow_html=True)
    st.markdown("<div style='background-color: #cce5ff; color: #000000; padding: 5px;'>投资类</div>", unsafe_allow_html=True)
    st.markdown("<div style='background-color: #fce8e6; color: #000000; padding: 5px;'>其他类</div>", unsafe_allow_html=True)
  

if user_input:
    try:
        stock_name = get_stock_name(data, user_input)
        risk = map_dict[user_input]
        st.markdown(f'<h5 style="color: gray;">Equity Structure Diagram of {user_input}（{stock_name}）:</h5>', unsafe_allow_html=True)
        edges = search(data, user_input)
        edges_shareholder = search_shareholder(df, user_input)
        edges1 = [edge for edge in edges if edge[6] == '1']
        edges2 = [edge for edge in edges if edge[6] == '0']
        edges = edges1 + get_top_n_subsidiaries(edges2, n=top_n) # 这里表示每个公司只留下持股比例最高的n(例如n=5)家子公司
        edges_layer_0_1 = [i for i in edges if i[7] == 0]
        edges_layer_1_2 = [i for i in edges if i[7] == 1]
        edges_layer_2_3 = [i for i in edges if i[7] == 2]
        edges_shareholder_0_1 = [i for i in edges_shareholder if i[7] == -1]
        edges_shareholder_1_2 = [i for i in edges_shareholder if i[7] == -2]
        number_of_layer1 = len(edges_layer_0_1)
        number_of_layer2 = len(edges_layer_1_2)
        number_of_layer3 = len(edges_layer_2_3)
        number_of_layer_neg1 = len(edges_shareholder_0_1)
        number_of_layer_neg2 = len(edges_shareholder_1_2)
        target_company_name = edges_layer_0_1[0][0]
        x, y = 200, 150
        elements_down_temp = []
        elements_up_temp = []

        if risk == 'A':
            style = {"color": "#5f9ea0"}
        elif risk == 'B':
            style = {"color": "#7b68ee"}
        elif risk == 'C':
            style = {"color": "orange"}
        else:
            style = {"color": "red"}
      
        elements1 = [{"id": target_company_name, "data": {"label": target_company_name}, "style": style, "position": {"x": x, "y": y}}] # 目标企业
        elements2 = []
        if number_of_layer1: # 向下一次股权穿透
            x_interval = 200
            x_layer1_first = x - int(number_of_layer1 / 2) * x_interval
            for index, edge in enumerate(edges_layer_0_1): # 目标公司 - 子公司1-n
                x_pos = x - int(number_of_layer1 / 2) * x_interval + x_interval * index
                y_pos = y + 200
                elements_down_temp.append(edge[1])
                style = {"width": "80px", "height": "120px"}
                if edge[4] == '1': # 海外实体，用虚线红框边界
                    style["border"] = "2px dashed red"
                                                  
                if edge[3] == '研发':
                    style["background-color"] = "#99ffcc"
                elif edge[3] == '生产':
                    style["background-color"] = "#ffcc99"
                elif edge[3] == '业务':
                    style["background-color"] = "#e6ffcc"
                elif edge[3] == '投资':
                    style["background-color"] = "#cce5ff"
                else:
                    style["background-color"] = "#fce8e6"         

      
      
                elements1.extend([{"id": edge[1], "data": {"label": edge[1]}, "position": {"x": x_pos, "y": y_pos}, "style": style}])
                elements2.extend([{"id": f"{edge[0]}-{edge[1]}", "source": edge[0], "target": edge[1], "label": (str(edge[2]) + '%' if not pd.isnull(edge[2]) else '')},])
              
        if number_of_layer_neg1: # 向上一次股权穿透
            x_interval = 200
            x_layer1_first = x - int(number_of_layer_neg1 / 2) * x_interval
            for index, edge in enumerate(edges_shareholder_0_1): # 目标公司 - 子公司1-n
                x_pos = x - int(number_of_layer_neg1 / 2) * x_interval + x_interval * index
                y_pos = y - 450
                elements_up_temp.append(edge[1])
                style = {"width": "80px", "height": "250px"}
                if edge[4] == '1': # 海外实体，用虚线红框边界
                    style["border"] = "2px dashed red"
                if '自然人' in edge[5]: # 实控人为 "color": "blue"
                    style["color"] = "blue"
                  
                elements1.extend([{"id": edge[1], "data": {"label": edge[1]}, "position": {"x": x_pos, "y": y_pos}, "style": style}])
                elements2.extend([{"id": f"{edge[0]}-{edge[1]}", "source": edge[1], "target": edge[0], "label": (str(edge[2]) + '%' if not pd.isnull(edge[2]) else '')},])
      
        if number_of_layer2: # 向下二次股权穿透
            edges_layer_1_2.sort(key=lambda x: x[0])
            edges_layer_1_2 = [list(group) for key, group in groupby(edges_layer_1_2, key=lambda x: x[0])]
            edges_layer_1_2 = [[i for i in sublist if i[1] not in [i[0][0] for i in edges_layer_1_2]] for sublist in edges_layer_1_2]
            x_pos = x_layer1_first
            for mini_edges_layer_1_2 in edges_layer_1_2:
                company = mini_edges_layer_1_2[0][0]
                number = len(mini_edges_layer_1_2)
                x_interval = 100
                for element in elements1:
                    if element['id'] == company:
                        position = element['position']
                        break
                x = position['x']
                for index, edge in enumerate(mini_edges_layer_1_2): # 子上市公司k - 子子公司k1, ..., kn
                    x_pos += x_interval
                    y_pos = y + 600
                    style = {"width": "80px", "height": "200px"}
                    if edge[1] not in elements_down_temp:
                        if edge[4] == '1': # 海外实体，用虚线红框边界
                            style["border"] = "2px dashed red"
                              
                        if edge[3] == '研发':
                            style["background-color"] = "#99ffcc"
                        elif edge[3] == '生产':
                            style["background-color"] = "#ffcc99"
                        elif edge[3] == '业务':
                            style["background-color"] = "#e6ffcc"
                        elif edge[3] == '投资':
                            style["background-color"] = "#cce5ff"
                        else:
                            style["background-color"] = "#fce8e6"   
                  
                        elements1.extend([{"id": edge[1], "data": {"label": edge[1]}, "position": {"x": x_pos, "y": y_pos}, "style": style}])
                        elements2.extend([{"id": f"{edge[0]}-{edge[1]}", "source": edge[0], "target": edge[1], "label": (str(edge[2]) + '%' if not pd.isnull(edge[2]) else '')},])
          
        if number_of_layer_neg2: # 向上二次股权穿透
            edges_shareholder_1_2.sort(key=lambda x: x[0])
            edges_shareholder_1_2 = [list(group) for key, group in groupby(edges_shareholder_1_2, key=lambda x: x[0])]
            edges_shareholder_1_2 = [[i for i in sublist if i[1] not in [i[0][0] for i in edges_shareholder_1_2]] for sublist in edges_shareholder_1_2]
            x_pos = x_layer1_first
            for mini_edges_layer_1_2 in edges_shareholder_1_2:
                company = mini_edges_layer_1_2[0][0]
                number = len(mini_edges_layer_1_2)
                x_interval = 120
                for element in elements1:
                    if element['id'] == company:
                        position = element['position']
                        break
                x = position['x']
                for index, edge in enumerate(mini_edges_layer_1_2): # 子上市公司k - 子子公司k1, ..., kn
                    x_pos += x_interval
                    y_pos = y - 800
                    if edge[1] not in elements_up_temp:
                        style = {"width": "80px", "height": "200px"}
                        if edge[4] == '1': # 海外实体，用虚线红框边界
                            style["border"] = "2px dashed red"
                        if '自然人' in edge[5]: # 实控人为 "color": "blue"
                            style["color"] = "blue"
                        elements1.extend([{"id": edge[1], "data": {"label": edge[1]}, "position": {"x": x_pos, "y": y_pos}, "style": style}])
                        elements2.extend([{"id": f"{edge[0]}-{edge[1]}", "source": edge[1], "target": edge[0], "label": (str(edge[2]) + '%' if not pd.isnull(edge[2]) else '')},])

        elements = elements1 + elements2
        flowStyles = {"height": 500, "width": 1000}
        react_flow("tree", elements=elements, flow_styles=flowStyles)
    except:
        pass# 您的源代码，请参考上面提供的完整代码。

```
