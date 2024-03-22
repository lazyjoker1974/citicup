from collections import defaultdict

import pandas as pd
import streamlit as st
from graphviz import Digraph, Source
from streamlit_agraph import Config, Edge, Node, agraph

st.set_page_config(page_title='Stock Relationships', page_icon=':chart_with_upwards_trend:')
st.title('Stock Relationships Visualization')
with st.sidebar:
    st.title('Exploration Panel')


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
        edges = edges + new_edges
        gen = list((sub_company(data[data['Symbol'] == ticker], not_first_layer=company) for company, ticker in subsidiary))
        new_edges, subsidiary = [edge for edges, _ in gen for edge in edges], [temp for _, temps in gen for temp in temps]
        level += 1
        if len(subsidiary) == 0 or level == 3:
            break

    edges = [edge for edge in edges if edge[6] == '1' or not pd.isnull(edge[2])]
    return edges

data = pd.read_csv('data/data.csv', dtype=str)
user_input = st.text_input("Enter stock code (e.g.: 000009)")

try:
    top_n = int(st.text_input("Enter the number of companies with the highest shareholding ratio (e.g.: 5):"))
except:
    top_n = 5
    
if user_input:
    try:
        stock_name = get_stock_name(data, user_input)
        st.markdown(f'<h5 style="color: gray;">Equity Structure Diagram of {user_input}（{stock_name}）:</h5>', unsafe_allow_html=True)
        edges = search(data, user_input)
        edges1 = [edge for edge in edges if edge[6] == '1']
        edges2 = [edge for edge in edges if edge[6] == '0']
        edges = edges1 + get_top_n_subsidiaries(edges2, n=top_n) # 这里表示每个公司只留下持股比例最高的n(例如n=5)家子公司
        nodes_list = []
        edges_list = []
        for name in list(set([edge[0] for edge in edges] + [edge[1] for edge in edges])):
            if name in list(set([edge[0] for edge in edges])):
                nodes_list.append(Node(id=name, label=name, size=100, shape="ellipse", color="rgba(255, 228, 196, 0.5)", clickNode=True, font={'bold': True, 'color': '#FF8C00'}))

            else:
                nodes_list.append(Node(id=name, label=name, size=100, shape="ellipse", color="rgba(128,128,128,0.1)", clickNode=True, font={'bold': False}))
        for edge in edges:
            edges_list.append(Edge(source=edge[0], label=str(edge[5][5:]) + (', 持股比例: ' + str(edge[2]) + '%' if not pd.isnull(edge[2]) else ''), target=edge[1], length=max(200, 10*len(edges)))) 
        
        config = Config(width=900, height=600, directed=True, physics=True, hierarchical=False, )
        return_value = agraph(nodes=nodes_list, edges=edges_list, config=config)
    except:
        pass

    
    
    



    # dot = Digraph()
    # for edge in edges:
    #     dot.node(edge[0], style='filled', fillcolor='lightblue')
    #     dot.node(edge[1], style='filled')
    #     dot.edge(edge[0], edge[1], label=str(edge[2])+'\%')
        
    # st.write(f'<div style="display:flex; justify-content:left; width:50vw;">'
    #         f'<div style="width:100%; max-width:80px; transform: scale(0.7); transform-origin: top left;">'
    #         f'{dot.pipe(format="svg").decode("utf-8")}</div>'
    #         f'</div>', unsafe_allow_html=True)
