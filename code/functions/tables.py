import pandas as pd
import os
import streamlit as st

#----------------------------------------------------------------------------------------------------

#Functions

#load reference file
@st.cache
def get_df_reference_geography():
    file_path = './data/00-Ref/'
    file_name = 'GeographyReference.xlsx'
    df_reference = pd.read_excel(f'{file_path}/{file_name}')
    return(df_reference)

#load reference file
@st.cache
def get_df_reference_city_list():
    file_path = f'./data/00-Ref/'
    file_name = 'USALargest200Cities.xlsx'
    df_reference = pd.read_excel(f'{file_path}/{file_name}')
    return(df_reference)

#load reference file
@st.cache
def get_df_reference_disciplines():
    file_path = f'./data/00-Ref/'
    file_name = 'DisciplineLookupFieldsForApp.xlsx'
    df_reference = pd.read_excel(f'{file_path}/{file_name}')
    return(df_reference)


#load df_demand
@st.cache
def get_df_demand(fcast_range):
    file_path = f'./data/02-Processed/MarketDemand'
    last_updated_file = os.listdir(file_path)[-1]
    df_demand = pd.read_excel(f'{file_path}/{last_updated_file}')
    df_demand = df_demand.loc[df_demand['ForecastRange'] == fcast_range]
    df_demand = df_demand.loc[df_demand['StateCode'] != 'USA']
    return(df_demand)


#load df_demand_detail
@st.cache
def get_df_demand_detail(fcast_range):
    file_path = f'./data/02-Processed/PMPCombinedFcastDetail'
    last_updated_file = os.listdir(file_path)[-1]
    df_demand = pd.read_excel(f'{file_path}/{last_updated_file}')
    df_demand = df_demand.loc[df_demand['Forecast'] == fcast_range]
    df_demand = df_demand.loc[df_demand['StateCode'] != 'USA']
    return(df_demand)


def table_regional_demand(df_supply, df_demand, discipline, status_list, avg_grad_class_size):

    #step 1: filter and apply graduate estimate
    df_step_supply = df_supply.loc[df_supply['StatusNorm'].isin(status_list)]
    df_step_supply = df_step_supply.groupby(['Region', 'StatusNorm'])[['Program']].nunique().reset_index()
    df_step_supply['Graduates'] = df_step_supply['Program'] * avg_grad_class_size

    #step 2: prepare demand table
    df_step_demand = df_demand.loc[df_demand['Discipline'] == discipline]
    df_step_demand = df_step_demand.groupby(['Region'])[[f'AvgAnnualOpenings']].sum().reset_index()

    #step 3: combine and aggregate (for "outlook")
    df_final = pd.merge(df_step_supply, df_step_demand, on='Region', how='right')
    x = {'Program': 'sum', 'Graduates': 'sum', 'AvgAnnualOpenings': 'max'}
    df_final = df_final.groupby(['Region']).agg(x).reset_index()

    #step 4: add estimated graduates entering market, then clean and save
    df_final['SatisfiedDemand%'] = round(df_final['Graduates'] / df_final['AvgAnnualOpenings'],4)
    df_final = df_final.sort_values(by='SatisfiedDemand%', ascending=False)

    #clean up
    df_final['Graduates'] = df_final['Graduates'].astype(int)
    df_final['SatisfiedDemand%'] = (round(df_final['SatisfiedDemand%'],3)*100)
        
    return(df_final)


def table_state_demand(df_supply, df_demand, discipline, region, status_list, avg_grad_class_size):
    
    #notes:
    #-use "All" for no region filter

    #step 1: filter and apply graduate estimate
    df_step_supply = df_supply.loc[df_supply['StatusNorm'].isin(status_list)]

    #condition allows for "All" states to be plotted
    if region != 'All':
        df_step_supply = df_step_supply.loc[df_step_supply['Region'] == region]
    else:
        pass

    df_step_supply = df_step_supply.groupby(['State', 'StateCode','Region', 'StatusNorm'])[['Program']].nunique().reset_index()
    df_step_supply['Graduates'] = df_step_supply['Program'] * avg_grad_class_size

    #step 2: prepare demand table
    if region == 'All':
        df_step_demand = df_demand.loc[df_demand['Discipline'] == discipline]
    else:
        df_step_demand = df_demand.loc[df_demand['Discipline'] == discipline]
        df_step_demand = df_demand.loc[df_demand['Region'] == region]

    df_step_demand = df_step_demand.groupby(['State', 'StateCode', 'Discipline'])[['AvgAnnualOpenings']].sum().reset_index()

    #step 3: combine and aggregate (for "outlook")
    df_final = pd.merge(df_step_demand, df_step_supply, on=['StateCode','State'], how='left')
    x = {'Program': 'sum', 'Graduates': 'sum', 'AvgAnnualOpenings': 'max'}

    #fills region for nan values that resulted from 0 programs in territory
    df_final['Region'] = df_final['Region'].fillna(region)
    df_final['Program'] = df_final['Program'].fillna(0).astype(int)
    df_final['Graduates'] = df_final['Graduates'].fillna(0).astype(int)

    df_final = df_final.groupby(['State', 'StateCode', 'Region', 'Discipline']).agg(x).reset_index()

    #step 4: add estimated graduates entering market, then clean and save
    df_final['SatisfiedDemand'] = round(df_final['Graduates'] / df_final['AvgAnnualOpenings'],4)
    df_final = df_final.sort_values(by='SatisfiedDemand', ascending=False)
    
    return(df_final)



