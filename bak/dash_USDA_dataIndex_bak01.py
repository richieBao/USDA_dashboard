# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 14:54:55 2023

@author: richie bao
"""
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
pd.set_option('display.max_columns', None)

import pyodbc
from sqlalchemy import create_engine
import json
import itertools

from dash import Dash, dcc, html, Input, Output, dash_table, State,no_update
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# import io
# buffer = io.StringIO()
# from base64 import b64encode
# html_bytes = buffer.getvalue().encode()
# encoded = b64encode(html_bytes).decode()

from sqlalchemy import create_engine

flatten_lst=lambda lst: [m for n_lst in lst for m in flatten_lst(n_lst)] if type(lst) is list else [lst]   
def update_df_foreign_keys(df,dn_foreign_keys_mapping):
    for col in df.columns:
        if col in dn_foreign_keys_mapping.keys():
            related_df=pd.read_sql('select * from %s'%(dn_foreign_keys_mapping[col][0]),conn)
            df[col]=df[col].apply(lambda idx:related_df[related_df.ID==idx][dn_foreign_keys_mapping[col][1]].item())     
   
    return df

def sql_query2list(statement,conn):
    cursor=conn.cursor()
    cursor.execute(statement) 
    fetched_data=[dict((cursor.description[i][0], value)  for i, value in enumerate(row)) for row in cursor.fetchall()]
    
    return  fetched_data


# datasets query
db_fn=r'./data/USDA_dataIndex.accdb'
conn=pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;'%db_fn)

dn_foreign_keys_mapping={'dn_1':['category','d_category'],
                         'dn_2':['sampleidx','sample_idx'],
                         'dn_3':['category','d_category'],
                         'dn_4':['category','d_category'],
                         'dn_5':['sampleidx','sample_idx'],
                         'dn_6':['sampleidx','sample_idx'],
                         'dn_7':['category','d_category'],
                         'dn_8':['category','d_category'],
                         'dn_9':['category','d_category'],
                         'dn_10':['category','d_category'],
                         'dn_11':['category','d_category'],
                         'dn_12':['category','d_category'],
                         'd_category':['category','d_category'],
                         'udn_1':['category','d_category']}

# dashboard
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) #
app.config.suppress_callback_exceptions = True

sample_data_list_=sql_query2list('select a.sample_idx from sampleidx as a',conn)
sample_data_list=[i['sample_idx'] for i in sample_data_list_ if i['sample_idx']!='Null']
# print(sample_data_list)

table_dict={'related_research':['usda','modelstudy'],
            'available_data':['category','dataset','sampleidx'],
            'sample_data':sample_data_list}

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [html.H2("数据集检索", style={"text-align": "center"}),html.P('USDA',style={"text-align": "center"})]
                ),                
            ]
        ),
        dbc.Row([
            dbc.Col([
                html.H5('研究模型'),
                dcc.Dropdown(id='d_related_research',options=table_dict['related_research']),
                html.Div(id='t_related_research'),
                # dash_table.DataTable(id='dt_related_research'),                
                dbc.Alert(id='alert_model_datasets'),
                ]),
            dbc.Col([
                html.H5('数据集'),
                dcc.Dropdown(id='d_available_data',options=table_dict['available_data']),
                html.Div(id='t_available_data'),
                ]),   
            dbc.Col([
                html.H5('样本集'),
                dcc.Dropdown(id='d_sample_data',options=table_dict['sample_data']),
                html.Div(id='t_sample_data'),
                ]),               
            ]),
        dbc.Row([html.H5('SQL 查询'),]),
        dbc.Row([   
            dbc.Col([                    
                dcc.Input(id='query',value='',placeholder="e.g.: select a.ref_citation from modelstudy as a",type='text',style={'width':'100%'}),
                ],width=4),     
            dbc.Col([        
                dbc.Button('submit',id='button_query_submit',color="dark",n_clicks=0, ),
                ],width='auto'),              
            dbc.Col([
                # dbc.Alert(id='alert_query'),
                html.Pre(id='pre_query', style=styles['pre']),
                ],),
            ]),        
        dbc.Row([ 
            html.Hr(style={'marginTop': '1em'}),
            html.H5('研究模型与数据集关系'),
            dcc.Checklist(id='cl_modelstudy',options=table_dict['related_research'],inline=True),
            dcc.Graph(id='g_sankey'),
            ]),   

        ]
    )

# dt_func=lambda df:dash_table.DataTable(df.to_dict('records'),[{"name": i, "id": i} for i in df.columns],style_table={'overflow':'auto'})

@app.callback(
    Output('t_related_research','children'),
    # Output('dt_related_research','data'),
    # Output('dt_related_research','columns'),
    Input('d_related_research',"value"),    
    )
def related_research_table(table_name):
    if table_name is not None:
        df=pd.read_sql('select * from %s'%(table_name),conn)  
        df=update_df_foreign_keys(df,dn_foreign_keys_mapping)
        
        # for col in df.columns:
        #     if col in dn_foreign_keys_mapping.keys():
        #         related_df=pd.read_sql('select * from %s'%(dn_foreign_keys_mapping[col][0]),conn)
        #         df[col]=df[col].apply(lambda idx:related_df[related_df.ID==idx][dn_foreign_keys_mapping[col][1]].item())     
                
        return  dash_table.DataTable(df.to_dict('records'),
                                      [{"name": i, "id": i} for i in df.columns],
                                      style_table={'overflow':'auto'},
                                      page_size=10,
                                      id='dt_related_research')
        # data=df.to_dict('records')
        # columns=[{"name": i, "id": i} for i in df.columns]
        
        # return data,columns
        
@app.callback(
    Output('t_available_data','children'),
    Input('d_available_data',"value"),    
    )
def available_data_table(table_name):
    if table_name is not None:
        df=pd.read_sql('select * from %s'%(table_name),conn)   
        return dash_table.DataTable(df.to_dict('records'),
                                    [{"name": i, "id": i} for i in df.columns],
                                    style_table={'overflow':'auto'},
                                    page_size=10,)
  
@app.callback(
    Output('t_sample_data','children'),
    Input('d_sample_data',"value"),    
    )
def sample_data_table(table_name):
    if table_name is not None:
        df=pd.read_sql('select * from %s'%(table_name),conn)   
        return dash_table.DataTable(df.to_dict('records'),
                                    [{"name": i, "id": i} for i in df.columns],
                                    style_table={'overflow':'auto'},
                                    page_size=10,)

@app.callback(
    Output('alert_model_datasets','children'),
    Input('dt_related_research','active_cell'),
    Input('dt_related_research','data'),
    Input('dt_related_research','columns'),      
    )
def model_datasets(active_cell,rows,columns):    
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    if active_cell:
        row_values=df.iloc[active_cell['row']]
        row_values_dn=row_values[[col for col in df.columns if col in dn_foreign_keys_mapping.keys()]]

        try:
            mm=row_values['model_method']
        except:
            mm=row_values['point']
        return f'{mm} 数据需求: {row_values_dn.values}.' 
    
@app.callback(
    Output('pre_query','children'),
    Input("button_query_submit", "n_clicks"),
    State('query','value'),
    )
def sql_query(n_clicks,statement):    
    if n_clicks:          
        cursor=conn.cursor()
        try:
            cursor.execute(statement) # select * from Biophysical_UHI_fake category; select a.ref_citation from modelmethod as a where model_method=='Urban Cooling Model'
            fetched_data=[dict((cursor.description[i][0], value)  for i, value in enumerate(row)) for row in cursor.fetchall()]
            # cursor.connection.close()
            
            return json.dumps(fetched_data)
        except:
            return json.dumps('SQL statement is wrong!')
            
    return json.dumps('Null')

@app.callback(
    Output('g_sankey','figure'),
    Input('cl_modelstudy',"value"),    
    )
def display_sankey(related_reserch):
    modelstudy=pd.read_sql('select * from %s'%('modelstudy'),conn) 
    # usda=pd.read_sql('select * from %s'%('usda'),conn) 
    # category=pd.read_sql('select * from %s'%('category'),conn) 
    dataset=pd.read_sql('select * from %s'%('dataset'),conn) 
    usda=pd.read_sql('select * from %s'%('usda'),conn) 
    # sampleidx=pd.read_sql('select * from %s'%('sampleidx'),conn) 
    modelstudy=update_df_foreign_keys(modelstudy,dn_foreign_keys_mapping)
    dataset=update_df_foreign_keys(dataset,dn_foreign_keys_mapping)     
    usda=update_df_foreign_keys(usda,dn_foreign_keys_mapping)  
    
    source_target_links=[]
    if related_reserch is not None:        
        if 'modelstudy' in related_reserch:
            for dn in dn_foreign_keys_mapping.keys():
                if dn in modelstudy.columns:
                    source_target_links.append(list(zip(modelstudy['model_method'],modelstudy[dn])))  
        if 'usda' in related_reserch:
            for dn in dn_foreign_keys_mapping.keys():
                if dn in usda.columns:
                    source_target_links.append(list(zip(usda['point'],usda[dn])))  
                    source_target_links.append(list(zip(usda['chapter'],usda['point'])))                
        for dn in dn_foreign_keys_mapping.keys():
            if dn in dataset.columns:
                source_target_links.append(list(zip(dataset[dn],dataset['d_name'])))        
    else:
        for dn in dn_foreign_keys_mapping.keys():
            if dn in modelstudy.columns:
                source_target_links.append(list(zip(modelstudy['model_method'],modelstudy[dn])))
            if dn in dataset.columns:
                source_target_links.append(list(zip(dataset[dn],dataset['d_name'])))
            if dn in usda.columns:
                source_target_links.append(list(zip(usda['point'],usda[dn])))  
                source_target_links.append(list(zip(usda['chapter'],usda['point']))) 
    
    source_target_links=flatten_lst(source_target_links)    
    labels=list(set(list(itertools.chain(*source_target_links))))
    source_target_links_df=pd.DataFrame(source_target_links,columns=['source','target'])
    source_target_links_df=source_target_links_df[(source_target_links_df['source']!='Null') & (source_target_links_df['target']!='Null')]
    source_target_links_df['source_id']=source_target_links_df.source.apply(lambda x:labels.index(x))
    source_target_links_df['target_id']=source_target_links_df.target.apply(lambda x:labels.index(x))
    
    style_sankey=dict(
                pad = 15,
                thickness = 15,
                line = dict(color = "black", width = 0.5),
                color = "lightgray")    
    
    node=dict(label = labels)
    node.update(style_sankey)
    
    link= dict(
      source =source_target_links_df['source_id'], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target =source_target_links_df['target_id'],
      value = [1]*len(source_target_links)
      )    
    
    fig = go.Figure(data=[go.Sankey(
        node = node,
        link =link,
        )])
    
    fig.update_layout(title_text="Sankey Diagram", font_size=13,autosize=False,height=1200)        
    return fig
    
if __name__ == '__main__':
    app.run_server(debug=True)
