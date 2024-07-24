from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import dash
from dash.dependencies import ALL
import plotly.express as px
import re
import dash_leaflet as dl

path = "data/data.csv"
df = pd.read_csv(path)

df['course'] = df['course'].str.replace(r'^\d+\.\s*', '', regex=True)
courses = df['course'].drop_duplicates()


location_data = pd.read_csv(path)

# Filter data for locations that have latitude and longitude
location_data = location_data.dropna(subset=['latitude', 'longitude'])

text_color = 'black'

def extract_number(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return 0

app = Dash(__name__, external_stylesheets=['/assets/style.css'])

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.Div([
            html.Div([html.H3("สาขา", className="card-title")], style={'fontSize': '40px', 'color': text_color}),
            dcc.Dropdown(courses, id='course-input', placeholder="กรุณาเลือกสาขา", style={'width': '300px', 'color': 'black'}, value='วิศวกรรมปัญญาประดิษฐ์'),
        ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '20px', 'alignItems': 'center', 'marginTop': '20px'}),

    html.Div([
        html.Div([      
            html.Div([
                html.Div([html.H3("หลักสูตร", className="card-title")], style={'alignItems': 'center', 'justifyContent': 'center', 'fontSize': '25px'}),
                html.Div(id='sub-course-list')
            ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': 'rgba(147, 177, 166, 0.8)', 'width': '500px', 'height': '470px', 'overflowY': 'scroll', 'padding': '20px', 'paddingBottom': '40px', 'borderRadius': '25px', 'marginRight': '20px', 'alignItems': 'center', 'color': text_color}),

        ], style={'display': 'flex', 'flexDirection': 'column', 'textAlign': 'center'}),
        html.Div([
            html.Div([
                html.Div([html.H3("ข้อมูลการรับสมัคร", className="card-title")], style={'justifyContent': 'center', 'textAlign': 'center', 'color': text_color}),
                dcc.Graph(id='bar-graph'),

            ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': 'rgb(24, 61, 61, 0.6)', 'width': '500px', 'height': '500px', 'padding': '10px', 'paddingBottom': '20px', 'borderRadius': '25px', 'marginRight': '20px', 'fontSize': '25px'}),
        ]),
        html.Div([
            html.Div([
                html.Div([html.H3("มหาวิทยาลัย", className="card-title")], style={'fontSize': '25px', 'color': text_color}),
                html.Div([html.Div(id='university-output')], style={'fontSize': '25px'})
            ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': '#93B1A6', 'width': '500px', 'height': '200px', 'padding': '20px', 'paddingBottom': '30px', 'borderRadius': '25px', 'marginLeft': '20px', 'marginBottom': '20px', 'alignItems': 'center', 'justifyContent': 'center'}),
            html.Div([
                html.Div([html.H3("ค่าธรรมเนียม", className="card-title")], style={'fontSize': '25px'}),
                html.Div([html.Div(id='fee-info')], style={'fontSize': '25px'})
            ], style={'backgroundColor': '#5C8374', 'width': '500px', 'height': '200px', 'padding': '20px', 'paddingBottom': '40px', 'borderRadius': '25px', 'alignItems': 'center', 'marginLeft': '20px', 'color': text_color, 'textAlign': 'center'}),
        ])

    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center'}),
    html.Div([
        html.H1("ตำแหน่ง", style={'textAlign': 'center'}),
        dl.Map(id='map', center=[13.736717, 100.523186], zoom=5, style={'height': '303px', 'width': '194vh'}, children=[
        dl.TileLayer(),
        dl.LayerGroup(id="markers")
        ])    
    ], style={'marginTop': '40px'})

], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center'})

@app.callback(
    Output('sub-course-list', 'children'),
    Input('course-input', 'value')
)
def update_sub_course_list(value):
    if value is None:
        return "กรุณาเลือกสาขา"
    
    sub_course = df[df['course'] == value]['sub_course']
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
        sub_course = df[df['course'] == course_value]['sub_course'].iloc[button_index]
        university = df[df['sub_course'] == sub_course]['university']

        if university.empty:
            return university_output, bar_figure, fee_info, map_center, map_zoom, markers

        first_university = university.iloc[0]

        # Filter the DataFrame for the selected university
        university_data = df[(df['university'] == first_university) & (df['sub_course'] == sub_course)]

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
            labels={'x': 'Admission Type', 'y': 'Count'},
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

if __name__ == '__main__':
    app.run(debug=True)
