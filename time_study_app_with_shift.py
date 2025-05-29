import streamlit as st
import time
import pandas as pd
from datetime import timedelta, datetime
import random
import os
import matplotlib.pyplot as plt
from io import BytesIO

# ----------------- Session Setup -----------------
if 'log' not in st.session_state:
    st.session_state.log = []
if 'active_element' not in st.session_state:
    st.session_state.active_element = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'total_time' not in st.session_state:
    st.session_state.total_time = 0.0
if 'elements' not in st.session_state:
    st.session_state.elements = []
if 'element_colours' not in st.session_state:
    st.session_state.element_colours = {}
if 'save_mode' not in st.session_state:
    st.session_state.save_mode = "Single File"
if 'project_name' not in st.session_state:
    st.session_state.project_name = ""
if 'time_format' not in st.session_state:
    st.session_state.time_format = "MM:SS"
if 'shift' not in st.session_state:
    st.session_state.shift = ""

# ----------------- Utilities -----------------
def generate_colour():
    return f"#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(100, 255):02x}"

def format_time(seconds):
    if st.session_state.time_format == "HH:MM:SS":
        return str(timedelta(seconds=round(seconds, 3)))
    mins, secs = divmod(round(seconds, 3), 60)
    return f"{int(mins):02}:{secs:06.3f}"

def get_save_filename():
    base = st.session_state.project_name.replace(" ", "_").lower()
    if st.session_state.save_mode == "New File Per Day":
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"{base}_{date_str}.csv"
    return f"{base}_log.csv"

