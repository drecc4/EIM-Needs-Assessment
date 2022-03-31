import streamlit as st
import numpy


#Section 1: Header
def show_section_one(professional_industry, professional_abbreviation, university_program_full_name, date_prepared):
    section_title = st.header(f'{professional_industry} ({professional_abbreviation}) Needs Assessment')
    section_subtitle = st.subheader(f'**{university_program_full_name}**')
    section_date = st.write(f'prepared on: {date_prepared}')
    return(section_title, section_subtitle, section_date)


#Section 2: Projected Growth in Needed Professionals
def show_section_two(professional_abbreviation, university_program_full_name, professional_education, 
discipline_name_with_abbreviation, program_campus_state, program_campus_major_city, discipline_abbreviation):
    section_title = st.subheader(f'**Projected Growth in Needed {professional_abbreviation} Professionals**')
    
    section_body = st.write(
        f'''
        {university_program_full_name} is proposing to increase access to {professional_education} education on a 
        national scale by developing a hybrid {discipline_name_with_abbreviation} Program at its 
        {program_campus_state} campus in the {program_campus_major_city} area. {program_campus_major_city} *is centrally located 
        with an international airport and direct flight access from most cities around the country*, making it an ideal location 
        for a hybrid program that will recruit students from both a regional and a national applicant pool. A thorough study 
        of the national, regional, and local need for a {discipline_abbreviation} program as been performed.
        ''')

    return(section_title, section_body)



#Section 3: National Outlook
#title
def show_section_three_header():
    section_title = st.subheader(f'**National Outlook**')
    return(section_title)

#body
def show_section_three_body(bls_supply_current, professional_title, bls_median_pay_current, professional_abbreviation, 
pmp_fcast_job_growth_pct_discipline, pmp_fcast_year_start, pmp_fcast_year_end, pmp_fcast_avg_annual_openings_discipline):

    #string formatting for dollars and thousands separator
    pmp_fcast_avg_annual_openings_discipline_str = "{:,}".format(pmp_fcast_avg_annual_openings_discipline)
    bls_median_pay_current_str = "${:,}".format(bls_median_pay_current)
    bls_supply_current_str = "{:,}".format(bls_supply_current)
    pmp_fcast_job_growth_pct_discipline_str = "{:.1%}".format(pmp_fcast_job_growth_pct_discipline)
    
    section_body = st.write(
        f'''
        According to the Bureau of Labor Statistics, there were {bls_supply_current_str} {professional_title}s in the U.S.,
        with a median pay of {bls_median_pay_current_str}. Employment of {professional_abbreviation}s is projected to grow
        {pmp_fcast_job_growth_pct_discipline_str} from {pmp_fcast_year_start} to {pmp_fcast_year_end} with 
        {pmp_fcast_avg_annual_openings_discipline_str} new job openings each year on average. This reflects a much faster growth rate
        than other occupations and places the {professional_abbreviation} profession as one of the fastest growing occupations
        in the nation.
        ''')

    return(section_body)



#Section 4: Regional & Local Outlook 
#title
def show_section_four_header():
    section_title = st.subheader(f'**Regional & Local Outlook**')
    return(section_title)

