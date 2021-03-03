from app import app
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_daq as daq


url = 'https://raw.githubusercontent.com/SimonTeg/multiple_regressions/main/MMM_data.csv'
df = pd.read_csv(url, error_bad_lines=False)
df_corr = df.corr()

variable_names = list(df.columns)

var_options = []
for var in list(df.columns):
    var_options.append({'label': str(var), 'value': var})

def line_graph_2axis(list1,list2,df,date):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    for var in list1:
        fig.add_trace(
            go.Scatter(x=date, y=df[var], name=var),
            secondary_y=False,
        )

    for var in list2:
        fig.add_trace(
            go.Scatter(x=date, y=df[var], name='sec_y '+var),
        secondary_y=True,
        )

    # Add figure title
    fig.update_layout(
        title_text="Visualize 2 variables",template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)'
    )

    # Set x-axis title
    fig.update_xaxes(title_text="date")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis ", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis ", secondary_y=True)
    return fig

def corr_heat_graph(variables_list,df):
    df_correlations = df[variables_list].corr()
    fig = px.imshow(df_correlations, labels=dict(x='Correlations between variables', y="Variables selected", color="Correlation"))
    fig.update_xaxes(side="top")
    fig.update_layout(template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)'
    )
    return fig

markers_dict = {i:df.date[i] for i in range(0,len(df.date))}

def bar_chart_selected(begin1,end1,begin2,end2,vars,df,sum_mean):
    '''
    Function to make a bar chart based on 2 selected time periode.
    :param begin1:
    :param end1: location end 1 in df
    :param begin2:
    :param end2:
    :param vars: the vars you want in the graph
    :param df: the df that contains all
    :return: a figure
    '''
    x = ['From: ' + markers_dict[begin1]+' till '+markers_dict[end1-1],'From: ' + markers_dict[begin2]+' till '+markers_dict[end2-1]]#['From: 1-7-2019 - 1-21-2019', 'From: 1-28-2019 - 2-4-2019']
    fig = go.Figure()
    for var in vars:
        if sum_mean == 'Mean':
            y = [df.iloc[begin1:(end1 + 1), ][var].mean(), df.iloc[begin2:(end2 + 1), ][var].mean()]
        else:
            y = [df.iloc[begin1:(end1 + 1), ][var].sum(), df.iloc[begin2:(end2 + 1), ][var].sum()]

        fig.add_trace(go.Bar(
            name=var,
            x=x,
            y=y
        ))
    fig.update_layout(barmode='group',template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)')
    fig.update_layout(title_text= sum_mean + ' over selected time period')

    return fig

def get_nth_marks(dates, Nth=5):
    ''' Returns the marks for labeling.
        Every Nth value will be used.
    '''

    result = {}
    for i in range(0,len(dates)):
        if(i%Nth == 1):
            # Append value to dict
            result[i] = df.date[i]

    return result

colors = {
    'background': '#111111',
    'text': '#FFFFFF',
    'button':'#FFFF00'
}

layout = html.Div([
    dbc.Card(
        dbc.CardBody([

            dbc.Row([
                dbc.Col([html.Div()
                ], width=3)
            ], align='center'),
            html.Br(),
#2axis GRAPH
            dbc.Row([
                dbc.Col([
                    html.Div(
                        [
                            dbc.Button(
                                "Explain",
                                id="collapse-button",
                                className="mb-3",
                                color="primary",

                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody(
                                    html.Div("For this graph you can select variables you want to explain. "
                                             "The first box if for variables you want on the Y1 axis, "
                                             "the second box is for the variables you want on the Y2 axis",
                                             style={'color': colors['text']}))),
                                id="collapse1",
                            ),
                        ], className="dash-bootstrap"
                    ),
                    html.Div(
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Dropdown(
                                            id='yaxis_1',
                                            options=var_options,
                                            value=[variable_names[1]],
                                            multi=True
                                        )
                            ]), className="dash-bootstrap"
                        ), className="dash-bootstrap"
                    ),
                    html.Br(),
                    html.Div(
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Dropdown(
                                            id='yaxis_2',
                                            options=var_options,
                                            value=[variable_names[3]],
                                            multi=True
                                        )
                            ]), className="dash-bootstrap"
                        ), className="dash-bootstrap"
                    ),
                ],  width={'size': 2}),

                dbc.Col([
                    html.Div(
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Graph(id='grafiek')
                            ], className="dash-bootstrap")
                        ), className="dash-bootstrap"
                    ),

                ], width={'size': 8})
            ], align='center'),

            html.Br(),
            html.Br(),
            html.Br(),
#Correlation GRAPH
            dbc.Row([

                dbc.Col([
                    html.Div(
                        [
                            dbc.Button(
                                "Explain",
                                id="collapse-button2",
                                className="mb-3",
                                color="primary",
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody(
                                    html.Div("For this graph you can decide between what variables you want to "
                                             "see the correlation. "
                                             "The colors represent how strongly they are correlated, the scale can "
                                             "change with new. "
                                             "variables. Hover over de graph to see the correlation value"
                                             ,
                                             style={'color': colors['text']}))),
                                id="collapse2",
                            ),
                        ]
                    ),

                    html.Div(
                        dbc.Card(
                            dbc.CardBody([
                                    dcc.Dropdown(
                                        id='corr_options',
                                        options=var_options,
                                        value=list(df.columns[1:4]),
                                        multi=True
                                        )
                            ]), className="dash-bootstrap"
                        ), className="dash-bootstrap"
                    )

                ], width=2),

                dbc.Col([
                    html.Div(
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Graph(id='correlaties',style={'height': '80vh'})
                            ], className="dash-bootstrap")
                        ), className="dash-bootstrap"
                    ),
                ], width=8)
            ], align='center'),

