import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import os
from fpdf import FPDF
import base64

from functions.plots import plot_programs_on_scatter_map, plot_states_in_region
from functions.tables import *
from functions.content import *

#call data tables from tables.pt
#!supply table further down in logic (dependent on user input)
df_reference_geo = get_df_reference_geography()
df_reference_cities = get_df_reference_city_list()
df_reference_discipline = get_df_reference_disciplines()
df_demand = get_df_demand()
df_demand_detail = get_df_demand_detail()

#-----------------------------------------------------------------------------------------------------------

#lookup
lookup_avg_graduating_class_size = {
    'DPT': 46,
    'OTD': 42,
    'PA': 44,
    'OD': 74, 
    'SLP': 35 #need to verify
}

def default_avg_grad_class_size(disciplineabbreviation):
    return(lookup_avg_graduating_class_size[disciplineabbreviation])

def get_state_list():
    return(list(df_reference_geo.State))

def get_city_selection(selected_state):
    df_temp = df_reference_cities.loc[df_reference_cities['State'] == program_campus_state].sort_values(by='City')
    filtered_cities = list(df_temp.City)
    return(filtered_cities)

#-----------------------------------------------------------------------------------------------------------

#Sidebar

#logo = pd.read_excel(f'./reference/EIM_LOGO.png')
#st.image(logo, output_format='PNG')

st.sidebar.title('EIM Needs Assessment Tool')
st.sidebar.markdown("""---""")

#USer Inputs
st.sidebar.write('**User Inputs**')
st.sidebar.caption('Complete the form below to populate the needs assessment template')


#User Selected Drivers
discipline_abbreviation = st.sidebar.selectbox("Discipline", ('DPT', 'OTD', 'SLP', 'OD')) #leaving PA off for now, need to fix issue with scatter map plot
university_program_full_name = st.sidebar.text_area("Name of Partner", 'Roseman University of Health Sciences')
program_campus_state = st.sidebar.selectbox("Program launch state", (get_state_list()),43)
program_campus_major_city = st.sidebar.selectbox("Closest major city", get_city_selection(program_campus_state))
st.sidebar.markdown("""---""")


#Default Settings
st.sidebar.write('**Default Settings**')
st.markdown(' ')

avg_grad_class_size = st.sidebar.number_input(
    'Avg graduating class size', min_value=20, max_value=200, 
    value=default_avg_grad_class_size(discipline_abbreviation), step=2
)

#-----------------------------------------------------------------------------------------------------------

#Smarter Drivers

#general
date_prepared = dt.date.today()

#geography drivers
program_campus_region = df_reference_geo.Region.loc[df_reference_geo['State'] == program_campus_state].max()
program_campus_state_code = df_reference_geo['State Code'].loc[df_reference_geo['State'] == program_campus_state].max()

#discipline drivers
df_lookup_discipline = df_reference_discipline.loc[df_reference_discipline['Discipline'] == discipline_abbreviation]
professional_abbreviation = df_lookup_discipline.Abbreviation.max()
professional_industry = df_lookup_discipline.Industry.max()
professional_title = df_lookup_discipline.Title.max()
professional_education = df_lookup_discipline.Education.max()
discipline_name_with_abbreviation = df_lookup_discipline.FullNameWithAbbreviation.max()
discipline_accreditor = df_lookup_discipline.Accreditor.max()

#demand drivers
df_demand_detail_period = df_demand_detail.loc[df_demand_detail['Forecast'] == 'LT']
pmp_fcast_year_start = df_demand_detail_period.BaseYear.max()
pmp_fcast_year_end = df_demand_detail_period.ProjectedYear.max()

#entire country (i.e. DPT in USA)
df_demand_detail_discipline = df_demand_detail_period.loc[df_demand_detail_period['Discipline'] == professional_abbreviation]
df_demand_detail_discipline = df_demand_detail_discipline.loc[df_demand_detail_discipline['State'] == 'United States']
pmp_fcast_total_jobs_base_year_discipline = df_demand_detail_discipline.BaseYearJobEst.max()
pmp_fcast_total_jobs_projected_year_discipline = df_demand_detail_discipline.ProjectedYearJobEst.max()
pmp_fcast_total_annual_openings_discipline = df_demand_detail_discipline.EstJobChange.max()
pmp_fcast_avg_annual_openings_discipline = df_demand_detail_discipline.AvgAnnualOpenings.max()
pmp_fcast_job_growth_pct_discipline = round(df_demand_detail_discipline.EstJobChangePct.max()/100,3)


