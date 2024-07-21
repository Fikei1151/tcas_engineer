import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

# Load the filtered CSV file
file_path = 'filtered_all_tcas.csv'
data = pd.read_csv(file_path)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "TCAS Data Dashboard"

# Navbar
navbar = dbc.NavbarSimple(
    brand="TCAS Data Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Map", href="/map")),
        dbc.NavItem(dbc.NavLink("Statistics", href="/statistics"))
    ]
)

# Layout for Home page
home_layout = html.Div([
    html.H1("TCAS Data Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("ค้นหามหาวิทยาลัย"),
        dcc.Dropdown(
            id='university-dropdown',
            options=[{'label': univ, 'value': univ} for univ in data['university'].dropna().unique()],
            placeholder="Select a University"
        ),
        html.Button('ค้นหา', id='university-search-button', n_clicks=0),
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("ค้นหาหลักสูตร"),
        dcc.Dropdown(
            id='course-dropdown',
            placeholder="Select a Course"
        ),
        html.Button('ค้นหา', id='course-search-button', n_clicks=0),
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Hr(),
    
    html.Div(id='course-details-output'),

    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in data.columns],
        page_size=10
    )
])

# Layout for Map page
map_layout = html.Div([
    html.H1("University Map", style={'textAlign': 'center'}),
    # Add map-related content here
])

# Layout for Statistics page
statistics_layout = html.Div([
    html.H1("Statistics", style={'textAlign': 'center'}),
    # Add statistics-related content here
])

# Main layout with Navbar and page content
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

@app.callback(
    Output('course-dropdown', 'options'),
    Input('university-search-button', 'n_clicks'),
    State('university-dropdown', 'value')
)
def update_course_dropdown(n_clicks, university):
    if n_clicks > 0 and university:
        filtered_courses = data[data['university'] == university]['course'].dropna().unique()
        return [{'label': course, 'value': course} for course in filtered_courses]
    return []

@app.callback(
    Output('data-table', 'data'),
    Output('course-details-output', 'children'),
    Input('course-search-button', 'n_clicks'),
    State('university-dropdown', 'value'),
    State('course-dropdown', 'value')
)
def update_table(n_clicks, university, course):
    if n_clicks > 0 and university and course:
        dff = data[(data['university'] == university) & (data['course'] == course)]
        
        course_details = html.Div([
            html.H4(f"รายละเอียดหลักสูตร: {course}"),
            html.P(f"มหาวิทยาลัย: {university}"),
            html.P(f"ค่าธรรมเนียมการศึกษา: {dff['fee'].values[0]}"),
            html.P(f"จำนวนรับรอบที่ 1: {dff['1 Portfolio'].values[0]}"),
            html.P(f"จำนวนรับรอบที่ 2: {dff['2 Quota'].values[0]}"),
            html.P(f"จำนวนรับรอบที่ 3: {dff['3 admission'].values[0]}"),
            html.P(f"จำนวนรับรอบที่ 4: {dff['4 direct'].values[0]}")
        ])

        return dff.to_dict('records'), course_details

    return [], html.Div()

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/map':
        return map_layout
    elif pathname == '/statistics':
        return statistics_layout
    else:
        return home_layout

if __name__ == '__main__':
    app.run_server(debug=True)
