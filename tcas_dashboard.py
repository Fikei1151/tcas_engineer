import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import dash_ag_grid as dag
import re

# Load the filtered CSV file
file_path = 'filtered_all_tcas.csv'
data = pd.read_csv(file_path)

data['fee_cleaned'] = data['fee'].str.extract('(\d+,\d+|\d+)').replace(',', '', regex=True).astype(float)
data['1 Portfolio_cleaned'] = data['1 Portfolio'].str.extract('(\d+)').astype(float)
data['2 Quota_cleaned'] = data['2 Quota'].str.extract('(\d+)').astype(float)
data['3 admission_cleaned'] = data['3 admission'].str.extract('(\d+)').astype(float)
data['4 direct_cleaned'] = data['4 direct'].str.extract('(\d+)').astype(float)

# Find universities that accept the most students in each round
max_portfolio_univ = data.groupby('university')['1 Portfolio_cleaned'].sum().idxmax()


max_quota_univ = data.groupby('university')['2 Quota_cleaned'].sum().idxmax()

max_admission_univ = data.groupby('university')['3 admission_cleaned'].sum().idxmax()

max_direct_univ = data.groupby('university')['4 direct_cleaned'].sum().idxmax()

data['courses'] = data['course'].str.replace(r'^\d+\.\s*', '', regex=True)
courses = data['courses'].drop_duplicates()
courses_df = pd.DataFrame(courses, columns=['courses'])
courses_df['details'] = 'แสดงรายละเอียด'


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
    html.Div([
        html.H1("Engineering courses", style={'textAlign': 'center'}),

    ], style={'paddingTop': '40px'}
    ),
    
    # html.Div([
    #     html.Label("ค้นหามหาวิทยาลัย"),
    #     dcc.Dropdown(
    #         id='university-dropdown',
    #         options=[{'label': univ, 'value': univ} for univ in data['university'].dropna().unique()],
    #         placeholder="Select a University"
    #     ),
    #     html.Button('ค้นหา', id='university-search-button', n_clicks=0, className='mt-2'),
    # ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("ค้นหาหลักสูตร"),
        dcc.Input(
            id='course-input',
            placeholder="พิมพ์หลักสูตรที่ต้องการค้นหา",
            type='text',
            debounce=False,  # ทำให้การค้นหาเริ่มทำงานเมื่อพิมพ์เสร็จ
            style={'width': '100%'}
        ),
    ], style={'width': '70%', 'display': 'inline-block'}),
    
    html.Hr(),
    
    # html.Div(id='course-details-output', className='mt-3'),
     html.Div([
        dash_table.DataTable(
            id='courses-table',
            columns=[
                {"name": "หลักสูตร", "id": "courses"},
                {
                    "name": "รายละเอียด", 
                    "id": "details", 
                    "presentation": "markdown"
                }
            ],
            data=courses_df.to_dict('records'),
            style_cell={'textAlign': 'left', 'border': 'none'},
            style_data={
                'borderBottom': '1px solid black',
                'paddingBottom': '20px',
                'paddingTop': '20px'
            }
        )
    ], style={'width': '50%', 'display': 'inline-block', 'justifyContent': 'center'}),
    html.Div(id='course-details-output', style={'marginTop': '20px'})
    # html.Ul([html.Li(sub_course) for sub_course in sub_courses])
], style={'width': '100%', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center'})

# Layout for Map page
map_layout = html.Div([
    html.H1("University Map", style={'textAlign': 'center'}),
    # Add map-related content here
])

# Layout for Statistics page
statistics_layout = html.Div([
    html.H1("Statistics", style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("จำนวนมหาวิทยาลัยทั้งหมด", className="card-title"),
                html.P(f"{data['university'].nunique()}", className="card-text"),
            ]), color="primary", inverse=True
        )),
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("จำนวนหลักสูตรทั้งหมด", className="card-title"),
                html.P(f"{data['course'].nunique()}", className="card-text"),
            ]), color="info", inverse=True
        )),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("ค่าธรรมเนียมการศึกษาเฉลี่ย", className="card-title"),
                html.P(f"{data['fee_cleaned'].mean():,.2f} บาท", className="card-text"),
            ]), color="success", inverse=True
        )),
     
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("จำนวนรับรวมในแต่ละรอบ", className="card-title"),
                html.P(f"รอบ Portfolio: {data['1 Portfolio_cleaned'].sum()} คน", className="card-text"),
                html.P(f"รอบ Quota: {data['2 Quota_cleaned'].sum()} คน", className="card-text"),
                html.P(f"รอบ Admission: {data['3 admission_cleaned'].sum()} คน", className="card-text"),
                html.P(f"รอบ Direct: {data['4 direct_cleaned'].sum()} คน", className="card-text"),
            ]), color="secondary", inverse=True
        )),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("มหาวิทยาลัยที่รับคนเยอะสุดในแต่ละรอบ", className="card-title"),
                html.P(f"รอบ Portfolio: {max_portfolio_univ} ", className="card-text"),
                html.P(f"รอบ Quota: {max_quota_univ} ", className="card-text"),
                html.P(f"รอบ Admission: {max_admission_univ} ", className="card-text"),
                html.P(f"รอบ Direct: {max_direct_univ} ", className="card-text"),
            ]), color="dark", inverse=True
        )),
    ], className="mb-4"),
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

# Callback สำหรับการอัพเดทตารางตามการค้นหา
@app.callback(
    Output('courses-table', 'data'),
    [Input('course-input', 'value')]
)
def update_table(search_value):
    if not search_value:
        # หากไม่มีการค้นหา ให้แสดงหลักสูตรทั้งหมด
        return courses_df.to_dict('records')
    else:
        # ค้นหาหลักสูตรที่ตรงกับการค้นหา
        filtered_courses = courses_df[courses_df['courses'].str.contains(search_value, case=False, na=False)]
        if filtered_courses.empty:
            # หากไม่พบหลักสูตรที่ตรงกับการค้นหา
            return [{'courses': 'ไม่พบหลักสูตร', 'details': ''}]
        return filtered_courses.to_dict('records')

# Callback สำหรับการแสดงรายละเอียดของหลักสูตร
@app.callback(
    Output('course-details-output', 'children'),
    [Input('courses-table', 'active_cell')],
    [State('courses-table', 'data')]
)
def display_course_details(active_cell, data):
    if active_cell:
        row = active_cell['row']
        course = data[row]['courses']
        return f"รายละเอียดของหลักสูตร: {course}"
    return "เลือกหลักสูตรเพื่อแสดงรายละเอียด"



# def update_table(n_clicks, university, course):
    
#     if n_clicks > 0 and university and course:
#         dff = data[(data['university'] == university) & (data['course'] == course)]
        
#         if dff.empty:
#             course_details = html.Div([
#                 html.H4("No data available for the selected course."),
#             ])
#         else:
#             course_details = html.Div([
#                 html.H4(f"รายละเอียดหลักสูตร: {course}"),
#                 html.P(f"มหาวิทยาลัย: {university}"),
#                 html.P(f"ค่าธรรมเนียมการศึกษา: {dff['fee'].values[0]}"),
#                 html.P(f"จำนวนรับรอบที่ 1: {dff['1 Portfolio'].values[0]}"),
#                                 html.P(f"จำนวนรับรอบที่ 2: {dff['2 Quota'].values[0]}"),
#                 html.P(f"จำนวนรับรอบที่ 3: {dff['3 admission'].values[0]}"),
#                 html.P(f"จำนวนรับรอบที่ 4: {dff['4 direct'].values[0]}")
#             ])

#         return dff.to_dict('records'), course_details

#     return [], html.Div()

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

