import hmac
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

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False) or st.secrets["password"] == "":
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

# Main Streamlit App
def main(app=Application):
    st.title(f"Check Info Tool {_VERSION}")
    st.caption('Powered by Streamlit, written by Chao Zhou')
    st.subheader("", divider='rainbow')

    with st.expander("Disclaimer", True):
        st.warning("""The developer of this efficiency tool has taken all reasonable measures to ensure its quality and functionality. However, it is provided "as is" and the developer makes no representations or warranties of any kind, express or implied, as to its accuracy, reliability, or suitability for a particular purpose.

The user assumes all risks associated with the use of this tool, and the developer will not be liable for any damages, including but not limited to direct, indirect, special, incidental, or consequential damages, arising out of the use or inability to use this tool.

The developer welcomes feedback and bug reports from users. If you encounter any issues or have any suggestions, please contact me at Teams. Your input will help us improve the tool and provide a better user experience.

By ENTERING PASSWORD "teradyne" of this tool, you acknowledge that you have read and understood this disclaimer and agree to be bound by its terms.""",
                   icon="⚠️")

    if not check_password():
        st.stop()  # Do not continue if check_password is not True.

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
        st.header("Other Tools")
        st.page_link("http://taishanstone:8502", label="Pattern Auto Edit Tool", icon="1️⃣")
        st.page_link("http://taishanstone:8503", label="Shmoo Detect Tool", icon="2️⃣")
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