#load Accreditor Annual Report
@st.cache
def get_accreditor_annual_report_data(discipline_abbreviation):
    file_path = f'./data/02-Processed/ProgramAnnualReportData'
    file_name = f'Annual_Report_Data.xlsx'
    df_raw = pd.read_excel(f'{file_path}/{file_name}')
    df_filtered = df_raw.loc[df_raw['Discipline'] == discipline_abbreviation]
    source_year = df_filtered.Year.max()
    df_filtered = df_filtered.loc[df_filtered['Year'] == source_year]
    return(df_filtered)


#Output Summary Table: Table 2: Regional Unment Demand
def report_output_table_2(df_region_demand_current, df_region_demand_outlook, avg_annual_openings_at_relative_geo):
    
    ##regional table summary --> generated from separate functions
    total_annual_new_graduates_current = df_region_demand_current.Graduates.sum()
    total_annual_new_graduates_outlook = df_region_demand_outlook.Graduates.sum()

    ##split then combine
    df_region_demand_current = df_region_demand_current[['Region', 'AvgAnnualOpenings', 'Program', 'SatisfiedDemand%']]
    df_region_demand_current = df_region_demand_current.rename(columns={'Program': 'Programs (c)', 'SatisfiedDemand%':'Satisfied Demand (c)', 'AvgAnnualOpenings': 'Avg Annual New Jobs'})
    df_region_demand_outlook = df_region_demand_outlook[['Region', 'Program', 'SatisfiedDemand%']]
    df_region_demand_outlook = df_region_demand_outlook.rename(columns={'Program': 'Programs (o)', 'SatisfiedDemand%':'Satisfied Demand (o)'})

    ##combine
    df_region_demand_combined = pd.merge(df_region_demand_current, df_region_demand_outlook, on='Region', how='left')
    df_region_demand_combined = df_region_demand_combined.sort_values(by='Satisfied Demand (o)', ascending=True).reset_index(drop=True)
    df_region_demand_combined = df_region_demand_combined[['Region', 'Avg Annual New Jobs', 'Programs (c)', 'Programs (o)', 'Satisfied Demand (c)', 'Satisfied Demand (o)']]

    #create total row
    df_totalrow_region = 'Total'
    df_totalrow_programsC = df_region_demand_combined['Programs (c)'].sum().astype(int)
    df_totalrow_programsO = df_region_demand_combined['Programs (o)'].sum().astype(int)
    df_totalrow_demandC = round(total_annual_new_graduates_current / df_region_demand_combined['Avg Annual New Jobs'].sum(),3)*100
    df_totalrow_demandO = round(total_annual_new_graduates_outlook / df_region_demand_combined['Avg Annual New Jobs'].sum(),3)*100
    df_totalrow_avgjobs = avg_annual_openings_at_relative_geo
    total_row = [df_totalrow_region, df_totalrow_avgjobs, df_totalrow_programsC, df_totalrow_programsO, df_totalrow_demandC, df_totalrow_demandO]

    #add total row to df
    df_region_demand_combined = df_region_demand_combined.append(pd.DataFrame([total_row], columns=df_region_demand_combined.columns), ignore_index=True)
    table_rows_with_index = len(list(df_region_demand_combined.Region))-1
    new_ranks = [str(x+1) for x in range(table_rows_with_index)]
    new_ranks.append("-")
    df_region_demand_combined['Rank'] = new_ranks
    df_region_demand_combined.set_index('Rank', inplace=True)
    df_region_demand_combined = df_region_demand_combined[['Region', 'Avg Annual New Jobs', 'Programs (c)', 'Programs (o)', 'Satisfied Demand (c)', 'Satisfied Demand (o)']]

    #clean up and write to app
    df_region_demand_combined['Avg Annual New Jobs'] = df_region_demand_combined['Avg Annual New Jobs'].fillna(0).astype(int)
    df_region_demand_combined['Satisfied Demand (c)'] = round(df_region_demand_combined['Satisfied Demand (c)'],3).astype(int).astype(str) + '%'
    df_region_demand_combined['Satisfied Demand (o)'] = round(df_region_demand_combined['Satisfied Demand (o)'],3).astype(int).astype(str) + '%'

    return(df_region_demand_combined)


