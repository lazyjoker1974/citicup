import pandas as pd
import streamlit as st
from graphviz import Digraph, Source


def sub_company(df, not_first_layer): # 给定dataframe，返回edges，以及子公司的(company, ticker)对
    if df.shape[0]:
        if not_first_layer:
            edges = list(zip([not_first_layer] * df.shape[0], df['RalatedParty'], df['DirectHoldingRatio'], df['IndirectHoldingRatio'], df['is_foreign']))
        else:
            edges = list(zip(df['Symbol'], df['RalatedParty'], df['DirectHoldingRatio'], df['IndirectHoldingRatio'], df['is_foreign']))
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

    edges = [edge for edge in edges if not pd.isnull(edge[2])]
    return edges


# Load data
data = pd.read_csv('data/data.csv', dtype=str)

# Page layout
st.set_page_config(page_title='Stock Relationships', page_icon=':chart_with_upwards_trend:')

st.title('Stock Relationships Visualization')

# User input
user_input = st.text_input("Enter stock code")

with st.sidebar:
    st.title('Exploration Panel')

# Search and display graph
if user_input:
    edges = search(data, user_input)[:10] # 先展示前十个吧，后期要做对于公司市值的筛选，筛选市值和持股比例最大的几个或十几个显示，不然太多会卡bug
    st.markdown(f'<h5 style="color: gray;">Equity Structure Diagram of {user_input}:</h5>', unsafe_allow_html=True)
    dot = Digraph()
    for edge in edges:
        dot.node(edge[0], style='filled', fillcolor='lightblue')
        dot.node(edge[1], style='filled')
        dot.edge(edge[0], edge[1], label=str(edge[2])+'\%')

    st.write(f'<div style="display:flex; justify-content:left; width:50vw;">'
            f'<div style="width:100%; max-width:80px; transform: scale(0.7); transform-origin: top left;">'
            f'{dot.pipe(format="svg").decode("utf-8")}</div>'
            f'</div>', unsafe_allow_html=True)

