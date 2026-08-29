import streamlit as st

st.title("Grade Decider")
st.write("Enter your marks to determine your grade.")
marks = st.number_input("Enter your marks", min_value=0, max_value=100)

if st.button("Check Grade"):
    if marks >= 90:
        st.info("Grade: A")
    elif marks >= 80:
        st.info("Grade: B")
    elif marks >= 60:
        st.info("Grade: C")
    elif marks >= 40:
        st.info("Grade: D")
    else:
        st.error("Grade: F")