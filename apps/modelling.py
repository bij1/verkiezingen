import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
import statsmodels.formula.api as smf
import numpy as np
from app import app
import dash
import plotly.io as pio


'''De data'''
url = 'https://raw.githubusercontent.com/SimonTeg/multiple_regressions/main/MMM_data.csv'
df = pd.read_csv(url, error_bad_lines=False)

variable_names = list(df.columns)
var_options = []
for var in list(df.columns):
    var_options.append({'label': str(var), 'value': var})

'''Functies'''
def decay(var,labda_):
    decayVariable = []
    decayVariable.append(var.values[0])
    for i in range(1,len(var)):
        decayVariable.append(var.values[i] + labda_*decayVariable[i-1])
    return pd.Series(data = decayVariable, dtype=float)

def decay_names_media(media,df):
    '''returns a list with media names and their decays'''
    try:
        df_totaal = pd.DataFrame()
        media_variables = media
        for media_var in media_variables:
            for decay_value in [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]:
                dec_var = media_var+'__'+str(decay_value).replace('.', '_')
                dec_values = decay(df[media_var],decay_value)
                df_totaal[dec_var] = dec_values
        return df_totaal.set_index(df.index)
    except:
        return []

def df_media(media,df):
    '''creates a pandas df with selected media_vars and their decays'''
    df_totaal = pd.DataFrame()
    media_variables = media
    for media_var in media_variables:
        for decay_value in [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]:
            dec_var = media_var+'__'+str(decay_value).replace('.', '_')
            dec_values = decay(df[media_var],decay_value)
            df_totaal[dec_var] = dec_values
    return df_totaal.set_index(df.index)

def s_curve(var,alpha_):
    s_curve_values = alpha_*(var/max(var))*(1-np.exp(-alpha_*(var/max(var)))) / (1 + alpha_*(var/max(var)))
    return s_curve_values

def formule(y, X):
    '''Returns a formula for OLS model'''
    f = y[0] + ' ~ '
    f += " + ".join(X)
    return f

def formule1(y, X, s_vars, s_values):
    if len(y)>0:
        s_values_str = [str(i) for i in s_values]
        f = y[0] + ' ~ '
        if len(X)>0:
            f += " + ".join(X)
        for s_var, value in zip(s_vars, s_values_str):
            if len(X) > 0:
                f += " + " + "s_curve(" + s_var + "," + value + ")"
            else:
                f += "s_curve(" + s_var + "," + value + ")"
        return f
    return 'sales ~ 1'

'''Fit vs actual'''
def actual_vs_fit_graph(var_date, df, formula, color_kpi='deepskyblue', color_fit='dimgray',
                        title_graph='Actual vs model'):
    '''

    This function has as output a graph of 2 lines, the actual kpi values
    and the fitted values from the model

    Input variables

        -var_date:  [df.date]
           this variable contains the dates you want to show in the graph

        -model: model
            The model that you want to use

        -color_kpi: 'red'
            here you can give a color to the kpi like 'yellow' or 'grey'...
            as default it is put on deepskyblue'
        -color_fit: 'red'
            here you can give a color to the fit like 'yellow' or 'grey'...
            as default it is put on dimgray'
            :param title_graph:
    '''
    # formula = formule(y, X)
    model = smf.ols(formula=formula, data=df)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=var_date, y=model.endog, name=model.endog_names,
                             line_color=color_kpi))

    fig.add_trace(go.Scatter(x=var_date, y=model.fit().fittedvalues,
                             name=model.endog_names + "_fitted",
                             line_color=color_fit))

    fig.update_layout(title_text=title_graph,
                      xaxis_rangeslider_visible=True, template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)')
    return fig

def x_beta_fitted_actual(model):
    beta = model.fit().params
    X = pd.DataFrame(model.exog, columns=beta.index)
    x_beta = X * 0
    model_fit = model.fit()
    for i in range(len(X)):
        for j in range(len(model_fit.params)):
            x_beta.iloc[i, j] = model.exog[i, j] * model_fit.params[j]
            # negatieve waardes van intercept halen
    sum_negatives = []
    for i in range(x_beta.shape[0]):
        negative_value = 0
        for j in range(x_beta.shape[1]):
            if x_beta.iloc[i, j] < 0:
                negative_value += x_beta.iloc[i, j]
        sum_negatives.append(negative_value)
    sum_negatives_pd = pd.DataFrame(sum_negatives)
    x_beta_intercept_correctie = x_beta.copy()
    x_beta_intercept_correctie.Intercept = x_beta_intercept_correctie.Intercept + sum_negatives_pd

    return x_beta, x_beta_intercept_correctie

