import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import dash_leaflet as dl
import dash_leaflet.express as dlx
import re
from dash.dependencies import ALL
import plotly.express as px

# Load the filtered CSV file
file_path = 'data/data.csv'
data = pd.read_csv(file_path)

# Clean and prepare data
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

data['course'] = data['course'].str.replace(r'^\d+\.\s*', '', regex=True)
courses = data['course'].drop_duplicates()

def extract_number(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return 0

# Load the CSV file with university locations
location_file_path = 'data/data.csv'
location_data = pd.read_csv(location_file_path)

# Filter data for locations that have latitude and longitude
location_data = location_data.dropna(subset=['latitude', 'longitude'])

text_color = 'black'

# Initialize the Dash app

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/style.css'], suppress_callback_exceptions=True)
app.title = "TCAS Data Dashboard"

# Navbar
navbar = dbc.NavbarSimple(
    brand="TCAS Data Dashboard",
    brand_href="/",
    color="dark",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Course", href="/")),
        dbc.NavItem(dbc.NavLink("Statistics", href="/statistics")),
        dbc.NavItem(dbc.NavLink("Map", href="/map")),
    ]
)

# Layout for course page
home_layout = html.Div([
    html.Div([
    html.Div([html.H1("สาขา", className="card-title")], style={'fontSize': '3.125rem', 'color': text_color, 'fontWeight': '900'}),
    dcc.Dropdown(courses, id='course-input', placeholder="กรุณาเลือกสาขา", style={'width': '18.75rem', 'color': 'black'}, value='วิศวกรรมปัญญาประดิษฐ์'),
], style={'display': 'flex', 'flexDirection': 'row', 'gap': '1.25rem', 'alignItems': 'center', 'marginTop': '3.75rem'}),

html.Div([
    html.Div([      
        html.Div([
            html.Div([html.H3("หลักสูตร", className="card-title")], style={'alignItems': 'center', 'justifyContent': 'center', 'fontSize': '1.5625rem', 'paddingTop': '1.25rem', 'paddingBottom': '1.25rem'}),
            html.Div(id='sub-course-list')
        ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': 'rgba(147, 177, 166, 0.8)', 'width': '31.25rem', 'height': '32.5rem', 'overflowY': 'scroll', 'padding': '1.25rem', 'paddingBottom': '2.5rem', 'borderRadius': '1.5625rem', 'marginRight': '1.25rem', 'alignItems': 'center', 'color': text_color}),
    ], style={'display': 'flex', 'flexDirection': 'column', 'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Div([html.H3("ข้อมูลการรับสมัคร", className="card-title")], style={'justifyContent': 'center', 'textAlign': 'center', 'color': text_color, 'paddingTop': '2.5rem'}),
            dcc.Graph(id='bar-graph'),
        ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': 'rgb(24, 61, 61, 0.6)', 'width': '31.25rem', 'height': '32.5rem', 'paddingBottom': '1.25rem', 'borderRadius': '1.5625rem', 'marginRight': '1.25rem', 'fontSize': '1.5625rem'}),
    ]),
    html.Div([
        html.Div([
            html.Div([html.H3("มหาวิทยาลัย", className="card-title")], style={'fontSize': '1.5625rem', 'color': text_color, 'paddingBottom': '1.25rem', 'paddingTop': '1.25rem'}),
            html.Div([html.Div(id='university-output')], style={'fontSize': '1.5625rem'})
        ], style={'backgroundColor': '#93B1A6', 'width': '31.25rem', 'height': '15.625rem', 'padding': '1.25rem', 'paddingBottom': '1.875rem', 'borderRadius': '1.5625rem', 'marginLeft': '1.25rem', 'marginBottom': '1.25rem', 'alignItems': 'center', 'justifyContent': 'center', 'textAlign': 'center'}),
        html.Div([
            html.Div([html.H3("ค่าธรรมเนียม", className="card-title")], style={'fontSize': '1.5625rem', 'paddingBottom': '1.25rem', 'paddingTop': '1.25rem'}),
            html.Div([html.Div(id='fee-info')], style={'fontSize': '1.5625rem'})
        ], style={'backgroundColor': '#5C8374', 'width': '31.25rem', 'height': '15.625rem', 'padding': '1.25rem', 'paddingBottom': '2.5rem', 'borderRadius': '1.5625rem', 'alignItems': 'center', 'marginLeft': '1.25rem', 'color': text_color, 'textAlign': 'center'}),
    ])
], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center', 'marginTop': '3.75rem'}),
html.Div([
    html.H1("ตำแหน่ง", style={'textAlign': 'center'}),
    dl.Map(id='map', center=[13.736717, 100.523186], zoom=5, style={'height': '18.9375rem', 'width': '121.25rem'}, children=[
    dl.TileLayer(),
    dl.LayerGroup(id="markers")
    ])    
], style={'marginTop': '2.5rem'})
], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center'})

# Layout for Map page
map_layout = html.Div([
    html.H1("แผนที่แสดงมหาวิทยาลัย", style={'textAlign': 'center', 'paddingTop': '60px', 'paddingBottom': '20px'}),
    dl.Map(style={'width': '100%', 'height': '80vh'}, center=[13.736717, 100.523186], zoom=6, children=[
        dl.TileLayer(),
        dl.LayerGroup(id="layer")
    ])
])

university_layout = html.Div([

])

# Layout for Statistics page
statistics_layout = html.Div([
    html.H1("Statistics", style={'textAlign': 'center', 'marginBottom': '50px'}),
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("จำนวนมหาวิทยาลัยทั้งหมด", className="card-title", style={"color":"Black", 'fontSize': '1.8rem', 'marginBottom': '20px'}),
                html.P(f"{data['university'].nunique()}", className="card-text", style={'fontSize': '1.2rem', 'color':'#32292f'}),
            ]), color="#8DB19A", inverse=True, style={'width': '500rm', 'height': '200rm','textAlign': 'center'}
        )),
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("จำนวนหลักสูตรทั้งหมด", className="card-title", style={"color":"Black", 'fontSize': '1.8rem', 'marginBottom': '20px'}),
                html.P(f"{data['course'].nunique()}", className="card-text", style={'fontSize': '1.2rem', 'color':'#32292f'}),
            ]), color="#8DB19A", inverse=True, style={'width': '500rm', 'height': '200rm','textAlign': 'center'}
        )),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("ค่าธรรมเนียมการศึกษาเฉลี่ย", className="card-title", style={"color":"Black", 'fontSize': '1.8rem', 'marginBottom': '20px'}),
                html.P(f"{data['fee_cleaned'].mean():,.2f} บาท", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
            ]), color="rgba(147, 177, 166, 0.8)", inverse=True, style={'width': '500rm', 'height': '200rm','textAlign': 'center'}
        )),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("จำนวนรับรวมในแต่ละรอบ", className="card-title", style={"color":"Black", 'textAlign':'center', 'fontSize': '1.8rem', 'marginBottom': '20px'}),
                html.P(f"รอบ Portfolio: {data['1 Portfolio_cleaned'].sum()} คน", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
                html.P(f"รอบ Quota: {data['2 Quota_cleaned'].sum()} คน", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
                html.P(f"รอบ Admission: {data['3 admission_cleaned'].sum()} คน", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
                html.P(f"รอบ Direct: {data['4 direct_cleaned'].sum()} คน", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
            ]), color="#718B7A", inverse=True, style={'width': '400rm', 'height': '200rm', 'textAlign':'center'}
        )),
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("จำนวนรับรวมในแต่ละรอบ", className="card-title", style={"color":"Black", 'textAlign':'center', 'fontSize': '1.8rem'}),
                html.P(f"รอบ Portfolio: {data['1 Portfolio_cleaned'].sum()} คน", className="card-text", style={'fontSize': '1.2rem'}),
                html.P(f"รอบ Quota: {data['2 Quota_cleaned'].sum()} คน", className="card-text", style={'fontSize': '1.2rem'}),
                html.P(f"รอบ Admission: {data['3 admission_cleaned'].sum()} คน", className="card-text", style={'fontSize': '1.2rem'}),
                html.P(f"รอบ Direct: {data['4 direct_cleaned'].sum()} คน", className="card-text", style={'fontSize': '1.2rem'}),
            ]), color="#718B7A", inverse=True, style={'width': '400rm', 'height': '200rm'}
        ))
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H3("มหาวิทยาลัยที่รับคนเยอะสุดในแต่ละรอบ", className="card-title", style={"color":"Black", 'fontSize': '1.8rem', 'marginBottom': '20px'}),
                html.P(f"รอบ Portfolio: {max_portfolio_univ} ", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
                html.P(f"รอบ Quota: {max_quota_univ} ", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
                html.P(f"รอบ Admission: {max_admission_univ} ", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
                html.P(f"รอบ Direct: {max_direct_univ} ", className="card-text", style={'fontSize': '1.2rem', 'color':'Black'}),
            ]), color="rgb(24, 61, 61, 0.6)", inverse=True, style={'width': '400rm', 'height': '200rm','textAlign': 'center'}
        )),
    ], className="mb-4"),
])

