import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from flask_caching import Cache
import plotly.express as px
import json

topic_names = ["Natural Disaster", "Economy", "General Terms", "Policy & Strategy",
               "Natural Resources", "Paris Agreement", "Carbon Emission", "Government",
               "Finance", "Energy", "Implementation & Action", "Methodology"
]

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "bdpp"
server = app.server

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

TIMEOUT = 600

df = pd.read_csv("./data/aggregated_data.csv", dtype={"ISO": str})
@cache.memoize(timeout=TIMEOUT)
def load_countries():
    return json.load(open("./data/countries.geojson"))

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
                        html.Img( # TODO: ETH logo?
                            className="logo",
                            src="https://ethz.ch/services/en/service/communication/corporate-design/logo/_jcr_content/par/twocolumn/par_right/fullwidthimage/image.imageformat.twocolumn.122310607.png",
                        ),

                        html.H1("Topic Modeling on Nationally Determined Contributions"),

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
                                        {"label": "Topic {}: {}".format(i+1, topic_names[i]), "value": i} for i in range(12) #TODO
                                    ],
                                    placeholder="Select a topic"
                                )
                            ],
                        ),
                        
                        
                        dcc.Markdown(
                            """
                            Sources: [Original UNFCCC NDCs](https://www4.unfccc.int/sites/NDCStaging/Pages/Home.aspx)
                            
                            Design Credits to: [Dash-sample-apps](https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-uber-rides-demo) 
                            
                            Disclaimer: The map features are by definition subject to change, debate and dispute. We use geojsons from [this repository](https://datahub.io/core/geo-countries#resource-countries)
                            with some modifications. 
                            """,
                            style = {"margin-top": "30px"}
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            children = [
                                html.H3("""Aggregated Topic Intensity of NDCs""", style = {"color":"#1E1E1E"}),
                                html.P("""Each NDC contains multiple paragraphs and each paragraph is modeled as a distribution of topics. 
                                The topic intensity is the average topic distribution.""", style = {"color":"#1E1E1E"}),
                                dcc.Graph(id="map-graph")
                                ]
                        ),
                        
                        html.Div(
                            children = [
                                html.H3(
                                    """LDA Topic Modeling Visualization:""",
                                    style = {"color":"#1E1E1E"}
                                ),
                                html.Iframe(src=app.get_asset_url("lda.html"))
                            ]
                        )
                    ],
                ),
            ],
        )
    ]
)


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
    countries = load_countries()
    if map_view == "continent" and continent is not None:
        scope = continent
    else:
        scope = "world"

    if topic is None:
        choropleth_map = px.choropleth(df, 
            locations = "ISO", 
            geojson=countries, 
            featureidkey = "properties.ISO_A3", 
            color_discrete_sequence = ["lightgrey"],
            scope=scope)
    else:
        choropleth_map = px.choropleth(
            df, 
            geojson=countries,
            color =  df[str(topic)],
            locations = "ISO",
            featureidkey = "properties.ISO_A3",
            range_color = [0, max(df[str(topic)])],
            color_continuous_scale="bugn",
            scope=scope
        )
    if topic is None:
        title_text = "Submitted Partiese of NDCs"
    else:
        title_text = "Intensity of Topic {}: {}".format(topic+1, topic_names[topic])
    choropleth_map.update_layout(
        title_text = title_text, 
        coloraxis_colorbar=dict(title="Topic Intensity"),
        geo = dict(
            showframe=False,
            showcoastlines=False,
            projection_type = 'equirectangular',
            visible=False
        ),
        margin={"r":0, "l":0, "b":0},
        geo_bgcolor = "#dbdbdb",
        paper_bgcolor = "#dbdbdb"
    )
    return choropleth_map

if __name__ == "__main__":
    app.run_server(debug=False)