def decomposition_graph(var_date, df, formula, color_kpi='deepskyblue'):
    '''
        This function has as output a bar plot with all the variables and
        the actual y used

        Input variables

            -model: model
                The model that you want to use
        '''
    # formula = formule(y, X)
    model = smf.ols(formula=formula, data=df)

    data_decomp = x_beta_fitted_actual(model)[1]

    x = var_date
    variabelen = data_decomp
    names = list(data_decomp)
    y_model = model.fit().fittedvalues

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y_model, name='y_model'))

    fig.add_trace(go.Scatter(x=var_date, y=model.endog, name=model.endog_names,
                             line_color=color_kpi))

    for i in range(0, variabelen.shape[1]):
        fig.add_trace(go.Bar(x=x, y=variabelen[names[i]], name=names[i]))

    fig.update_layout(barmode='relative', title_text='Decompositie', bargap=0, template='plotly_dark',
                      plot_bgcolor='rgba(0, 0, 0, 0)')
    return fig

def model_characteristics(formula, df):
    '''functie de DW, JB teruggeeft
    Input: een res.summary() van een ols model
    Output: AdjR2, DW, JB  '''
    # formula = formule(y, X)
    model = smf.ols(formula=formula, data=df)

    results = model.fit()
    R2 = round(results.rsquared, 3)
    AdjR2 = round(results.rsquared_adj, 3)
    results_summary = results.summary()
    results_as_html2 = results_summary.tables[2].as_html()
    dwjb = pd.read_html(results_as_html2, index_col=0)[0]
    DW = round(dwjb.iloc[0, 2], 3)
    JB = round(dwjb.iloc[2, 2], 3)
    return {"Metric:": ['R Squared', 'Adj RSquared', 'Durbin Watson', ' Jarque-Bera'], 'Values': [R2, AdjR2, DW, JB]}

def plot_curves(media_var, alphas_scurve,df):
    # pio.renderers.default = 'browser'
    max_value = max(df[media_var].max())
    x = np.arange(max_value + 0.1 * max_value)

    fig = go.Figure()

    for i in range(0,len(alphas_scurve)):
        fig.add_trace(go.Scatter(x=x, y=s_curve(x, alphas_scurve[i]),
                             name='s_curve' + ' alpha = ' + str(alphas_scurve[i])))



        # to plot virtical lines min/mean/max
        l = [i for i in list(df[media_var[i]].array) if i > 0]  # remove all 0 values
        min_ = min(l)
        max_ = max(l)
        mean_ = sum(l) / len(l)

        fig.add_shape(
            # Line Vertical min
            dict(
                type="line",
                x0=min_,
                y0=0,
                x1=min_,
                y1=1,
                line=dict(
                    color="RoyalBlue",
                    width=4,
                    dash="dot",
                )
            ))
        fig.add_shape(
            # Line Vertical mean
            dict(
                type="line",
                x0=mean_,
                y0=0,
                x1=mean_,
                y1=1,
                line=dict(
                    color="Red",
                    width=4,
                    dash="dot",
                )
            ))
        fig.add_shape(
            # Line Vertical min
            dict(
                type="line",
                x0=max_,
                y0=0,
                x1=max_,
                y1=1,
                line=dict(
                    color="Orange",
                    width=4,
                    dash="dot",
                )
            ))
        # Create scatter trace of text labels
        fig.add_trace(go.Scatter(
            x=[min_, mean_, max_],
            y=[1.01, 1.01, 1.01],
            text=["Min GRPs " + media_var[i],
                  "Average GRPs "+ media_var[i],
                  "Max GRPs "+ media_var[i]],
            mode="text",
            name="Inzet values",
        ))


    fig.update_layout(title='Response Curves in the model',
                      xaxis_title='GRPs',
                      yaxis_title='Impact (will be multiplied with your estimated beta)',template='plotly_dark',
                      plot_bgcolor='rgba(0, 0, 0, 0)')

    return fig

colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}

title_formula = html.Div(id='title', className="dash-bootstrap")

variable_selection = html.Div(children=[html.H6("Y variable to be explained:", style={'color': 'white'}),
                                        dcc.Dropdown(
                                            id='y',
                                            options=var_options,
                                            value=[variable_names[1]],
                                            multi=True
                                        ),
                                        html.H6("X variables for the model:", style={'color': 'white'}),
                                        html.Div(id = 'returning'),
                                        dcc.Dropdown(
                                            id='X',
                                            # options=var_options,
                                            value=[variable_names[9],variable_names[6]],
                                            multi=True
                                        ),
                                        html.Br(),
                                        html.H6("Create decay variables:", style={'color': 'white'}),
                                        dcc.Dropdown(
                                            id='decay-var',
                                            options=var_options,
                                            value=[],
                                            multi=True
                                        ),
                                        html.H6("Response curve variables:", style={'color': 'white'}),
                                        dcc.Dropdown(
                                            id='response-curve',
                                            options=var_options,
                                            value=['tv'],
                                            multi=True
                                        ),
                                        html.Br(),
                                        html.Div(id='title-response-cuves'),
                                        html.Div(id='amount-of-picks'),
                                        html.Div(id='formula-used')

                                        ], className="dash-bootstrap")

grafiek_fit_vs_actual = html.Div(children=[dcc.Graph(id='graph-fit-vs-actual')])

grafiek_decomposition = html.Div(children=[dcc.Graph(id='graph-decomposition')])

grafiek_curves = html.Div(children=[dcc.Graph(id='graph-curves')])

explain_button = html.Div([
    dbc.Button(
        "Explain",
        id="collapse-button",
        className="mb-3",
        color="primary",
    ),
    dbc.Collapse(
        dbc.Card(dbc.CardBody(
            html.Div("For these graphs you can select variables you want to explain by other variables. "
                     "The first box if for variables you want to explain (Y). "
                     "The second box is for the variables (X) you want to use to explain Y. ",
                     style={'color': colors['text']}))),
        id="collapse",
    ),
], className="dash-bootstrap")

explain_button_decay = html.Div([
    dbc.Button(
        "Explain",
        id="collapse-button-decay",
        className="mb-3",
        color="primary",
    ),
    dbc.Collapse(
        dbc.Card(dbc.CardBody(
            html.Div("The variables you pick in the above box will be added to the data frame as transformed variables "
                     "with decays from 10% till 90%. After chosing them here, they will appear in the box with X "
                     "variables. If you pick "
                     "tv for example, tv__0_1, ..., tv__0_9 will appear and means a decay of 10%,...,90% (10%,...,"
                     "90% will remain after 1 week)",
                     style={'color': colors['text']}))),
        id="collapse-decay",
    ),
], className="dash-bootstrap")

explain_button_metrics = html.Div([
    dbc.Button(
        "Explain",
        id="collapse-button-metrics",
        className="mb-3",
        color="primary",
    ),
    dbc.Collapse(
        dbc.Card(dbc.CardBody(
            html.Div("RSquared is a value between 0-1 and represents the fit (1 is perfect fit). "
                     "Adj RSquared is the RSquared adjusted for extra variables. "
                     "Durbin Watson is a test statistic used to detect the presence of autocorrelation at lag 1 "
                     "in the residuals. We usually want this to be close too 2. "
                     "Jarque–Bera test is a goodness-of-fit test of whether sample data have the skewness and "
                     "kurtosis matching a normal distribution. We want this value to be bigger than 0.05",
                     style={'color': colors['text']}))),
        id="collapse-metrics",
    ),
], className="dash-bootstrap")

explain_button_response_curves = html.Div([
    dbc.Button(
        "Explain",
        id="collapse-button-response-curves",
        className="mb-3",
        color="primary",
    ),
    dbc.Collapse(
        dbc.Card(dbc.CardBody(
            html.Div("Here are the curves shown that are used in your model"
                     "It also shows the min, average and maximum values of your variables for the response curves "
                     "this way you get a feeling of what you are actually testing",
                     style={'color': colors['text']}))),
        id="collapse-response-curves",
    ),
], className="dash-bootstrap")

