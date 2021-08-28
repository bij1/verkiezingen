from dash.dependencies import Input, Output
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
import dash_html_components as html
from app import app
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
import os
import pickle
import dash_daq as daq
import dash
import numpy as np

df_amsterdam_google_sheet = pd.read_csv("data/flyer_amsterdam.csv", delimiter=',', encoding='utf-8')

# def refresh_data():
#     main()
#     df_refresh=pd.DataFrame(values_input[1:], columns=values_input[0])
#     return df_refresh

# ssl._create_default_https_context = ssl._create_unverified_context
if 'MAPBOX_TOKEN' in os.environ:
    token = os.environ['MAPBOX_TOKEN']
else:
    throw('please set the MAPBOX_TOKEN environment variable, to be obtained from https://account.mapbox.com/.')
#wcomment

# df_amsterdam_buurten = pd.read_csv("data/buurten_data_cbs_amsterdam_v1.csv", delimiter=',', decimal='.',
#                                    encoding='utf-8')

df_amsterdam_buurten = pd.read_csv("data/buurten_data_cbs_amsterdam_v2.csv", delimiter=',', decimal='.',
                                   encoding='utf-8', dtype={
                                       'Bijstand ': np.float64,
                                       'AO':        np.float64,
                                       'WW':        np.float64,
                                       'AOW':       np.float64,
                                       })
df_potentie = df_amsterdam_google_sheet.merge(df_amsterdam_buurten[df_amsterdam_buurten['Huishoudens'] > 20], on='Buurt')

df_potentie['% Niet_Westers'] = df_potentie['Niet-westers']/df_potentie['Aantal inwoners']
df_potentie['% Suriname/Antillen/Aruba'] = (df_potentie['Nederlandse Antillen en Aruba '] +
                                            df_potentie['Suriname']) \
                                           /df_potentie['Aantal inwoners']
df_potentie['% Uitkering'] = (df_potentie['Bijstand '] + df_potentie['AO'] + df_potentie['WW'] + df_potentie['AOW'])/df_potentie['Aantal inwoners']

df_potentie.fillna

def flyers_amsterdam_map_potentie(df,potentie_keuze):
    fig = px.choropleth_mapbox(df,
        geojson='https://maps.amsterdam.nl/open_geodata/geojson.php?KAARTLAAG=GEBIED_BUURTEN&THEMA=gebiedsindeling',
        color= potentie_keuze, #"Flyers",
        color_continuous_scale = kleuren_bij1,
        locations="Buurt", featureidkey="properties.Buurt"
        ,zoom=10,  center={"lat": 52.37220844333981, "lon": 4.89968264189926}
                               )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_accesstoken=token)
    return fig
# potentie_keuze = ['% Suriname/Antillen/Aruba']
# potentie_keuze = ['% Niet_Westers']
# flyers_amsterdam_map_potentie(df_potentie[df_potentie['Geflyerd'] == 'Nog niet'],potentie_keuze)

def flyers_amsterdam_map(df,doorzichtigheid):
    fig = px.choropleth_mapbox(df,
        geojson='https://maps.amsterdam.nl/open_geodata/geojson.php?KAARTLAAG=GEBIED_BUURTEN&THEMA=gebiedsindeling',
        color= 'Geflyerd', #"Flyers",
        locations="Buurt", featureidkey="properties.Buurt",
        opacity = doorzichtigheid
        ,zoom=10,  center={"lat": 52.37220844333981, "lon": 4.89968264189926}
        ,color_discrete_map = {
        "Gedaan": "rgba(0,0,0,255)",
        "Nog niet": "#ffff00",
        "In afwachting": '#4fd600'}
                               )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_accesstoken=token)
    return fig

flyers_amsterdam_map(df_amsterdam_google_sheet,1)




kleuren_bij1 = [ '#ff9600','#ff00ba' , '#4fd600','#c700bf','#ff0000','#00ccff' ]

def bar_chart_maps(buurt,selectie):
    x = selectie
    y = df_amsterdam_buurten.loc[df_amsterdam_buurten['Buurt'] == buurt[0]][selectie].values.tolist()[0]
    fig = go.Figure([go.Bar(x=x, y=y, marker_color=kleuren_bij1)])
    fig.update_layout(title_text=buurt[0], template='ygridoff')
    fig.update_layout(
        # font_family="Courier New",
        # font_color="blue",
        # title_font_family="Times New Roman",
        title_font_color="#000000",
        legend_title_font_color="#000000"
    )
    return fig


migratieachtergrond = ['Westers', 'Niet-westers', 'Marokko', 'Nederlandse Antillen en Aruba ', 'Suriname',
                       'Turkije', 'Overig']
huishoudens = ['Huishoudens', 'Eenpersoonshuishoudens', 'Zonder kinderen', 'Met kinderen']
uitkering = ['Bijstand ', 'AO', 'WW', 'AOW']
flyers_inw = ['Aantal Flyers', 'Aantal inwoners', 'Huishoudens']