#profession within Region (i.e. DPT in South)
df_demand_detail_region = df_demand_detail_period.loc[df_demand_detail_period['Discipline'] == professional_abbreviation]
df_demand_detail_region = df_demand_detail_region.loc[df_demand_detail_region['Region'] == program_campus_region]
pmp_fcast_total_jobs_base_year_region = df_demand_detail_region.BaseYearJobEst.sum()
pmp_fcast_total_jobs_projected_year_region = df_demand_detail_region.ProjectedYearJobEst.sum()
pmp_fcast_total_annual_openings_region = df_demand_detail_region.EstJobChange.sum()
pmp_fcast_avg_annual_openings_region = df_demand_detail_region.AvgAnnualOpenings.sum()

pmp_fcast_job_growth_pct_region = (df_demand_detail_region.EstJobChange.sum() / df_demand_detail_region.BaseYearJobEst.sum())
pmp_fcast_job_growth_pct_region = (round(pmp_fcast_job_growth_pct_region,3))

pmp_fcast_job_growth_pct_region_min = df_demand_detail_region.EstJobChangePct.min()
pmp_fcast_job_growth_pct_region_max = df_demand_detail_region.EstJobChangePct.max()


#profession within State (i.e. DPT in Texas)
df_demand_detail_state = df_demand_detail_period.loc[df_demand_detail_period['Discipline'] == professional_abbreviation]
df_demand_detail_state = df_demand_detail_state.loc[df_demand_detail_state['State'] == program_campus_state]
pmp_fcast_total_jobs_base_year_state = df_demand_detail_state.BaseYearJobEst.max()
pmp_fcast_total_jobs_projected_year_state = df_demand_detail_state.ProjectedYearJobEst.max()
pmp_fcast_total_annual_openings_state = df_demand_detail_state.EstJobChange.max()
pmp_fcast_avg_annual_openings_state = df_demand_detail_state.AvgAnnualOpenings.max()
pmp_fcast_job_growth_pct_state = df_demand_detail_state.EstJobChangePct.max()


#annual report data - dynamic, based on selected accreditor
df_annual_report_data = get_accreditor_annual_report_data(discipline_accreditor)

discipline_total_accredited_programs_current = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Total_Accredited_Programs'].max()
annual_report_avg_applicants = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Avg_Total_Applicants'].max()
annual_report_avg_applicants_qualified = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Avg_Applicants_Qualified'].max()
annual_report_avg_annual_admitted_students = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Avg_Applicants_Enrolled'].max()
annual_report_total_annual_new_grads = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Total_Degrees_Conferred'].max()
annual_report_total_applicants = annual_report_avg_applicants * discipline_total_accredited_programs_current
annual_report_total_applicants_qualified = annual_report_avg_applicants_qualified * discipline_total_accredited_programs_current
annual_report_total_annual_admitted_students = annual_report_avg_annual_admitted_students * discipline_total_accredited_programs_current



#!!replace with dynamic values later!!
bls_supply_current = '258,200'
bls_median_pay_current = '$91,010'

#call supply tables from tables.pt
df_supply = get_df_supply(discipline_accreditor)


#-----------------------------------------------------------------------------------------------------------

#Report (New)

#!Section 1: Header
show_section_one(professional_industry, professional_abbreviation, university_program_full_name, date_prepared)
st.markdown("""---""")


#!Section 2: Projected Growth in Needed Professionals
show_section_two(professional_abbreviation, university_program_full_name, professional_education, discipline_name_with_abbreviation, program_campus_state, program_campus_major_city, discipline_abbreviation)
st.markdown(' ')


#!Section 3: National Outlook
show_section_three_header()

#plot 1: US Scatter Map of All Program Locations
summary_table_country = table_state_demand(df_supply, df_demand,professional_abbreviation, 'All', ['Accredited', 'Developing'], avg_grad_class_size)
summary_plot_country = plot_programs_on_scatter_map(df_supply, summary_table_country, 'Outlook')
st.caption(f"*Plot 1: Outlook of Accredited + Developing {discipline_abbreviation} Programs*")
st.write(summary_plot_country)
st.markdown(' ')