# Main layout with Navbar and page content
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
], style={'overflowX': 'hidden'})

#callback map
@app.callback(
    Output('layer', 'children'),
    [Input('url', 'pathname')]
)
def update_map(pathname):
    if pathname == '/map':
        markers = [
            dl.Marker(position=[row['latitude'], row['longitude']], children=[
                dl.Tooltip(row['university']),
                dl.Popup([
                    html.H4(row['university']),
                    html.P(f"Latitude: {row['latitude']}"),
                    html.P(f"Longitude: {row['longitude']}")
                ])
            ]) for index, row in location_data.iterrows()
        ]
        return markers
    return []

# Callback สำหรับการอัพเดทตารางตามการค้นหา
# @app.callback(
#     Output('courses-table', 'data'),
#     [Input('course-input', 'value')]
# )
# def update_table(search_value):
#     if not search_value:
#         # หากไม่มีการค้นหา ให้แสดงหลักสูตรทั้งหมด
#         return courses_df.to_dict('records')
#     else:
#         # ค้นหาหลักสูตรที่ตรงกับการค้นหา
#         filtered_courses = courses_df[courses_df['courses'].str.contains(search_value, case=False, na=False)]
#         if filtered_courses.empty:
#             # หากไม่พบหลักสูตรที่ตรงกับการค้นหา
#             return [{'courses': 'ไม่พบหลักสูตร', 'details': ''}]
#         return filtered_courses.to_dict('records')

