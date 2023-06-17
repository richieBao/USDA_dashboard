# -*- coding: utf-8 -*-
"""
Created on Sun May 28 20:31:47 2023

@author: richie bao
"""
# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
import numbers
import json
import numpy as np
import pkg_resources

ghg_fn=pkg_resources.resource_filename('usda_dashboard', 'data/EDGARv7.0_FT2021_fossil_CO2_booklet_2022.xlsx')
# ghg_fn='./data/EDGARv7.0_FT2021_fossil_CO2_booklet_2022.xlsx'
ghg_df=pd.ExcelFile(ghg_fn)
# print(ghg_df.sheet_names)
# ['info', 'fossil_CO2_totals_by_country', 'fossil_CO2_by_sector_and_countr', 'fossil_CO2_per_GDP_by_country', 'fossil_CO2_per_capita_by_countr', 'LULUCF by macro regions']
fossil_CO2_totals_by_country=pd.read_excel(ghg_fn,sheet_name='fossil_CO2_totals_by_country').round(3)
fossil_CO2_by_sector_and_country=pd.read_excel(ghg_fn,sheet_name='fossil_CO2_by_sector_and_countr').round(3)
fossil_CO2_per_GDP_by_country=pd.read_excel(ghg_fn,sheet_name='fossil_CO2_per_GDP_by_country').round(3)
fossil_CO2_per_capita_by_country=pd.read_excel(ghg_fn,sheet_name='fossil_CO2_per_capita_by_countr').round(3)
LULUCF_by_macro_regions=pd.read_excel(ghg_fn,sheet_name='LULUCF by macro regions').round(3)
keys_year=[i for i in fossil_CO2_totals_by_country.columns if isinstance(i,numbers.Number)]

countries_fn=pkg_resources.resource_filename('usda_dashboard', 'data/countries.geojson')
# countries_fn=r'./data/countries.geojson'
# with open(countries_fn, encoding="utf8") as f:
#     counties = json.load(f)    
countries_gdf=gpd.read_file(countries_fn)

# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)

tabs_styles = {
    'height': '44px'
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

# App layout
app.layout = dmc.Container([
    dmc.Title(r'各国【化石】二氧化碳排放量（Fossil CO_2 emissions by country）', color="blue", size="h3"),
    dcc.Tabs(id='tabs_co2',value='tab-1',children=[
        dcc.Tab(label='fossil CO2 totals by country', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='fossil CO2 by sector_and_country', value='tab-2', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='fossil CO2 per GDP by country', value='tab-3', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='fossil CO2 per capita by country', value='tab-4', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='LULUCF by macro regions', value='tab-5', style=tab_style, selected_style=tab_selected_style),
        ],style=tabs_styles),
    html.Div(id='tabs-content-inline'),
    html.Label(r'历年 CO_2 排放量:（选择国家）'),
    dcc.Dropdown(
        fossil_CO2_totals_by_country['Country'].tolist(),['China','United States','India','Russia','United Kingdom','Iran'],multi=True,id='countries4co2totals'                
        ), 
    dcc.Graph(id='co2_totals'),  
    html.Label(r'历年 CO_2 排放量地图'),     
    dcc.Graph(id='co2_worldmap'),
    dcc.Slider(id='year-slider',min=min(keys_year),max=max(keys_year),marks={x: {'label': str(x)} for x in range(min(keys_year),max(keys_year))},value=2018),
    ],
    fluid=True
    )

@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs_co2', 'value'))
def render_co2_tables(tab):
    if tab == 'tab-1':
        return html.Div([
            dash_table.DataTable(data=fossil_CO2_totals_by_country.to_dict('records'), page_size=11, style_table={'overflowX': 'auto'},columns=[{"name": str(i), "id": str(i)} for i in fossil_CO2_totals_by_country.columns]),
                      ])
    elif tab == 'tab-2':
        return html.Div([
            dash_table.DataTable(data=fossil_CO2_by_sector_and_country.to_dict('records'), page_size=11, style_table={'overflowX': 'auto'},columns=[{"name": str(i), "id": str(i)} for i in fossil_CO2_by_sector_and_country.columns]),
        ])
    elif tab == 'tab-3':
        return html.Div([
            dash_table.DataTable(data=fossil_CO2_per_GDP_by_country.to_dict('records'), page_size=11, style_table={'overflowX': 'auto'},columns=[{"name": str(i), "id": str(i)} for i in fossil_CO2_per_GDP_by_country.columns]),
        ])
    elif tab == 'tab-4':
        return html.Div([
            dash_table.DataTable(data=fossil_CO2_per_capita_by_country.to_dict('records'), page_size=11, style_table={'overflowX': 'auto'},columns=[{"name": str(i), "id": str(i)} for i in fossil_CO2_per_capita_by_country.columns]),
        ])
    elif tab == 'tab-5':
        return html.Div([
            dash_table.DataTable(data=LULUCF_by_macro_regions.to_dict('records'), page_size=11, style_table={'overflowX': 'auto'},columns=[{"name": str(i), "id": str(i)} for i in LULUCF_by_macro_regions.columns]),
        ])
    
@app.callback(Output('co2_totals', 'figure'),
               Input('countries4co2totals', 'value'))   
def update_co2_totals_by_country(countries):
    df=fossil_CO2_totals_by_country[fossil_CO2_totals_by_country.Country.isin(countries)] 
    # keys_year=[i for i in df.columns if isinstance(i,numbers.Number)]
    df_ys=df[keys_year+['Country']]
    df_melted=df_ys.melt('Country', value_name='vals')
    fig=px.line(df_melted,x='variable',y='vals',color='Country',markers=True).update_layout(plot_bgcolor='rgba(0, 0, 0, 0)',yaxis_title=r'CO_2 totals (Mt CO2/yr)',xaxis_title="Year")
    fig.update_yaxes(gridcolor='lightgrey')
    fig.update_xaxes(gridcolor='lightgrey')
    
    return fig
    
@app.callback(
    Output('co2_worldmap', 'figure'),
    Input('year-slider', 'value'))
def update_co2_worldmap(selected_year):
    df_ys=fossil_CO2_totals_by_country[keys_year+['Country','EDGAR Country Code']]
    df_melted=df_ys.melt(['Country','EDGAR Country Code'], value_name='vals')
    df_melted_yr=df_melted[df_melted['variable']==selected_year]
    countries_copy_gdf=countries_gdf.copy(deep=True)
    
    def merging(row):      
        try:
            key=row['ISO_A3']
            selection=df_melted_yr[df_melted_yr['EDGAR Country Code']==key]
            return pd.Series(selection[['Country','vals']].values[0])
        except:
            return pd.Series([np.nan,np.nan])   
    countries_copy_gdf[['Country','vals']]=countries_copy_gdf.apply(merging,axis=1)
    
    fig = go.Figure(px.choropleth_mapbox(countries_copy_gdf, 
                                         geojson=countries_copy_gdf.geometry,
                                         locations=countries_copy_gdf.index,
                                         color='vals',
                                         color_continuous_scale='thermal', # px.colors.diverging.BrBG, "Viridis",
                                         mapbox_style="open-street-map", # "carto-positron",
                                         zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                                         opacity=0.5,
                                         hover_data=["Country", "vals"],
                                         # height=1000,
                                         ))    
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)