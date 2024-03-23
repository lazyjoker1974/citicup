from collections import defaultdict
from itertools import groupby

import pandas as pd
# import pygraphviz as pgv
import streamlit as st
# from graphviz import Digraph, Source
# from streamlit_agraph import Config, Edge, Node, agraph
from streamlit_react_flow import react_flow


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
            edges = list(zip([not_first_layer] * df.shape[0], df['RalatedParty'], df['DirectHoldingRatio'].astype(float), df['IndirectHoldingRatio'], df['is_foreign'], df['Relationship'], df['is_subsidiary_listed']))
        else:
            edges = list(zip(df['Name'], df['RalatedParty'], df['DirectHoldingRatio'].astype(float), df['IndirectHoldingRatio'], df['is_foreign'], df['Relationship'], df['is_subsidiary_listed']))
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
user_input = st.text_input("Enter stock code (e.g.: 000009)")

try:
    top_n = int(st.text_input("Enter the number of companies with the highest shareholding ratio (e.g.: 5):"))
except:
    top_n = 5
    
            
import streamlit as st
from streamlit_react_flow import react_flow

with st.sidebar:
    st.markdown("# 股权穿刺图查询软件")
    st.markdown("通过搜索股票代码可以展示对应上市公司的股权穿刺图：")
    st.markdown("<style> .red-dashed-box { border: 2px dashed red; padding: 5px; margin-bottom: 10px; } .black-solid-box { border: 2px solid black; padding: 5px; margin-bottom: 10px; } </style>", unsafe_allow_html=True)
    st.markdown("<div class='red-dashed-box'>红色虚线框：海外实体</div>", unsafe_allow_html=True)
    st.markdown("<div class='black-solid-box'>黑色实线框：国内实体</div>", unsafe_allow_html=True)
    st.markdown("黑色字体：公司名称</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: blue;'>蓝色字体：控制人</div>", unsafe_allow_html=True)


if user_input:
    try:
        stock_name = get_stock_name(data, user_input)
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
        elements1, elements2 = [{"id": target_company_name, "data": {"label": target_company_name}, "position": {"x": x, "y": y}}], [] # 目标企业
        
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
        pass




# if user_input:
#     try:
#         stock_name = get_stock_name(data, user_input)
#         st.markdown(f'<h5 style="color: gray;">Equity Structure Diagram of {user_input}（{stock_name}）:</h5>', unsafe_allow_html=True)
#         edges = search(data, user_input)
#         edges1 = [edge for edge in edges if edge[6] == '1']
#         edges2 = [edge for edge in edges if edge[6] == '0']
#         edges = edges1 + get_top_n_subsidiaries(edges2, n=top_n) # 这里表示每个公司只留下持股比例最高的n(例如n=5)家子公司
#         nodes_list = []
#         edges_list = []
#         for name in list(set([edge[0] for edge in edges] + [edge[1] for edge in edges])):
#             if name in list(set([edge[0] for edge in edges])):
#                 nodes_list.append(Node(id=name, label=name, size=100, shape="ellipse", color="rgba(255, 228, 196, 0.5)", clickNode=True, font={'bold': True, 'color': '#FF8C00'}))

#             else:
#                 nodes_list.append(Node(id=name, label=name, size=100, shape="ellipse", color="rgba(128,128,128,0.1)", clickNode=True, font={'bold': False}))
#         for edge in edges:
#             edges_list.append(Edge(source=edge[0], label=str(edge[5][5:]) + (', 持股比例: ' + str(edge[2]) + '%' if not pd.isnull(edge[2]) else ''), target=edge[1], length=max(200, 10*len(edges)))) 
        
#         config = Config(width=900, height=600, directed=True, physics=True, hierarchical=True, )
#         return_value = agraph(nodes=nodes_list, edges=edges_list, config=config)
#     except:
#         pass
