import os
from pathlib import Path
from datetime import datetime
import streamlit as st
from src.check_info import CheckInfo
from tempfile import TemporaryDirectory
from src.gui_application import _VERSION



# Placeholder for CheckInfo class
class Application:
    def __init__(self, check_info_instance):
        # Initialize any necessary variables
        self.selected_flow_table = ""
        self.check_info = check_info_instance
        self.flow_table_list = []

    def run(self, flow_table, work_dir="./"):
        # st.write("Running checks...")
        return self.check_info.run(flow_table, work_dir)

    def import_flow(self, device_path, platform_type, cycle_format, log_area, progressbarOne):
        self.check_info.read_device(device_path, "", "", platform_type, log_area, cycle_format, progressbarOne)
        job_list_dict = self.check_info.get_job_list()
        # Update the log area - this is just a placeholder
        log_area(f"Flow imported for platform {platform_type} from {device_path}")
        if job_list_dict:
            self.flow_table_list = job_list_dict.keys()
        return self.flow_table_list


# Main Streamlit App
def main(app=Application):
    st.title(f"Check Info Tool {_VERSION}")
    st.caption('Powered by Streamlit, written by Chao Zhou')
    st.subheader("", divider='rainbow')
    work_path = os.path.abspath('.')
    WorkPath = os.path.join(work_path, "workDir")
    if not os.path.exists(WorkPath):  # check the directory is existed or not
        os.mkdir(WorkPath)
    OutputPath = os.path.join(work_path, "Output")
    if not os.path.exists(OutputPath):  # check the directory is existed or not
        os.mkdir(OutputPath)

    if "flow_table_list" not in st.session_state:
        st.session_state["flow_table_list"] = []
    if "FilePath" not in st.session_state:
        st.session_state["FilePath"] = ""
    if "check_info_app" not in st.session_state:
        st.session_state["check_info_app"] = app
    if "check_info_log" not in st.session_state:
        st.session_state["check_info_log"] = ""
    if "check_info_result" not in st.session_state:
        st.session_state["check_info_result"] = ""

    # Sidebar for menu options
    with st.sidebar:
        st.header("Help")
        if st.button("About"):
            st.info(
                "Thank you for using!\nCreated by Chao Zhou.\nAny suggestions please mail zhouchao486@gmail.com]")

    # Main UI Components
    st.subheader('Step 1. Config Setting')
    file_path = st.file_uploader("`1. Upload a test program`",
                                 type=["igxl", "zip", "xlsm"],
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

    with st.expander("Run Logs"):
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

    st.subheader('Step 2. Run to check info')
    if st.button('Run Check Info'):
        result_file = st.session_state["check_info_app"].run(flow_selected, OutputPath)
        st.session_state["check_info_result"] = result_file
        # Add a completion message to the logs.
        send_log("Run completed")
        st.info("Run completed")

    if len(st.session_state["check_info_result"]) > 0:
        result_file_path = st.session_state["check_info_result"]
        result_file_name = os.path.basename(result_file_path)
        with open(result_file_path, "rb") as file:
            btn = st.download_button(
                label="Download Result XLSX File",
                data=file,
                file_name=result_file_name,
                mime="application/octet-stream"
            )
        send_log("Report available for download.")




# Run the main function
if __name__ == "__main__":
    with TemporaryDirectory(dir="./") as temp_directory:
        CheckInfo_Inst = CheckInfo(temp_directory)
        app = Application(CheckInfo_Inst)
        main(app)
