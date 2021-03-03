import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import json
import dash_bootstrap_components as dbc
import dash_daq as daq


import dash
from app import app
# FA = "https://use.fontawesome.com/releases/v5.15.1/css/all.css"
# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CYBORG, FA], suppress_callback_exceptions=True)

#data
# url_weekly = 'https://raw.githubusercontent.com/SimonTeg/multiple_regressions/main/weekly_donations_3.csv'
# df_weekly = pd.read_csv(url_weekly, error_bad_lines=False)
df_weekly = pd.read_csv("data/weekly_donations_3.csv", delimiter =',', decimal ='.', encoding ='utf-8',na_values=['#DIV/0!'])
df_weekly_cumulatief = df_weekly[['Bedrag','Aantal_donaties','Eerste donatie','Tweede donatie','Derde donatie','Terugkerende donatie']].cumsum()
df_weekly_cumulatief['Datum'] = df_weekly['Datum']

# url_daily = 'https://raw.githubusercontent.com/SimonTeg/multiple_regressions/main/daily_donations.csv'
# df_daily = pd.read_csv(url_daily, error_bad_lines=False)

var_opties = [{'label': 'Bedrag', 'value': 'Bedrag'}, {'label': 'Aantal_donaties', 'value': 'Aantal_donaties'}, {'label': 'Eerste donatie', 'value': 'Eerste donatie'}, {'label': 'Tweede donatie', 'value': 'Tweede donatie'}, {'label': 'Derde donatie', 'value': 'Derde donatie'}, {'label': 'Terugkerende donatie', 'value': 'Terugkerende donatie'}, {'label': 'Racisme search', 'value': 'Racisme search'}, {'label': 'Anti racism search', 'value': 'Anti racism search'}, {'label': 'BIJ1 search', 'value': 'BIJ1 search'}, {'label': 'KOZP search', 'value': 'KOZP search'}, {'label': 'Mailing', 'value': 'Mailing'}]

var_options = []
for var in list(df_weekly.columns):
    var_options.append({'label': str(var), 'value': var})

def bar_graph(var_list,df,datum):
    # Create figure with secondary y-axis
    fig = go.Figure()
    for var in var_list:
        fig.add_trace(go.Bar(x=df[datum], y=df[var], name=var))

    # fig.update_layout(title_text="Donaties",
    #                   xaxis_rangeslider_visible=True, template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)')
    fig.update_layout(barmode='relative', title_text='Donaties', bargap=0, template='plotly_dark',
                      plot_bgcolor='rgba(0, 0, 0, 0)')
    return fig

def line_graph(var_list,df,datum):
    # Create figure with secondary y-axis
    fig = go.Figure()
    for var in var_list:
        fig.add_trace(go.Scatter(x=df[datum], y=df[var], name=var))

    # fig.update_layout(title_text="Donaties",
    #                   xaxis_rangeslider_visible=True, template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)')
    fig.update_layout(barmode='relative', title_text='Donaties', bargap=0, template='plotly_dark',
                      plot_bgcolor='rgba(0, 0, 0, 0)')
    return fig


var_list = ['Eerste donatie','Terugkerende donatie','Derde donatie']
df=df_weekly
datum = 'Datum'
line_graph(var_list,df,datum)



layout = html.Div([
    html.Br(),
    html.Br(),
#bars
    dbc.Row([
        dbc.Col([
            html.Div(
                dbc.Card(
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='graph_options',
                            options=var_options,
                            value=['Eerste donatie','Terugkerende donatie','Derde donatie'],
                            multi=True
                        )
                    ]), className="dash-bootstrap"
                ), className="dash-bootstrap"
            ),
            dcc.Graph(id='donaties-graph'),
            html.Div(
                daq.BooleanSwitch(
                    id='switch_mean_sum',
                    on=True,
                    labelPosition="top",
                    color = '#FFFF00'
                )
            ),
            html.Div(id='boolean-switch-output',
                                        style={'textAlign': 'center' #'color': colors['text'],
                                        })
        ], width={"size": 8, "offset": 2})
    ]),
    html.Br(),
    html.Br(),
#lines
    dbc.Row([
        dbc.Col([
            html.Div(
                dbc.Card(
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='graph_options_2',
                            options=var_options,
                            value=['Racisme search','Anti racism search','KOZP search'],
                            multi=True
                        )
                    ]), className="dash-bootstrap"
                ), className="dash-bootstrap"
            ),

            # html.Div([
                dcc.Graph(id='line-graph')
            # ])
        ], width={"size": 8, "offset": 2})
    ])
])
# app.layout = layout

@app.callback(
    Output(component_id='donaties-graph', component_property='figure'),
    [Input(component_id='graph_options', component_property='value')]
)
def graph_update(input_vars):
    fig = bar_graph(input_vars,df,datum)
    return fig

@app.callback(
    Output(component_id='line-graph', component_property='figure'),
    [Input(component_id='graph_options_2', component_property='value')]
)
def graph_update(input_vars):
    fig = line_graph(input_vars,df,datum)
    return fig
# if __name__ == '__main__':
#     app.run_server(debug=True)