#body, paragraphs conditioned on "which significantly exceeds.."
def show_section_four_body(program_campus_state, program_campus_region, pmp_fcast_job_growth_pct_region, pmp_fcast_year_start,
pmp_fcast_year_end, pmp_fcast_job_growth_pct_region_min, pmp_fcast_job_growth_pct_region_max, pmp_fcast_job_growth_pct_discipline, 
professional_abbreviation, pmp_fcast_total_jobs_base_year_state, professional_title, pmp_fcast_total_jobs_projected_year_state,
pmp_fcast_job_growth_pct_state):

    #string formatting for dollars and thousands separator
    pmp_fcast_total_jobs_base_year_state_str = "{:,}".format(pmp_fcast_total_jobs_base_year_state)
    pmp_fcast_total_jobs_projected_year_state_str = "{:,}".format(pmp_fcast_total_jobs_projected_year_state)
    pmp_fcast_job_growth_pct_region_str = "{:.1%}".format(pmp_fcast_job_growth_pct_region)
    pmp_fcast_job_growth_pct_discipline_str = "{:.1%}".format(pmp_fcast_job_growth_pct_discipline)

    #conditional statements
    section_body_exceeds = (f'''
        Projections Central indicates that {program_campus_state} and other {program_campus_region}ern states 
        are projected to experience a {pmp_fcast_job_growth_pct_region_str}  increase in growth from {pmp_fcast_year_start} 
        to {pmp_fcast_year_end} (between {pmp_fcast_job_growth_pct_region_min}% to {pmp_fcast_job_growth_pct_region_max}%), 
        which significantly exceeds the national growth rate of {pmp_fcast_job_growth_pct_discipline_str}. Employment prospects 
        for {program_campus_state} are highly favorable, therefore the need for {professional_abbreviation}s will remain 
        high for the next 10 years.

        For example, {program_campus_state} had {pmp_fcast_total_jobs_base_year_state_str} licensed {professional_title}s 
        in {pmp_fcast_year_start} and is projecting a need for {pmp_fcast_total_jobs_projected_year_state_str} therapists 
        by the year {pmp_fcast_year_end} representing a {pmp_fcast_job_growth_pct_state}% increase, which is significantly 
        higher than the national average. {professional_abbreviation} salaries for the region are in-line 
        with national trends (Table 1).
        ''')

    section_body_equal = (f'''
        Projections Central indicates that {program_campus_state} and other {program_campus_region}ern states 
        are projected to experience a {pmp_fcast_job_growth_pct_region_str}  increase in growth from {pmp_fcast_year_start} 
        to {pmp_fcast_year_end} (between {pmp_fcast_job_growth_pct_region_min}% to {pmp_fcast_job_growth_pct_region_max}%), 
        which aligns with the national growth rate of {pmp_fcast_job_growth_pct_discipline_str}. Employment prospects 
        for {program_campus_state} are highly favorable, therefore the need for {professional_abbreviation}s will remain 
        high for the next 10 years.

        For example, {program_campus_state} had {pmp_fcast_total_jobs_base_year_state_str} licensed {professional_title}s 
        in {pmp_fcast_year_start} and is projecting a need for {pmp_fcast_total_jobs_projected_year_state_str} therapists 
        by the year {pmp_fcast_year_end} representing a {pmp_fcast_job_growth_pct_state}% increase, which is significantly 
        higher than the national average. {professional_abbreviation} salaries for the region are in-line 
        with national trends (Table 1).
        ''')

    section_body_under = (f'''
        Projections Central indicates that {program_campus_state} and other {program_campus_region}ern states 
        are projected to experience a {pmp_fcast_job_growth_pct_region_str}  increase in growth from {pmp_fcast_year_start} 
        to {pmp_fcast_year_end} (between {pmp_fcast_job_growth_pct_region_min}% to {pmp_fcast_job_growth_pct_region_max}%),
        while the national growth rate is projected to experience {pmp_fcast_job_growth_pct_discipline_str} growth. Employment prospects 
        for {program_campus_state} are highly favorable, therefore the need for {professional_abbreviation}s will remain 
        high for the next 10 years.

        For example, {program_campus_state} had {pmp_fcast_total_jobs_base_year_state_str} licensed {professional_title}s 
        in {pmp_fcast_year_start} and is projecting a need for {pmp_fcast_total_jobs_projected_year_state_str} therapists 
        by the year {pmp_fcast_year_end} representing a {pmp_fcast_job_growth_pct_state}% increase, which is significantly 
        higher than the national average. {professional_abbreviation} salaries for the region are in-line 
        with national trends (Table 1).
        ''')

    #logic for conditional statement
    delta_growth_rate = pmp_fcast_job_growth_pct_region - pmp_fcast_job_growth_pct_discipline

    if delta_growth_rate >= .05:
        section_body = section_body_exceeds
    elif delta_growth_rate <= -.05:
        section_body = section_body_under
    else:
        section_body = section_body_equal
            
    return(st.write(section_body))



