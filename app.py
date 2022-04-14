from hashlib import new
from plistlib import FMT_XML
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import os
from fpdf import FPDF
import base64

#local modules required
#from code.functions import *
from code.functions.content import *
from code.functions.tables import *
from code.functions.plots import *


#call data tables from tables.pt
#!supply table further down in logic (dependent on user input)
df_reference_geo = get_df_reference_geography()
df_reference_cities = get_df_reference_city_list()
df_reference_discipline = get_df_reference_disciplines()
df_demand = get_df_demand()
df_demand_detail = get_df_demand_detail()


#-------------------------------------------------------------------------------------------------------------------------------

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

#-------------------------------------------------------------------------------------------------------------------------------

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

#-------------------------------------------------------------------------------------------------------------------------------

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
bls_supply_current = df_lookup_discipline.BLSTotalSupply2020.max()
bls_median_pay_current = df_lookup_discipline.BLSMedianPay2020.max()
bls_median_job_growth_10yr_fcast = df_lookup_discipline.BLS10YrJobOutlook2020.max()

#demand drivers
df_demand_detail_period = df_demand_detail.loc[df_demand_detail['Forecast'] == 'ST']
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
df_annual_report_data = get_accreditor_annual_report_data(discipline_abbreviation)
annual_report_data_last_updated_year = df_annual_report_data.Year.max()
discipline_total_accredited_programs_current = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Discipline_Total_Accredited_Programs'].max()
annual_report_avg_applicants = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Cohort_Avg_Applicants_Overall'].max()
annual_report_avg_applicants_qualified = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Cohort_Avg_Applicants_Qualified'].max()
annual_report_avg_annual_admitted_students = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Cohort_Avg_Applicants_Enrolled'].max()
annual_report_total_annual_new_grads = df_annual_report_data.Value.loc[df_annual_report_data['NormalizedLabel'] == 'Discipline_Total_Graduates'].max()
annual_report_total_applicants = annual_report_avg_applicants * discipline_total_accredited_programs_current
annual_report_total_applicants_qualified = annual_report_avg_applicants_qualified * discipline_total_accredited_programs_current
annual_report_total_annual_admitted_students = annual_report_avg_annual_admitted_students * discipline_total_accredited_programs_current


#call supply tables from tables.pt
df_supply = get_df_supply(discipline_accreditor)


#-------------------------------------------------------------------------------------------------------------------------------

#Report (New)

#!Section 1: Header
show_section_one(professional_industry, professional_abbreviation, university_program_full_name, date_prepared)
st.markdown("""---""")



#!Section 2: Projected Growth in Needed Professionals
show_section_two(professional_abbreviation, university_program_full_name, professional_education, discipline_name_with_abbreviation, program_campus_state, program_campus_major_city, discipline_abbreviation)
st.markdown(' ')


#-------------------------------------------------------------------------------------------------------------------------------

#!Section 3: National Outlook
show_section_three_header()

show_section_three_body(bls_supply_current, professional_title, bls_median_pay_current, professional_abbreviation, pmp_fcast_job_growth_pct_discipline, pmp_fcast_year_start, pmp_fcast_year_end, pmp_fcast_avg_annual_openings_discipline)
st.markdown(' ')


#-------------------------------------------------------------------------------------------------------------------------------

#!Section 4: Regional & Local Outlook
show_section_four_header()
show_section_four_body(program_campus_state, program_campus_region, pmp_fcast_job_growth_pct_region, pmp_fcast_year_start, pmp_fcast_year_end, pmp_fcast_job_growth_pct_region_min, pmp_fcast_job_growth_pct_region_max, pmp_fcast_job_growth_pct_discipline, professional_abbreviation, pmp_fcast_total_jobs_base_year_state, professional_title, pmp_fcast_total_jobs_projected_year_state, pmp_fcast_job_growth_pct_state)
st.markdown(' ')

#Table 1
#!!new table added by JC!!
#**need to move to function in separate file**
def highlight_selected_state(s):
    return ['background-color: #b5e6cf']*len(s) if s.State == program_campus_state else ['background-color: white']*len(s)

df_new_table_1 = df_demand_detail_region[['State', 'BaseYearJobEst', 'ProjectedYearJobEst', 'EstJobChangePct']]
df_new_table_1['BaseYearJobEst'] = df_new_table_1['BaseYearJobEst'].astype(int)
df_new_table_1['ProjectedYearJobEst'] = df_new_table_1['ProjectedYearJobEst'].astype(int)
df_new_table_1['EstJobChangePct'] = df_new_table_1['EstJobChangePct'].astype(int).astype(str) + '%'

