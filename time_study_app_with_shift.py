
import streamlit as st
import random
import pandas as pd
import time
from datetime import timedelta

# ---------- Utilities ----------
def generate_colour():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def format_time(seconds):
    mins, secs = divmod(round(seconds, 3), 60)
    return f"{int(mins):02}:{secs:06.3f}"

# ---------- Session State Setup ----------
for key, default in {
    "project_name": "",
    "shift": "",
    "elements": [],
    "element_colours": {},
    "log": [],
    "active_element": None,
    "start_time": None,
    "total_time": 0.0,
    "start_timers": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Title ----------
st.title("⏱️ Time Study App")

# ---------- Project + Shift Selection ----------
if not st.session_state["project_name"]:
    st.session_state["project_name"] = st.text_input("📁 Enter Project Name")

if st.session_state["project_name"] and not st.session_state["shift"]:
    st.session_state["shift"] = st.selectbox("👷 Select Shift", ["", "Shift 1", "Shift 2", "Shift 3"])

# ---------- Add Element Page ----------
def show_add_elements_page():
    st.markdown("### ➕ Add a New Element")
    with st.form("add_element_form"):
        new_element = st.text_input("Element name", key="element_input")
        submitted = st.form_submit_button("Add Element")
        if submitted and new_element.strip():
            name = new_element.strip()
            if name not in st.session_state.elements:
                st.session_state.elements.append(name)
                st.session_state.element_colours[name] = generate_colour()
                st.success(f"Added element: {name}")
                st.session_state["element_input"] = ""
            else:
                st.warning("Element already exists.")
    if st.session_state.elements:
        st.markdown("### ✅ Current Elements:")
        for i, el in enumerate(st.session_state.elements, 1):
            st.markdown(f"{i}. **{el}**")
        if st.button("➡️ NEXT", key="next_btn"):
            st.session_state["start_timers"] = True
            st.rerun()

# ---------- Timing Page ----------
def show_timing_page():
    st.markdown("### ⏱️ Timing Mode")
    total_placeholder = st.empty()

    if st.session_state.active_element and st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
    else:
        elapsed = 0

    total = st.session_state.total_time + elapsed
    total_placeholder.subheader(f"Total Time: {format_time(total)}")

    for element in st.session_state.elements:
        if st.button(f"▶️ Start '{element}'", key=f"start_{element}"):
            now = time.time()
            if st.session_state.active_element:
                elapsed = now - st.session_state.start_time
                st.session_state.log.append({
                    "Project": st.session_state.project_name,
                    "Shift": st.session_state.shift,
                    "Element": st.session_state.active_element,
                    "Duration (s)": round(elapsed, 3),
                    "Formatted Time": format_time(elapsed)
                })
                st.session_state.total_time += elapsed
            st.session_state.active_element = element
            st.session_state.start_time = now
            st.rerun()

    if st.session_state.active_element:
        st.markdown(f"**Currently Timing: _{st.session_state.active_element}_**")
        if st.button("⏹️ Stop Current Timer"):
            now = time.time()
            elapsed = now - st.session_state.start_time
            st.session_state.log.append({
                "Project": st.session_state.project_name,
                "Shift": st.session_state.shift,
                "Element": st.session_state.active_element,
                "Duration (s)": round(elapsed, 3),
                "Formatted Time": format_time(elapsed)
            })
            st.session_state.total_time += elapsed
            st.session_state.active_element = None
            st.session_state.start_time = None
            st.success("Timer stopped.")
            st.rerun()

    if st.session_state.log:
        df = pd.DataFrame(st.session_state.log)
        st.markdown("### 📋 Time Log")
        st.dataframe(df)
        st.download_button("📥 Download CSV", df.to_csv(index=False), "time_log.csv", "text/csv")

# ---------- Page Flow Control ----------
if not st.session_state["project_name"] or not st.session_state["shift"]:
    st.info("Please enter project name and shift to begin.")
elif not st.session_state["start_timers"]:
    show_add_elements_page()
else:
    show_timing_page()