#Output Summary Table: Table 2: Regional Unment Demand
def report_output_table_3(df_state_demand_current, df_state_demand_outlook, avg_annual_openings_at_relative_geo):
    
    #metrics
    total_annual_new_graduates_current = df_state_demand_current.Graduates.sum()
    total_annual_new_graduates_outlook = df_state_demand_outlook.Graduates.sum()

    ##split then combine
    df_state_demand_current_a = df_state_demand_current[['StateCode', 'AvgAnnualOpenings', 'Program', 'SatisfiedDemand']]
    df_state_demand_current_a = df_state_demand_current_a.rename(columns={'Program': 'Programs (c)', 'SatisfiedDemand':'Satisfied Demand (c)', 'AvgAnnualOpenings': 'Avg Annual New Jobs'})
    df_state_demand_outlook_b = df_state_demand_outlook[['StateCode', 'Program', 'SatisfiedDemand']]
    df_state_demand_outlook_b = df_state_demand_outlook_b.rename(columns={'Program': 'Programs (o)', 'SatisfiedDemand':'Satisfied Demand (o)'})

    ##combine
    df_state_demand_combined = pd.merge(df_state_demand_current_a, df_state_demand_outlook_b, on='StateCode', how='left')
    df_state_demand_combined = df_state_demand_combined.sort_values(by='Satisfied Demand (o)', ascending=True).reset_index(drop=True)
    df_state_demand_combined = df_state_demand_combined[['StateCode', 'Avg Annual New Jobs', 'Programs (c)', 'Programs (o)', 'Satisfied Demand (c)', 'Satisfied Demand (o)']]
    df_state_demand_combined['Satisfied Demand (c)'] = df_state_demand_combined['Satisfied Demand (c)'] * 100
    df_state_demand_combined['Satisfied Demand (o)'] = df_state_demand_combined['Satisfied Demand (o)'] * 100

    #create total row
    df_totalrow_state = 'Total'
    total_demand_in_region = df_state_demand_combined['Avg Annual New Jobs'].sum().astype(int)
    df_totalrow_programsC = df_state_demand_combined['Programs (c)'].sum().astype(int)
    df_totalrow_programsO = df_state_demand_combined['Programs (o)'].sum().astype(int)
    df_totalrow_demandC = round(total_annual_new_graduates_current / total_demand_in_region,2)*100
    df_totalrow_demandO = round(total_annual_new_graduates_outlook / total_demand_in_region,2)*100
    df_totalrow_avgjobs = avg_annual_openings_at_relative_geo
    total_row = [df_totalrow_state, df_totalrow_avgjobs, df_totalrow_programsC, df_totalrow_programsO, df_totalrow_demandC, df_totalrow_demandO]

    #add total row to df
    df_state_demand_combined = df_state_demand_combined.append(pd.DataFrame([total_row], columns=df_state_demand_combined.columns), ignore_index=True)
    table_rows_with_index = len(list(df_state_demand_combined.StateCode))-1
    new_ranks = [str(x+1) for x in range(table_rows_with_index)]
    new_ranks.append("-")
    df_state_demand_combined['Rank'] = new_ranks
    df_state_demand_combined.set_index('Rank', inplace=True)
    df_state_demand_combined = df_state_demand_combined[['StateCode', 'Avg Annual New Jobs', 'Programs (c)', 'Programs (o)', 'Satisfied Demand (c)', 'Satisfied Demand (o)']]

    #clean up and write to app
    df_state_demand_combined['Satisfied Demand (c)'] = round(df_state_demand_combined['Satisfied Demand (c)'],2).astype(int).astype(str) + '%'
    df_state_demand_combined['Satisfied Demand (o)'] = round(df_state_demand_combined['Satisfied Demand (o)'],2).astype(int).astype(str) + '%'
    df_state_demand_combined['Avg Annual New Jobs'] = df_state_demand_combined['Avg Annual New Jobs'].astype(int)

    return(df_state_demand_combined)



#New Tables Below ----------------------------------------------------------

def table_market_demand_detail_entire_country(df_demand, forecast_range, professional_abbreviation):
    df_temp = df_demand.loc[df_demand['ForecastRange'] == forecast_range]
    df_temp = df_temp.loc[df_temp['Discipline'] == professional_abbreviation]
    df_temp = df_temp.loc[df_temp['Region'] != 'USA']
    return(df_temp)