radioitems_onderwerp = dbc.FormGroup([
        # dbc.Label("Onderwerp:"),
        dbc.RadioItems(
            options=[{'label': 'Migratieachtergrond', 'value': migratieachtergrond},
                     {'label': 'Huishoudens', 'value': huishoudens},
                    {'label': 'Uitkering', 'value': uitkering},
                    {'label': 'Flyers nodig', 'value': flyers_inw}],
            value=flyers_inw,
            id="onderwerp-input-graph",
            inline=True,

            labelCheckedStyle={"color": "#ffff00"}
        ),
    ])

radioitems_potentie = dbc.FormGroup([
        dbc.Label("Input voor de kaart:"),
        dbc.RadioItems(
            options=[{'label': 'Alle buurten', 'value': 'Alle buurten'},
                     {'label': 'Nog doen % Niet-Westers', 'value': '% Niet_Westers'},
                    {'label': 'Nog doen % Suriname/Antillen/Aruba', 'value': '% Suriname/Antillen/Aruba'},
                    {'label': 'Nog doen % Uitkering', 'value': '% Uitkering'}],
            value= 'Alle buurten',
            id="potentie-input-graph",
            inline=True,

            labelCheckedStyle={"color": "#ffff00"}
        ),
    ])

layout = html.Div([
    html.P(['Waar kun je flyers krijgen? Zie ', html.A('hier', href='https://bij1.org/campagnemateriaal/'), '!'], id='link', style={'textAlign': 'center'}),

    html.P(['Wil je doorgeven dat je ergens gaat flyeren? Geef dit dan door in onze Signal groepen!'], id='link', style={'textAlign': 'center'}),

    # html.Div(
    #     daq.BooleanSwitch(
    #         id='switch_doorzichtig',
    #         on=True,
    #         labelPosition="top",
    #         color='#FFFF00'
    #     )
    # ),
    # html.Div(id='switch-output-doorzichtig',
    #          style={'textAlign': 'center'  # 'color': colors['text'],
    #                 }),
    html.Br(),
    dbc.Row([
       dbc.Col([radioitems_potentie], width={"size": 8, "offset": 2})
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='flyer-plot' #,figure=flyers_amsterdam_map(df_amsterdam_google_sheet)
                          )])
        ], width={"size": 8, "offset": 2})
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([radioitems_onderwerp], width={"size": 8, "offset": 2})
        ]),
    #Bar Graph
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='Bar-plot-buurten'#, figure=bar_chart_maps(buurt,selectie)
                          )])
        ], width={"size": 8, "offset": 2})
    ])
])

# @app.callback(
#     Output(component_id='output-keuze', component_property='children'),
#     Input(component_id="potentie-input-graph", component_property='value')
# )
# def update_output_div(input_value):
#     return 'Output: {} type{}'.format(input_value, type(input_value))
#
# @app.callback(
#     dash.dependencies.Output('switch-output-doorzichtig', 'children'),
#     [dash.dependencies.Input('switch_doorzichtig', 'on')])
# def update_output(on):
#     if on:
#         pick = "DOORZICHTIG"
#     else:
#         pick = "ON-DOORZICHTIG "
#     return '{}'.format(pick)

#
@app.callback(
    Output('flyer-plot', "figure"),
    [Input("potentie-input-graph", 'value')]
)
def on_form_change(keuze_maps):
    if keuze_maps =='Alle buurten':
        fig = flyers_amsterdam_map(df_amsterdam_google_sheet,0.4)
        return fig
    else:
        fig = flyers_amsterdam_map_potentie(df_potentie[df_potentie['Geflyerd'] == 'Nog niet'],keuze_maps)
        return fig
# @app.callback(
#     Output('flyer-plot', "figure"),
#     [Input('switch_doorzichtig', 'on')]
# )
# def on_form_change(doorzichtheid_on):
#     if doorzichtheid_on:
#         fig = flyers_amsterdam_map(df_amsterdam_google_sheet,0.4)
#         return fig
#     else:
#         fig = flyers_amsterdam_map(df_amsterdam_google_sheet,1)
#         return fig

@app.callback(
    Output('Bar-plot-buurten', 'figure'),
    [Input('flyer-plot', 'hoverData'),
     Input("onderwerp-input-graph", "value")])
def callback_image(hoverData,selectie_onderwerp):
    try:
        buurt_hover = [hoverData['points'][0]["location"]]
        # title =  hoverData['points'][0]['hovertext']
        return bar_chart_maps(buurt_hover, selectie_onderwerp)
    except:
        return bar_chart_maps(['Westelijke eilanden'], selectie_onderwerp)

# app.layout = layout

# if __name__ == '__main__':
#     app.run_server(debug=True)