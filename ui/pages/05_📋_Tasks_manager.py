import streamlit as st
import ee
import pandas as pd

from sqlalchemy.sql import text
from glourbee import ui

ui.addHeader(title='GEE tasks manager')

if not st.session_state['authenticated']: 
    st.switch_page('pages/01_🕶️_Authentication.py')


tlist = pd.DataFrame(ee.data.getTaskList())

st.dataframe(tlist, 
             hide_index=True,
             column_config={
                 'creation_timestamp_ms': st.column_config.DatetimeColumn(
                     "creation"
                 ),
                 'update_timestamp_ms': st.column_config.DatetimeColumn(
                     "update"
                 ),
                 'start_timestamp_ms': st.column_config.DatetimeColumn(
                     "start"
                 ),
             })

st.info('Coming soon: ability to cancel tasks', icon='🙃')

# Mettre à jour l'état des taches lancées par l'utilisateur
db_tasks = st.session_state['db'].query('SELECT * FROM glourbmetrics WHERE run_by = :u AND state != \'COMPLETED\'',
                                             ttl=0,
                                             params={'u': st.session_state['user']})

for _, tsk in db_tasks.iterrows():
    gee_tasks = tlist.query(f'description.str.contains("{tsk["run_id"]}")')
    state_values = gee_tasks['state'].unique()

    new_state = None
    if len(state_values) == 1 and state_values == 'COMPLETED':
        new_state = 'COMPLETED'
    elif 'FAILED' in state_values:
        new_state = 'FAILED'
    elif 'RUNNING' in state_values:
        new_state = 'RUNNING'
    elif 'PENDING' in state_values:
        new_state = 'PENDING'
    else:
        new_state = 'SUBMITTED'
    
    if new_state != tsk['state']:
        with st.session_state['db'].session as session:
            session.execute(text('UPDATE glourbmetrics SET state = :s WHERE id = :i'),
                            params={
                                's': new_state,
                                'i': tsk['id']
                            })
            session.commit()
    