table = html.Div(id='table')

layout = html.Div([
    dbc.Card(
        dbc.CardBody([

            dbc.Row([
                dbc.Col([explain_button, variable_selection,explain_button_decay], width={"size": 2, "offset": 1}),
                dbc.Col([grafiek_fit_vs_actual], width=8)
            ], align='center'),

            html.Br(),
            html.Br(),

            dbc.Row([
                dbc.Col([explain_button_metrics, table], width={"size": 2, "offset": 1}),
                dbc.Col([grafiek_decomposition], width=8)
                # dbc.Col([table],width=3)
            ], align='center'),

            html.Br(),

            dbc.Row([
                dbc.Col([title_formula], width={"size": 8, "offset": 3})
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([explain_button_response_curves], width={"size": 2, "offset": 1}),
                dbc.Col([grafiek_curves], width=8)
            ], align='center')


        ]), className="dash-bootstrap"
    )
], className="dash-bootstrap")

@app.callback(
    Output(component_id='response-curve', component_property='options'),
    [Input(component_id='decay-var', component_property='value')]
)
def create_decay_options_rc(decay_selection):
    if len(decay_names_media(decay_selection, df)) > 0:
        new_vars = list(decay_names_media(decay_selection, df).columns)
        decay_selection_options = []
        for var in new_vars:
            decay_selection_options.append({'label': str(var), 'value': var})
        return var_options + decay_selection_options
    else:
        return var_options

@app.callback(
    Output(component_id='X', component_property='options'),
    [Input(component_id='decay-var', component_property='value')]
)
def create_decay_options(decay_selection):
    if len(decay_names_media(decay_selection, df)) > 0:
        new_vars = list(decay_names_media(decay_selection, df).columns)
        decay_selection_options = []
        for var in new_vars:
            decay_selection_options.append({'label': str(var), 'value': var})
        return var_options + decay_selection_options
    else:
        return var_options

@app.callback(
    Output(component_id='title-response-cuves', component_property='children'),
    [Input(component_id='response-curve', component_property='value')]
)
def title_output(input):
    variables = ""
    for var in input:
        variables = variables + var + ", "
    if len(input)>0:
        Title = "Shapes for " + variables[:-2] + ':'
    else:
        Title = ""
    return html.H6(Title, style={'color': 'white'})

@app.callback(
    Output(component_id='amount-of-picks', component_property='children'),
    [Input(component_id='response-curve', component_property='value')]
)
def update_output(input):
    dropdowns = []
    for var in input:
        dropdowns.append(
            dcc.Dropdown(
                id={'type': 'response-curve-shape',
                    'index': var},
                options=[{'label':i, 'value':i} for i in range(0,101)],
                value=5,
                multi=False
            )
        )
    return dropdowns

@app.callback(
    Output('title', 'children'),
    [Input(component_id='y', component_property='value'),
     Input(component_id='X', component_property='value'),
     Input({'type': 'response-curve-shape', 'index': ALL}, 'value'),
    Input(component_id='response-curve', component_property='value')
     ]
)
def display_output(y,X,values,respons_vars):
    formula = formule1(y, X, respons_vars, values)
    return html.H5('Your model: ' + formula, style={'color': colors['text'],'font-weight': 'bold'})

@app.callback(
    Output(component_id='graph-fit-vs-actual', component_property='figure'),
    [Input(component_id='y', component_property='value'),
     Input(component_id='X', component_property='value'),
     Input(component_id='decay-var', component_property='value'),
     Input({'type': 'response-curve-shape', 'index': ALL}, 'value'),
     Input(component_id='response-curve', component_property='value')
     ]
)
def graph_update_actual_vs_fit(y, X, devay_vars,values,respons_vars):
    # formula = formule(y, X)
    formula = formule1(y, X, respons_vars, values)
    # formula = 'sales ~ holidays + s_curve(tv, 2) + s_curve(radio, 5)' #
    if len(devay_vars) > 0:
        df_media_decays = df_media(devay_vars, df)
        df_merged = pd.concat([df, df_media_decays], axis=1).reset_index()
        model_data = df_merged
    else:
        model_data = df
    try:
        fig = actual_vs_fit_graph(model_data.date, model_data, formula, color_kpi='deepskyblue', color_fit='dimgray')
        return fig
    except:
        return actual_vs_fit_graph(model_data.date, model_data, 'sales ~ 1', color_kpi='deepskyblue',
                                   color_fit='dimgray', title_graph='THIS IS NOT A VALID SELECTION, PLZ TRY AGAIN:)')