def create_excel(log_df, summary_df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        log_df.to_excel(writer, sheet_name='Time Log', index=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    return output.getvalue()

# ----------------- Sidebar Settings -----------------
st.sidebar.markdown("### ⏱️ Time Display Format")
st.session_state.time_format = st.sidebar.radio("Choose time format:", ["MM:SS", "HH:MM:SS"])

st.sidebar.markdown("### 💾 Save Mode")
st.session_state.save_mode = st.sidebar.radio("Choose how logs are saved:", ["Single File", "New File Per Day"])

# ----------------- Project Picker -----------------
if st.session_state.get("_trigger_rerun"):
    del st.session_state["_trigger_rerun"]
    st.rerun()

st.title("⏱️ Time Study App")

project_files = [f for f in os.listdir() if f.endswith(".csv")]
existing_projects = sorted(list({
    f.split("_log.csv")[0].replace("_", " ") if "_log.csv" in f
    else f.rsplit("_", 1)[0].replace("_", " ")
    for f in project_files
}))

st.markdown("### 🗂️ Select or Create a Project")
selected_project = st.selectbox("Choose existing or enter new", ["(New Project)"] + existing_projects)
manual_project = ""

if selected_project == "(New Project)":
    manual_project = st.text_input("Enter new project name (required)")
    if manual_project.strip():
        st.session_state.project_name = manual_project.strip()
else:
    st.session_state.project_name = selected_project

if not st.session_state.project_name:
    st.warning("Please enter or select a project name to begin.")
    st.stop()

# ----------------- Shift Selection -----------------
st.markdown("### 👷 Select Shift")
st.session_state.shift = st.selectbox("Select your current shift", ["", "Shift 1", "Shift 2", "Shift 3"])
if not st.session_state.shift:
    st.warning("Please select a shift to begin.")
    st.stop()

# ----------------- Load Previous Log -----------------
load_file = get_save_filename()
if os.path.exists(load_file) and not st.session_state.log:
    df_existing = pd.read_csv(load_file)
    st.session_state.log = df_existing.to_dict(orient="records")

# ----------------- Display Total Time -----------------
current_duration = 0
if st.session_state.active_element and st.session_state.start_time:
    current_duration = time.time() - st.session_state.start_time

total_recorded = st.session_state.total_time + current_duration
formatted_total = format_time(total_recorded)
st.subheader(f"🧮 Total Time for '{st.session_state.project_name}' — {st.session_state.shift}: **{formatted_total}** ({round(total_recorded, 3)} seconds)")


# ----------------- Mode Switch: Add Elements vs Timer -----------------
if not st.session_state.get("start_timers", False):
    if not st.session_state.get("start_timers", False):
    st.markdown("### ➕ Add a New Element")
    form_key = "add_element_form_master_key"  # completely static key to avoid duplicate errors"
        with st.form(form_key):
        new_element = st.text_input("Enter element name")
        submitted = st.form_submit_button("Add Element")
        if submitted and new_element.strip():
            name = new_element.strip()
            if name not in st.session_state.elements:
                st.session_state.elements.append(name)
                st.session_state.element_colours[name] = generate_colour()
                st.success(f"Added element: {name}")
                st.session_state["_trigger_rerun"] = True
            else:
                st.warning("Element already exists.")

        # Show list of added elements
        if st.session_state.elements:
        st.markdown("### ✅ Current Elements:")
        for i, el in enumerate(st.session_state.elements, 1):
            st.markdown(f"{i}. **{el}**")
                if st.button("➡️ NEXT", key="next_btn_key"):  # inside visibility block
            st.session_state["start_timers"] = True
else:
    st.markdown("### ⏱️ Timing Mode")

if not st.session_state.get("start_timers", False):
    st.markdown("### ➕ Add a New Element")
form_key = "add_element_form_master_key"  # completely static key to avoid duplicate errors"
    with st.form(form_key):
    new_element = st.text_input("Enter element name")
    submitted = st.form_submit_button("Add Element")
    if submitted and new_element.strip():
        name = new_element.strip()
        if name not in st.session_state.elements:
            st.session_state.elements.append(name)
            st.session_state.element_colours[name] = generate_colour()
            st.success(f"Added element: {name}")
            st.session_state["_trigger_rerun"] = True
        else:
            st.warning("Element already exists.")

    # Show list of added elements
    if st.session_state.elements:
    st.markdown("### ✅ Current Elements:")
    for i, el in enumerate(st.session_state.elements, 1):
        st.markdown(f"{i}. **{el}**")

    # Proceed to timer section
            if st.button("➡️ NEXT", key="next_btn_key"):  # inside visibility block  # unique key placeholder
        st.session_state["start_timers"] = True
if not st.session_state.get("start_timers", False):
    st.markdown("### ➕ Add a New Element")
with st.form("add_element_form"):
    new_element = st.text_input("Enter element name")
    submitted = st.form_submit_button("Add Element")
    if submitted and new_element.strip():
        name = new_element.strip()
        if name not in st.session_state.elements:
            st.session_state.elements.append(name)
            st.session_state.element_colours[name] = generate_colour()
            st.success(f"Added element: {name}")
            st.session_state["_trigger_rerun"] = True
        else:
            st.warning("Element already exists.")

    # Show list of added elements
    if st.session_state.elements:
    st.markdown("### ✅ Current Elements:")
    for i, el in enumerate(st.session_state.elements, 1):
        st.markdown(f"{i}. **{el}**")

    # Proceed to timer section
            if st.button("➡️ NEXT", key="next_btn_key"):  # inside visibility block  # unique key placeholder
        st.session_state["start_timers"] = True
if not st.session_state.get("start_timers", False):
    st.markdown("### ➕ Add a New Element")
with st.form("add_element_form"):
    new_element = st.text_input("Enter element name")
    submitted = st.form_submit_button("Add Element")
    if submitted and new_element.strip():
        name = new_element.strip()
        if name not in st.session_state.elements:
            st.session_state.elements.append(name)
            st.session_state.element_colours[name] = generate_colour()
            st.success(f"Added element: {name}")
            st.session_state["_trigger_rerun"] = True
        else:
            st.warning("Element already exists.")
if not st.session_state.get("start_timers", False):
    st.markdown("### ➕ Add a New Element")
new_element = st.text_input("Enter element name")
if st.button("Add Element") and new_element.strip():
    name = new_element.strip()
    if name not in st.session_state.elements:
        st.session_state.elements.append(name)
        st.session_state.element_colours[name] = generate_colour()
        st.success(f"Added element: {name}")
        st.session_state["_trigger_rerun"] = True
    else:
        st.warning("Element already exists.")