show_section_three_body(bls_supply_current, professional_title, bls_median_pay_current, professional_abbreviation, pmp_fcast_job_growth_pct_discipline, pmp_fcast_year_start, pmp_fcast_year_end, pmp_fcast_avg_annual_openings_discipline)
st.markdown(' ')

#table 1: Regional Summary of Satisfied Demand
#**need to move to function in separate file**

def highlight_selected_region(s):
    return ['background-color: #b5e6cf']*len(s) if s.Region == program_campus_region else ['background-color: white']*len(s)

##regional table summary
df_region_demand_current = table_regional_demand(df_supply, df_demand, professional_abbreviation, ['Accredited'], avg_grad_class_size)
df_region_demand_outlook = table_regional_demand(df_supply, df_demand, professional_abbreviation, ['Accredited', 'Developing'], avg_grad_class_size)
total_annual_new_graduates_current = df_region_demand_current.Graduates.sum()
total_annual_new_graduates_outlook = df_region_demand_outlook.Graduates.sum()

##split then combine
df_region_demand_current = df_region_demand_current[['Region', 'AvgAnnualOpenings', 'Program', 'SatisfiedDemand%']]
df_region_demand_current = df_region_demand_current.rename(columns={'Program': 'Programs (c)', 'SatisfiedDemand%':'Satisfied Demand (c)', 'AvgAnnualOpenings': 'Avg Annual New Jobs'})
df_region_demand_outlook = df_region_demand_outlook[['Region', 'Program', 'SatisfiedDemand%']]
df_region_demand_outlook = df_region_demand_outlook.rename(columns={'Program': 'Programs (o)', 'SatisfiedDemand%':'Satisfied Demand (o)'})

##combine & rank
df_region_demand_combined = pd.merge(df_region_demand_current, df_region_demand_outlook, on='Region', how='left')
df_region_demand_combined = df_region_demand_combined.sort_values(by='Satisfied Demand (o)', ascending=True).reset_index(drop=True)
df_region_demand_combined['Rank'] = df_region_demand_combined.index+1
df_region_demand_combined = df_region_demand_combined[['Rank', 'Region', 'Avg Annual New Jobs', 'Programs (c)', 'Programs (o)', 'Satisfied Demand (c)', 'Satisfied Demand (o)']]
df_region_demand_combined.set_index('Rank', inplace=True)

#create total row & add to df
df_totalrow_region = 'Total'
df_totalrow_programsC = df_region_demand_combined['Programs (c)'].sum()
df_totalrow_programsO = df_region_demand_combined['Programs (o)'].sum()
df_totalrow_demandC = round(total_annual_new_graduates_current / df_region_demand_combined['Avg Annual New Jobs'].sum(),3)*100
df_totalrow_demandO = round(total_annual_new_graduates_outlook / df_region_demand_combined['Avg Annual New Jobs'].sum(),3)*100
df_totalrow_avgjobs = pmp_fcast_avg_annual_openings_discipline
total_row = [df_totalrow_region, df_totalrow_avgjobs, df_totalrow_programsC, df_totalrow_programsO, df_totalrow_demandC, df_totalrow_demandO]
df_region_demand_combined = df_region_demand_combined.append(pd.DataFrame([total_row], columns=df_region_demand_combined.columns), ignore_index=True)

#clean up and write to app
df_region_demand_combined['Satisfied Demand (c)'] = df_region_demand_combined['Satisfied Demand (c)'].astype(int)
df_region_demand_combined['Satisfied Demand (o)'] = df_region_demand_combined['Satisfied Demand (o)'].astype(int)
st.caption(f"*Table 1: Regional Ranking of Unmet Need for {discipline_abbreviation} Programs in the U.S.*")
st.table(df_region_demand_combined.style.apply(highlight_selected_region, axis=1))
st.markdown(' ')


#!Section 4: Regional & Local Outlook
show_section_four_header()
show_section_four_body(program_campus_state, program_campus_region, pmp_fcast_job_growth_pct_region, pmp_fcast_year_start, pmp_fcast_year_end, pmp_fcast_job_growth_pct_region_min, pmp_fcast_job_growth_pct_region_max, pmp_fcast_job_growth_pct_discipline, professional_abbreviation, pmp_fcast_total_jobs_base_year_state, professional_title, pmp_fcast_total_jobs_projected_year_state, pmp_fcast_job_growth_pct_state)
st.markdown(' ')

