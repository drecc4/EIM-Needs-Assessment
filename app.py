import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import os

from functions.plots import plot_programs_on_scatter_map, plot_states_in_region
from functions.tables import *

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
st.sidebar.title('EIM Needs Assessment Generator Tool')
st.sidebar.markdown("""---""")

#USer Inputs
st.sidebar.write('**User Inputs**')
st.sidebar.caption('Complete the form below to populate the needs assessment template')


#User Selected Drivers
discipline_abbreviation = st.sidebar.selectbox("What discipline?", ('DPT', 'OTD', 'SLP', 'OD')) #leaving PA off for now, need to fix issue with scatter map plot
university_program_full_name = st.sidebar.text_area("Who is the partner (full name)?", 'Roseman University of Health Sciences')
program_campus_state = st.sidebar.selectbox("In what state will they launch?", (get_state_list()),43)
program_campus_major_city = st.sidebar.selectbox("In what major city?", get_city_selection(program_campus_state))
#program_campus_major_city = st.sidebar.text_input("In what major city?", "San Antonio")
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
pmp_fcast_total_jobs_base_year_discipline = df_demand_detail_discipline.BaseYearJobEst.max()
pmp_fcast_total_jobs_projected_year_discipline = df_demand_detail_discipline.ProjectedYearJobEst.max()
pmp_fcast_total_annual_openings_discipline = df_demand_detail_discipline.EstJobChange.max()
pmp_fcast_avg_annual_openings_discipline = df_demand_detail_discipline.AvgAnnualOpenings.max()
pmp_fcast_job_growth_pct_discipline = df_demand_detail_discipline.EstJobChangePct.max()

#profession within Region (i.e. DPT in South)
df_demand_detail_region = df_demand_detail_discipline.loc[df_demand_detail_discipline['Region'] == program_campus_region]
pmp_fcast_total_jobs_base_year_region = df_demand_detail_region.BaseYearJobEst.sum()
pmp_fcast_total_jobs_projected_year_region = df_demand_detail_region.ProjectedYearJobEst.sum()
pmp_fcast_total_annual_openings_region = df_demand_detail_region.EstJobChange.sum()
pmp_fcast_avg_annual_openings_region = df_demand_detail_region.AvgAnnualOpenings.sum()

pmp_fcast_job_growth_pct_region = pmp_fcast_job_growth_pct_region = (df_demand_detail_region.EstJobChange.sum() / df_demand_detail_region.BaseYearJobEst.sum())
pmp_fcast_job_growth_pct_region = (round(pmp_fcast_job_growth_pct_region,3)*100).astype(int)

pmp_fcast_job_growth_pct_region_min = df_demand_detail_region.EstJobChangePct.min()
pmp_fcast_job_growth_pct_region_max = df_demand_detail_region.EstJobChangePct.max()


#profession within State (i.e. DPT in Texas)
df_demand_detail_state = df_demand_detail_discipline.loc[df_demand_detail_discipline['State'] == program_campus_state]
pmp_fcast_total_jobs_base_year_state = df_demand_detail_state.BaseYearJobEst.max()
pmp_fcast_total_jobs_projected_year_state = df_demand_detail_state.ProjectedYearJobEst.max()
pmp_fcast_total_annual_openings_state = df_demand_detail_state.EstJobChange.max()
pmp_fcast_avg_annual_openings_state = df_demand_detail_state.AvgAnnualOpenings.max()
pmp_fcast_job_growth_pct_state = df_demand_detail_state.EstJobChangePct.max()


#replace with dynamic values later!
bls_supply_current = '258,200'
bls_median_pay_current = '$91,010'


#-----------------------------------------------------------------------------------------------------------

#call supply tables from tables.pt
df_supply = get_df_supply(discipline_accreditor)




#-----------------------------------------------------------------------------------------------------------

#Report

#header
st.header(f'**{professional_industry} Needs Assessment**')
st.subheader(f'{university_program_full_name}')
st.write(f'prepared on: {date_prepared}')
st.markdown("""---""")

#section 1
st.subheader(f'**Projected Growth in Needed {professional_abbreviation} Professionals**')
st.write(
    f'''
    **{university_program_full_name}** is proposing to increase access to **{professional_education}** education on a 
    national scale by developing a hybrid {discipline_name_with_abbreviation} Program at its 
    **{program_campus_state}** campus in the **{program_campus_major_city}** area. **{program_campus_major_city}** *is centrally located 
    with an international airport and direct flight access from most cities around the country*, making it an ideal location 
    for a hybrid program that will recruit students from both a regional and a national applicant pool. A thorough study 
    of the national, regional, and local need for a **{discipline_abbreviation}** program as been performed.

''')

