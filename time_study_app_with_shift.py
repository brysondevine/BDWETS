
import streamlit as st
import time
import random
import matplotlib.pyplot as plt
import pandas as pd

def generate_colour():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def show_add_element_ui():
    st.markdown("### ➕ Add a New Element")
    form_key = "add_element_form_master_key"
    with st.form(form_key):
        new_element = st.text_input("Enter element name")
        submitted = st.form_submit_button("Add Element")
        if submitted and new_element.strip():
            name = new_element.strip()
            if name not in st.session_state.elements:
                st.session_state.elements.append(name)
                st.session_state.element_colours[name] = generate_colour()
                st.success(f"Added element: {name}")
            else:
                st.warning("Element already exists.")

    if st.session_state.elements:
        st.markdown("### ✅ Current Elements:")
        for i, el in enumerate(st.session_state.elements, 1):
            st.markdown(f"{i}. **{el}**")
        if st.button("➡️ NEXT", key="next_btn_key"):
            st.session_state["start_timers"] = True

# ------------------- Session Setup -------------------
if "elements" not in st.session_state:
    st.session_state.elements = []
if "element_colours" not in st.session_state:
    st.session_state.element_colours = {}
if "start_timers" not in st.session_state:
    st.session_state["start_timers"] = False

st.title("⏱️ Time Study App")

# ------------------- Flow -------------------
if not st.session_state["start_timers"]:
    show_add_element_ui()
else:
    st.markdown("### ⏱️ Timing Mode")
    st.write("Start button logic would go here...")
