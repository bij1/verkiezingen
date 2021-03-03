import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import dash_daq as daq

import json
import dash_bootstrap_components as dbc
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Output, Input
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import numpy as np
import base64


from app import app
FA = "https://use.fontawesome.com/releases/v5.15.1/css/all.css"
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CYBORG, FA], suppress_callback_exceptions=True)#,prevent_initial_callbacks=True
token = "pk.eyJ1IjoiaHVtYW5pbmciLCJhIjoiY2tpcHJiN3BlMDBjaDJ1b2J6ODQ4dzNlcyJ9.55HzvciQ31i0_ODARa9rLQ"

# df = pd.read_csv("../data/tk2017_maps_so_far2.csv", delimiter =';', decimal =',', encoding ='utf-8',na_values=['#DIV/0!'])
df = pd.read_csv("tk2017_maps_so_far2_test.csv", delimiter =';', decimal =',', encoding ='utf-8',na_values=['#DIV/0!'])
df_flyer = pd.read_csv("../data/fl2.csv", delimiter =',', decimal ='.', encoding ='utf-8',na_values=['#DIV/0!'])

# df = pd.read_csv("../data/tk2017_maps_so_far2.csv", delimiter =';', decimal =',', encoding ='utf-8',na_values=['#DIV/0!'])

df['kleur'] = 0
def fig_maps(df,token,size,color):
    if color == 'kleur':
        fig = px.scatter_mapbox(df, lat="Lat", lon="Long", hover_name="bureau_label", hover_data=['Artikel 1', 'PvdD',"GL","DENK","D66"],
                                    size=size, zoom=6, height=650)
    else:
        fig = px.scatter_mapbox(df, lat="Lat", lon="Long", hover_name="bureau_label", hover_data=['Artikel 1','PvdD', "GL","DENK","D66"],
                                    size=size, zoom=6, height=650,color=color)
    fig.update_layout(mapbox_accesstoken=token) #
    fig.update_layout(margin={"r": 0, "t": 0,"l": 0, "b": 0})
    fig.update_layout(uirevision=True)
    # fig.update_layout(hovermode="text")

    return fig

test_fig = fig_maps(df,token,'Artikel 1','kleur')
test_fig.layout.update(mapbox_layers =mylayers)
test_fig.show()
def get_polygon(lons, lats, color='blue'):
    if len(lons) != len(lats):
        raise ValueError('the legth of longitude list  must coincide with that of latitude')
    geojd = {"type": "FeatureCollection"}
    geojd['features'] = []
    coords = []
    for lon, lat in zip(lons, lats):
        coords.append((lon, lat))
    coords.append((lons[0], lats[0]))  #close the polygon
    geojd['features'].append({ "type": "Feature",
                               "geometry": {"type": "Polygon",
                                            "coordinates": [coords] }})
    layer=dict(sourcetype = 'geojson',
             source =geojd,
             below='',
             type = 'fill',
             color = color)
    return layer

mylayers =[]
# mylayers.append(get_polygon(lons=[14, 16, 16, 14], lats=[58.55, 58.55, 60.6, 60.6],  color='gold'))
lat = [52.40208673,52.39964529,52.39727065]
lon = [4.911449615,4.919536571,4.91367751]
mylayers.append(get_polygon(lons=lon, lats=lat,  color='gold'))

def fig_campagne(df,token):
    fig = px.scatter_mapbox(df, lat="Lat", lon="Long", size="Flyers",
                            color_discrete_sequence=["fuchsia"], size_max=50, zoom=12, height=650)
    fig.update_layout(mapbox_accesstoken=token)
    fig.update_layout(margin={"r": 0, "t": 0,"l": 0, "b": 0})
    fig.update_layout(uirevision=True)
    return fig

def filter_data(list,df):
    if list in ([2, 1], [1, 2]):
        df1 = df[(df['percentage_gestemd_95_100'] == 1) | (df['percentage_gestemd_65_95'] == 1)]
    elif list in ([3, 1], [1, 3]):
        df1 = df[(df['percentage_gestemd_95_100'] == 1) | (df['percentage_gestemd_tot_65'] == 1)]
    elif list in ([3, 2], [2, 3]):
        df1 = df[(df['percentage_gestemd_65_95'] == 1) | (df['percentage_gestemd_tot_65'] == 1)]
    elif list == [1]:
        df1 = df[(df['percentage_gestemd_95_100'] == 1)]
    elif list == [2]:
        df1 = df[(df['percentage_gestemd_65_95'] == 1)]
    elif list == [3]:
        df1 = df[(df['percentage_gestemd_tot_65'] == 1)]
    else:
        df1 = df
    return df1

