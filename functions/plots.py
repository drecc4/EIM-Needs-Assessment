import glob
import json
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from urllib.request import urlopen
import pandas as pd
import streamlit as st

#---------------------------------------------------------------------------------------------------------------

plot_style = {
    'margin': dict(l=0, r=0, b=50, t=50, pad=0),
    'showlegend':False,
    'paper_bgcolor':'rgb(250,250,250)',
    'plot_bgcolor':'rgb(250,250,250)',
    'geo_bgcolor':'rgb(250,250,250)',
    'title_font_size': 26,
    'title_xanchor': 'center',
    'font_family': 'Arial',
    'font_color': '#171717',
    'geo_scope':'usa',
    'geo_projection_type':'albers usa',
    'geo_showlakes':True, # lakes,
    'geo_showsubunits':True,
    'geo_showframe':False,
    'geo_showland':True,
}

#---------------------------------------------------------------------------------------------------------------

#Plot #1: Scatter Map Plot (All Locations for Program, Colored by Status)
@st.cache
def plot_programs_on_scatter_map(df_scatter, df_state_demand, scope):

    #step 1: split into two tables for easier control over styling
    df_plot_a = df_scatter.loc[df_scatter['StatusNorm'] == 'Accredited'].dropna()
    df_plot_b = df_scatter.loc[df_scatter['StatusNorm'] == 'Developing'].dropna()

    #step 2: create chlorpleth map
    
    #step 2a: prepare table with regional satisfied demand
    #!!logic doesnt consider scope, not huge deal since regions won't change much in current vs outlook, but add later!
    df_temp = df_state_demand.groupby(['Region'])[['Graduates', 'AvgAnnualOpenings']].sum().reset_index()
    df_temp['RegionalSatisfiedDemand'] = round(df_temp['Graduates'] / df_temp['AvgAnnualOpenings'],3)
    lookup_satisfied_demand = dict(zip(df_temp.Region, df_temp.RegionalSatisfiedDemand))
    df_state_demand['RegionalSatisfiedDemand'] = df_state_demand['Region'].map(lookup_satisfied_demand)
    
    #step 2b: create plot fig
    fig = go.Figure(data=go.Choropleth(
        locations=df_state_demand['StateCode'],
        z = df_state_demand['RegionalSatisfiedDemand'].astype(float),
        locationmode = 'USA-states',
        marker_line_color='#134a44',
        marker_line_width = 1,
        colorscale = [[0, 'rgb(165, 219, 194)'], [1, 'rgb(18, 63, 90)']],
        #colorscale='Cividis',
        colorbar_thickness=20,
        showscale=False,
    ))

    
    #step 3: create scatter plot
    
    if scope == 'Outlook':

        #Accredited Programs
        fig.add_scattergeo(
            lon = df_plot_a['Lng'],
            lat = df_plot_a['Lat'],
            text = df_plot_a['Program'],
            name = 'Current (c)',
            mode = 'markers',
            marker_color='#FDC3AB',
            marker_line_color='black',
            marker_line_width=1.5,
            marker_size=10
        )
        
        #Developing Programs
        fig.add_scattergeo(
            lon = df_plot_b['Lng'],
            lat = df_plot_b['Lat'],
            text = df_plot_b['Program'],
            name = 'Outlook (o)',
            mode = 'markers',
            marker_color='#e86733',
            marker_line_color='black',
            marker_line_width=1.5,
            marker_size=10
        )
        
        #for title
        title_subheader = 'Accredited and Developing Programs'
    
    else:
        
        #Accredited Programs
        fig.add_scattergeo(
            lon = df_plot_a['Lng'],
            lat = df_plot_a['Lat'],
            text = df_plot_a['Program'],
            mode = 'markers',
            marker_color='#FDC3AB',
            marker_line_color='black',
            marker_line_width=1.5,
            marker_size=10
        )
        
        #for title
        title_subheader = 'Accredited Programs'
    
    
    #update plot layout
    fig.update_layout(plot_style)
    fig.update_layout(
        height=525,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.05,
            xanchor="center",
            x=0.5
        )
    )

    return(fig)

#Plot #2: Bar Chart of Satisfied Demand by State
@st.cache
def plot_states_in_region(df_current, df_outlook):
    
    #step 1: prepare table with change metric
    
    df_plot = pd.merge(df_current, df_outlook[['StateCode', 'SatisfiedDemand']], 
                       on='StateCode', how='left', suffixes=('_Accredited', '_Outlook'))

    df_plot['SatisfiedDemand_Chg'] = df_plot['SatisfiedDemand_Outlook'] - df_plot['SatisfiedDemand_Accredited']
    df_plot = df_plot.sort_values(by='SatisfiedDemand_Outlook', ascending=False)

    discipline = df_plot.Discipline.max()
    region = df_plot.Region.max()

    #------------------------------------------------------------------------------------------------

    #step 2: create chart

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_plot['StateCode'],
        y=df_plot['SatisfiedDemand_Accredited'],
        #text=round(df_plot['SatisfiedDemand_Accredited'],2),
        #texttemplate='%{text:.0%}',
        name='Current (c)',
        #textposition='outside',
        marker_color='rgba(18, 63, 90, 1.0)',
        marker_line_color='rgba(18, 63, 90, 1.0)',
        marker_line_width=2
    ))

    fig.add_trace(go.Bar(
        x=df_plot['StateCode'],
        y=df_plot['SatisfiedDemand_Chg'],
        text=round(df_plot['SatisfiedDemand_Chg'],2),
        texttemplate='+%{text:.0%}',
        name='Outlook (o)',
        textposition='outside',
        marker_color='rgba(107, 207, 161, 0.8)',
        marker_line_color='rgba(107, 207, 161, 1.0)',
        marker_line_width=2
    ))


    fig.add_hline(y=1.0, line_width=2.0, line_dash="dash", line_color="#171717", annotation_font_size=13,
                  annotation_text='100% of Demand Satisfied')
    
    fig.update_traces(textfont_size=12)
    fig.update_yaxes(range=[0, 2.05])

    #update plot layout
    fig.update_layout(
        yaxis_tickformat = '0.0%',
        bargap=0.15,
        font_size=12,
        barmode='stack',
        xaxis_tickangle=0,
        margin=dict(l=80, r=60, b=90, t=40, pad=1),
        paper_bgcolor='rgb(250,250,250)',
        plot_bgcolor='rgb(250,250,250)',
        geo_bgcolor='rgb(250,250,250)',
        title_font_size = 26,
        title_xanchor = 'center',
        font_family = 'Arial',
        font_color = 'black',
        legend=dict(
            font_size=12,
            orientation="h",
            yanchor="bottom",
            y=-0.19,
            xanchor="right",
            x=0.65)
    )


    return(fig)
