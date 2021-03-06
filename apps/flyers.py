
import numpy as np
import dash_core_components as dcc
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash_html_components as html
from app import app

# ssl._create_default_https_context = ssl._create_unverified_context
token = "pk.eyJ1IjoiaHVtYW5pbmciLCJhIjoiY2tpcHJiN3BlMDBjaDJ1b2J6ODQ4dzNlcyJ9.55HzvciQ31i0_ODARa9rLQ"

df_amsterdam = pd.read_csv("data/GEBIED_BUURTEN_2.csv", delimiter =';', decimal =',', encoding ='utf-8')
df_amsterdam["Flyers"] = np.where(df_amsterdam.Opp_m2 == 1, 'Gedaan', np.where(df_amsterdam.Opp_m2 == 2, 'Moet nog', 'Deels Gedaan'))

def flyers_amsterdam_map(df):
    fig = px.choropleth_mapbox(df,
        geojson='https://maps.amsterdam.nl/open_geodata/geojson.php?KAARTLAAG=GEBIED_BUURTEN&THEMA=gebiedsindeling',
        color="Flyers",
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
                dcc.Graph(id='flyer-plot' ,figure=flyers_amsterdam_map(df_amsterdam)
                          )])
        ], width={"size": 8, "offset": 2})
    ])
])

# app.layout = layout

# if __name__ == '__main__':
#     app.run_server(debug=True)