st.markdown(' ')

#--------------------------------------------------------------------------------------------------------------------

#section 2
st.subheader(f'**National Outlook**')

#Plot 1: US Scatter Map of All Program Locations
summary_table_country = table_state_demand(df_supply, df_demand,professional_abbreviation, 'All', ['Accredited', 'Developing'], avg_grad_class_size)
summary_plot_country = plot_programs_on_scatter_map(df_supply, summary_table_country, 'Outlook')
st.caption(f"*Plot 1: Outlook of Accredited + Developing {discipline_abbreviation} Programs*")
st.write(summary_plot_country)
st.markdown(' ')

st.write(
    f'''
    According to the Bureau of Labor Statistics, there were **{bls_supply_current}** **{professional_title}s** in the U.S.,
    with a median pay of **{bls_median_pay_current}**. Employment of **{professional_abbreviation}s** is projected to grow
    **{pmp_fcast_job_growth_pct_discipline}%** from **{pmp_fcast_year_start}** to **{pmp_fcast_year_end}** with 
    **{pmp_fcast_avg_annual_openings_discipline}** new job openings each year on average. This reflects a much faster growth rate
    than other occupations and places the **{professional_abbreviation}** profession as one of the fastest growing occupations
    in the nation.

''')

st.markdown(' ')

#Table 1: Regional Summary of Satisfied Demand

def highlight_selected_region(s):
    return ['background-color: #b5e6cf']*len(s) if s.Region == program_campus_region else ['background-color: white']*len(s)

##regional table summary
df_region_demand_current = table_regional_demand(df_supply, df_demand, professional_abbreviation, ['Accredited'], avg_grad_class_size)
df_region_demand_outlook = table_regional_demand(df_supply, df_demand, professional_abbreviation, ['Accredited', 'Developing'], avg_grad_class_size)

##split then combine
df_region_demand_current = df_region_demand_current[['Region', 'AvgAnnualOpenings', 'Program', 'SatisfiedDemand%']]
df_region_demand_current = df_region_demand_current.rename(columns={'Program': 'Programs(c)', 'SatisfiedDemand%':'Satisfied Demand(c)', 'AvgAnnualOpenings': 'Avg Annual New Jobs'})

df_region_demand_outlook = df_region_demand_outlook[['Region', 'Program', 'SatisfiedDemand%']]
df_region_demand_outlook = df_region_demand_outlook.rename(columns={'Program': 'Programs(o)', 'SatisfiedDemand%':'Satisfied Demand(o)'})

##combine
df_region_demand_combined = pd.merge(df_region_demand_current, df_region_demand_outlook, on='Region', how='left')
df_region_demand_combined = df_region_demand_combined.sort_values(by='Satisfied Demand(o)', ascending=True).reset_index(drop=True)
df_region_demand_combined['Rank'] = df_region_demand_combined.index+1
df_region_demand_combined = df_region_demand_combined[['Rank', 'Region', 'Avg Annual New Jobs', 'Programs(c)', 'Programs(o)', 'Satisfied Demand(c)', 'Satisfied Demand(o)']]
df_region_demand_combined.set_index('Rank', inplace=True)
st.caption(f"*Table 1: Regional Ranking of Unmet Need for {discipline_abbreviation} Programs in the U.S.*")
st.table(df_region_demand_combined.style.apply(highlight_selected_region, axis=1))
st.markdown(' ')

#--------------------------------------------------------------------------------------------------------------------

#section 3
st.subheader(f'**Regional & Local Outlook**')

st.write(
    f'''
    Projections Central indicates that **{program_campus_state}** and other {program_campus_region}ern states 
    are projected to experience a **{pmp_fcast_job_growth_pct_region}%**  increase in growth from **{pmp_fcast_year_start}** 
    to **{pmp_fcast_year_end}** (between **{pmp_fcast_job_growth_pct_region_min}%** to **{pmp_fcast_job_growth_pct_region_max}%**), 
    which significantly exceeds the national growth rate of **{pmp_fcast_job_growth_pct_discipline}%**. Employment prospects 
    for **{program_campus_state}** are highly favorable, therefore the need for **{professional_abbreviation}s** will remain 
    high for the next 5 to 10 years.

    For example, **{program_campus_state}** had **{pmp_fcast_total_jobs_base_year_state}** licensed **{professional_title}** 
    in **{pmp_fcast_year_start}** and is projecting a need for **{pmp_fcast_total_jobs_projected_year_state}** therapists 
    by the year **{pmp_fcast_year_end}** representing a **{pmp_fcast_job_growth_pct_state}%** increase, which is significantly 
    higher than the national average. **{professional_abbreviation}** salaries for the region are in-line 
    with national trends (Table 1).

''')
st.markdown(' ')


