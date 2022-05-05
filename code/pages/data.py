import streamlit as st

#local modules required
from code.functions.content import *
from code.functions.tables import *
from code.functions.plots import *
from code.processing.process_pmp_data import *


#-------------------------------------------------------------------------------------------

#General Functions

def select_accreditor_based_on_profession(professional_abbreviation):
    lookup_accreditor = {
        'PT': 'CAPTE',
        'OT': 'ACOTE',
        'PA': 'ARCPA',
        'OD': 'ASCO',
        'SLP': 'ASHA'
    }

    accreditor = lookup_accreditor[professional_abbreviation]
    return(accreditor)

def default_avg_grad_class_size(professional_abbreviation):
    lookup_avg_graduating_class_size = {
        'PT': 46,
        'OT': 42,
        'PA': 44,
        'OD': 74, 
        'SLP': 35 #need to verify
    }
    avg_class_size = lookup_avg_graduating_class_size[professional_abbreviation]
    return(avg_class_size)


#-------------------------------------------------------------------------------------------

def app():
    st.title('Source Data')
    st.write('This page contains the underlying source data used in the Needs Assment Tool')
    st.markdown("""---""")
    st.markdown(" ")

    # #local variables (user inputs)
    professional_abbreviation = st.sidebar.selectbox("Profession", ('PT', 'OT', 'PA', 'SLP', 'OD'))
    region = st.sidebar.selectbox("Region", ('Northeast', 'Midwest', 'South', 'West'))
    

    #global variables
    accreditation_status = ['Accredited', 'Developing']
    pmp_base_year = 2020
    pmp_forecast_year = 2028
    avg_grad_class_size = st.sidebar.number_input('Avg graduating class size', min_value=20, max_value=200, value=default_avg_grad_class_size(professional_abbreviation), step=2)
    forecast_range = st.sidebar.selectbox("Forecast Range", ('ST', 'LT'))
    accreditor = select_accreditor_based_on_profession(professional_abbreviation)
    

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    st.subheader('Demand Data')
    st.markdown(" ")
    
    with st.expander('PMP Market Demand Data Detail, Complete Data Set', expanded=False):
        df_market_demand_raw = run_process_to_update_pmp_data()
        df_market_demand_raw = df_market_demand_raw[['State', 'StateCode', 'Region', 'Discipline', 'ForecastRange', 'BaseYear', 'BaseYearJobEst', 'ProjectedYear', 'ProjectedYearJobEst', 'EstJobChange', 'EstJobChangePct', 'AvgAnnualOpenings']]
        record_count = len(df_market_demand_raw.index)
        st.caption(f'Total Records: {record_count}')
        st.dataframe(df_market_demand_raw.style.background_gradient(subset=['EstJobChange', 'EstJobChangePct', 'AvgAnnualOpenings']), height=600)

    with st.expander('PMP Market Demand Data Detail, All States in USA', expanded=False):
        df_market_demand_country = table_market_demand_detail_entire_country(df_market_demand_raw, forecast_range, professional_abbreviation)
        record_count = len(df_market_demand_country.index)
        st.caption(f'Total Records: {record_count}')
        st.dataframe(df_market_demand_country.style.background_gradient(), height=600)

    with st.expander('PMP Market Demand Data Detail, States within Region', expanded=False):
        df_market_demand_state_agg = table_market_demand_detail_states_within_selected_region(df_market_demand_raw, forecast_range, professional_abbreviation, region)
        record_count = len(df_market_demand_state_agg.index)
        st.caption(f'Total Records: {record_count}')
        st.dataframe(df_market_demand_state_agg.style.background_gradient(), height=600)

    with st.expander('PMP Market Demand Data, Regional Aggregation', expanded=False):
        df_market_demand_region_agg = table_market_demand_detail_region_agg(df_market_demand_country)
        record_count = len(df_market_demand_region_agg.index)
        st.caption(f'Total Records: {record_count}')
        st.dataframe(df_market_demand_region_agg.style.background_gradient(), height=600)

    st.markdown(" ")
    st.markdown(" ")

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    st.subheader('Supply Data')
    st.markdown(" ")

    with st.expander(f'{accreditor} Program Directory, Complete Data Set', expanded=False):
        df_supply = get_df_supply(accreditor)
        record_count = len(df_supply.index)
        st.caption(f'Total Records: {record_count}')
        st.dataframe(df_supply, height=600)

    with st.expander(f'Program Directory, Regional Aggregation', expanded=False):
        df_market_supply_region_agg = table_market_supply_region_agg(df_supply, avg_grad_class_size, accreditation_status)
        st.dataframe(df_market_supply_region_agg.style.background_gradient(), height=600)

    with st.expander(f'Program Directory, State Aggregation', expanded=False):
        df_market_supply_state_agg = table_market_supply_state_agg(df_supply, avg_grad_class_size, accreditation_status)
        st.dataframe(df_market_supply_state_agg.style.background_gradient(), height=600)

    st.markdown(" ")
    st.markdown(" ")

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    st.subheader('Report Tables')
    st.markdown(" ")

    with st.expander(f'Table 1: Projected Growth in PT Employment by Region', expanded=False):
        df_table1 = table_projected_demand_by_region(df_market_demand_region_agg, pmp_base_year, pmp_forecast_year)
        df_table1 = df_table1.rename(columns={'BaseYearJobEst': f'{pmp_base_year} Job Estimate', 'ProjectedYearJobEst': f'{pmp_forecast_year} Job Forecast', 'EstJobChange': 'Total Job Growth', 'AvgAnnualOpenings': 'Avg Annual Job Growth'})
        st.dataframe(df_table1.style.background_gradient(subset=['Total Job Growth', 'Avg Annual Job Growth']), height=600)

    with st.expander(f'Table 2: Summary of Unsatisfied Demand, Regional Aggregation', expanded=False):
        df_table2 = table_unsatisfied_demand_by_region(df_market_supply_region_agg, df_market_demand_region_agg)
        record_count = len(df_table2.index)
        st.caption(f'Total Records: {record_count}')
        st.dataframe(df_table2.style.background_gradient(subset=['Unsatisfied Demand', 'Unsatisfied Demand %']), height=600)

    with st.expander(f'Table 3: Summary of Unsatisfied Demand, State Detail Within Region', expanded=False):
        df_table3 = table_unsatisfied_demand_by_state_within_selected_region(df_market_demand_state_agg, df_market_supply_state_agg)
        record_count = len(df_table3.index)
        st.caption(f'Total Records: {record_count}')
        st.dataframe(df_table3.style.background_gradient(subset=['Unsatisfied Demand', 'Unsatisfied Demand %']), height=600)

