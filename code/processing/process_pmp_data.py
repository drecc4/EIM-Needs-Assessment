import os
import pandas as pd
import datetime
import streamlit as st

@st.cache
def run_process_to_update_pmp_data():

    #load regions table for reference
    file_path = './data/00-Ref'
    file_name = 'GeographyReference.xlsx'
    df_regions = pd.read_excel(f'{file_path}/{file_name}')

    #load pmp raw files
    file_path = './data/01-Raw/ProjectionsCentral/'
    recent_files = os.listdir(file_path)

    file_a = [x for x in recent_files if "Long" in x][0]
    file_b = [x for x in recent_files if "Short" in x][0]
    df_long = pd.read_excel(f'{file_path}/{file_a}')
    df_short = pd.read_excel(f'{file_path}/{file_b}')

    #filter tables on occupation
    occupation_names_to_include = [
        'Physical Therapists', 
        'Occupational Therapists', 
        'Physician Assistants',
        'Optometrists',
        'Speech-Language Pathologists'
    ]

    df_long = df_long.loc[df_long['Occupation Name'].isin(occupation_names_to_include)]
    df_long['ForecastRange'] = 'LT'
    df_short = df_short.loc[df_short['Occupation Name'].isin(occupation_names_to_include)]
    df_short['ForecastRange'] = 'ST'

    #combine tables
    df_combined = pd.concat([df_long, df_short])

    #rename columns
    header_names = {
        'State FIPS': 'StateFIPS',
        'Area Name': 'State',
        'Occupation Code': 'OccupationCode',
        'Occupation Name': 'OccupationName',
        'Base Year': 'BaseYear',
        'Base': 'BaseYearJobEst',
        'Projected Year': 'ProjectedYear',
        'Projection': 'ProjectedYearJobEst',
        'Change': 'EstJobChange',
        'Percent Change': 'EstJobChangePct',
        'Average Annual Openings': "AvgAnnualOpenings"
    }

    df_combined = df_combined.rename(columns=header_names)

    #pull in data from regional spreadheeet
    df_combined = pd.merge(df_combined, df_regions[['State', 'State Code', 'Region']], on='State', how='left').fillna('USA')
    df_combined = df_combined.rename(columns={'State Code': 'StateCode'})

    #add discipline abbreviation
    discipline_assignment = {
        'Physical Therapists': 'PT', 
        'Occupational Therapists': 'OT', 
        'Physician Assistants': 'PA',
        'Optometrists': 'OD',
        'Speech-Language Pathologists': 'SLP'
    }

    df_combined['Discipline'] = df_combined['OccupationName'].map(discipline_assignment)

    #filter tables on region --> exclude foreign territories
    exclude_foreign_territories = ['Puerto Rico', 'Virgin Islands']
    df_combined = df_combined.loc[~df_combined['State'].isin(exclude_foreign_territories)]

    #reorder columns
    new_column_order = [
        'StateFIPS',
        'State',
        'StateCode',
        'Region',
        'Discipline',
        'ForecastRange',
        'OccupationCode',
        'OccupationName',
        'BaseYear',
        'BaseYearJobEst',
        'ProjectedYear',
        'ProjectedYearJobEst',
        'EstJobChange',
        'EstJobChangePct',
        'AvgAnnualOpenings',
    ]
    df_combined = df_combined[new_column_order]

    #save file to directory
    date_today = datetime.date.today()
    date_year = date_today.year
    date_month = date_today.month
    path = './data/02-Processed/MarketDemand'
    df_combined.to_excel(f'{path}/{date_year}.{date_month} - PMP Combined Forecast With Detail.xlsx', index=False)

    return(df_combined)