@app.callback(
    Output(component_id='graph-decomposition', component_property='figure'),
    [Input(component_id='y', component_property='value'),
     Input(component_id='X', component_property='value'),
     Input(component_id='decay-var', component_property='value'),
     Input({'type': 'response-curve-shape', 'index': ALL}, 'value'),
     Input(component_id='response-curve', component_property='value')]
)
def graph_update_decomposition(y, X, devay_vars,values,respons_vars):
    formula = formule1(y, X, respons_vars, values)
    if len(devay_vars) > 0:
        df_media_decays = df_media(devay_vars, df)
        df_merged = pd.concat([df, df_media_decays], axis=1).reset_index()
        model_data = df_merged
    else:
        model_data = df
    try:
        fig = decomposition_graph(model_data.date, model_data, formula, color_kpi='deepskyblue')
        return fig
    except:
        return actual_vs_fit_graph(model_data.date, model_data, 'sales ~ 1', color_kpi='deepskyblue',
                                   color_fit='dimgray', title_graph='This might not be a valid selection of Y and X')

@app.callback(
    Output(component_id='table', component_property='children'),
    [Input(component_id='y', component_property='value'),
     Input(component_id='X', component_property='value'),
     Input(component_id='decay-var', component_property='value'),
     Input({'type': 'response-curve-shape', 'index': ALL}, 'value'),
     Input(component_id='response-curve', component_property='value')]
)
def graph_update_decomposition(y, X, devay_vars,values,respons_vars):
    formula = formule1(y, X, respons_vars, values)
    if len(devay_vars) > 0:
        df_media_decays = df_media(devay_vars, df)
        df_merged = pd.concat([df, df_media_decays], axis=1).reset_index()
        model_data = df_merged
    else:
        model_data = df
    try:
        df_table = pd.DataFrame(model_characteristics(formula, model_data))
        return dbc.Table.from_dataframe(df_table, striped=True, bordered=True, hover=True)
    except:
        return dbc.Table.from_dataframe(pd.DataFrame(
            {"Metric:": ['RSquared', 'Adj RSquared', 'Durbin Watson', ' Jarque-Bera'], 'Values': [999, 999, 999, 999]}),
                                        striped=True, bordered=True, hover=True)

# id='graph-decomposition'
@app.callback(
    Output(component_id='graph-curves', component_property='figure'),
    [Input(component_id='decay-var', component_property='value'),
     Input({'type': 'response-curve-shape', 'index': ALL}, 'value'),
     Input(component_id='response-curve', component_property='value')]
)
def graph_update_cuves(devay_vars,values,respons_vars):
    if len(devay_vars) > 0:
        df_media_decays = df_media(devay_vars, df)
        df_merged = pd.concat([df, df_media_decays], axis=1).reset_index()
        model_data = df_merged
    else:
        model_data = df
    try:
        fig = plot_curves(respons_vars, values,model_data)
        return fig
    except:
        fig = go.Figure()
        fig.update_layout(title='Use Response Curves to fill this Graph',
                          xaxis_title='GRPs',
                          yaxis_title='Impact (will be multiplied with your estimated beta)', template='plotly_dark',
                          plot_bgcolor='rgba(0, 0, 0, 0)')
        return fig
    # go.Figure(data=[go.Scatter(x=[], y=[])])

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-decay", "is_open"),
    [Input("collapse-button-decay", "n_clicks")],
    [State("collapse-decay", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open

@app.callback(
    Output("collapse-metrics", "is_open"),
    [Input("collapse-button-metrics", "n_clicks")],
    [State("collapse-metrics", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-response-curves", "is_open"),
    [Input("collapse-button-response-curves", "n_clicks")],
    [State("collapse-response-curves", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
