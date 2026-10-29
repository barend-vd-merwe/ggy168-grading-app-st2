import streamlit as st


home_page = st.Page(
    "pages/home.py",
    title = "Dashboard",
    default = True
)

section_a = st.Page(
    "pages/section-a.py",
    title = "Section A — Theory"
)

section_b = st.Page(
    "pages/section-b.py",
    title = "Section B — Cartography"
)

pages = st.navigation({
    "Main": [home_page],
    "Semester Test 2" : [section_a, section_b]
})

st.set_page_config(page_title="GGY 168 Grading App", layout="wide")
pages.run()
