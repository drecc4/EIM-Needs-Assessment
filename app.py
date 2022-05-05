import streamlit as st
import pandas as pd
from code.pages import data
from code.pages import report
from PIL import Image


pages = {
    "Report": report,
    #"Source Data": data
}

#-------------------------------------------------------------------------------------------

#logo = pd.read_excel(f'./data/00-Ref/eim_logo.png')
logo = Image.open(f'./data/00-Ref/eim_logo_black.png')
st.sidebar.image(logo, width=40)
st.sidebar.title('Needs Assessment Tool')
st.sidebar.markdown(" ")

selection = st.sidebar.radio("Page Navigation", list(pages.keys()))
st.sidebar.markdown("""---""")

page = pages[selection]
page.app()
