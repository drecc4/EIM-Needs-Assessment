import glob
import json
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from urllib.request import urlopen

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

#Scatter Map Plot (All Locations for Program, Colored by Status)
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

    return(fig)
