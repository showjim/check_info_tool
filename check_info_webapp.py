import os
from pathlib import Path
from datetime import datetime
import streamlit as st
import time
from check_info import CheckInfo
from tempfile import TemporaryDirectory

_VERSION = "Beta 1.4.7"


# Placeholder for CheckInfo class
class Application:
    def __init__(self, check_info_instance):
        # Initialize any necessary variables
        self.selected_flow_table = ""
        self.check_info = check_info_instance
        self.flow_table_list = []

    def run(self, flow_table):
        st.write("Running checks... (this is a mock implementation)")
        self.check_info.run(flow_table)

    def import_flow(self, device_path, platform_type, cycle_format, log_area, progressbarOne):
        self.check_info.read_device(device_path, "", "", platform_type, log_area, cycle_format, progressbarOne)
        job_list_dict = self.check_info.get_job_list()
        # Mock implementation
        st.write(f"Importing flow for path: {device_path} and platform type: {platform_type}")
        # Update the log area - this is just a placeholder
        log_area(f"Flow imported for platform {platform_type} from {device_path}")
        if job_list_dict:
            self.flow_table_list = job_list_dict.keys()
        return self.flow_table_list


# Main Streamlit App
def main(app):
    st.title(f"Check Info Tool {_VERSION}")

    work_path = os.path.abspath('.')
    WorkPath = os.path.join(work_path, "workDir")
    if not os.path.exists(WorkPath):  # check the directory is existed or not
        os.mkdir(WorkPath)

    if "flow_table_list" not in st.session_state:
        st.session_state["flow_table_list"] = []
    if "FilePath" not in st.session_state:
        st.session_state["FilePath"] = ""
    if "check_info_app" not in st.session_state:
        st.session_state["check_info_app"] = app
    if "check_info_log" not in st.session_state:
        st.session_state["check_info_log"] = ""

    # Sidebar for menu options
    with st.sidebar:
        st.header("Help")
        if st.button("About"):
            st.info(
                "Thank you for using!\nCreated by [Your Name], maintained by [Maintainer Name].\nAny suggestions please mail [your-email@example.com]")
        if st.button("User Guide"):
            st.info("Please wait...")

    # Main UI Components
    file_path = st.file_uploader("`1. Upload a test program`",
                                 type=["igxl", "zip"],
                                 accept_multiple_files=False)
    if st.button("Upload Test Program"):
        if file_path is not None:
            # save file
            with st.spinner('Reading file'):
                uploaded_path = os.path.join(WorkPath, file_path.name)
                with open(uploaded_path, mode="wb") as f:
                    f.write(file_path.getbuffer())
                if os.path.exists(uploaded_path) == True:
                    st.session_state["FilePath"] = uploaded_path
                    st.write(f"✅ {Path(uploaded_path).name} uploaed")

    platform_type = st.selectbox("`2. Select Platform:`", ['UltraFLEX Plus', 'UltraFLEX', 'J750'])

    cycle_format = st.radio("`3. Cycle Mode:`", ('Period', 'Frequency'))

    load_enabled = st.button('Load')

    flow_selected_placeholder = st.empty()

    with st.expander("Logs"):
        log_text_area = st.empty()  # text_area("", key="logs", height=300)

    def send_log(data_log):
        st.session_state["check_info_log"] += f'{datetime.now()} - {data_log}\n'
        log_text_area.code(st.session_state["check_info_log"])

    # Mock progress bar
    progress_bar_placeholder = st.empty()
    progress_bar_placeholder.progress(0)

    def update_processbar(val):
        progress_bar_placeholder.progress(int(val))

    if load_enabled:
        st.session_state["flow_table_list"] = st.session_state["check_info_app"].import_flow(
            st.session_state["FilePath"], platform_type, cycle_format,
            send_log,
            update_processbar)
        load_enabled = False

    flow_selected = flow_selected_placeholder.multiselect("Select flow:", st.session_state["flow_table_list"])

    if st.button('Run'):
        st.session_state["check_info_app"].run(flow_selected)
        # Add a completion message to the logs.
        st.info("Run completed")




# Run the main function
if __name__ == "__main__":
    with TemporaryDirectory(dir="./") as temp_directory:
        CheckInfo_Inst = CheckInfo(temp_directory)
        app = Application(CheckInfo_Inst)
        main(app)