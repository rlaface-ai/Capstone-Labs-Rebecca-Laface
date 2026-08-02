# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px


# Load the SpaceX dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")


# Create the Dash application
app = Dash(__name__)


# Minimum and maximum payload values
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()


# App layout
app.layout = html.Div(children=[

    html.H1(
        "SpaceX Launch Records Dashboard",
        style={
            "textAlign": "center",
            "color": "#503D36",
            "fontSize": 40
        }
    ),

    # Launch site dropdown
    dcc.Dropdown(
        id="site-dropdown",
        options=[
            {"label": "All Sites", "value": "ALL"},
            {"label": "CCAFS LC-40", "value": "CCAFS LC-40"},
            {"label": "CCAFS SLC-40", "value": "CCAFS SLC-40"},
            {"label": "KSC LC-39A", "value": "KSC LC-39A"},
            {"label": "VAFB SLC-4E", "value": "VAFB SLC-4E"}
        ],
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # Pie chart
    dcc.Graph(id="success-pie-chart"),

    html.Br(),

    html.P("Payload range (Kg):"),

    # Payload range slider
    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={
            0: "0",
            2500: "2500",
            5000: "5000",
            7500: "7500",
            10000: "10000"
        }
    ),

    html.Br(),

    # Scatter plot
    dcc.Graph(id="success-payload-scatter-chart")
])


# Callback for the pie chart
@app.callback(
    Output(
        component_id="success-pie-chart",
        component_property="figure"
    ),
    Input(
        component_id="site-dropdown",
        component_property="value"
    )
)
def update_pie_chart(selected_site):

    if selected_site == "ALL":

        successful_launches = (
            spacex_df[spacex_df["class"] == 1]
            .groupby("Launch Site")
            .size()
            .reset_index(name="Success Count")
        )

        fig = px.pie(
            successful_launches,
            values="Success Count",
            names="Launch Site",
            title="Total Successful Launches by Site"
        )

    else:

        filtered_df = spacex_df[
            spacex_df["Launch Site"] == selected_site
        ]

        outcome_counts = (
            filtered_df["class"]
            .value_counts()
            .rename_axis("class")
            .reset_index(name="count")
        )

        outcome_counts["Outcome"] = outcome_counts["class"].map({
            0: "Failure",
            1: "Success"
        })

        fig = px.pie(
            outcome_counts,
            values="count",
            names="Outcome",
            title=f"Launch Outcomes for {selected_site}"
        )

    return fig


# Callback for the scatter plot
@app.callback(
    Output(
        component_id="success-payload-scatter-chart",
        component_property="figure"
    ),
    [
        Input(
            component_id="site-dropdown",
            component_property="value"
        ),
        Input(
            component_id="payload-slider",
            component_property="value"
        )
    ]
)
def update_scatter_chart(selected_site, payload_range):

    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low) &
        (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if selected_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == selected_site
        ]

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=f"Payload vs. Launch Outcome for {selected_site}"
    )

    return fig


# Run the application
if __name__ == "__main__":
    app.run(debug=True)