#Plot 2: bar plot for selected region, by state
df_state_demand_current = table_state_demand(df_supply, df_demand_detail_region, professional_abbreviation, program_campus_region, ['Accredited'], avg_grad_class_size)
df_state_demand_outlook = table_state_demand(df_supply, df_demand_detail_region, professional_abbreviation, program_campus_region, ['Accredited', 'Developing'], avg_grad_class_size)

summary_barplot_country = plot_states_in_region(df_state_demand_current, df_state_demand_outlook)
st.caption(f"*Plot 2: Satisfied Demand for {discipline_abbreviation} Programs in the {program_campus_region}ern U.S.*")
st.write(summary_barplot_country)
st.markdown(' ')


#--------------------------------------------------------------------------------------------------------------------

#section 4
st.subheader(f'**Educational Outlook**')
st.write(
    f'''
    Despite the expansion in the number of **{discipline_abbreviation}** programs nationally, programs have been unable to keep pace with employment 
    demand and student interest with **total applicants** (**qualified applicants**) applicants vying for **avg admitted students** placements 
    in the average **{discipline_abbreviation}** program. **{discipline_accreditor}'s** website shows there are currently *number of program in region* 
    accredited **{discipline_abbreviation}** programs in the region. As shown in **Table 2**, there are currently only **annual graduates** 
    seats available for DPT students in the Western U.S., when there is a projected need of **{pmp_fcast_avg_annual_openings_region}**
    professionals in this region annually. **(Table 2)**. Therefore, less than **regionally satisfied demand** of the projected employment demand
    is being satisfied by the current level of **{discipline_abbreviation}** program capacity.

''')

st.markdown(' ')

def highlight_selected_state(s):
    return ['background-color: #b5e6cf']*len(s) if s.StateCode == program_campus_state_code else ['background-color: white']*len(s)

#Table 2: summart of states within selected region
##split then combine
df_state_demand_current_a = df_state_demand_current[['StateCode', 'AvgAnnualOpenings', 'Program', 'SatisfiedDemand']]
df_state_demand_current_a = df_state_demand_current_a.rename(columns={'Program': 'Programs(c)', 'SatisfiedDemand':'Satisfied Demand(c)', 'AvgAnnualOpenings': 'Avg Annual New Jobs'})

df_state_demand_outlook_b = df_state_demand_outlook[['StateCode', 'Program', 'SatisfiedDemand']]
df_state_demand_outlook_b = df_state_demand_outlook_b.rename(columns={'Program': 'Programs(o)', 'SatisfiedDemand':'Satisfied Demand(o)'})

##combine
df_state_demand_combined = pd.merge(df_state_demand_current_a, df_state_demand_outlook_b, on='StateCode', how='left')
df_state_demand_combined = df_state_demand_combined.sort_values(by='Satisfied Demand(o)', ascending=True).reset_index(drop=True)
df_state_demand_combined['Rank'] = df_state_demand_combined.index+1
df_state_demand_combined = df_state_demand_combined[['Rank', 'StateCode', 'Avg Annual New Jobs', 'Programs(c)', 'Programs(o)', 'Satisfied Demand(c)', 'Satisfied Demand(o)']]
df_state_demand_combined.set_index('Rank', inplace=True)

df_state_demand_combined['Satisfied Demand(c)'] = (round(df_state_demand_combined['Satisfied Demand(c)'],3)*100).astype(int)
df_state_demand_combined['Satisfied Demand(o)'] = (round(df_state_demand_combined['Satisfied Demand(o)'],3)*100).astype(int)

st.caption(f"*Table 2: State Ranking of Unmet Need for {discipline_abbreviation} Programs in the U.S.*")
st.table(df_state_demand_combined.style.apply(highlight_selected_state, axis=1))
#df_state_demand_combined.set_index('StateCode', inplace=True) --> fix later!
st.markdown(' ')

#--------------------------------------------------------------------------------------------------------------------

