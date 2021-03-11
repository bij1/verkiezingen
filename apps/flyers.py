from dash.dependencies import Input, Output
import numpy as np
import json
import dash_core_components as dcc
import dash_table
import plotly.express as px
import plotly.graph_objs as go

import pandas as pd
import geopandas
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

# geo_path = 'https://maps.amsterdam.nl/open_geodata/geojson.php?KAARTLAAG=GEBIED_BUURTEN&THEMA=gebiedsindeling'
geo_path = './data/amsterdam.geojson'
gdf = geopandas.GeoDataFrame.from_file(geo_path)
gdf['center'] = gdf.centroid

# ssl._create_default_https_context = ssl._create_unverified_context
token = "pk.eyJ1IjoiaHVtYW5pbmciLCJhIjoiY2tpcHJiN3BlMDBjaDJ1b2J6ODQ4dzNlcyJ9.55HzvciQ31i0_ODARa9rLQ"

# geojson = 'https://maps.amsterdam.nl/open_geodata/geojson.php?KAARTLAAG=GEBIED_BUURTEN&THEMA=gebiedsindeling',
# geo_file = './data/amsterdam.geojson'
# # geo_file = './data/nl.geojson'
# with open(geo_file) as fp:
#     geojson = json.load(fp)


def flyers_amsterdam_map(df):
    fig = px.choropleth_mapbox(df,
        geojson='https://maps.amsterdam.nl/open_geodata/geojson.php?KAARTLAAG=GEBIED_BUURTEN&THEMA=gebiedsindeling',
        # geojson=geojson,
        color= 'Geflyerd', #"Flyers",
        locations="Buurt", featureidkey="properties.Buurt",
        opacity = 0.4, zoom=10,  center={"lat": 52.37220844333981, "lon": 4.89968264189926})
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_accesstoken=token)
    return fig

df_amsterdam_buurten = pd.read_csv("data/buurten_data_cbs_amsterdam_v1.csv", delimiter=',', decimal='.',
                                   encoding='utf-8', dtype={
                                       'Bijstand ': np.float64,
                                       'AO':        np.float64,
                                       'WW':        np.float64,
                                       'AOW':       np.float64,
                                       })

migratieachtergrond = ['Westers', 'Niet-westers', 'Marokko', 'Nederlandse Antillen en Aruba ', 'Suriname',
                       'Turkije', 'Overig']
huishoudens = ['Huishoudens', 'Eenpersoonshuishoudens', 'Zonder kinderen', 'Met kinderen']
uitkering = ['Bijstand ', 'AO', 'WW', 'AOW']
flyers_inw = ['Aantal inwoners', 'Aantal Flyers']
x = ['Potentie', 'Huidig']
# buurt = ['Westelijke eilanden']

selectie = huishoudens
# df_amsterdam_buurten.loc[df_amsterdam_buurten['Buurt'] == buurt[0]][selectie]

def percent(x, digits=2):
    return round(x * 100, digits)

table_df = gdf[['Buurt', 'geometry', 'center']].merge(
    df_amsterdam_buurten,
    how='inner',
    on='Buurt',
).merge(
    df_amsterdam_google_sheet[df_amsterdam_google_sheet['Geflyerd'] != 'Gedaan'].drop(columns=['Aantal Flyers']),
    how='left',
    on='Buurt')
table_df['Niet-westers (%)'] = table_df.apply(lambda x: percent(x['Niet-westers'] / x['Aantal inwoners']) if x['Aantal inwoners'] else 0, axis=1)
table_df['Mensen/huishouden'] = table_df.apply(lambda x: round(x['Aantal inwoners'] / x['Huishoudens'], 2) if x['Huishoudens'] else 0, axis=1)
table_df['Uitkering (%)'] = table_df.apply(lambda x: percent((x['Bijstand '] + x['AO'] + x['WW'] + x['AOW']) / x['Aantal inwoners']) if x['Aantal inwoners'] else 0, axis=1)
first_point = table_df['center'].iloc[0]
table_df['distance'] = round(table_df['center'].distance(first_point), 3)
# table_df['Score'] = table_df.apply(lambda x: round(x['Niet-westers (%)'] + x['Uitkering (%)'], 2) if x['Geflyerd'] != 'Gedaan' else 0, axis=1)
# table_df['Score'] = table_df['distance']
# table_df = table_df.sort_values(by='Score', ascending=False)
table_df = table_df.sort_values(by='distance', ascending=True)
table_df = table_df[['Buurt', 'Huishoudens', 'Mensen/huishouden', 'Niet-westers (%)', 'Uitkering (%)', 'Geflyerd', 'distance', 'center', 'geometry']] # , 'Score'
table_df_ = table_df.drop(columns=['center', 'geometry'])

def discrete_background_color_bins(df, columns, n_bins=5):
    import colorlover
    df_numeric_columns = df[columns]
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins)]['seq']['YlGn'][i - 1]
        color = 'white' if i > len(bounds) / 2. else 'black'
        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'column_id': column,
                    'filter_query': f'{{{column}}} >= {min_bound} && {{{column}}} < {max_bound}',
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
    return styles

styles = discrete_background_color_bins(table_df, columns=['Niet-westers (%)', 'Uitkering (%)']) + \
        [{'if':{'column_id': col, 'filter_query': f'{{{col}}} = "Gedaan"'}, 'backgroundColor': 'red'} for col in ['Geflyerd']]
# TODO: cities

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

    html.P(['Waar kun je flyers krijgen? Zie ', html.A('hier', href='https://bij1.org/campagnemateriaal/'), '!'], id='link', style={'textAlign': 'center'}),

    html.P(['Wil je doorgeven dat je ergens gaat flyeren? Zie ', html.A('hier', href='https://docs.google.com/spreadsheets/d/1_xU8TGUOc0WJVdW0V6Z5cHs7yWsO3FoX7rya9wy9G7Q'), '!'], id='link', style={'textAlign': 'center'}),

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
    # legend,
    html.Div(id='table-container'),
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
    ]),
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


@app.callback(
    Output('table-container', 'children'),
    [Input('flyer-plot', 'hoverData')])
def callback_distance(hoverData):
    try:
        buurt_hover = hoverData['points'][0]["location"]
    except:
        buurt_hover = 'Westelijke eilanden'
    current_idx = table_df['Buurt'] == buurt_hover
    current_point = table_df.loc[current_idx].iloc[0]['center']
    table_df['distance'] = round(table_df['center'].distance(current_point), 3)
    table_df_ = table_df.drop(columns=['geometry', 'center']).sort_values(by='distance', ascending=True).rename(columns={'distance': f'distance from {buurt_hover}'})
    styles = discrete_background_color_bins(table_df_, columns=['Niet-westers (%)', 'Uitkering (%)'])
    return [
        dash_table.DataTable(
            id='table',
            columns=[{"name": k, "id": k} for k in table_df_.columns],
            data=table_df_.to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
            page_action="native",
            page_current=0,
            page_size=25,
            # row_selectable='multi',
            filter_action="native",
            sort_action="native",
            sort_mode='multi',
            style_data_conditional=styles,
        )
    ]

# app.layout = layout

# if __name__ == '__main__':
#     app.run_server(debug=True)