import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def plot_trend(df, date_col, value_col, title, color=None):
    """
    Plots a line chart showing the trend of a value over time.
    """
    if color:
        fig = px.line(df, x=date_col, y=value_col, color=color, title=title)
    else:
        fig = px.line(df, x=date_col, y=value_col, title=title)
    return fig

def plot_bar_distribution(df, x_col, y_col, title, color=None):
    """
    Plots a bar chart for categorical distribution.
    """
    fig = px.bar(df, x=x_col, y=y_col, color=color, title=title)
    return fig

def plot_donut(df, values, names, title):
    """
    Plots a donut chart.
    """
    fig = px.pie(df, values=values, names=names, title=title, hole=0.4)
    return fig

def plot_treemap(df, path, values, title):
    """
    Plots a treemap.
    path: list of columns for hierarchy e.g. ['state', 'district']
    """
    fig = px.treemap(df, path=path, values=values, title=title)
    return fig

def plot_scatter(df, x_col, y_col, title, color=None, size=None, hover_data=None):
    """
    Plots a scatter plot.
    """
    fig = px.scatter(df, x=x_col, y=y_col, color=color, size=size, hover_data=hover_data, title=title)
    return fig

def plot_metric_card(label, value):
    """
    Placeholder for a custom metric card if needed, 
    but Streamlit's st.metric is usually sufficient.
    """
    pass