#section 5
st.subheader(f'**Population Demographics**')
st.write(
    f'''
    According to the U.S. Census Bureau, the U.S. is expected to grow in population by 78 million in the next four decades 
    from 326 to 404 million (1.8 million growth per year). The demand for additional healthcare professionals by 2030 is fueled in part 
    by the large number of aging baby boomers, who are staying more active later in life than their counterparts of previous generations. 
    The number of individuals older than 65 is expected to double from 49 million to 95 million by 2060. The year 2030 marks a demographic 
    turning point in the U.S. as all baby boomers will be over 65 years of age. This will expand the size of the older population to 25% 
    compared to 15% today. This means that one in every four Americans is expected to be of retirement age. In 2035, the older population 
    will outnumber children for the first time in US history. Life expectancy is 83.5 years for women and 79.5 for men. Older adults are 
    more likely to experience heart attacks, strokes, and mobility-related injuries that require extensive medical and rehabilitation services. 
    In addition, a number of chronic conditions such as diabetes and obesity have become more prevalent in recent years. More healthcare 
    professionals will be needed to help these patients maintain their mobility and manage the effects of chronic conditions.

''')

st.markdown(' ')

#--------------------------------------------------------------------------------------------------------------------

#section 6
st.subheader(f'**Healthcare Reform**')
st.write(
    f'''
    Given the opioid epidemic and well documented over utilization of high-cost procedures such as surgery and diagnostic imaging, 
    non-physician healthcare professionals are projected to be a cost-effective solution within healthcare reform. Advances in medical 
    technology have increased the use of outpatient surgery to treat a variety of injuries and illnesses. Medical and technological 
    developments also are expected to permit a greater percentage of trauma victims and newborns with birth defects to survive, creating 
    additional demand for medical and rehabilitative care. Non-physician healthcare professionals will continue to play an important role 
    in helping these patients recover more quickly from surgery. Job opportunities are expected to be robust for non-physician healthcare 
    professionals in all settings. Job prospects should be particularly strong in acute-care hospitals, skilled-nursing facilities, and 
    orthopedic settings, where the elderly are most often treated. Job prospects should be especially favorable in rural areas because 
    many non-physician healthcare professionals live in highly populated urban and suburban areas.

''')

st.markdown(' ')

#--------------------------------------------------------------------------------------------------------------------

#section 7
st.subheader(f'**Hybrid Education Model**')
st.write(
    f'''
    Graduate healthcare education is currently faced with extensive challenges such as a shortage of qualified faculty and quality 
    clinical education/externship sites, the inability to meet the education and healthcare needs of rural communities, and the unsustainable 
    cost of education. The COVID-19 pandemic has further magnified these challenges and highlighted the need for programs to be delivered in a 
    hybrid, accelerated format that increases flexibility, improves access, reduces student debt by assisting graduates getting into the 
    workforce sooner, meets workforce demands, and impacts health care in underserved communities by increasing diversity and keeping students 
    connected to the communities where they live.
    
    This highly differentiated program addresses many of the current challenges because of the innovative hybrid, accelerated model. Our hybrid, 
    accelerated curriculum will leverage best-in-class educational technology, with online coursework being delivered by faculty in a highly 
    interactive and engaging environment. Synchronous and asynchronous learning activities will be utilized to foster student discovery. Onsite 
    lab instruction will be provided in an immersive, highly organized, well-executed, and active hands-on learning environment that is critical 
    to psychomotor skill development. This educational model allows students and faculty to live anywhere in the country and commute to the 
    campus for onsite immersion lab experiences. Students will also participate in highly structured, full-time clinical education experiences. 

''')


st.markdown("""---""")


#-----------------------------------------------------------------------------------------------------------

#section 8
st.subheader(f'**References**')
st.write(
    f'''
    Bureau of Labor Statistics, U.S. Department of Labor, Occupational Outlook Handbook,
    Physical Therapists, on the Internet at https://www.bls.gov/ooh/healthcare/physical-therapists.htm

    CAPTE Aggregate Data 2019-2020 - https://www.capteonline.org/globalassets/capte-docs/aggregate-data/2019-2020-aggregate-pt-program-data.pdf 

    CAPTE Directory of Physical Therapy Programs, https://www.capteonline.org/programs

    Projections Central, Long-Term Occupational Projections (2018-2028), https://projectionscentral.org/Projections/LongTerm

    U.S. Census Bureau Quick Facts - https://www.census.gov/quickfacts

''')

st.markdown(' ')