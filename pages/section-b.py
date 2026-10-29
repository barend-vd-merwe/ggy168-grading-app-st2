import streamlit as st
import cv2 as cv
import pandas as pd
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import io
from io import BytesIO
from streamlit_image_zoom import image_zoom
import base64
from datetime import datetime
import yaml
from streamlit_gsheets import GSheetsConnection
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# custom functions
# ------------------------------------------------------------
def submission_viewer(img_url, height=1000, max_zoom_ratio=4.0, key="osd_viewer"):
    # openseadragon
    html_osd = f"""
    <!DOCTYPE html>
    <html style="height:100%">
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/openseadragon.min.js"></script>
        <style>
            body {{
    margin: 0;
    padding: 0;
    background-color: #F5F5DC;
    height: 100%;
    width: 100%;
    overflow: hidden;}}
            #openseadragon-container {{
                width: 100vw;
                height: 100vh;
                background: #F5F5DC;
                border: 10px solid #374151;
                border-radius: 8px;
    box-sizing: border-box;
            }}
        </style>
    </head>
    <body>
        <div id="openseadragon-container"></div>
        <script type="text/javascript">
            var viewer = OpenSeadragon({{
                id: "openseadragon-container",
                prefixUrl: "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/images/",
                tileSources: {{
                    type: 'image',
                    url:  '{img_url}'
                }},
                // Performance and Zoom configuration
                maxZoomPixelRatio: {max_zoom_ratio},
                minZoomImageRatio: 0.8,
                visibilityRatio: 0.8,
                constrainDuringPan: true,
                
                // Controls setup
                showNavigationControl: true,
                navigationControlAnchor: OpenSeadragon.ControlAnchor.TOP_LEFT,
                showRotationControl: false,
                showFullPageControl: true,
                showHomeControl: true,
                
                // Smooth interaction tuning
                animationTime: 0.3,
                bllendTime: 0.1,
                springStiffness: 10
            }});
        </script>
    </body>
    </html>
    """
    st.iframe(html_osd, height=height)

# ------------------------------------------------------------
def grade_submission():
    with open (BASE_DIR / "tst2-memo.yaml", "r", encoding = "utf-8") as file:
        memo = yaml.safe_load(file)

def next_submission():
    st.session_state["script_index"] += 1
    del st.session_state["graded_submission"]
    # ============================================================

    # ============================================================
    st.rerun()

def clear_files():
     st.session_state["uploader_key"] += 1
     del st.session_state["script_index"]
     if "graded_submission" in st.session_state:
         del st.session_state["graded_submission"]

