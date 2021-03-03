import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import json
import dash_bootstrap_components as dbc

from app import app

url_maps_data = 'https://raw.githubusercontent.com/SimonTeg/multiple_regressions/main/dutch_cities.csv'
dutch_cities = pd.read_csv(url_maps_data, error_bad_lines=False)
token = "pk.eyJ1IjoiaHVtYW5pbmciLCJhIjoiY2tpcHJiN3BlMDBjaDJ1b2J6ODQ4dzNlcyJ9.55HzvciQ31i0_ODARa9rLQ"

def fig_maps(df,hover_vars,token):
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name="city", hover_data=hover_vars,
                            color_discrete_sequence=["fuchsia"], zoom=6, height=450)
    fig.update_layout(mapbox_accesstoken=token) #mapbox_style="dark",
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def bar_chart_maps(y,title): #[19, 73] and labelMaastricht
    x = ['Potentie', 'Huidig']
    fig = go.Figure([go.Bar(x=x, y=y)])
    fig.update_layout(title_text=title, template="simple_white") #
    return fig

layout = html.Div([
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='maps-plot',figure=fig_maps(dutch_cities,['var1','var2'],token)
            )])
        ], width={"size": 4, "offset": 2}),
        dbc.Col([
            html.Div([dcc.Graph(id='bar-chart-hover')])
        ], width={"size": 4, "offset": 0})
    ])
])

@app.callback(
    Output('hover-data', 'children'),
    [Input('maps-plot', 'hoverData')])
def callback_image(hoverData):
    return json.dumps(hoverData, indent=2)

@app.callback(
    Output('bar-chart-hover', 'figure'),
    [Input('maps-plot', 'hoverData')])
def callback_image(hoverData):
    try:
        y=hoverData['points'][0]['customdata']
        title =  hoverData['points'][0]['hovertext']
        return bar_chart_maps(y,title)
    except:
        return bar_chart_maps([69,73],"Deventer")
