import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the data
data = pd.read_csv("spacex_launch_dash.csv")
max_payload = data['Payload Mass (kg)'].max()
min_payload = data['Payload Mass (kg)'].min()

# Generate launch site options
site_options = [
    {'label': 'All Sites', 'value': 'All Sites'}
] + [{'label': site, 'value': site} for site in data['Launch Site'].unique()]

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Analysis Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    
    # Dropdown for selecting launch site
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=site_options,
            placeholder='Select a Launch Site',
            searchable=True,
            clearable=False,
            value='All Sites'
        ),
    ]),
    html.Br(),
    
    # Pie chart for launch success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # Slider for payload range selection
    html.P("Payload range (Kg):"),
    html.Div([
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: {'label': f'{i} Kg'} for i in range(0, 11000, 1000)},
            value=[min_payload, max_payload]
        ),
    ]),
    html.Br(),
    
    # Scatter plot for payload vs. launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for updating pie chart based on selected site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        filtered_data = data[data['class'] == 1]
        fig = px.pie(filtered_data, names='Launch Site', title='Total Successful Launches by Site')
    else:
        filtered_data = data[data['Launch Site'] == selected_site]
        fig = px.pie(filtered_data, names='class', title=f'Total Launch Outcomes for {selected_site}')
    return fig

# Callback for updating scatter plot based on selected site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), 
     Input('payload-slider', 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    if selected_site == 'All Sites':
        filtered_data = data[
            (data['Payload Mass (kg)'] > low) & 
            (data['Payload Mass (kg)'] < high)
        ]
        title = 'Payload vs. Launch Success for All Sites'
    else:
        filtered_data = data[
            (data['Launch Site'] == selected_site) & 
            (data['Payload Mass (kg)'] > low) & 
            (data['Payload Mass (kg)'] < high)
        ]
        title = f'Payload vs. Launch Success for {selected_site}'
    
    fig = px.scatter(
        filtered_data,
        x='Payload Mass (kg)',
        y='class',
        color='class',
        title=title,
        labels={'class': 'Success (1) / Failure (0)'}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
