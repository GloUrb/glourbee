#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import ee_interface_function as eef
import os

class SessionState:
    def __init__(self):
        self.authenticated = False
        self.mail = 'jlimonet@ee-glourb.iam.gserviceaccount.com'
        self.key = 'ee-glourb-58e556f00841.json'
        self.uploaded_key_path = ''
        self.key_path = ''


class HomePage:
    def __init__(self , session_state):
        self.title = "Authentification"
        self.session_state = session_state

    def show(self):
        st.title(self.title)
        st.write("This is the Home Page for authentification")

        if "mail" not in st.session_state:
            st.session_state.mail = 'jlimonet@ee-glourb.iam.gserviceaccount.com'
        if "key" not in st.session_state:
            st.session_state.key = 'ee-glourb-58e556f00841.json'
        if "uploaded_key" not in st.session_state:
            st.session_state.uploaded_key = ""

        mail = st.text_input("mail", value=st.session_state.mail)
        key = st.text_input("key", value=st.session_state.key)
        uploaded_key = st.file_uploader("Upload file", type=["json"])

        if st.button("Authenticate"):
            if uploaded_key:
                self.session_state.uploaded_key_path = eef.temp_key_path(uploaded_key)

            if key:
                self.session_state.key_path = os.path.abspath(
                    os.path.join(os.getcwd(), str(key))
                )

            if mail and key or mail and uploaded_key:
                if eef.credentials(str(mail), self.session_state.key_path, self.session_state.uploaded_key_path):
                    st.write("Authentication successful!")
                    self.session_state.authenticated = True
                else:
                    st.write("Authentication failed")
            else:
                st.write("Please enter mail and key, or mail and upload a JSON file.")
        else:
            st.write("Please enter your credentials.")

class PageOne:
    def __init__(self, session_state):
        self.title = "Page One"
        self.shp_file = None
        self.ee_project_name = 'ee-glourb'
        self.dgo_features = None
        self.session_state = session_state

    def show(self):        
        st.title(self.title)
        self.ee_project_name = st.text_input("Project Name", value=self.ee_project_name)
        self.shp_file = st.file_uploader("Upload Shape file", type=["shp"])

        
        if self.shp_file:
            shp_key_path = eef.temp_key_path(self.shp_file)
            self.dgo_assetId, self.dgo_features = eef.assets(shp_key_path, ee_project_name=self.ee_project_name, simplify_tolerance=15)
        
        if self.dgo_features is not None:
            if st.button("Load Map"):
                map_object = eef.plot_map(self.dgo_features)
                st.pydeck_chart(map_object)  # Or use st.map(map_object) if applicable


class PageTwo:
    def __init__(self):
        self.title = "Page Two"

    def show(self):
        st.title(self.title)
        st.write("Welcome to Page Two.")


class MultiPageApp:
    def __init__(self):
        self.session_state = SessionState()
        self.pages = {"Authentication": HomePage(self.session_state),
                      "Page One": PageOne(self.session_state),
                      "Page Two": PageTwo()}

    def run(self):
        st.title("GEE Interface")
        selection = None
        for page_name in self.pages.keys():
            if st.sidebar.button(page_name):
                selection = page_name

        # if selection == "Authentication"  or selection == None:
        #     self.pages["Authentication"].show()

        # if self.session_state.authenticated and selection:
        #     self.pages[selection].show()

        # if not self.session_state.authenticated and selection:
        #     st.write("Please authenticate to access this page.")


        if not self.session_state.authenticated and selection != "Authentication":
            self.pages["Authentication"].show()
        elif selection:
            self.pages[selection].show()
        else:
            st.write("Please select a page.")


def run():
    app = MultiPageApp()
    app.run()


if __name__ == "__main__":
    run()
