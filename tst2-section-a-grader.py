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

# custom functions
# ------------------------------------------------------------
def submission_viewer(img_url, height=1000, max_zoom_ratio=4.0, key="osd_viewer"):
    if isinstance(img, Image.Image):
        pil_img = img
    else:
        pil_img = Image.open(img)

    buffered = BytesIO()
    if pil_img.mode in ("RGB", "P"):
        pil_img = pil_img.convert("RGB")

    pil_img.save(buffered, format="PNG", quality=95)
    img_b64 = base64.b64encode(buffered.getvalue()).decode()

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
    # memo q1
    q1 = pd.read_csv("memo-q1.csv")
    q1[q1["q"] == "a", "sub"] = st.session_state["q1a_sub"]
    q1[q1["q"] == "b", "sub"] = st.session_state["q1b_weathering"]
    q1[q1["q"] == "c", "sub"] = st.session_state["q1c_motivation"]
    q1_units = st.session_state["q1a_unit"]

    q1a_fc = q1[q1["q"] == "a", "sub"].between((q1["q"] == "a", "ans") - (q1["q"] == "a", "fc"),
                                               (q1["q"] == "a", "ans") + (q1["q"] == "a", "fc"))
    q1a_pc = q1[q1["q"] == "a", "sub"].between((q1["q"] == "a", "ans") - (q1["q"] == "a", "pc"),
                                               (q1["q"] == "a", "ans") + (q1["q"] == "a", "pc"))
    q1a_opt = [q1a_fc, q1a_pc]
    q1a_grd = [1.0, 0.5]
    q1[q1["q"] == "a", "grade"] += np.select(q1_opt, q1a_grd, default = 0.0)
    q1[q1["q"] == "a", "grade"] += (q1_units == "fc").astype(float)

    q1b = st.session_state["q1b_weathering"]
    q1[q1["q"] == "b", "grade"] += (q1_units == "fc").astype(float)

    q1c_fc = st.session_state["q1c_motivation"] == "fc"
    q1c_pc = st.session_state["q1c_motivation"] == "pc"
    q1c_nc = st.session_state["q1c_motivation"] == "nc"
    q1c_opt = [q1c_fc, q1c_pc, q1c_nc]
    q1c_grd = [4.0, 2.0, 0.0]

    q1[q1["q"] == "c", "grade"] += np.select(q1c_opt, q1c_grd, default = 0.0)

    st.session_state["q1a"] = q1[q1["q"] == "a", "grade"]
    st.session_state["q1b"] = q1[q1["q"] == "b", "grade"]
    st.session_state["q1c"] = q1[q1["q"] == "c", "grade"]
    st.session_state["q1_total"] = q1["grade"].sum()

    # ============================================================

    q2 = {
        "q"     : ["a", "b"],
        "ans"   : ["Clay", "Fine Silt"],
        "sub"   : [st.session_state["q2a"],
                   st.session_state["q2b"]],
        "grade" : [0.0,0.0]
    }

    q2 = pd.DataFrame(q2)
    q2_fc = q2["sub"] == q2["ans"]
    q2_nc = q2["sub"] != q2["ans"]
    q2_opt = [q2_fc, q2_nc]
    q2_grd = [0.5,0.0]
    q2["grade"] += np.select(q2_opt, q2_grd, default = 0.0)

    st.session_state["q2a"] = q2[q2["q"] == "a", "grade"]
    st.session_state["q2b"] = q2[q2["q"] == "b", "grade"]
    st.session_state["q2_total"] = q2["grade"].sum()

    # ============================================================

    q3 = pd.read_csv("memo-q3.csv")
    q3["sub"].iloc[0] = st.session_state[""] 

    
    
def next_submission():
    st.session_state["script_index"] += 1
    
    
    st.rerun()

def clear_files():
     st.session_state["uploader_key"] += 1
     del st.session_state["script_index"]
     if "graded_submission" in st.session_state:
         del st.session_state["graded_submission"]
# ------------------------------------------------------------
    
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

st.set_page_config(layout="wide")

title_col1, title_col2= st.columns(2)
with title_col1:
    st.image("NAS_Faculty Logo.jpg")

with title_col2:
    st.title("GGY 168 — Introduction to Physical Geography")
    st.header("Semester Test 2")

with st.expander("Instructions", expanded = False):
    st.markdown("""
    1. Enter your name in the provided space.
    2. Load the student submission.
    3. If there is an error during loading, refresh your browser window and try again.
    4. If it still doesn't work, send me an email with the student's details and move on to the next submission.
    5. Verify that the name on the submission matches the name of the file.
    6. Transfer the answers on the submission to the spaces provided.
    7. **DON'T** use commas for decimal marks. Please use a full-stop.
    9. When you are done, press the grade button.
    10. Download the graded submission and store it in a separate folder. **DON'T** change the filename.
    """)

