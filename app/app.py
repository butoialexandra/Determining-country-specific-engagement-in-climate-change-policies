import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "bdpp"
server = app.server


# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

# Dictionary of important locations in New York
list_of_locations = {
    "Madison Square Garden": {"lat": 40.7505, "lon": -73.9934},
    "Yankee Stadium": {"lat": 40.8296, "lon": -73.9262},
    "Empire State Building": {"lat": 40.7484, "lon": -73.9857},
    "New York Stock Exchange": {"lat": 40.7069, "lon": -74.0113},
    "JFK Airport": {"lat": 40.644987, "lon": -73.785607},
    "Grand Central Station": {"lat": 40.7527, "lon": -73.9772},
    "Times Square": {"lat": 40.7589, "lon": -73.9851},
    "Columbia University": {"lat": 40.8075, "lon": -73.9626},
    "United Nations HQ": {"lat": 40.7489, "lon": -73.9680},
}

# Initialize data frame
df1 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv",
    dtype=object,
)
df2 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data2.csv",
    dtype=object,
)
df3 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data3.csv",
    dtype=object,
)
df = pd.concat([df1, df2, df3], axis=0)
df["Date/Time"] = pd.to_datetime(df["Date/Time"], format="%Y-%m-%d %H:%M")
df.index = df["Date/Time"]
df.drop("Date/Time", 1, inplace=True)
totalList = []
for month in df.groupby(df.index.month):
    dailyList = []
    for day in month[1].groupby(month[1].index.day):
        dailyList.append(day[1])
    totalList.append(dailyList)
totalList = np.array(totalList, dtype=object)

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.A(
                            html.Img( # TODO: ETH logo?
                                className="logo",
                                src="https://ethz.ch/services/en/service/communication/corporate-design/logo/_jcr_content/par/twocolumn/par_right/fullwidthimage/image.imageformat.twocolumn.122310607.png",
                            )
                        ),

                        html.H2("Topic Modeling on Nationally Determined Contributions"),

                        #Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                
                                html.Div(
                                    className="div-for-radioitem",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.RadioItems( #TODO
                                            id="view-radioitems",
                                            options=[
                                                {"label": "World View", "value": "world"},
                                                {"label": "Continent View", "value": "continent"}
                                            ],
                                            value = "world",
                                            labelStyle={'display': 'inline-block'}
                                        )
                                    ],
                                ),
                                
                                html.Div(
                                    id = "continent-dropdown-div",
                                    className="div-for-dropdown",
                                    children=[
                                        dcc.Dropdown(id = "continent-dropdown", disabled=True)
                                    ],
                                ),
                            ],
                        ),
                        html.P(
                            """Select a topic:"""
                        ),
                        html.Div(
                            className="div-for-radioitem",
                            children=[
                                dcc.Dropdown(
                                    id="topic_dropdown",
                                    options = [
                                        {"label": "Topic {}".format(i), "value": "{}".format(i)} for i in range(10)
                                    ],
                                    placeholder="Select a topic"
                                )
                            ],
                        ),
                        
                        
                        dcc.Markdown(
                            """
                            Sources: [NDCs](https://www4.unfccc.int/sites/NDCStaging/Pages/Home.aspx)
                            Design Credits to: [Dash-sample-apps](https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-uber-rides-demo) 
                            
                            Disclaimer: Due to time constraint, we use the default map which does not represent authors' belief. 
                            More to read in [Using Built-in Country and State Geometries](https://plotly.com/python/choropleth-maps/). 
                            """
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            children = [dcc.Graph(id="map-graph")]
                        ),
                        
                        html.Div(
                            children = [
                                html.H3(
                                    """LDA Topic Modeling Visualization:"""
                                ),
                                html.Iframe(src=app.get_asset_url("lda.html"), style=dict(width="95%", height="400%"))
                            ]
                        )
                    ],
                ),
            ],
        )
    ]
)

import plotly.express as px
import json
df = pd.read_csv("./data/aggregated_data.csv", dtype={"ISO": str})
countries = json.load(open("./data/countries.geo.json"))

@app.callback(
    Output("continent-dropdown-div", "children"),
    Input("view-radioitems", "value")
)
def show_continent_dropbox(map_view):
    if map_view == "continent":
        container=[html.P(
                            """Select a continent:"""
                        ),
                dcc.Dropdown(
                id = "continent-dropdown",
                options = [
                    {'label': 'Africa', 'value': 'africa'},
                    {'label': 'Asia', 'value': 'asia'},
                    {'label': 'Europe', 'value': 'europe'},
                    {'label': 'North America', 'value': 'north america'},
                    {'label': 'South America', 'value': 'south america'}
                ],
                placeholder="Select a continent"
                )
        ]      
        return container
    else:
        return dcc.Dropdown(id = "continent-dropdown", disabled=True)
    

@app.callback(
    Output("map-graph", "figure"),
    Input("topic_dropdown", "value"),
    Input("view-radioitems", "value"),
    Input("continent-dropdown", "value"), suppress_callback_exceptions=True
)
def display_map(topic, map_view, continent):
    
    if map_view == "continent" and continent is not None:
        scope = continent
    else:
        scope = "world"

    if topic is None:
        choropleth_map = px.choropleth(df, geojson=countries, locations = "ISO", featureidkey = "id", scope=scope)
    else:
        choropleth_map = px.choropleth(
            df, 
            geojson=countries,
            color =  df[topic],
            locations = "ISO",
            featureidkey = "id",
            range_color = [0, 1],
            color_continuous_scale="bugn",
            scope=scope
        )
    choropleth_map.update_layout(
        title_text = "NDCs Topic Intensity", #TODO
        geo = dict(
            showframe=False,
            showcoastlines=True,
            projection_type = 'equirectangular'
        ),
        margin={"r":0, "l":0, "b":0}
    )
    return choropleth_map
if __name__ == "__main__":
    app.run_server(debug=True)