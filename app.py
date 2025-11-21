import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import random, hashlib

st.set_page_config(page_title="HemaVision (Simulated)", layout="wide")

st.markdown("""
<style>
body { background-color: #0b0f14; color: #e6eef6; }
.stApp { color: #e6eef6; }
</style>
""", unsafe_allow_html=True)

st.title("HemaVision – Automated Blood Smear Analyzer (Demo)")
st.caption("Simulated detection and WBC subtype classification for presentation purposes; not clinically validated.")

CLASSES = ["RBC", "WBC", "Platelet"]
COLORS = {
    "RBC": (0,180,190),
    "WBC": (180,90,255),
    "Platelet": (255,140,0)
}
WBC_SUBTYPES = ["neutrophil", "lymphocyte", "monocyte", "eosinophil", "basophil"]

def deterministic_subtype(x1,y1,x2,y2):
    s = f"{x1}-{y1}-{x2}-{y2}"
    h = hashlib.md5(s.encode()).hexdigest()
    return WBC_SUBTYPES[int(h[:2],16) % len(WBC_SUBTYPES)]

st.sidebar.header("Demo Controls")
seed = st.sidebar.number_input("Deterministic seed (change for different layouts)", value=42, step=1)
random.seed(seed)
conf_slider = st.sidebar.slider("Simulated confidence threshold (display only)", 0.0, 1.0, 0.25, 0.01)
max_boxes = st.sidebar.slider("Max simulated boxes", 1, 40, 12)

uploaded = st.file_uploader("Upload a slide image (jpg/png/webp). If you don't have one, upload any photo for demo.", type=["jpg","jpeg","png","webp"])

if not uploaded:
    st.info("Upload an image to run the demo.")
    st.stop()

img = Image.open(uploaded).convert("RGB")
w, h = img.size

num_boxes = min(max_boxes, max(3, int((w*h)/(200*200)) + random.randint(-2, 4)))
draw = ImageDraw.Draw(img)
counts = {"RBC":0, "WBC":0, "Platelet":0}
wbc_crops = []

for i in range(num_boxes):
    base = int(hashlib.sha256(f"{seed}-{i}-{w}-{h}".encode()).hexdigest()[:8],16)
    x1 = (base % (w-60)) 
    y1 = ((base>>8) % (h-60))
    box_w = 30 + ((base>>4) % 60)
    box_h = 30 + ((base>>12) % 60)
    x2 = min(w, x1 + box_w)
    y2 = min(h, y1 + box_h)

    label = CLASSES[ (base >> 5) % 3 ]
    counts[label] += 1

    color = COLORS[label]
    draw.rectangle([x1,y1,x2,y2], outline=color, width=3)
    draw.text((x1, max(0,y1-12)), f"{label}", fill=(255,255,255))

    if label == "WBC":
        crop = img.crop((x1,y1,x2,y2))
        subtype = deterministic_subtype(x1,y1,x2,y2)
        wbc_crops.append((crop, subtype))

left, right = st.columns([2,1])

with left:
    st.markdown("### Annotated slide")
    st.image(img, use_column_width=True)

with right:
    st.markdown("### Counts")
    c1, c2, c3 = st.columns(3)
    c1.metric("RBC", counts["RBC"])
    c2.metric("WBC", counts["WBC"])
    c3.metric("Platelets", counts["Platelet"])

    st.markdown("---")
    st.markdown("### Detected WBC crops (deterministic subtypes)")
    if not wbc_crops:
        st.write("No WBCs detected (try another image or increase max boxes).")
    else:
        cols = st.columns(3)
        for idx, (crop, subtype) in enumerate(wbc_crops[:9]):
            with cols[idx % 3]:
                st.image(crop, width=120, caption=subtype)

st.markdown("---")
st.write("**Note:** This is a prototype/demo. Real clinical models require training on medical datasets and rigorous validation.")
