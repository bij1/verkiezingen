import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from apps import donaties, mapping, campaign, flyers
from app import server

colors = {
    'background': '#111111',
    'text': '#FFFFFF',
    'button':'#FFFF00'
}

logo ='https://bij1.org/wp-content/uploads/2021/01/bij1logorgb012-1.png'
    #'https://filantropius.files.wordpress.com/2013/11/nederland-wordt-beter.jpg?w=600&h=600'


sidebar = html.Div(
    [
        html.Div(
            [
                # width: 12rem ensures the logo is the exact width of the
                # collapsed sidebar (accounting for padding)
                html.Img(src=logo, style={"width": "12rem"})
                # html.H2("Menu"),
            ],
            className="sidebar-header",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-calculator mr-2"), html.Span("Donations")],
                    href="/",
                    id="home-link",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-chart-area mr-2"),
                        html.Span("Flyers"),
                    ],
                    href="/apps/flyers",
                    id="calendar-link",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-map-marked-alt mr-2"),
                        html.Span("Verkiezingen 2017"),
                    ],
                    href="/apps/maps",
                    id="messages-link",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)

content = html.Div(id="page-content", className="content")

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# set the content according to the current pathname
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return donaties.layout
    if pathname == '/apps/flyers':
        return flyers.layout
    elif pathname == '/apps/maps':
        return mapping.layout
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# sets the active property on the navlink corresponding to the current page
@app.callback(
    [
        Output(link_id, "active")
        for link_id in ["home-link", "calendar-link", "messages-link"]
    ],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        return True, False, False
    elif pathname == "/apps/app_modelling":
        return False, True, False
    elif pathname == "/apps/maps":
        return False, False, True
    return False, False, False

if __name__ == '__main__':
    app.run_server(debug=True)