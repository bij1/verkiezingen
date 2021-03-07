import numpy as np
import dash_core_components as dcc
import plotly.express as px
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

# df_amsterdam = pd.read_csv("data/GEBIED_BUURTEN_2.csv", delimiter =';', decimal =',', encoding ='utf-8')
# df_amsterdam["Flyers"] = np.where(df_amsterdam.Opp_m2 == 1, 'Gedaan', np.where(df_amsterdam.Opp_m2 == 2, 'Moet nog', 'Deels Gedaan'))

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

# FA = "https://use.fontawesome.com/releases/v5.15.1/css/all.css"
# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CYBORG, FA], suppress_callback_exceptions=True)#,prevent_initial_callbacks=True
token = "pk.eyJ1IjoiaHVtYW5pbmciLCJhIjoiY2tpcHJiN3BlMDBjaDJ1b2J6ODQ4dzNlcyJ9.55HzvciQ31i0_ODARa9rLQ"

layout = html.Div([

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='flyer-plot' ,figure=flyers_amsterdam_map(df_amsterdam_google_sheet)
                          )])
        ], width={"size": 8, "offset": 2})
    ])
])

# app.layout = layout

# if __name__ == '__main__':
#     app.run_server(debug=True)