#callback course
@app.callback(
    Output('sub-course-list', 'children'),
    Input('course-input', 'value')
)
def update_sub_course_list(value):
    if value is None:
        return "กรุณาเลือกสาขา"
    
    sub_course = data[data['course'] == value]['sub_course']
    if sub_course.empty:
        return "ไม่พบข้อมูล"
    
    sub_courses_list = [
        html.Button(
            course,
            id={'type': 'sub-course-button', 'index': i},
            n_clicks=0,
            className='button-hover',
        ) for i, course in enumerate(sub_course)
    ]
    return sub_courses_list

@app.callback(
    [Output('university-output', 'children'),
     Output('bar-graph', 'figure'),
     Output('fee-info', 'children'),
     Output('map', 'center'),
     Output('map', 'zoom'),
     Output('markers', 'children')],
    [Input({'type': 'sub-course-button', 'index': ALL}, 'n_clicks'),
     Input('course-input', 'value')]
)
def update_university_output_and_bar_graph(n_clicks, course_value):
    ctx = dash.callback_context

    # Default return values
    university_output = "กรุณาเลือกหลักสูตร"
    bar_figure = {}
    fee_info = []
    markers = []
    map_center = [13.736717, 100.523186]  # Default center coordinates
    map_zoom = 5  # Default zoom level

    if not ctx.triggered:
        return university_output, bar_figure, fee_info, map_center, map_zoom, markers

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if 'index' in triggered_id:
        button_index = eval(triggered_id)['index']
        sub_course = data[data['course'] == course_value]['sub_course'].iloc[button_index]
        university = data[data['sub_course'] == sub_course]['university']

        if university.empty:
            return university_output, bar_figure, fee_info, map_center, map_zoom, markers

        first_university = university.iloc[0]

        # Filter the DataFrame for the selected university
        university_data = data[(data['university'] == first_university) & (data['sub_course'] == sub_course)]

        # Ensure columns are numeric, replacing non-numeric values with 0
        numeric_columns = ['1 Portfolio', '2 Quota', '3 admission', '4 direct']
        for col in numeric_columns:
            university_data.loc[:, col] = university_data[col].apply(lambda x: extract_number(x))

        # Sum the values for the bar graph
        bar_data = university_data[numeric_columns].sum()

        # Create the bar graph
        fig = px.bar(
            x=bar_data.index,
            y=bar_data.values,
            labels={'x': 'TCAS TYPE (รอบ)', 'y': 'Count (คน)'},
            title=f'{first_university}'
        )

        # Update the layout to make the background transparent
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
            title_font=dict(size=18, color=text_color),
            xaxis_title_font=dict(size=14, color=text_color),
            yaxis_title_font=dict(size=14, color=text_color),
            xaxis=dict(color=text_color),
            yaxis=dict(color=text_color)
        )

        fig.update_traces(marker_color='#F8EDED')
        fig.update_xaxes(
            showline=True, 
            linecolor=text_color,
            gridcolor='rgba(0,0,0,0)'  # Transparent grid lines
        )
        fig.update_yaxes(
            showline=True, 
            linecolor='black',
            gridcolor='rgba(0,0,0,0)'  # Transparent grid lines
        )

        fee_data = university_data['fee']
        fee_info = [html.P(f'{amount}') for amount in fee_data]

        university_output = html.P(first_university)
        
        # Filter location data for the selected university
        location_data_filtered = location_data[location_data['university'] == first_university]
        if not location_data_filtered.empty:
            first_location = location_data_filtered.iloc[0]
            map_center = [first_location['latitude'], first_location['longitude']]
            map_zoom = 12  # Zoom in closer to the university

            markers = [
                dl.Marker(position=[row['latitude'], row['longitude']], children=[
                    dl.Tooltip(row['university']),
                    dl.Popup([
                        html.H4(row['university']),
                        html.P(f"Latitude: {row['latitude']}"),
                        html.P(f"Longitude: {row['longitude']}")
                    ])
                    ]) for index, row in location_data_filtered.iterrows()
                ]

        return university_output, fig, fee_info, map_center, map_zoom, markers

    return university_output, bar_figure, fee_info, map_center, map_zoom, markers


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

#callback page path 
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