#Section 5: Educational Outlook
#title
def show_section_five_header():
    section_title = st.subheader(f'**Educational Outlook**')
    return(section_title)

#body
def show_section_five_body(discipline_abbreviation, annual_report_total_applicants, annual_report_total_applicants_qualified, 
annual_report_avg_annual_admitted_students, discipline_accreditor, regional_total_accredited_programs_current, regional_total_annual_new_grads,
program_campus_region, regional_avg_new_jobs, regional_satisfied_demand_current):

    #string formatting for dollars and thousands separator
    regional_avg_new_jobs_str = "{:,}".format(regional_avg_new_jobs)
    annual_report_total_applicants_str = "{:,}".format(annual_report_total_applicants)
    annual_report_total_applicants_qualified_str = "{:,}".format(annual_report_total_applicants_qualified)
    regional_total_annual_new_grads_str = "{:,}".format(regional_total_annual_new_grads)
    regional_total_accredited_programs_current_str = "{:,}".format(regional_total_accredited_programs_current)
    
    section_body = st.write(
        f'''
        Despite the expansion in the number of {discipline_abbreviation} programs nationally, programs have been unable to keep pace with employment 
        demand and student interest with {annual_report_total_applicants_str} ({annual_report_total_applicants_qualified_str} qualified applicants) applicants vying 
        for {annual_report_avg_annual_admitted_students} placements in the average {discipline_abbreviation} program. {discipline_accreditor}'s website 
        shows there are currently {regional_total_accredited_programs_current_str} accredited {discipline_abbreviation} programs in the region. As shown in Table 2, 
        there are currently only {regional_total_annual_new_grads_str} seats available for DPT students in the {program_campus_region}ern U.S., when there is a projected 
        need of {regional_avg_new_jobs_str} professionals in this region annually. (Table 2). Therefore, less than {regional_satisfied_demand_current} regionally satisfied demand 
        of the projected employment demand is being satisfied by the current level of {discipline_abbreviation} program capacity.
        '''
        )

    return(section_body)

# df_region_demand_selected = df_region_demand_combined.loc[df_region_demand_combined['Region'] == program_campus_region]
# regional_avg_new_jobs = df_region_demand_selected['Avg Annual New Jobs']
# regional_total_accredited_programs_outlook = df_region_demand_selected['Programs (o)']
# regional_satisfied_demand_current = df_region_demand_selected['Satisfied Demand (c)']
# regional_satisfied_demand_outlook = df_region_demand_selected['Satisfied Demand (o)']



#Section 6: Population Demographics
#title
def show_section_six_header():
    section_title = st.subheader(f'**Population Demographics**')
    return(section_title)

#body
def show_section_six_body():    
    section_body = st.write(
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
        '''
        )
    return(section_body)



#Section 7: Healthcare Reform
#title
def show_section_seven_header():
    section_title = st.subheader(f'**Healthcare Reform**')
    return(section_title)

#body
def show_section_seven_body():    
    section_body = st.write(
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
        '''
        )
    return(section_body)



#Section 8: Hybrid Education Model
#title
def show_section_eight_header():
    section_title = st.subheader(f'**Hybrid Education Model**')
    return(section_title)

#body
def show_section_eight_body():    
    section_body = st.write(
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
        '''
        )
    return(section_body)



#Section 9: References
#title
def show_section_nine_header():
    section_title = st.subheader(f'**References**')
    return(section_title)

#body
def show_section_nine_body(df_reference_table, discipline_abbreviation):
    #!condition on discipline selection
    df_filtered_on_discipline = df_reference_table.loc[df_reference_table['Discipline'] == discipline_abbreviation]
    referenceOne = df_filtered_on_discipline.ReferenceOne.item()
    referenceTwo = df_filtered_on_discipline.ReferenceTwo.item()
    referenceThree = df_filtered_on_discipline.ReferenceThree.item()
    referenceFour = df_filtered_on_discipline.ReferenceFour.item()
    referenceFive = df_filtered_on_discipline.ReferenceFive.item()
    return(referenceOne, referenceTwo, referenceThree, referenceFour, referenceFive)