# ============================================================
# ============================================================

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    /* 1. Add Tuks Red border strip across the top of the app */
    header[data-testid="stHeader"] {
        border-top: 5px solid #D12631 !important;
    }

    /* 2. Style primary headers with UP Navy Blue */
    h1, h2, h3 {
        color: #002B49 !important;
    }

    /* 3. Style Sidebar header with a Gold bottom accent */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        border-bottom: 2px solid #E8A800;
        padding-bottom: 5px;
    }

    /* Custom utility classes */
    .tuks-red { color: #D12631; font-weight: bold; }
    .up-gold { color: #E8A800; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

title_col1, title_col2= st.columns(2)
with title_col1:
    st.image(BASE_DIR / "NAS_Faculty Logo.jpg")

with title_col2:
    st.title("GGY 168 — Introduction to Physical Geography")
    st.header("Semester Test 2")
    st.subheader("Section B — Cartography")

with st.expander("Instructions", expanded = False):
    st.markdown("""
    1. Enter your name in the provided space.
    2. Load the student submission.
    3. If there is an error during loading, refresh your browser window and try again.
    4. If it still doesn't work, send me an email with the student's details and move on to the next submission.
    5. Verify that the name on the submission matches the name of the file.
    6. Transfer the answers on the submission to the spaces provided.
    7. For the work shown requirement for question 14:
        - "Full Credit": At least four (4) of the circles contain a compass interval.
        - "Partial Credit": Compass marks are present, but correspond with three (3) or less of the indicated circles.
        - "No Credit": Compass marks are absent.
    8. **DON'T** use commas for decimal marks. Please use a full-stop.
    9. When you are done, press the grade button.
    10. Download the graded submission and store it in a separate folder. **DON'T** change the filename.
    """)

if "script_index" not in st.session_state:
    st.session_state["script_index"] = 0

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 100

# load class list and submission
with st.sidebar:
    grader = st.text_input("Name of grader", key="graderName")
    uploaded_files = st.file_uploader("Select the student submission",
                                      type = ["png"],
                                      accept_multiple_files = True,
                                      key = str(st.session_state["uploader_key"]))
    st.button("Clear", on_click = clear_files)

if uploaded_files and grader.strip():
    total_scripts = len(uploaded_files)
    current_script = st.session_state["script_index"] + 1
    progress = min(current_script / total_scripts, 1.0)
    st.progress(progress)

    # extract student details from img filename
    image = uploaded_files[st.session_state["script_index"]]
    filename = image.name
    filename = filename.replace(".png","")
    surname, name, emplid = filename.split("_")
    st.session_state["student"] = f"{name} {surname} ({emplid})"

    # store the submission in memory as cv2 object
    img_bytes = np.frombuffer(image.getvalue(), dtype=np.uint8)
    cv_img = cv.imdecode(img_bytes, cv.IMREAD_COLOR)
    img_gray = cv.cvtColor(cv_img, cv.COLOR_BGR2GRAY)

    # prepare values for detector
    aruco_dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
    parameters = cv.aruco.DetectorParameters()
    parameters.cornerRefinementMethod = cv.aruco.CORNER_REFINE_SUBPIX
    parameters.cornerRefinementWinSize = 5
    parameters.cornerRefinementMaxIterations = 100
    parameters.cornerRefinementMinAccuracy = 0.01

    # instantiate detector
    detector = cv.aruco.ArucoDetector(aruco_dictionary, parameters)

    try:
        # use detector to detect aruco markers
        corners, ids, _ = detector.detectMarkers(img_gray)

        # get the coordinates of the center points of each aruco marker
        ids = ids.flatten().tolist()

        aruco_0_index = ids.index(0)
        aruco_0_corners = corners[aruco_0_index]
        aruco_0_corners_rshp = aruco_0_corners.reshape((4,2))

        aruco_1_index = ids.index(1)
        aruco_1_corners = corners[aruco_1_index]
        aruco_1_corners_rshp = aruco_1_corners.reshape((4,2))

        aruco_2_index = ids.index(2)
        aruco_2_corners = corners[aruco_2_index]
        aruco_2_corners_rshp = aruco_2_corners.reshape((4,2))

        aruco_3_index = ids.index(3)
        aruco_3_corners = corners[aruco_3_index]
        aruco_3_corners_rshp = aruco_3_corners.reshape((4,2))

        aruco_markers = [aruco_0_corners_rshp,
                         aruco_1_corners_rshp,
                         aruco_2_corners_rshp,
                         aruco_3_corners_rshp]

        current_coords_list = []
        for marker in aruco_markers:
            for i in range(4):
                x_coord = marker[i,0]
                y_coord = marker[i,1]
                current_coords_list.append([x_coord, y_coord])
        current_coords = np.array(current_coords_list, dtype=np.float32)

        # Set target coordinates

        ac = pd.read_csv(BASE_DIR / "aruco.csv")

        target_coords_list = []

        for i in range(len(ac)):
            x_coord = ac.iloc[i,4]
            y_coord = ac.iloc[i,5]
            target_coords_list.append([x_coord, y_coord])

        target_coords = np.array(target_coords_list, dtype=np.float32)

        # transform the image
        homography_matrix, mask = cv.findHomography(current_coords, target_coords, cv.RANSAC, 5.0)
        warped_img = cv.warpPerspective(cv_img,
                                        homography_matrix,
                                        (2480, 3508),
                                        flags=cv.INTER_LINEAR,
                                        borderMode=cv.BORDER_CONSTANT,
                                        borderValue=(255, 255, 255))
        # add compass intervals
        shift = 8
        factor = 1 << shift
        bubble_radius = int(round(24 * factor))

        ci = pd.read_csv(BASE_DIR / "compass-intervals.csv")

        for i in range(len(ci)):
            rawx = ci.iloc[i]["cvx"]
            rawy = ci.iloc[i]["cvy"]
            cix = int(round(rawx * factor))
            ciy = int(round(rawy * factor))
            cv.circle(warped_img, (cix, ciy), bubble_radius, (0,0,255), 2, shift = shift)

        st.session_state["submission"] = warped_img

        processed_img = cv.imencode(".png",warped_img)[1]
        b64_str = base64.b64encode(processed_img).decode("utf-8")
        img_url = f"data:image/png;base64,{b64_str}"


    except Exception as e:
        st.error(f"Processing failed: {e}")
        img_url = None

    # display submission and grading tools in two cols
    col1, col2 = st.columns(2)

    with col1:    
        submission_viewer(img_url)

    with col2:
        # display student details
        with st.expander("Student Details", expanded = False):
            st.markdown(f"""
            - *Name*: **{name}**
            - *Surname*: **{surname}**
            - *Student Number*: **{emplid}**
            """)

        with st.expander("Questions", expanded = True):
            st.markdown("**Question 9**")
            q9_col1, q9_col2 = st.columns(2)

            with q9_col1:
                st.text_input("Tfb (Bryn to Mox)", key = "q9a_val")
                st.text_input("Tbb (Bryn to Mox)", key = "q9b_val")

            with q9_col2:
                st.selectbox("Units",
                             ("fc", "nc"),
                             index = None,
                             placeholder = "Make a selection...",
                             key = "q9a_unt")
                st.selectbox("Units",
                             ("fc", "nc"),
                             index = None,
                             placeholder = "Make a selection...",
                             key = "q9b_unt")

            st.markdown("**Question 10**")
            q10_col1, q10_col2 = st.columns(2)

            with q10_col1:
                st.text_input("Magnetic Declination", key = "q10_val")

            with q10_col2:
                st.selectbox("Units",
                             ("fc", "nc"),
                             index = None,
                             placeholder = "Make a selection...")

            st.markdown("**Question 11**")
            q11_col1, q11_col2 = st.columns(2)

            with q11_col1:
                st.text_input("Mfb (Kelt to Zuni)", key = "q11a_val")
                st.text_input("Mbb (Kelt to Zuni)", key = "q11b_val")

            with q11_col2:
                st.selectbox("Units",
                             ("fc", "nc"),
                             index = None,
                             placeholder = "Make a selection...",
                             key = "q11a_unt")
                st.selectbox("Units",
                             ("fc", "nc"),
                             index = None,
                             placeholder = "Make a selection...",
                             key = "q11b_unt")

            st.markdown("**Question 12**")
            q12_col1, q12_col2 = st.columns(2)

            with q12_col1:
                st.text_input("True Forward Bearing", key = "q12_val")

            with q12_col2:
                st.selectbox("Units",
                             ("fc","nc"),
                             index = None,
                             placeholder = "Make a selection...",
                             key = "q12_unt")

            st.markdown("**Question 13**")
            q13_col1, q13_col2 = st.columns(2)

            with q13_col1:
                st.text_input("Straight line distance", key = "q13_val")

            with q13_col2:
                st.selectbox("Units",
                             ("fc","nc"),
                             index = None,
                             placeholder = "Make a selection...",
                             key = "q13_unt")

            st.markdown("**Question 14**")
            q14_col1, q14_col2, q14_col3 = st.columns(3)

            with q14_col1:
                st.text_input("Road length", key = "q14_val")

            with q14_col2:
                st.selectbox("Units",
                             ("fc","nc"),
                             index = None,
                             placeholder = "Make a selection...",
                             key = "q14_unt")

            with q14_col3:
                st.selectbox("Work shown",
                             ("fc","pc","nc"),
                             index = None,
                             placeholder = "Make a selection...",
                             key = "q14_wrk")
            

