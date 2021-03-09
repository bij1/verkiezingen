from dash.dependencies import Input, Output
import numpy as np
import json
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

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# here enter the id of your google sheet
SAMPLE_SPREADSHEET_ID_input ='1_xU8TGUOc0WJVdW0V6Z5cHs7yWsO3FoX7rya9wy9G7Q' #'1cvZswLiDo3LfhnA7RcS8vFqacx73RGor-OZ_FtvyLE8'
SAMPLE_RANGE_NAME = 'A1:AH1000'

def main():
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'data/credentials.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])

    if not values_input and not values_expansion:
        print('No data found.')

main()

df_amsterdam_google_sheet=pd.DataFrame(values_input[1:], columns=values_input[0])

# ssl._create_default_https_context = ssl._create_unverified_context
token = "pk.eyJ1IjoiaHVtYW5pbmciLCJhIjoiY2tpcHJiN3BlMDBjaDJ1b2J6ODQ4dzNlcyJ9.55HzvciQ31i0_ODARa9rLQ"



def flyers_amsterdam_map(df):
    fig = px.choropleth_mapbox(df,
        geojson='https://maps.amsterdam.nl/open_geodata/geojson.php?KAARTLAAG=GEBIED_BUURTEN&THEMA=gebiedsindeling',
        color= 'Geflyerd', #"Flyers",
        locations="Buurt", featureidkey="properties.Buurt",
        opacity = 0.4, zoom=10,  center={"lat": 52.37220844333981, "lon": 4.89968264189926})
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_accesstoken=token)
    return fig

df_amsterdam_buurten = pd.read_csv("data/buurten_data_cbs_amsterdam_v1.csv", delimiter=',', decimal='.',
                                   encoding='utf-8')

migratieachtergrond = ['Westers', 'Niet-westers', 'Marokko', 'Nederlandse Antillen en Aruba ', 'Suriname',
                       'Turkije', 'Overig']
huishoudens = ['Huishoudens', 'Eenpersoonshuishoudens', 'Zonder kinderen', 'Met kinderen']
uitkering = ['Bijstand ', 'AO', 'WW', 'AOW']
flyers_inw = ['Aantal inwoners', 'Aantal Flyers']
x = ['Potentie', 'Huidig']
# buurt = ['Westelijke eilanden']

selectie = huishoudens
# df_amsterdam_buurten.loc[df_amsterdam_buurten['Buurt'] == buurt[0]][selectie]


def bar_chart_maps(buurt,selectie): #[19, 73] and labelMaastricht
    x = selectie
    y = df_amsterdam_buurten.loc[df_amsterdam_buurten['Buurt'] == buurt[0]][selectie].values.tolist()[0]
    fig = go.Figure([go.Bar(x=x, y=y)])
    fig.update_layout(title_text=buurt[0], template="simple_white") #
    return fig

# bar_chart_maps(buurt,selectie).show()

# FA = "https://use.fontawesome.com/releases/v5.15.1/css/all.css"
# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CYBORG, FA], suppress_callback_exceptions=True)#,prevent_initial_callbacks=True

migratieachtergrond = ['Westers', 'Niet-westers', 'Marokko', 'Nederlandse Antillen en Aruba ', 'Suriname',
                       'Turkije', 'Overig']
huishoudens = ['Huishoudens', 'Eenpersoonshuishoudens', 'Zonder kinderen', 'Met kinderen']
uitkering = ['Bijstand ', 'AO', 'WW', 'AOW']
flyers_inw = ['Aantal Flyers', 'Aantal inwoners', 'Huishoudens']

radioitems_onderwerp = dbc.FormGroup([
        dbc.Label("Onderwerp:"),
        dbc.RadioItems(
            options=[{'label': 'Migratieachtergrond', 'value': migratieachtergrond},
                     {'label': 'Huishoudens', 'value': huishoudens},
                    {'label': 'Uitkering', 'value': uitkering},
                    {'label': 'Flyers nodig', 'value': flyers_inw}],
            value=flyers_inw,
            id="onderwerp-input-graph",
            inline=True
        ),
    ])

layout = html.Div([

    html.P('Waar kun je flyers krijgen? Zie https://bij1.org/campagnemateriaal/', style={'text-align': 'center'}),

    html.Br(),

    # html.Div([
    #         html.Pre(id='hover-data')#, style=styles['pre']
    #     ], className='three columns'),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='flyer-plot' ,figure=flyers_amsterdam_map(df_amsterdam_google_sheet)
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

@app.callback(
    Output('hover-data', 'children'),
    [Input('flyer-plot', 'hoverData')])
def callback_image(hoverData):
    return json.dumps(hoverData, indent=2)

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