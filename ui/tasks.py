import streamlit as st
import pandas as pd

from glourbee.worker import app

st.header("Tasks Manager")

st.info('''
The task manager allows users to visualize the tasks for creation, data downloading, and metric calculations launched via GloUrbEE-UI. 
Currently, it does not provide the ability to track the progress of each task or cancel them, but these features are planned on the 
application\'s development roadmap.
''')

if st.button('Refresh', icon='🔍'):
    st.rerun()

with st.spinner("Inspecting background workers"):
    i = app.control.inspect()
    active_tasks = i.active()
    reserved_tasks = i.reserved()
    scheduled_tasks = i.scheduled()

@st.fragment
def list_tasks(tasks):
    workers_data = list()
    for worker in tasks:
        workers_data.append(pd.DataFrame(tasks[worker]))
    
    tasks_df = pd.concat(workers_data)

    if len(tasks_df) > 0:
        active_selected = st.dataframe(pd.json_normalize(tasks_df['kwargs']), hide_index=True, on_select="rerun", selection_mode="single-row",)

        with st.popover('Cancel selected', icon='🟥', disabled=(len(active_selected.selection.rows) != 1)):
            st.error('Sorry, not possible yet', icon='🥺')
    else:
        st.warning('Nothing to see here')

st.title("Active tasks")
st.write("Tasks currently executed on workers")
list_tasks(active_tasks)

st.title("Tasks in queue")
st.write("Tasks that have been received, but are still waiting for a slot on a worker to be executed")
list_tasks(reserved_tasks)

st.title("Scheduled tasks")
st.write("Tasks executed periodically (prune old images and failed processes)")
scheduled_tasks