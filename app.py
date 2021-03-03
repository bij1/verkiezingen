import dash
import dash_bootstrap_components as dbc

FA = "https://use.fontawesome.com/releases/v5.15.1/css/all.css"
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.CYBORG, FA], suppress_callback_exceptions=True)
# app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server