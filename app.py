# Task 2: Dash Application — Superstore Sales Dashboard
# Course  : 606475 – Data Exploration and Visualization
# Phase   : 2 – Interactive & Business Intelligence Dashboards
# Based on: Doctor's Dash example (Interactive_Visualization_Libraries.ipynb)
# Same libraries the doctor used in class
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
 
# ── Load dataset (same way doctor loaded data) ────────────────────────────────
df = pd.read_csv('Superstore.csv', encoding='latin1')
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Year']       = df['Order Date'].dt.year
 
# ── Create Dash app (same as doctor's example) ────────────────────────────────
app    = Dash(__name__)
server = app.server  # Needed for deployment on Render
 
# ── Define layout (same structure as doctor's example) ────────────────────────
app.layout = html.Div([
 
    # Title
    html.H1('Superstore Sales Dashboard'),
    html.P('Use the filters below to explore sales data interactively.'),
 
    # Filter 1 — Category Dropdown (same as doctor's species-dropdown)
    html.Label('Select Category:'),
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': 'All Categories', 'value': 'All'}] +
                [{'label': c, 'value': c} for c in sorted(df['Category'].unique())],
        value='All'
    ),
 
    html.Br(),
 
    # Filter 2 — Region Dropdown (second filter component)
    html.Label('Select Region:'),
    dcc.Dropdown(
        id='region-dropdown',
        options=[{'label': 'All Regions', 'value': 'All'}] +
                [{'label': r, 'value': r} for r in sorted(df['Region'].unique())],
        value='All'
    ),
 
    html.Br(),
 
    # Filter 3 — Year Slider
    html.Label('Select Year:'),
    dcc.Slider(
        id='year-slider',
        min=int(df['Year'].min()),
        max=int(df['Year'].max()),
        step=1,
        value=int(df['Year'].max()),
        marks={int(y): str(int(y)) for y in sorted(df['Year'].unique())},
        tooltip={'placement': 'bottom', 'always_visible': True}
    ),
 
    html.Br(),
 
    # Charts (same as doctor's dcc.Graph usage)
    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='pie-chart'),
    dcc.Graph(id='scatter-chart'),
    dcc.Graph(id='line-chart'),
 
])
 
 
# ── Define callback (same structure as doctor's callback) ─────────────────────
@app.callback(
    [Output('bar-chart',     'figure'),
    Output('pie-chart',     'figure'),
    Output('scatter-chart', 'figure'),
    Output('line-chart',    'figure')],
    [Input('category-dropdown', 'value'),
    Input('region-dropdown',   'value'),
    Input('year-slider',       'value')]
)
def update_graphs(selected_category, selected_region, selected_year):
 
    # Filter data based on user selections
    filtered = df[df['Year'] == selected_year].copy()
 
    if selected_category != 'All':
        filtered = filtered[filtered['Category'] == selected_category]
 
    if selected_region != 'All':
        filtered = filtered[filtered['Region'] == selected_region]
 
    # Chart 1: Bar chart — Sales by Sub-Category
    bar_data = (
        filtered.groupby('Sub-Category')['Sales']
        .sum().reset_index()
        .sort_values('Sales', ascending=False)
    )
    fig1 = px.bar(
        bar_data,
        x='Sub-Category',
        y='Sales',
        color='Sales',
        color_continuous_scale='Greens',
        title=f'Sales by Sub-Category ({selected_year})',
        text='Sales',
        template='plotly_white'
    )
    fig1.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>'
    )
    fig1.update_layout(
        xaxis_tickangle=-40,
        coloraxis_showscale=False,
        xaxis_title='Sub-Category',
        yaxis_title='Total Sales ($)'
    )
 
    # Chart 2: Pie chart — Sales share by Category
    pie_data = filtered.groupby('Category')['Sales'].sum().reset_index()
    fig2 = px.pie(
        pie_data,
        values='Sales',
        names='Category',
        title=f'Sales Distribution by Category ({selected_year})',
        color_discrete_sequence=['#1B5E20', '#388E3C', '#81C784'],
        hole=0.35,
        template='plotly_white'
    )
    fig2.update_traces(
        hovertemplate='<b>%{label}</b><br>Sales: $%{value:,.0f}'
                    '<br>Share: %{percent}<extra></extra>'
    )
 
    # Chart 3: Scatter chart — Sales vs Profit (same concept as doctor's iris scatter)
    fig3 = px.scatter(
        filtered,
        x='Sales',
        y='Profit',
        color='Category',
        color_discrete_sequence=['#1B5E20', '#66BB6A', '#A5D6A7'],
        hover_name='Product Name',
        hover_data={'Sales': ':$,.0f', 'Profit': ':$,.0f', 'Region': True},
        title=f'Sales vs Profit ({selected_year})',
        opacity=0.6,
        template='plotly_white'
    )
    fig3.add_hline(
        y=0,
        line_dash='dash',
        line_color='red',
        annotation_text='Loss Zone ↓',
        annotation_position='bottom right',
        annotation_font_color='red'
    )
    fig3.update_layout(
        xaxis_title='Sales ($)',
        yaxis_title='Profit ($)'
    )
 
    # Chart 4: Line chart — Monthly Sales Trend
    monthly = (
        filtered.set_index('Order Date')
        .resample('ME')['Sales']
        .sum().reset_index()
    )
    monthly.columns = ['Order Date', 'Sales']
    fig4 = px.line(
        monthly,
        x='Order Date',
        y='Sales',
        title=f'Monthly Sales Trend ({selected_year})',
        markers=True,
        color_discrete_sequence=['#2E7D32'],
        template='plotly_white'
    )
    fig4.update_traces(
        hovertemplate='<b>%{x|%B %Y}</b><br>Sales: $%{y:,.0f}<extra></extra>'
    )
    fig4.update_layout(
        xaxis_title='Month',
        yaxis_title='Total Sales ($)'
    )
 
    return fig1, fig2, fig3, fig4
 
 
# ── Run the app (same as doctor's run_server) ─────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
 