partijen = ['Artikel 1','VVD', 'PvDA', 'PVV', 'SP', 'CDA', 'D66', 'CU',
       'GL', 'SGP', 'PvdD', '50PLUS', 'OndernemersPartij',
       'VNL (VoorNederland)', 'DENK', 'Forum voor Democratie',
       'De Burger Beweging', 'Vrijzinnige Partij', 'GeenPeil', 'Piratenpartij']
partij_options = []
for partij in partijen:
    partij_options.append({'label': str(partij), 'value': partij})

radioitems = dbc.FormGroup([
        dbc.Label("Kies een partij uit de tweede kamer verkiezingen van 2017:"),
        dbc.RadioItems(
            options=partij_options,
            value="Artikel 1",
            id="radioitems-input",
        ),
    ])

radioitems_kleur = dbc.FormGroup([
        dbc.Label("Welke kleur van de bollen:"),
        dbc.RadioItems(
            options=[{'label': 'Stembureaus', 'value': 'kleur'},{'label': 'Grootste Partij', 'value': 'grootste_partij'},
                    {'label': 'Tweede Grootste Partij', 'value': 'tweede_grootste_partij'},
                    {'label': 'Derde Grootste Partij', 'value': 'derde_grootste_partij'}],
            value='kleur',
            id="radioitems-input-grote",
            inline=True
        ),
    ])

checklist = dbc.FormGroup([
        dbc.Label("Kies de voorwaarden voor Stembureau's"),
        dbc.Checklist(
            options=[
                {"label": 'percentage_gestemd_95_100', "value": 1},
                {"label": 'percentage_gestemd_65_95', "value": 2},
                {"label": 'percentage_gestemd_tot_65', "value": 3}
            ],
            value=[1,2,3],
            id="checklist-input",
        ),
    ])

# image_filename = '../assets/bij1_streep.png' # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())

layout = html.Div([

    # dbc.Row([
    #     dbc.Col([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height':'10%', 'width':'14%'})
    #              ], width={"size": 8, "offset": 1})
    # ]),
    html.Br(),
    # html.P(id="radioitems-checklist-output"),

    dbc.Row([
        dbc.Col([radioitems_kleur], width={"size": 8, "offset": 2})
    ]),

    dbc.Row([
        dbc.Col([radioitems], width={"size": 1, "offset": 1}),
        dbc.Col([
            html.Div([
                dcc.Graph(id='maps-plot'#,figure=fig_maps(df,hover_vars,token,size)
            )])
        ], width={"size": 8, "offset": 0}),
        dbc.Col([checklist]),
    ]),


    # dbc.Row([
    html.Br(),

    html.Div(
        daq.BooleanSwitch(
            id='switch_vk_flyer',
            on=True,
            labelPosition="top",
            color='#FFFF00'
        )
    ),
    html.Div(id='boolean-switch-output',
             style={'textAlign': 'center'  # 'color': colors['text'],
                    })
# ])


    # dbc.Row([html.Div([html.Button("Download csv", id="btn"), Download(id="download")])])

])

app.layout = layout

@app.callback(
    dash.dependencies.Output('boolean-switch-output', 'children'),
    [dash.dependencies.Input('switch_vk_flyer', 'on')])
def update_output(on):
    if on:
        pick = "Tweede Kamer Verkiezingen"
    else:
        pick = "Flyers"
    return '{}'.format(pick)

@app.callback(
    Output("radioitems-checklist-output", "children"),
    [Input("checklist-input", "value")]
)
def on_form_change(radio_items_value):
    template = "Radio button {} and type {}".format(radio_items_value, type(radio_items_value))
    return template

@app.callback(
    Output('maps-plot', "figure"),
    [Input("radioitems-input", "value"),
     Input("radioitems-input-grote", "value"),
     Input("checklist-input","value"),
     Input('switch_vk_flyer', 'on')]
)
def on_form_change(radio_items_value,color_value,filter,tk_flyer):
    if tk_flyer:
        df_filtered = filter_data(filter,df)
        fig = fig_maps(df_filtered, token, radio_items_value,color_value)
    else:
        fig = fig_campagne(df_flyer,token)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)