#Time GRAPH
            html.Br(),
            html.Br(),
            html.Br(),

            dbc.Row([
                dbc.Col([
                    html.Div(
                        [
                            dbc.Button(
                                "Explain",
                                id="collapse-button3",
                                className="mb-3",
                                color="primary",
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody(
                                    html.Div("This graph shows you two bar graphs for selected time frames (below). "
                                             "In the box can you select the variables you want to be shown. "
                                             "The switch button can be used to show the mean or the sum over the "
                                             "selected variables in the pariod of time "
                                             ,
                                             style={'color': colors['text']}))),
                                id="collapse3",
                            ),
                        ]
                    ),
                    html.Div(
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Dropdown(
                                    id='variable_selection',
                                    options=var_options,
                                    value=[variable_names[1], variable_names[2]],
                                    multi=True
                                )
                            ]), className="dash-bootstrap"
                        ), className="dash-bootstrap"
                    ),
                    html.Br(),
                    html.Div(
                        daq.BooleanSwitch(
                            id='switch_mean_sum',
                            on=True,
                            labelPosition="top",
                            color = '#FFFF00'
                        )
                    ),
                    html.Div(id='boolean-switch-output',
                                        style={'color': colors['text'],'textAlign': 'center'
                                        }),


                ], width=2),

                dbc.Col([
                    html.Div(
                        dbc.Card(
                            dbc.CardBody([
                                dcc.Graph(id='bar_chart')
                            ], className="dash-bootstrap")
                        ), className="dash-bootstrap"
                    ),
                ], width=8)
            ], align='center'),

            html.Br(),
            html.Br(),

            dbc.Row([
                dbc.Col([
                    html.Div(
                        dbc.Card(
                            dbc.CardBody([

                                html.H6('Select the range for the 1st period:',
                                        style={'color': colors['text']
                                        }),

                                html.Div([
                                    dcc.RangeSlider(
                                        id='date_slider',
                                        min=0,
                                        max=len(df.date),
                                        value=[0, len(df)],
                                        marks=get_nth_marks(df.date, Nth=10)
                                    )
                                ], className="dash-bootstrap"),
                                html.Br(),
                                html.Br(),
                                html.H6('Select the range for the 2e period:',
                                        style={'color': colors['text']
                                        }),
                                html.Div([
                                    dcc.RangeSlider(
                                        id='date_slider_2',
                                        min=0,
                                        max=len(df.date),
                                        value=[5, len(df)],
                                        marks=get_nth_marks(df.date, Nth=10)
                                    )
                                ])


                            ]), className="dash-bootstrap"
                        ), className="dash-bootstrap"
                    )





                         ], width={"size":8, "offset": 2})
            ])#, align='center'


        ])
    )
])

@app.callback(
    Output(component_id='grafiek', component_property='figure'),
    [Input(component_id='yaxis_1', component_property='value'),
     Input(component_id='yaxis_2', component_property='value')]
)
def graph_update(input_var1, input_var2):
    fig = line_graph_2axis(input_var1, input_var2, df, df.date)
    return fig

@app.callback(
    Output(component_id='correlaties', component_property='figure'),
    [Input(component_id='corr_options', component_property='value')]
)
def graph_update_correlations(input_var):
    fig = corr_heat_graph(input_var,df)
    return fig

@app.callback(
    dash.dependencies.Output('boolean-switch-output', 'children'),
    [dash.dependencies.Input('switch_mean_sum', 'on')])
def update_output(on):
    if on:
        pick = "Mean"
    else:
        pick = "Sum"
    return '{}'.format(pick)


@app.callback(
    Output(component_id='bar_chart',component_property='figure'),
    [Input(component_id='variable_selection',component_property='value'),
    Input(component_id='date_slider',component_property='value'),
    Input(component_id='date_slider_2',component_property='value'),
    Input('switch_mean_sum', 'on')]
)
def bar_chart(input_vars,values,values_2,sum_mean_value):
    begin1 = values[0]
    end1 = values[1]
    begin2 = values_2[0]
    end2 = values_2[1]
    sum_mean = sum_mean_value
    if sum_mean_value:
        sum_mean = "Mean"
    else:
        sum_mean = "Sum"
    return bar_chart_selected(begin1,end1,begin2,end2,input_vars,df,sum_mean)

@app.callback(
    Output("collapse1", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse1", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse2", "is_open"),
    [Input("collapse-button2", "n_clicks")],
    [State("collapse2", "is_open")],
)
def toggle_collapse2(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse3", "is_open"),
    [Input("collapse-button3", "n_clicks")],
    [State("collapse3", "is_open")],
)
def toggle_collapse3(n, is_open):
    if n:
        return not is_open
    return is_open