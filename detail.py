from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import dash
from dash.dependencies import ALL
import plotly.express as px
import re
import dash_leaflet as dl
import json

path = "data/data.csv"
df = pd.read_csv(path)

df['course'] = df['course'].str.replace(r'^\d+\.\s*', '', regex=True)
courses = df['course'].drop_duplicates()

location_data = pd.read_csv(path)
location_data = location_data.dropna(subset=['latitude', 'longitude'])

universities = df['university'].drop_duplicates().to_frame()
universities.columns = ['label']
universities['value'] = universities['label']
universities = universities['label']  # Convert to list of dictionaries

text_color = 'black'

def extract_number(text):
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else 0

app = Dash(__name__, external_stylesheets=['/assets/style.css'])

app.config.suppress_callback_exceptions = True
app.layout = html.Div([
    html.Div([
        html.Div([html.H3("มหาวิทยาลัย", className="card-title")], style={'fontSize': '40px', 'color': text_color}),
        dcc.Dropdown(
            options=universities,
            id='university-input',
            placeholder="กรุณาเลือกมหาวิทยาลัย",
            style={'width': '300px', 'color': 'black'},
            value='มหาวิทยาลัยสงขลานครินทร์',  # Set default value if needed
        ),
    ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '20px', 'alignItems': 'center', 'marginTop': '20px'}),

    html.Div([
        html.Div([      
            html.Div([
                html.Div([html.H3("สาขา", className="card-title")], style={'alignItems': 'center', 'justifyContent': 'center', 'fontSize': '25px'}),
                html.Div(id='course-list')
            ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': 'rgba(147, 177, 166, 0.8)', 'width': '400px', 'height': '470px', 'overflowY': 'scroll', 'padding': '20px', 'paddingBottom': '40px', 'borderRadius': '25px', 'marginRight': '20px', 'alignItems': 'center', 'color': text_color}),

        ], style={'display': 'flex', 'flexDirection': 'column', 'textAlign': 'center'}),
        html.Div([      
            html.Div([
                html.Div([html.H3("หลักสูตร", className="card-title")], style={'alignItems': 'center', 'justifyContent': 'center', 'fontSize': '25px'}),
                html.Div(id='sub-course-list')
            ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': 'rgba(147, 177, 166, 0.8)', 'width': '400px', 'height': '470px', 'overflowY': 'scroll', 'padding': '20px', 'paddingBottom': '40px', 'borderRadius': '25px', 'marginRight': '20px', 'alignItems': 'center', 'color': text_color}),

        ], style={'display': 'flex', 'flexDirection': 'column', 'textAlign': 'center'}),
        html.Div([
            html.Div([
                html.Div([html.H3("ค่าธรรมเนียม", className="card-title")], style={'fontSize': '25px'}),
                html.Div([html.Div(id='fee-info')], style={'fontSize': '25px'})
            ], style={'backgroundColor': '#5C8374', 'width': '400px', 'height': '200px', 'padding': '20px', 'paddingBottom': '40px', 'borderRadius': '25px', 'alignItems': 'center', 'marginLeft': '20px', 'color': text_color, 'textAlign': 'center'}),
        ])

    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center'}),
    html.Div([
        html.H1([
            html.Div([html.H3("ข้อมูลการรับสมัคร", className="card-title")], style={'justifyContent': 'center', 'textAlign': 'center', 'color': text_color}),
            dcc.Graph(id='bar-graph'),], 
            style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': 'rgb(24, 61, 61, 0.6)', 'width': '1000px', 'height': '500px', 'padding': '10px', 'paddingBottom': '20px', 'borderRadius': '25px', 'marginRight': '20px', 'fontSize': '25px'}),
        ]),
    html.Div([
        html.H1("ตำแหน่ง", style={'textAlign': 'center'}),
        dl.Map(id='map', center=[13.736717, 100.523186], zoom=5, style={'height': '303px', 'width': '194vh'}, children=[
        dl.TileLayer(),
        dl.LayerGroup(id="markers")
        ])    
    ], style={'marginTop': '40px'})
], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center'})

@app.callback(
    Output('course-list', 'children'),
    Input('university-input', 'value')
)
def update_course_list(university_value):
    if not university_value:
        return "กรุณาเลือกมหาวิทยาลัย"
    
    courses = df[df['university'] == university_value]['course'].drop_duplicates()

    if courses.empty:
        return "ไม่พบข้อมูล"
    
    course_buttons = [
        html.Div(
            course,
            id={'type': 'course-button', 'index': i},
            n_clicks=0,
            className='button-hover',
        ) for i, course in enumerate(courses)
    ]
    return course_buttons

@app.callback(
    Output('sub-course-list', 'children'),
    Input({'type': 'course-button', 'index': ALL}, 'n_clicks'),
    Input('university-input', 'value')
)
def update_sub_course_list(n_clicks, university_value):
    ctx = dash.callback_context
    sub_course_list = []  # Initialize sub_course_list

    if not ctx.triggered:
        return "กรุณาเลือกสาขา"

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if 'index' in triggered_id:
        button_index = json.loads(triggered_id)['index']
        courses = df[df['university'] == university_value]['course'].drop_duplicates().reset_index(drop=True)

        if button_index >= len(courses):
            return "ไม่พบข้อมูล"
        
        course_value = courses.iloc[button_index]
        sub_courses = df[(df['university'] == university_value) & (df['course'] == course_value)]['sub_course'].drop_duplicates().reset_index(drop=True)

        if sub_courses.empty:
            return "ไม่พบข้อมูล"
        
        sub_course_list = [
            html.Button(
                sub_course,
                id={'type': 'sub-course-button', 'index': i},
                n_clicks=0,
                className='button-hover',
            ) for i, sub_course in enumerate(sub_courses)
        ]

    return sub_course_list


@app.callback(
    [Output('bar-graph', 'figure'),
     Output('fee-info', 'children'),
     Output('map', 'center'),
     Output('map', 'zoom'),
     Output('markers', 'children')],
    [Input({'type': 'sub-course-button', 'index': ALL}, 'n_clicks'),
     Input({'type': 'course-button', 'index': ALL}, 'n_clicks'),
     Input('university-input', 'value')]
)
def update_bar_graph_and_map(sub_course_n_clicks, course_n_clicks, university_value):
    ctx = dash.callback_context

    bar_figure = {}
    fee_info = []
    markers = []
    map_center = [13.736717, 100.523186]
    map_zoom = 5

    if not ctx.triggered:
        return bar_figure, fee_info, map_center, map_zoom, markers

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if 'sub-course-button' in triggered_id:
        button_index = json.loads(triggered_id)['index']
        courses = df[df['university'] == university_value]['course'].drop_duplicates().reset_index(drop=True)

        if any(n_clicks > 0 for n_clicks in course_n_clicks):
            selected_course_index = course_n_clicks.index(max(course_n_clicks))
            course_value = courses.iloc[selected_course_index]
        else:
            return bar_figure, fee_info, map_center, map_zoom, markers
        
        sub_courses = df[(df['university'] == university_value) & (df['course'] == course_value)]['sub_course'].drop_duplicates().reset_index(drop=True)

        if button_index >= len(sub_courses):
            return bar_figure, fee_info, map_center, map_zoom, markers
        
        sub_course = sub_courses.iloc[button_index]
        university_data = df[(df['university'] == university_value) & (df['sub_course'] == sub_course)]

        if university_data.empty:
            return bar_figure, fee_info, map_center, map_zoom, markers

        numeric_columns = ['1 Portfolio', '2 Quota', '3 admission', '4 direct']
        university_data[numeric_columns] = university_data[numeric_columns].applymap(lambda x: extract_number(x))

        bar_data = university_data[numeric_columns].sum()

        fig = px.bar(
            x=bar_data.index,
            y=bar_data.values,
            labels={'x': 'Admission Type', 'y': 'Count'},
            title=f'{sub_course}'
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
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
            gridcolor='rgba(0,0,0,0)'
        )
        fig.update_yaxes(
            showline=True, 
            linecolor='black',
            gridcolor='rgba(0,0,0,0)'
        )

        fee_info = [html.P(f'{amount}') for amount in university_data['fee']]

        location_data_filtered = location_data[location_data['university'] == university_value]
        if not location_data_filtered.empty:
            first_location = location_data_filtered.iloc[0]
            map_center = [first_location['latitude'], first_location['longitude']]
            map_zoom = 12

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

        return fig, fee_info, map_center, map_zoom, markers

    return bar_figure, fee_info, map_center, map_zoom, markers

if __name__ == '__main__':
    app.run(debug=True)