# Inject CSS with Markdown
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """


st.markdown(hide_table_row_index, unsafe_allow_html=True)

st.markdown(' ')
st.table(df_new_table_1.style.apply(highlight_selected_state, axis=1))
st.caption(f"Table 1. Projected % Growth in PT Employment 2018-2028 in the {program_campus_region}ern U.S.")
st.markdown(' ')
st.markdown(' ')


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#!Section 5: Educational Outlook

#region tables
df_region_demand_current = table_regional_demand(df_supply, df_demand, professional_abbreviation, ['Accredited'], avg_grad_class_size)
df_region_demand_outlook = table_regional_demand(df_supply, df_demand, professional_abbreviation, ['Accredited', 'Developing'], avg_grad_class_size)
df_region_demand_combined = report_output_table_2(df_region_demand_current, df_region_demand_outlook, pmp_fcast_avg_annual_openings_discipline)

#metrics from region table
df_region_demand_selected = df_region_demand_combined.loc[df_region_demand_combined['Region'] == program_campus_region]

regional_avg_new_jobs = df_region_demand_selected['Avg Annual New Jobs'].max()
regional_total_accredited_programs_current = df_region_demand_selected['Programs (c)'].max()
regional_total_accredited_programs_outlook = df_region_demand_selected['Programs (o)'].max()
regional_satisfied_demand_current = df_region_demand_selected['Satisfied Demand (c)'].max()
regional_satisfied_demand_outlook = df_region_demand_selected['Satisfied Demand (o)'].max()
regional_total_annual_new_grads = regional_total_accredited_programs_current * avg_grad_class_size

#Section Five, Part 1 of 3
show_section_five_header()
show_section_five_body_a(discipline_accreditor, discipline_abbreviation, discipline_total_accredited_programs_current)
st.markdown(' ')

#Plot 1: US Scatter Map of All Program Locations
summary_table_country = table_state_demand(df_supply, df_demand,professional_abbreviation, 'All', ['Accredited', 'Developing'], avg_grad_class_size)
summary_plot_country = plot_programs_on_scatter_map(df_supply, summary_table_country, 'Outlook')
st.markdown(' ')
st.write(summary_plot_country)
st.caption(f"*Figure 1: Currently Accredited + Developing {discipline_abbreviation} Programs*")
st.markdown(' ')
st.markdown(' ')


#Section Five, Part 2 of 3

show_section_five_body_b(discipline_abbreviation, program_campus_region, professional_abbreviation)
st.markdown(' ')

#Table 2
def highlight_selected_region(s):
    return ['background-color: #b5e6cf']*len(s) if s.Region == program_campus_region else ['background-color: white']*len(s)

st.table(df_region_demand_combined.style.apply(highlight_selected_region, axis=1))
st.caption(f"*Table 2: Unmet Need for {discipline_abbreviation} Programs in the U.S. by Region (c: current, o: outlook)*")
st.markdown(' ')


#Section Five, Part 3 of 3

#Body
show_section_five_body_c(discipline_abbreviation, annual_report_total_applicants, annual_report_total_applicants_qualified, 
annual_report_avg_annual_admitted_students, discipline_accreditor, regional_total_accredited_programs_current, regional_total_annual_new_grads,
program_campus_region, regional_avg_new_jobs, program_campus_state, professional_abbreviation, 
regional_satisfied_demand_current, regional_satisfied_demand_outlook)
st.markdown(' ')

#state tables
df_state_demand_current = table_state_demand(df_supply, df_demand_detail_region, professional_abbreviation, program_campus_region, ['Accredited'], avg_grad_class_size)
df_state_demand_outlook = table_state_demand(df_supply, df_demand_detail_region, professional_abbreviation, program_campus_region, ['Accredited', 'Developing'], avg_grad_class_size)
df_state_demand_combined = report_output_table_3(df_state_demand_current, df_state_demand_outlook, pmp_fcast_avg_annual_openings_state)


#Table 3: summary of states within selected region
def highlight_selected_state(s):
    return ['background-color: #b5e6cf']*len(s) if s.StateCode == program_campus_state_code else ['background-color: white']*len(s)

st.table(df_state_demand_combined.style.apply(highlight_selected_state, axis=1))
st.caption(f"*Table 3: State Ranking of Unmet Need for {discipline_abbreviation} Programs in the {program_campus_region}ern U.S. (c: current, o:outlook)*")
st.markdown(' ')


#Plot 2: bar plot for selected region, by state
summary_barplot_country = plot_states_in_region(df_state_demand_current, df_state_demand_outlook)
st.markdown(' ')
st.write(summary_barplot_country)
st.caption(f"*Figure 2: Satisfied Demand for {discipline_abbreviation} Programs in the {program_campus_region}ern U.S.*")
st.markdown(' ')


#-------------------------------------------------------------------------------------------------------------------------------


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


#-------------------------------------------------------------------------------------------------------------------------------


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



