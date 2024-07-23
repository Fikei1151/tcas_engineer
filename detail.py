from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import dash
from dash.dependencies import ALL
import plotly.express as px
import re

# โหลดข้อมูลจากไฟล์ CSV
path = "data/data.csv"
df = pd.read_csv(path)

# ทำความสะอาดข้อมูลหลักสูตร
df['course'] = df['course'].str.replace(r'^\d+\.\s*', '', regex=True)
courses = df['course'].drop_duplicates()

def extract_number(text):
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return 0

app = Dash(__name__, external_stylesheets=['/assets/style.css'])

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.Div([      
        html.Div([
            html.Div([html.H3("สาขา", className="card-title")], style={'fontSize': '40px', 'color': 'black'}),
            dcc.Dropdown(courses, id='course-input', placeholder="กรุณาเลือกสาขา", style={'width': '300px', 'color': 'black'}, value='วิศวกรรมปัญญาประดิษฐ์'),
        ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '20px', 'alignItems': 'center', 'margin': '20px', 'marginBottom': '5px'}),
        
        html.Div([
            html.Div([html.H3("หลักสูตร", className="card-title")], style={'alignItems': 'center', 'justifyContent': 'center', 'fontSize': '25px'}),
            html.Div(id='sub-course-list')
        ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': '#FF8225', 'width': '500px', 'height': '400px', 'overflowY': 'scroll', 'padding': '20px', 'paddingBottom': '40px', 'borderRadius': '25px', 'margin': '20px', 'alignItems': 'center', 'marginTop': '10px', 'color': 'white'}),
        
        html.Div([
            html.Div([html.H3("มหาวิทยาลัย", className="card-title")], style={'fontSize': '25px', 'color': 'white'}),
            html.Div([html.Div(id='university-output')], style={'fontSize': '25px'})
        ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': '#B43F3F', 'width': '500px', 'height': '180px', 'padding': '20px', 'paddingBottom': '30px', 'borderRadius': '25px', 'marginBottom': '10px', 'margin': '20px', 'alignItems': 'center', 'justifyContent': 'center'}),
    ], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Div([html.H3("ข้อมูลการรับสมัคร", className="card-title")], style={'justifyContent': 'center', 'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='bar-graph'),

        ], style={'display': 'flex', 'flexDirection': 'column', 'backgroundColor': '#173B45', 'width': '500px', 'height': '550px', 'padding': '10px', 'paddingBottom': '20px', 'borderRadius': '25px', 'margin': '20px', 'fontSize': '25px'}),
        html.Div([
            html.Div([html.H3("ค่าธรรมเนียม", className="card-title")], style={'fontSize': '25px'}),
            html.Div([html.Div(id='fee-info')], style={'fontSize': '25px'})
        ], style={'backgroundColor': '#FF8225', 'width': '480px', 'height': '200px', 'padding': '20px', 'paddingBottom': '40px', 'borderRadius': '25px', 'alignItems': 'center', 'marginTop': '60px', 'marginBottom': '10px', 'marginLeft': '20px', 'color': 'white', 'textAlign': 'center'})
    ])
    
    
], style={'display': 'flex', 'flexDirection': 'row'})

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
     Output('fee-info', 'children')],
    [Input({'type': 'sub-course-button', 'index': ALL}, 'n_clicks'),
     Input('course-input', 'value')]
)
def update_university_output_and_bar_graph(n_clicks, course_value):
    ctx = dash.callback_context

    # Default return values
    university_output = "กรุณาเลือกหลักสูตร"
    bar_figure = {}
    fee_info = []

    if not ctx.triggered:
        return university_output, bar_figure, fee_info

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if 'index' in triggered_id:
        button_index = eval(triggered_id)['index']
        sub_course = df[df['course'] == course_value]['sub_course'].iloc[button_index]
        university = df[df['sub_course'] == sub_course]['university']

        if university.empty:
            return university_output, bar_figure, fee_info

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
            title_font=dict(size=18, color='white'),
            xaxis_title_font=dict(size=14, color='white'),
            yaxis_title_font=dict(size=14, color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )

        fig.update_traces(marker_color='#F8EDED')
        fig.update_xaxes(
            showline=True, 
            linecolor='white',
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

        return university_output, fig, fee_info

    return university_output, bar_figure, fee_info


if __name__ == '__main__':
    app.run(debug=True)
