import pandas as pd
import os

db = '../../03 - Database/'


#----------------------------------------------------------------------------------------------------

#Functions

#load reference file
def get_df_reference_geography():
    file_path = f'./reference/'
    file_name = 'GeographyReference.xlsx'
    df_reference = pd.read_excel(f'{file_path}/{file_name}')
    return(df_reference)

#load reference file
def get_df_reference_disciplines():
    file_path = f'./reference/'
    file_name = 'DisciplineLookupFieldsForApp.xlsx'
    df_reference = pd.read_excel(f'{file_path}/{file_name}')
    return(df_reference)

#load df_supply
def get_df_supply(accreditor):
    file_path = f'{db}/02-Staging/ProgramDirectoryNormalizedAndFiltered'
    last_updated_file = os.listdir(file_path)[-1][0:7]
    file_name = f'{last_updated_file} - {accreditor} Normalized Program Directory.xlsx'
    df_supply = pd.read_excel(f'{file_path}/{file_name}')
    return(df_supply)


#load df_demand
def get_df_demand():
    file_path = f'{db}/02-Staging/MarketDemand'
    last_updated_file = os.listdir(file_path)[-1]
    df_demand = pd.read_excel(f'{file_path}/{last_updated_file}')
    return(df_demand)


#load df_demand_detail
def get_df_demand_detail():
    file_path = f'{db}/02-Staging/PMPCombinedFcastDetail'
    last_updated_file = os.listdir(file_path)[-1]
    df_demand = pd.read_excel(f'{file_path}/{last_updated_file}')
    return(df_demand)



def table_regional_demand(df_supply, df_demand, discipline, status_list, avg_grad_class_size):

    #step 1: filter and apply graduate estimate
    df_step_supply = df_supply.loc[df_supply['StatusNorm'].isin(status_list)]
    df_step_supply = df_step_supply.groupby(['Region', 'StatusNorm'])[['Program']].nunique().reset_index()
    df_step_supply['Graduates'] = df_step_supply['Program'] * avg_grad_class_size

    #step 2: prepare demand table
    df_step_demand = df_demand.loc[df_demand['Discipline'] == discipline]
    df_step_demand = df_step_demand.groupby(['Region'])[['AvgAnnualOpenings']].sum().reset_index()

    #step 3: combine and aggregate (for "outlook")
    df_final = pd.merge(df_step_supply, df_step_demand, on='Region', how='right')
    x = {'Program': 'sum', 'Graduates': 'sum', 'AvgAnnualOpenings': 'max'}
    df_final = df_final.groupby(['Region']).agg(x).reset_index()

    #step 4: add estimated graduates entering market, then clean and save
    df_final['SatisfiedDemand%'] = round(df_final['Graduates'] / df_final['AvgAnnualOpenings'],4)
    df_final = df_final.sort_values(by='SatisfiedDemand%', ascending=False)

    #clean up
    df_final['Graduates'] = df_final['Graduates'].astype(int)
    df_final['SatisfiedDemand%'] = (round(df_final['SatisfiedDemand%'],3)*100).astype(int)
    
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