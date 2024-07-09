import dash
from dash import dcc, html, Input, Output, dash_table, State
import pandas as pd

# Load the filtered CSV file
file_path = 'filtered_all_tcas.csv'
data = pd.read_csv(file_path)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "TCAS Data Dashboard"

app.layout = html.Div([
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

if __name__ == '__main__':
    app.run_server(debug=True)