if "script_index" not in st.session_state:
    st.session_state["script_index"] = 0

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

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

    # read and display image
    img = Image.open(image)

    # store the submission in memory as cv2 object
    img_bytes = np.frombuffer(image.getvalue(), dtype=np.uint8)
    cv_img = cv.imdecode(img_bytes, cv.IMREAD_COLOR)

    # prepare values for detector
    aruco_dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
    parameters = cv.aruco.DetectorParameters()
    
    # instantiate detector
    detector = cv.aruco.ArucoDetector(aruco_dictionary, parameters)

    try:
        # use detector to detect aruco markers
        corners, ids, _ = detector.detectMarkers(cv_img)

        # get the coordinates of the center points of each aruco marker
        ids = ids.flatten().tolist()

        aruco_0_index = ids.index(0)
        aruco_0_corners = corners[aruco_0_index]
        aruco_0_corners_rshp = aruco_0_corners.reshape((4,2))
        topleft_x = int(np.mean(aruco_0_corners_rshp[:,0]))
        topleft_y = int(np.mean(aruco_0_corners_rshp[:,1]))

        aruco_1_index = ids.index(1)
        aruco_1_corners = corners[aruco_1_index]
        aruco_1_corners_rshp = aruco_1_corners.reshape((4,2))
        topright_x = int(np.mean(aruco_1_corners_rshp[:,0]))
        topright_y = int(np.mean(aruco_1_corners_rshp[:,1]))

        aruco_2_index = ids.index(2)
        aruco_2_corners = corners[aruco_2_index]
        aruco_2_corners_rshp = aruco_2_corners.reshape((4,2))
        bottomleft_x = int(np.mean(aruco_2_corners_rshp[:,0]))
        bottomleft_y = int(np.mean(aruco_2_corners_rshp[:,1]))

        aruco_3_index = ids.index(3)
        aruco_3_corners = corners[aruco_3_index]
        aruco_3_corners_rshp = aruco_3_corners.reshape((4,2))
        bottomright_x = int(np.mean(aruco_3_corners_rshp[:,0]))
        bottomright_y = int(np.mean(aruco_3_corners_rshp[:,1]))

        # Prepare the image for warping
        current_coords = np.float32([[topleft_x, topleft_y],
                                     [topright_x, topright_y],
                                     [bottomright_x, bottomright_y],
                                     [bottomleft_x, bottomleft_y]])

        ac = pd.read_csv("tst2-aruco-markers.csv")
                
        target_coords = np.float32([[ac.iloc[0,3], ac.iloc[0,4]],
                                    [ac.iloc[1,3], ac.iloc[1,4]],
                                    [ac.iloc[3,3], ac.iloc[3,4]],
                                    [ac.iloc[2,3], ac.iloc[2,4]]])
        
        affine_matrix, _ = cv.estimateAffine2D(current_coords, target_coords)
        warped_img = cv.warpAffine(cv_img,
                                   affine_matrix,
                                   (2480, 3508),
                                   flags=cv.INTER_LINEAR,
                                   borderMode=cv.BORDER_CONSTANT,
                                   borderValue=(255, 255, 255))

        # get zingg point
        shift = 8
        factor = 1 << shift
        zingg=pd.read_csv("zingg.csv")
        radius = int(round(((300/25.4) * 2.0) * factor))

        ax = int(round(zingg["cvx"].item() * factor))
        ay = int(round(zingg["cvy"].item() * factor))
        cv.circle(warped_img, (ax,ay), radius, (0,0,255), 2, shift = shift)

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

        with st.expander("Questions", expanded = False):
            st.markdown("**Question 1**")
            q1_col1, q1_col2 = st.columns(2)

            with q1_col1:
                st.text_input("Change in Gibbs Free Energy", key = "q1a_sub")
                st.selectbox("Weathering Reaction", ("Yes", "Other"), index = None, placeholder = "Make a selection..", key = "q1b_weathering")

            with q1_col2:
                st.selectbox("Units", ("fc","pc","nc"), index = None, placeholder="Make a selection...", key = "q1a_unit")
                st.selectbox("Motivation", ("fc","pc","nc"), index = None, placeholder = "Make a selection..", key = "q1c_motivation")

            st.markdown("**Question 2**")
            q2_col1, q2_col2 = st.columns(2)

            with q2_col1:
                st.selectbox("a) 0.002 mm", ("Clay", "Other"), index = None, placeholder = "Make a selection...", key = "q2a")

            with q2_col2:
                st.selectbox("a) 0.01 mm", ("Fine Silt", "Other"), index = None, placeholder = "Make a selection...", key = "q2b")

            st.markdown("**Question 3**")
            st.text_input("Phi size", key = "q3_sub")

        button_col1, button_col2, button_col3 = st.columns(3)

        with button_col1:
            st.button("Grade", on_click=grade_submission)

        if "graded_submission" in st.session_state:
            final_img_rgb = cv.cvtColor(st.session_state["graded_submission"], cv.COLOR_BGR2RGB)
            final_img_pil = Image.fromarray(final_img_rgb)

            filename = filename + ".png"
            grader_timestamp = datetime.now().isoformat()
            meta_info = PngInfo()
            meta_info.add_text("Grader", grader.strip())
            meta_info.add_text("GradedAt", grader_timestamp)
            meta_info.add_text("final", st.session_state["final_grade"])
            meta_info.add_text("q1", st.session_state["q1_grade"])
            meta_info.add_text("q2", st.session_state["q2_grade"])  
            meta_info.add_text("q3", st.session_state["q3_grade"])  
            meta_info.add_text("q4", st.session_state["q4_grade"])  
            meta_info.add_text("q5", st.session_state["q5_grade"])  
            meta_info.add_text("q6", st.session_state["q6_grade"])  
            meta_info.add_text("q7", st.session_state["q7_grade"])  
            meta_info.add_text("q8", st.session_state["q8_grade"])  
            meta_info.add_text("q9", st.session_state["q9_grade"])  
            meta_info.add_text("q10", st.session_state["q10_grade"])  
            meta_info.add_text("q11", st.session_state["q11_grade"]) 
            buffer = io.BytesIO()
            final_img_pil.save(buffer, format="PNG", pnginfo=meta_info)
            
            with button_col2:
                st.download_button(label=f"Download {filename}", data=buffer, file_name=filename, mime="image/png")

            if st.session_state["script_index"] < len(uploaded_files) - 1:
                with button_col3:
                    st.button("Next Submission", on_click = next_submission)