def table_market_demand_detail_states_within_selected_region(df_demand, forecast_range, professional_abbreviation, region):
    df_temp = df_demand.loc[df_demand['ForecastRange'] == forecast_range]
    df_temp = df_temp.loc[df_temp['Discipline'] == professional_abbreviation]
    df_temp = df_temp.loc[df_temp['Region'] == region]
    return(df_temp)

def table_market_demand_detail_region_agg(df_demand):
    agg_cols = {'BaseYearJobEst': 'sum', 'ProjectedYearJobEst': 'sum', 'EstJobChange': 'sum', 'AvgAnnualOpenings': 'sum'}
    df_temp = df_demand.groupby(['Region',]).agg(agg_cols).reset_index()
    return(df_temp)

@st.cache
def get_df_supply(accreditor):
    file_path = f'./data/02-Processed/ProgramDirectoryNormalizedAndFiltered'
    last_updated_file = os.listdir(file_path)[-1][0:7]
    file_name = f'{last_updated_file} - {accreditor} Normalized Program Directory.xlsx'
    df_supply = pd.read_excel(f'{file_path}/{file_name}')
    return(df_supply)

def table_market_supply_region_agg(df_supply, avg_grad_class_size, accreditation_status):
    df_temp = df_supply.loc[df_supply['StatusNorm'].isin(accreditation_status)]
    df_temp = df_temp.groupby(['Region', 'StatusNorm'])[['Program']].nunique().reset_index()
    df_temp = df_temp.pivot(index='Region', columns='StatusNorm', values='Program').fillna(0).astype(int).reset_index()
    df_temp['Program Outlook'] = df_temp['Accredited'] + df_temp['Developing']
    df_temp['Graduate Outlook'] = df_temp['Program Outlook'] * avg_grad_class_size
    return(df_temp)

def table_market_supply_state_agg(df_supply, avg_grad_class_size, accreditation_status):
    df_temp = df_supply.loc[df_supply['StatusNorm'].isin(accreditation_status)]
    df_temp = df_temp.groupby(['State', 'StatusNorm'])[['Program']].nunique().reset_index()
    df_temp = df_temp.pivot(index='State', columns='StatusNorm', values='Program').fillna(0).astype(int).reset_index()
    df_temp['Program Outlook'] = df_temp['Accredited'] + df_temp['Developing']
    df_temp['Graduate Outlook'] = df_temp['Program Outlook'] * avg_grad_class_size
    return(df_temp)

def table_projected_demand_by_region(df_demand, pmp_base_year, pmp_forecast_year):
    df_table = df_demand.rename(columns={
        'BaseYearJobEst': f'{pmp_base_year} Job Estimate', 'ProjectedYearJobEst': f'{pmp_forecast_year} Job Forecast', 
        'EstJobChange': 'Total Job Growth', 'AvgAnnualOpenings': 'Avg Annual Job Growth'})
    df_table = df_table.sort_values(by='Avg Annual Job Growth', ascending=False)
    return(df_table)

def table_unsatisfied_demand_by_region(df_demand, df_supply):
    df_table = pd.merge(df_demand, df_supply, on='Region', how='left')
    df_table = df_table[['Region', 'Accredited', 'Developing', 'Program Outlook', 'Graduate Outlook', 'AvgAnnualOpenings']]
    df_table = df_table.rename(columns={'AvgAnnualOpenings': 'Avg Annual New Jobs'})
    df_table['Unsatisfied Demand'] = df_table['Avg Annual New Jobs'] - df_table['Graduate Outlook']
    df_table['Unsatisfied Demand %'] = round(df_table['Unsatisfied Demand'] / df_table['Avg Annual New Jobs'],3)
    df_table = df_table.sort_values(by='Unsatisfied Demand %', ascending=False)
    return(df_table)

def table_unsatisfied_demand_by_state_within_selected_region(df_demand, df_supply):
    df_table = pd.merge(df_demand, df_supply, on='State', how='left')
    df_table = df_table[['State', 'Accredited', 'Developing', 'Program Outlook', 'Graduate Outlook', 'AvgAnnualOpenings']]
    df_table = df_table.rename(columns={'AvgAnnualOpenings': 'Avg Annual New Jobs'})
    df_table['Unsatisfied Demand'] = df_table['Avg Annual New Jobs'] - df_table['Graduate Outlook']
    df_table['Unsatisfied Demand %'] = round(df_table['Unsatisfied Demand'] / df_table['Avg Annual New Jobs'],3)
    df_table = df_table.sort_values(by='Unsatisfied Demand %', ascending=False)
    return(df_table)