#plot 2: bar plot for selected region, by state
df_state_demand_current = table_state_demand(df_supply, df_demand_detail_region, professional_abbreviation, program_campus_region, ['Accredited'], avg_grad_class_size)
df_state_demand_outlook = table_state_demand(df_supply, df_demand_detail_region, professional_abbreviation, program_campus_region, ['Accredited', 'Developing'], avg_grad_class_size)

summary_barplot_country = plot_states_in_region(df_state_demand_current, df_state_demand_outlook)
st.caption(f"*Plot 2: Satisfied Demand for {discipline_abbreviation} Programs in the {program_campus_region}ern U.S.*")
st.write(summary_barplot_country)
st.markdown(' ')


#!Section 5: Educational Outlook
show_section_five_header()
show_section_five_body(discipline_abbreviation, annual_report_total_applicants, annual_report_total_applicants_qualified, annual_report_avg_annual_admitted_students, discipline_accreditor, discipline_total_accredited_programs_current, annual_report_total_annual_new_grads, program_campus_region, pmp_fcast_avg_annual_openings_region)
st.markdown(' ')

#table 2: State Ranking of Unmet Need for DPT Programs in the U.S.
#**need to move to function in separate file**
def highlight_selected_state(s):
    return ['background-color: #b5e6cf']*len(s) if s.StateCode == program_campus_state_code else ['background-color: white']*len(s)

#Table 2: summart of states within selected region
##split then combine
df_state_demand_current_a = df_state_demand_current[['StateCode', 'AvgAnnualOpenings', 'Program', 'SatisfiedDemand']]
df_state_demand_current_a = df_state_demand_current_a.rename(columns={'Program': 'Programs (c)', 'SatisfiedDemand':'Satisfied Demand (c)', 'AvgAnnualOpenings': 'Avg Annual New Jobs'})

df_state_demand_outlook_b = df_state_demand_outlook[['StateCode', 'Program', 'SatisfiedDemand']]
df_state_demand_outlook_b = df_state_demand_outlook_b.rename(columns={'Program': 'Programs (o)', 'SatisfiedDemand':'Satisfied Demand (o)'})

##combine
df_state_demand_combined = pd.merge(df_state_demand_current_a, df_state_demand_outlook_b, on='StateCode', how='left')
df_state_demand_combined = df_state_demand_combined.sort_values(by='Satisfied Demand (o)', ascending=True).reset_index(drop=True)
df_state_demand_combined['Rank'] = df_state_demand_combined.index+1
df_state_demand_combined = df_state_demand_combined[['Rank', 'StateCode', 'Avg Annual New Jobs', 'Programs (c)', 'Programs (o)', 'Satisfied Demand (c)', 'Satisfied Demand (o)']]
df_state_demand_combined.set_index('Rank', inplace=True)

df_state_demand_combined['Satisfied Demand (c)'] = (round(df_state_demand_combined['Satisfied Demand (c)'],3)*100).astype(int)
df_state_demand_combined['Satisfied Demand (o)'] = (round(df_state_demand_combined['Satisfied Demand (o)'],3)*100).astype(int)

st.caption(f"*Table 2: State Ranking of Unmet Need for {discipline_abbreviation} Programs in the U.S.*")
st.table(df_state_demand_combined.style.apply(highlight_selected_state, axis=1))
#df_state_demand_combined.set_index('StateCode', inplace=True) --> fix later!
st.markdown(' ')


#!Section 6: Population Demographics
show_section_six_header()
show_section_six_body()
st.markdown(' ')

#!Section 7: Healthcare Reform
show_section_seven_header()
show_section_seven_body()
st.markdown(' ')

#!Section 8: Hybrid Education Model
show_section_eight_header()
show_section_eight_body()
st.markdown("""---""")

#!Section 9: References
show_section_nine_header()
reference_list = show_section_nine_body(df_reference_discipline, discipline_abbreviation)
return_references = [st.write(x) for x in reference_list if len(str(x))>20]
st.markdown(' ')


#-----------------------------------------------------------------------------------------------------------


#Testing

export_as_pdf = st.button("Export Report")

def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

if export_as_pdf:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(80, 20, "Test")
    
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")

    st.markdown(html, unsafe_allow_html=True)



