# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # A dropdown list to enable Launch Site selection
                                dcc.Dropdown(id='site-dropdown', 
                                            options=[{'label':'All Sites','value':'ALL'},
                                                     {'label':'CCAFS LC-40','value':'CCAFS LC-40'},
                                                     {'label':'VAFB SLC-4E','value':'VAFB SLC-4E'},
                                                     {'label':'KSC LC-39A','value':'KSC LC-39A'},
                                                     {'label':'CCAFS SLC-40','value':'CCAFS SLC-40'},],
                                                     value='ALL', placeholder='Select a Launch Site here',
                                                     searchable=True),
                                # The default select value is for ALL sites
                                html.Br(),

                                # A pie chart to show the total successful launches count for all sites
                                # If a specific launch site is selected, Success vs. Failed counts for the site will be displayed
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # A slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0:'0',2500:'2500',5000:'5000',7500:'7500',10000:'10000'},value=[min_payload, max_payload]),

                                # A scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df=spacex_df
    if entered_site=='ALL':
        fig=px.pie(filtered_df,values='class',names='Launch Site',title='Chart of Launch Sites Success')
        return fig
    else:
        df=filtered_df[['Launch Site','class']]
        new_df=df[df['Launch Site']==entered_site]
        new_df=new_df.groupby(['class'],as_index=False).count()
        new_df.rename(columns={'Launch Site':'count'}, inplace=True)
        fig=px.pie(new_df,values='count', names='class', title=f'{entered_site} Successes & Failures')
        return fig        

# callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( Output(component_id='success-payload-scatter-chart',component_property='figure'),
               [Input(component_id='site-dropdown',component_property='value'),
               Input(component_id='payload-slider',component_property='value')])              
def get_scatter_chart(entered_site,payload_value):
    df=spacex_df
    
    def func(x):
        return (x>=payload_value[0] and x<=payload_value[1])
    
    if entered_site=='ALL':
        df=df[df['Payload Mass (kg)'].apply(func)]
        fig=px.scatter(df,x='Payload Mass (kg)',y='class', color='Booster Version Category', title='Correlation between Payload & Success rates for all Launch Sites')
        return fig
    else:
        df_new=spacex_df[spacex_df['Launch Site']==entered_site]
        df_new2=df_new[df_new['Payload Mass (kg)'].apply(func)]
        fig=px.scatter(df_new2,x='Payload Mass (kg)',y='class',color='Booster Version Category', title=f'Correlation between Payload & Success Rate for {entered_site}')        
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()