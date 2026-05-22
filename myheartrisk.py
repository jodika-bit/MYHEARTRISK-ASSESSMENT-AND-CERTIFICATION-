
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import json
import hashlib
import base64
from pathlib import Path
from html import escape
import textwrap
import warnings

warnings.filterwarnings("ignore")

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except Exception:
    FPDF_AVAILABLE = False


# ============================================================
# MyHeartRisk NADI Training Completion Assessment
# Revised Full Version
# ============================================================

st.set_page_config(
    page_title="MyHeartRisk NADI Certification",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# CONFIGURATION
# -----------------------------
PASS_MARK = 80
TOTAL_CASES_REQUIRED = 5

GOOGLE_FORM_URL = "https://forms.gle/X4BR3ormnZRtcZWA8"
CERTIFICATE_VERIFY_BASE_URL = "https://myheartrisk.uitm.edu.my/verify"

APP_DIR = Path(__file__).parent
ASSET_DIR = APP_DIR / "assets"


def resolve_asset(*names: str) -> Path:
    for name in names:
        path = ASSET_DIR / name
        if path.exists():
            return path
    return ASSET_DIR / names[0]


UITM_CARE_LOGO = resolve_asset("uitm_care_logo.png")
MYHEARTRISK_ICON = resolve_asset("myheartrisk_icon.png", "myheart_icon.png")
SIGNATURE_IMAGE = resolve_asset(
    "signature_sazzli_transparent.png",
    "signature_sazzli.png",
    "signature_sazli.png",
    "signature.png",
)
GOLD_SEAL_IMAGE = resolve_asset("myheartrisk_gold_seal.png")


# -----------------------------
# CASE SCENARIOS
# -----------------------------
CASES = [
    {
        "case_no": 1,
        "title": "Community participant with low FRS and low REDISCOVER risk",
        "name": "Ahmad Hakim Razali",
        "ic": "Test 1",
        "dob_age": "29 Nov 1994 (31 years)",
        "gender": "Male",
        "race": "Malay",
        "phone": "012-345 6789",
        "state_centre": "Selangor / NADI Sri Damansara",
        "residential_area": "Urban",
        "occupation": "Technician",
        "marital_status": "Single",
        "education": "Diploma",
        "height_weight": "172 cm / 70 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Never",
            "Diabetes": "No",
            "Total Cholesterol": "4.7 mmol/L",
            "HDL": "1.3 mmol/L",
            "BP": "117/68 mmHg",
            "HR": "73 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "FRS Low + REDISCOVER Low",
        "expected_action": "Send result with health recommendation only",
        "teaching_point": "Low-risk community participant should receive result and healthy lifestyle recommendation.",
    },
    {
        "case_no": 2,
        "title": "Community participant with low FRS but high REDISCOVER risk",
        "name": "Nur Afiqah Binti Rahman",
        "ic": "Test 2",
        "dob_age": "15 Apr 1980 (46 years)",
        "gender": "Female",
        "race": "Malay",
        "phone": "013-778 2211",
        "state_centre": "Johor / NADI Muar",
        "residential_area": "Semi-urban",
        "occupation": "Clerk",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "158 cm / 70 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Never",
            "Diabetes": "Yes",
            "Total Cholesterol": "5.2 mmol/L",
            "HDL": "1.4 mmol/L",
            "BP": "124/76 mmHg",
            "HR": "80 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "FRS Low + REDISCOVER High",
        "expected_action": "Send result and referral letter",
        "teaching_point": "If REDISCOVER is high, staff must follow the higher-risk action even if FRS is low.",
    },
    {
        "case_no": 3,
        "title": "Community participant with high FRS but low REDISCOVER risk",
        "name": "Muthu Kumar Ramasamy",
        "ic": "Test 3",
        "dob_age": "2 Feb 1970 (56 years)",
        "gender": "Male",
        "race": "Indian",
        "phone": "017-600 4455",
        "state_centre": "Perak / NADI Bagan Datuk",
        "residential_area": "Rural",
        "occupation": "Lorry driver",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "168 cm / 88 kg",
        "heart_attack_history": "No",
        "inputs": {
            "Smoking": "Former smoker",
            "Diabetes": "Yes",
            "Total Cholesterol": "6.2 mmol/L",
            "HDL": "0.9 mmol/L",
            "BP": "165/95 mmHg",
            "HR": "92 bpm",
        },
        "expected_pathway": "FRS + REDISCOVER",
        "expected_result": "FRS High + REDISCOVER Low",
        "expected_action": "Send result and referral letter",
        "teaching_point": "If FRS is high, the participant should still receive referral action even if REDISCOVER is low.",
    },
    {
        "case_no": 4,
        "title": "Post-heart attack participant with low ACS risk",
        "name": "Mohd Faizal Zulkifli",
        "ic": "Test 4",
        "dob_age": "12 Jan 1968 (58 years)",
        "gender": "Male",
        "race": "Malay",
        "phone": "016-345 8899",
        "state_centre": "Selangor / NADI Subang",
        "residential_area": "Urban",
        "occupation": "Security guard",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "152 cm / 69 kg",
        "heart_attack_history": "Yes",
        "inputs": {
            "Killip": "I",
            "Renal Disease": "No",
            "PCI": "Yes",
            "Beta blocker": "Yes",
            "ACE inhibitor": "Yes",
            "Statin": "Yes",
            "HR": "70 bpm",
            "Total Cholesterol": "5.2 mmol/L",
            "Fasting Glucose": "5.5 mmol/L",
        },
        "expected_pathway": "ACS",
        "expected_result": "ACS Low",
        "expected_action": "Send result with health recommendation only",
        "teaching_point": "Low-risk ACS participant still receives result and advice, but no referral letter unless threshold is high.",
    },
    {
        "case_no": 5,
        "title": "Post-heart attack participant with high ACS risk",
        "name": "Rosmah Binti Salleh",
        "ic": "Test 5",
        "dob_age": "22 Oct 1963 (62 years)",
        "gender": "Female",
        "race": "Malay",
        "phone": "014-555 1212",
        "state_centre": "Sarawak / NADI Sibu",
        "residential_area": "Semi-urban",
        "occupation": "Housewife",
        "marital_status": "Married",
        "education": "SPM",
        "height_weight": "150 cm / 70 kg",
        "heart_attack_history": "Yes",
        "inputs": {
            "Killip": "II",
            "Renal Disease": "Yes",
            "PCI": "Yes",
            "Beta blocker": "Yes",
            "ACE inhibitor": "Yes",
            "Statin": "Yes",
            "HR": "85 bpm",
            "SBP": "150 mmHg",
            "Total Cholesterol": "6.0 mmol/L",
            "Fasting Glucose": "9.0 mmol/L",
        },
        "expected_pathway": "ACS",
        "expected_result": "ACS High",
        "expected_action": "Send result and referral letter",
        "teaching_point": "High-risk ACS participant should receive the result and referral letter for early follow-up.",
    },
]


# -----------------------------
# KNOWLEDGE CHECK
# -----------------------------
KNOWLEDGE_QUESTIONS = [
    {
        "question": "If the participant has NO previous heart attack or ACS, which pathway should be used?",
        "options": ["ACS pathway", "FRS + REDISCOVER pathway", "Referral pathway only", "No assessment needed"],
        "answer": "FRS + REDISCOVER pathway",
        "explanation": "Participants without previous heart attack or ACS should use the FRS + REDISCOVER pathway.",
    },
    {
        "question": "If the participant HAS previous heart attack or ACS, which pathway should be used?",
        "options": ["FRS only", "REDISCOVER only", "ACS pathway", "Lifestyle pathway only"],
        "answer": "ACS pathway",
        "explanation": "Previous heart attack or ACS means the ACS pathway should be used.",
    },
    {
        "question": "If FRS is high but REDISCOVER is low, what should staff do?",
        "options": ["Follow the lower result", "Repeat next year", "Follow the highest-risk action", "Ignore the FRS result"],
        "answer": "Follow the highest-risk action",
        "explanation": "The staff should follow the highest-risk result for action.",
    },
    {
        "question": "If FRS is low but REDISCOVER is high, what should staff do?",
        "options": ["Send health advice only", "Follow the highest-risk action", "Ignore the REDISCOVER result", "Delete the assessment"],
        "answer": "Follow the highest-risk action",
        "explanation": "A high REDISCOVER result should trigger the higher action level even when FRS is low.",
    },
    {
        "question": "How does the participant start the result retrieval process?",
        "options": ["Call any NADI staff directly", "Scan QR code and start WhatsApp chat", "Wait for public announcement", "Walk in again to the centre only"],
        "answer": "Scan QR code and start WhatsApp chat",
        "explanation": "The flow starts with scanning the QR code and opening WhatsApp.",
    },
    {
        "question": "After scanning the QR code, what should the participant do in WhatsApp?",
        "options": ["Say hi to admin", "Send IC photo to group", "Wait silently", "Ask another participant to reply"],
        "answer": "Say hi to admin",
        "explanation": "The participant initiates the chat by saying hi to admin.",
    },
    {
        "question": "Before sending the result, what should admin verify?",
        "options": ["Only the centre name", "Name and telephone number", "Only age", "Only state"],
        "answer": "Name and telephone number",
        "explanation": "Admin should verify participant identity using name and telephone number before sending results.",
    },
    {
        "question": "If the participant is low risk, what should admin send?",
        "options": ["Referral letter only", "Result with health recommendation", "Nothing", "Send to public WhatsApp group"],
        "answer": "Result with health recommendation",
        "explanation": "Low-risk participants should receive their result plus health recommendation.",
    },
    {
        "question": "If the participant is high risk, what should admin send?",
        "options": ["Health recommendation only", "Result only", "Result and referral letter", "Nothing"],
        "answer": "Result and referral letter",
        "explanation": "High-risk participants should receive both the result and referral letter.",
    },
    {
        "question": "Which statement is correct about privacy when sending results?",
        "options": [
            "Results can be shared in a WhatsApp group",
            "Results can be sent to any number given by a friend",
            "Results should be sent only after verification to the participant or consented caregiver",
            "Results should be posted publicly for tracking",
        ],
        "answer": "Results should be sent only after verification to the participant or consented caregiver",
        "explanation": "Results must be shared privately and only after identity verification or caregiver consent.",
    },
]


# -----------------------------
# STYLES
# -----------------------------
def inject_css():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 38px;
            font-weight: 800;
            color: #003B73;
            margin-bottom: 0;
        }
        .subtitle {
            font-size: 18px;
            color: #4A6378;
            margin-top: 0;
        }
        .metric-card {
            background: #F3F8FF;
            border: 1px solid #D8E7F7;
            border-radius: 14px;
            padding: 16px;
            text-align: center;
        }
        .success-box {
            background: #EAF7EE;
            border-left: 6px solid #17A34A;
            border-radius: 12px;
            padding: 14px;
        }
        .warning-box {
            background: #FFF8E6;
            border-left: 6px solid #F2A900;
            border-radius: 12px;
            padding: 14px;
        }
        .danger-box {
            background: #FDECEC;
            border-left: 6px solid #D92D20;
            border-radius: 12px;
            padding: 14px;
        }
        .blue-box {
            background: #EAF3FF;
            border-left: 6px solid #005B96;
            border-radius: 12px;
            padding: 14px;
        }
        .celebration-banner {
            background: linear-gradient(90deg, #EAF7EE, #EAF3FF);
            border: 1px solid #B7E4C7;
            border-left: 8px solid #17A34A;
            border-radius: 16px;
            padding: 16px 18px;
            margin: 14px 0;
        }
        .celebration-title {
            font-size: 20px;
            font-weight: 800;
            color: #0B5D1E;
            margin-bottom: 4px;
        }
        .celebration-detail {
            color: #1B2B3A;
            font-size: 15px;
        }
        .next-action-box {
            background: #F8FBFF;
            border: 1px dashed #0B4A7B;
            border-radius: 14px;
            padding: 14px;
            margin-top: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# HELPERS
# -----------------------------
def init_state():
    defaults = {
        "current_step": "1. Training",
        "trainee": {},
        "case_answers": {},
        "knowledge_answers": {},
        "google_form_submitted": False,
        "declaration_agreed": False,
        "certificate_id": None,
        "section_completed": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def unique_in_order(items):
    seen = set()
    output = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


def mark_section_complete(section_name: str):
    st.session_state.section_completed[section_name] = True


def celebrate_once(event_key: str, message: str = "Section completed. Well done!"):
    state_key = f"celebrated_{event_key}"
    if not st.session_state.get(state_key, False):
        try:
            st.balloons()
        except Exception:
            pass
        try:
            st.toast(message, icon="🎉")
        except Exception:
            pass
        st.session_state[state_key] = True


def celebration_banner(title: str, detail: str):
    st.markdown(
        f"""
        <div class="celebration-banner">
            <div class="celebration-title">🎉 {title}</div>
            <div class="celebration-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def go_next_button(label: str, next_step: str, key: str):
    if st.button(label, type="primary", key=key):
        st.session_state.current_step = next_step
        st.rerun()


def image_data_uri(path: Path) -> str:
    try:
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    except Exception:
        return ""
    return ""


def safe_pdf_image(pdf, path: Path, x: float, y: float, w: float = 0, h: float = 0):
    try:
        if path.exists():
            pdf.image(str(path), x=x, y=y, w=w, h=h)
    except Exception:
        pass


def pdf_safe(text: str) -> str:
    if text is None:
        return ""
    replacements = {
        "•": "|",
        "×": "x",
        "–": "-",
        "—": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "…": "...",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "ignore").decode("latin-1")


def get_certificate_id(name: str, email: str) -> str:
    today = datetime.now().strftime("%Y%m%d")
    raw = f"{name}-{email}-{today}-MyHeartRisk-NADI"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:8].upper()
    return f"MHR-NADI-{today}-{digest}"


def get_case_score():
    total = len(CASES)
    correct = 0
    for case in CASES:
        ans = st.session_state.case_answers.get(case["case_no"], {})
        if (
            ans.get("completed")
            and ans.get("pathway") == case["expected_pathway"]
            and ans.get("result") == case["expected_result"]
            and ans.get("action") == case["expected_action"]
        ):
            correct += 1
    return correct, total


def get_knowledge_score():
    total = len(KNOWLEDGE_QUESTIONS)
    correct = 0
    for i, q in enumerate(KNOWLEDGE_QUESTIONS):
        if st.session_state.knowledge_answers.get(i) == q["answer"]:
            correct += 1
    percent = round((correct / total) * 100, 1) if total else 0
    return correct, total, percent


def is_eligible():
    case_correct, case_total = get_case_score()
    _, _, knowledge_percent = get_knowledge_score()
    trainee = st.session_state.trainee
    required_trainee = all([
        trainee.get("full_name"),
        trainee.get("email"),
        trainee.get("role"),
        trainee.get("centre"),
        trainee.get("state"),
    ])
    return (
        required_trainee
        and case_correct == case_total
        and knowledge_percent >= PASS_MARK
        and st.session_state.google_form_submitted
        and st.session_state.declaration_agreed
    )


def trainee_table():
    trainee = st.session_state.trainee
    return pd.DataFrame(
        [
            ["Full name", trainee.get("full_name", "")],
            ["Email", trainee.get("email", "")],
            ["Phone", trainee.get("phone", "")],
            ["Role", trainee.get("role", "")],
            ["Organisation", trainee.get("organisation", "")],
            ["NADI centre / site", trainee.get("centre", "")],
            ["State", trainee.get("state", "")],
            ["Training mode", trainee.get("mode", "")],
            ["Cohort", trainee.get("cohort", "")],
        ],
        columns=["Item", "Details"],
    )


def build_completion_record():
    case_correct, case_total = get_case_score()
    knowledge_correct, knowledge_total, knowledge_percent = get_knowledge_score()
    trainee = st.session_state.trainee
    cert_id = st.session_state.certificate_id or get_certificate_id(
        trainee.get("full_name", "UNKNOWN"),
        trainee.get("email", "UNKNOWN"),
    )

    return {
        "app": "MyHeartRisk NADI Training Completion Assessment",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "trainee": trainee,
        "completion": {
            "case_score": f"{case_correct}/{case_total}",
            "knowledge_score": f"{knowledge_correct}/{knowledge_total}",
            "knowledge_percent": knowledge_percent,
            "google_form_submitted": st.session_state.google_form_submitted,
            "declaration_agreed": st.session_state.declaration_agreed,
            "eligible_for_certificate": is_eligible(),
            "certificate_id": cert_id,
        },
        "case_answers": st.session_state.case_answers,
        "knowledge_answers": st.session_state.knowledge_answers,
    }


def certificate_html():
    trainee = st.session_state.trainee
    full_name = escape(trainee.get("full_name", "[FULL NAME OF PARTICIPANT]"))
    mode = escape(trainee.get("mode", "Online / Hybrid / Onsite"))
    cohort = escape(trainee.get("cohort", "1"))
    today = datetime.now().strftime("%d %b %Y")
    cert_id = st.session_state.certificate_id or get_certificate_id(
        trainee.get("full_name", ""),
        trainee.get("email", ""),
    )
    verify_url = f"{CERTIFICATE_VERIFY_BASE_URL}/{cert_id}"

    uitm_logo = image_data_uri(UITM_CARE_LOGO)
    mhr_icon = image_data_uri(MYHEARTRISK_ICON)
    signature = image_data_uri(SIGNATURE_IMAGE)
    gold_seal = image_data_uri(GOLD_SEAL_IMAGE)

    left_logo_html = f'<img class="cert-logo-left" src="{uitm_logo}" alt="UiTM CARE Logo">' if uitm_logo else ""
    right_logo_html = f'<img class="cert-logo-right" src="{mhr_icon}" alt="MyHeartRisk Icon">' if mhr_icon else ""
    signature_html = f'<img class="signature-img" src="{signature}" alt="Signature">' if signature else ""
    seal_html = f'<img class="seal-img" src="{gold_seal}" alt="Gold Seal">' if gold_seal else ""
    watermark_html = f'<div class="cert-watermark"><img src="{gold_seal}" alt=""></div>' if gold_seal else ""

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MyHeartRisk Certificate</title>
<style>
    body {{
        margin: 0;
        padding: 14px;
        background: #f0f0f0;
        font-family: Georgia, "Times New Roman", serif;
    }}
    .certificate-wrap {{
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    .certificate {{
        position: relative;
        width: 1120px;
        min-height: 760px;
        border: 12px solid #D4AF37;
        border-radius: 22px;
        padding: 22px 36px 28px 36px;
        background: radial-gradient(circle at top, #fffdf7 0%, #fff7e8 58%, #fbe7b2 100%);
        text-align: center;
        box-shadow: 0 10px 32px rgba(0,0,0,0.16);
        overflow: hidden;
        box-sizing: border-box;
    }}
    .certificate::before {{
        content: "";
        position: absolute;
        inset: 16px;
        border: 2px solid #0B4A7B;
        border-radius: 14px;
        pointer-events: none;
    }}
    .certificate::after {{
        content: "";
        position: absolute;
        inset: 28px;
        border: 1px solid rgba(212,175,55,0.85);
        border-radius: 10px;
        pointer-events: none;
    }}
    .certificate-header {{
        position: relative;
        display: grid;
        grid-template-columns: 1fr 90px;
        align-items: start;
        gap: 18px;
        margin-bottom: 8px;
        z-index: 2;
    }}
    .cert-logo-left {{
        max-width: 620px;
        height: 78px;
        object-fit: contain;
        object-position: left center;
    }}
    .cert-logo-right {{
        width: 62px;
        height: 62px;
        object-fit: contain;
        justify-self: end;
        margin-top: 6px;
    }}
    .cert-title-main {{
        color: #003B73;
        font-size: 54px;
        font-weight: 800;
        margin: 6px 0 2px 0;
        line-height: 1.1;
        letter-spacing: 0.2px;
        position: relative;
        z-index: 2;
    }}
    .cert-title-sub {{
        color: #B42318;
        font-size: 30px;
        font-weight: 800;
        margin: 0 0 4px 0;
        letter-spacing: 0.8px;
        position: relative;
        z-index: 2;
    }}
    .cert-programme {{
        color: #0B4A7B;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 12px;
        position: relative;
        z-index: 2;
    }}
    .cert-intro {{
        font-size: 18px;
        color: #1F2A37;
        margin-bottom: 6px;
        position: relative;
        z-index: 2;
    }}
    .cert-name {{
        display: inline-block;
        min-width: 62%;
        padding: 8px 24px 10px 24px;
        margin: 8px 0 18px 0;
        font-size: 34px;
        font-weight: 800;
        color: #003B73;
        border-bottom: 3px solid #D4AF37;
        line-height: 1.2;
        position: relative;
        z-index: 2;
    }}
    .cert-body {{
        max-width: 820px;
        margin: 0 auto;
        font-size: 16px;
        line-height: 1.55;
        color: #243746;
        position: relative;
        z-index: 2;
    }}
    .cert-meta {{
        margin: 20px auto 8px auto;
        font-size: 14px;
        color: #243746;
        line-height: 1.6;
        position: relative;
        z-index: 2;
    }}
    .cert-signature-area {{
        margin-top: 10px;
        text-align: center;
        position: relative;
        z-index: 2;
    }}
    .signature-img {{
        height: 84px;
        object-fit: contain;
        margin-bottom: -8px;
    }}
    .signature-line {{
        width: 250px;
        border-top: 1.3px solid #1F2A37;
        margin: 0 auto 6px auto;
    }}
    .signature-name {{
        font-size: 17px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1px;
    }}
    .signature-role {{
        font-size: 14px;
        color: #374151;
    }}
    .cert-footer {{
        margin-top: 14px;
        font-size: 11.5px;
        color: #536878;
        line-height: 1.5;
        position: relative;
        z-index: 2;
    }}
    .seal-img {{
        position: absolute;
        right: 54px;
        bottom: 46px;
        width: 82px;
        height: 82px;
        object-fit: contain;
        opacity: 0.98;
        z-index: 2;
    }}
    .cert-watermark {{
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
        opacity: 0.05;
        z-index: 1;
    }}
    .cert-watermark img {{
        width: 250px;
        height: 250px;
        object-fit: contain;
    }}
</style>
</head>
<body>
<div class="certificate-wrap">
    <div class="certificate">
        {watermark_html}

        <div class="certificate-header">
            <div>{left_logo_html}</div>
            <div>{right_logo_html}</div>
        </div>

        <div class="cert-title-main">MyHeartRisk</div>
        <div class="cert-title-sub">CERTIFICATE OF COMPLETION</div>
        <div class="cert-programme">NADI MADANI: Jantung Sihat [MyHeartRisk] - Train-the-Trainer (ToT)</div>

        <div class="cert-intro">This certificate is proudly presented to</div>
        <div class="cert-name">{full_name}</div>

        <div class="cert-body">
            For successfully completing the MyHeartRisk Train-the-Trainer programme and demonstrating
            competency to conduct standardized cardiovascular risk screening and participant counselling at NADI centres.
        </div>

        <div class="cert-meta">
            <strong>Date of Completion:</strong> {today}
            &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
            <strong>Venue/Mode:</strong> {mode}
            &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
            <strong>Cohort:</strong> {cohort}
        </div>

        <div class="cert-signature-area">
            {signature_html}
            <div class="signature-line"></div>
            <div class="signature-name">Prof. Dr. Sazzli Shahlan Kasim</div>
            <div class="signature-role">Director of CARE Institute, UiTM</div>
        </div>

        <div class="cert-footer">
            <strong>Certificate ID:</strong> {cert_id}
            &nbsp; | &nbsp;
            <strong>Verification:</strong> {verify_url}
            <br>
            Generated by CARE Institute UiTM x NADI/MCMC
        </div>

        {seal_html}
    </div>
</div>
</body>
</html>
"""
    return textwrap.dedent(html).strip()


def generate_certificate_pdf():
    trainee = st.session_state.trainee
    full_name = pdf_safe(trainee.get("full_name", "[FULL NAME OF PARTICIPANT]"))
    mode = pdf_safe(trainee.get("mode", "Online / Hybrid / Onsite"))
    cohort = pdf_safe(trainee.get("cohort", "1"))
    today = datetime.now().strftime("%d %b %Y")
    cert_id = pdf_safe(st.session_state.certificate_id or get_certificate_id(
        trainee.get("full_name", ""),
        trainee.get("email", ""),
    ))
    verify_url = pdf_safe(f"{CERTIFICATE_VERIFY_BASE_URL}/{cert_id}")

    if not FPDF_AVAILABLE:
        return None

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    # Background
    pdf.set_fill_color(255, 250, 240)
    pdf.rect(0, 0, 297, 210, style="F")

    # Borders
    pdf.set_draw_color(212, 175, 55)
    pdf.set_line_width(3.2)
    pdf.rect(10, 10, 277, 190)

    pdf.set_draw_color(11, 74, 123)
    pdf.set_line_width(0.8)
    pdf.rect(16, 16, 265, 178)

    pdf.set_draw_color(212, 175, 55)
    pdf.set_line_width(0.3)
    pdf.rect(21, 21, 255, 168)

    # Logos
    safe_pdf_image(pdf, UITM_CARE_LOGO, x=20, y=16, w=120)
    safe_pdf_image(pdf, MYHEARTRISK_ICON, x=256, y=18, w=18)

    # Titles
    pdf.set_xy(0, 42)
    pdf.set_font("Helvetica", "B", 29)
    pdf.set_text_color(0, 59, 115)
    pdf.cell(0, 11, pdf_safe("MyHeartRisk"), ln=True, align="C")

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(180, 35, 24)
    pdf.cell(0, 10, pdf_safe("CERTIFICATE OF COMPLETION"), ln=True, align="C")

    pdf.set_font("Helvetica", "B", 11.2)
    pdf.set_text_color(11, 74, 123)
    pdf.cell(0, 8, pdf_safe("NADI MADANI: Jantung Sihat [MyHeartRisk] - Train-the-Trainer (ToT)"), ln=True, align="C")

    # Intro
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11.2)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 7, pdf_safe("This certificate is proudly presented to"), ln=True, align="C")

    # Participant name
    pdf.set_font("Helvetica", "B", 21)
    pdf.set_text_color(0, 59, 115)
    pdf.cell(0, 12, full_name[:80], ln=True, align="C")

    # Underline
    pdf.set_draw_color(212, 175, 55)
    pdf.set_line_width(0.8)
    pdf.line(70, 95, 227, 95)

    # Body
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 10.8)
    pdf.set_text_color(20, 20, 20)
    paragraph = pdf_safe(
        "For successfully completing the MyHeartRisk Train-the-Trainer programme and "
        "demonstrating competency to conduct standardized cardiovascular risk screening "
        "and participant counselling at NADI centres."
    )
    pdf.set_x(34)
    pdf.multi_cell(229, 6.2, paragraph, align="C")

    # Meta
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(36, 55, 70)
    meta_line = pdf_safe(
        f"Date of Completion: {today}   |   Venue/Mode: {mode}   |   Cohort: {cohort}"
    )
    pdf.cell(0, 6.6, meta_line, ln=True, align="C")

    # Signature
    safe_pdf_image(pdf, SIGNATURE_IMAGE, x=118, y=136, w=60)
    pdf.set_draw_color(40, 40, 40)
    pdf.set_line_width(0.35)
    pdf.line(112, 160, 187, 160)

    pdf.set_xy(0, 161)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5.2, pdf_safe("Prof. Dr. Sazzli Shahlan Kasim"), ln=True, align="C")

    pdf.set_font("Helvetica", "", 9.2)
    pdf.cell(0, 4.8, pdf_safe("Director of CARE Institute, UiTM"), ln=True, align="C")

    # Seal
    safe_pdf_image(pdf, GOLD_SEAL_IMAGE, x=248, y=150, w=24)

    # Footer
    pdf.set_y(183)
    pdf.set_font("Helvetica", "", 8.1)
    pdf.set_text_color(83, 104, 120)
    footer1 = pdf_safe(f"Certificate ID: {cert_id} | Verification: {verify_url}")
    footer2 = pdf_safe("Generated by CARE Institute UiTM x NADI/MCMC")
    pdf.cell(0, 4.4, footer1, ln=True, align="C")
    pdf.cell(0, 4.4, footer2, ln=True, align="C")

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)


# -----------------------------
# SIDEBAR
# -----------------------------
def sidebar():
    st.sidebar.markdown("## ❤️ MyHeartRisk")
    st.sidebar.markdown("### NADI Certification")

    steps = [
        "1. Training",
        "2. Trainee Details",
        "3. Case Scenarios",
        "4. Knowledge Check",
        "5. Google Form",
        "6. Certificate",
    ]

    selected = st.sidebar.radio(
        "Go to section",
        options=steps,
        index=steps.index(st.session_state.current_step)
        if st.session_state.current_step in steps
        else 0,
    )
    st.session_state.current_step = selected

    st.sidebar.divider()

    case_correct, case_total = get_case_score()
    _, _, knowledge_percent = get_knowledge_score()

    st.sidebar.metric("Case completion", f"{case_correct}/{case_total}")
    st.sidebar.metric("Knowledge score", f"{knowledge_percent}%")
    st.sidebar.metric("Pass mark", f"{PASS_MARK}%")

    if is_eligible():
        st.sidebar.success("Eligible for certificate")
    else:
        st.sidebar.warning("Not yet eligible")

    st.sidebar.divider()
    st.sidebar.markdown("### Session progress")
    completed_sections = st.session_state.get("section_completed", {})
    for section_label in [
        "Training briefing",
        "Trainee details",
        "Case scenarios",
        "Knowledge check",
        "Google form",
        "Certificate",
    ]:
        if completed_sections.get(section_label):
            st.sidebar.success(f"✅ {section_label}")
        else:
            st.sidebar.caption(f"⬜ {section_label}")

    st.sidebar.divider()
    st.sidebar.caption("Training rule: complete all case scenarios, submit form, pass knowledge check, and agree declaration.")


# -----------------------------
# PAGES
# -----------------------------
def page_training():
    st.markdown('<p class="main-title">MyHeartRisk NADI Training Completion Assessment</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">5 Case Scenarios + Knowledge Check → Certificate of Completion</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><h3>{TOTAL_CASES_REQUIRED}</h3><p>Case Scenarios</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><h3>{len(KNOWLEDGE_QUESTIONS)}</h3><p>Knowledge Questions</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h3>{PASS_MARK}%</h3><p>Pass Mark</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><h3>1</h3><p>Certificate</p></div>', unsafe_allow_html=True)

    st.markdown("### Training flow")
    st.markdown(
        """
        <div class="blue-box">
        <strong>Training → Complete 5 cases → Compare expected outputs → Complete Google Form → Knowledge Check → Verification → Certificate</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### What the trainee must learn")
    st.write(
        """
        - Select the correct pathway:
          - **Heart Attack History = No → FRS + REDISCOVER**
          - **Heart Attack History = Yes → ACS pathway**
        - Follow the **highest-risk action rule**
        - For low risk: **send result with health recommendation**
        - For high risk: **send result and referral letter**
        - Participant result flow:
          1. Scan QR code
          2. Open WhatsApp
          3. Say hi to admin
          4. Admin verifies name and phone number
          5. Admin sends result
        """
    )

    st.markdown("### Certification requirement")
    st.markdown(
        f"""
        <div class="success-box">
        Certificate is unlocked only after all conditions are met:<br>
        1. Trainee details completed<br>
        2. All {TOTAL_CASES_REQUIRED} cases completed correctly<br>
        3. Knowledge check score ≥ {PASS_MARK}%<br>
        4. Google Form submission confirmed<br>
        5. SOP declaration agreed
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="next-action-box"><strong>Complete this session:</strong> Click below after reading the training flow and certification requirement.</div>',
        unsafe_allow_html=True,
    )

    if st.button("✅ Mark Training Briefing Complete", type="primary", key="complete_training_briefing"):
        mark_section_complete("Training briefing")
        celebrate_once("training_briefing", "Training briefing completed.")
        celebration_banner("Training Briefing Completed", "You may now proceed to trainee details.")

    if st.session_state.section_completed.get("Training briefing"):
        go_next_button("Next: Enter Trainee Details ➜", "2. Trainee Details", "next_to_trainee_details")


def page_trainee_details():
    st.title("Trainee Details")

    with st.form("trainee_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full name *", value=st.session_state.trainee.get("full_name", ""))
            email = st.text_input("Email *", value=st.session_state.trainee.get("email", ""))
            phone = st.text_input("Phone number", value=st.session_state.trainee.get("phone", ""))
            role = st.selectbox(
                "Role *",
                ["", "NADI staff", "Admin", "Nurse", "Medical officer", "Research assistant", "Volunteer", "Other"],
                index=0,
            )
        with col2:
            organisation = st.text_input("Organisation", value=st.session_state.trainee.get("organisation", "NADI / MCMC"))
            centre = st.text_input("NADI centre / screening site *", value=st.session_state.trainee.get("centre", ""))
            state = st.selectbox(
                "State *",
                [
                    "",
                    "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang",
                    "Perak", "Perlis", "Pulau Pinang", "Sabah", "Sarawak", "Selangor",
                    "Terengganu", "WP Kuala Lumpur", "WP Labuan", "WP Putrajaya",
                ],
                index=0,
            )
            mode = st.selectbox("Venue / Mode", ["Online", "Hybrid", "Onsite"], index=0)
            cohort = st.text_input("Cohort", value=st.session_state.trainee.get("cohort", "1"))

        submitted = st.form_submit_button("Save trainee details", type="primary")

    if submitted:
        st.session_state.trainee = {
            "full_name": full_name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "role": role,
            "organisation": organisation.strip(),
            "centre": centre.strip(),
            "state": state,
            "mode": mode,
            "cohort": cohort.strip(),
        }
        if full_name and email and role and centre and state:
            mark_section_complete("Trainee details")
            celebrate_once("trainee_details", "Trainee details completed.")
            st.success("Trainee details saved.")
            celebration_banner("Trainee Details Completed", "Your profile has been saved. Continue to the case scenario assessment.")
        else:
            st.warning("Please complete all required fields marked with *.")

    if st.session_state.trainee:
        st.markdown("### Saved trainee profile")
        st.dataframe(trainee_table(), use_container_width=True, hide_index=True)

    if st.session_state.section_completed.get("Trainee details"):
        go_next_button("Next: Start Case Scenarios ➜", "3. Case Scenarios", "next_to_cases")
    else:
        st.info("Save complete trainee details first to unlock the next section.")


def case_card(case):
    st.markdown(f"## Case {case['case_no']}: {case['title']}")

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Participant demographics")
        demo_rows = [
            ["Name", case["name"]],
            ["IC", case["ic"]],
            ["DOB / Age", case["dob_age"]],
            ["Gender", case["gender"]],
            ["Race", case["race"]],
            ["Phone", case.get("phone", "")],
            ["State / Centre", case["state_centre"]],
            ["Residential Area", case["residential_area"]],
            ["Occupation", case["occupation"]],
            ["Marital Status", case["marital_status"]],
            ["Education Level", case["education"]],
            ["Height / Weight", case["height_weight"]],
            ["Heart Attack History", case["heart_attack_history"]],
        ]
        st.dataframe(pd.DataFrame(demo_rows, columns=["Item", "Details"]), use_container_width=True, hide_index=True)

    with right:
        st.markdown("#### Risk inputs")
        input_rows = [[k, v] for k, v in case["inputs"].items()]
        st.dataframe(pd.DataFrame(input_rows, columns=["Input", "Value"]), use_container_width=True, hide_index=True)

        if case["heart_attack_history"].lower() == "yes":
            st.markdown('<div class="danger-box"><strong>Expected pathway:</strong> ACS pathway</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box"><strong>Expected pathway:</strong> FRS + REDISCOVER pathway</div>', unsafe_allow_html=True)

    st.markdown("#### Trainee assessment")
    ans_key = case["case_no"]
    prev = st.session_state.case_answers.get(ans_key, {})

    result_options = [""] + unique_in_order([c["expected_result"] for c in CASES])
    action_options = [""] + unique_in_order([c["expected_action"] for c in CASES])

    col1, col2, col3 = st.columns(3)
    with col1:
        completed = st.checkbox(
            f"I completed Case {case['case_no']} in MyHeartRisk",
            value=prev.get("completed", False),
            key=f"completed_{ans_key}",
        )
    with col2:
        pathway = st.selectbox(
            "Pathway selected",
            ["", "FRS + REDISCOVER", "ACS"],
            index=["", "FRS + REDISCOVER", "ACS"].index(prev.get("pathway", "")) if prev.get("pathway", "") in ["", "FRS + REDISCOVER", "ACS"] else 0,
            key=f"pathway_{ans_key}",
        )
    with col3:
        result = st.selectbox(
            "System result obtained",
            result_options,
            index=result_options.index(prev.get("result", "")) if prev.get("result", "") in result_options else 0,
            key=f"result_{ans_key}",
        )

    action = st.selectbox(
        "NADI action selected",
        action_options,
        index=action_options.index(prev.get("action", "")) if prev.get("action", "") in action_options else 0,
        key=f"action_{ans_key}",
    )

    if st.button(f"Save Case {case['case_no']} answer", key=f"save_case_{ans_key}"):
        st.session_state.case_answers[ans_key] = {
            "completed": completed,
            "pathway": pathway,
            "result": result,
            "action": action,
        }
        if (
            completed
            and pathway == case["expected_pathway"]
            and result == case["expected_result"]
            and action == case["expected_action"]
        ):
            celebrate_once(f"case_{case['case_no']}_completed", f"Case {case['case_no']} completed correctly.")
            st.success("Correct. Case saved.")
            celebration_banner(
                f"Case {case['case_no']} Completed",
                "Pathway, result and NADI action match the expected answer."
            )
        else:
            st.error("Please recheck the expected pathway, result, or NADI action.")

    with st.expander("Show expected answer and teaching point"):
        st.write(f"**Expected pathway:** {case['expected_pathway']}")
        st.write(f"**Expected result:** {case['expected_result']}")
        st.write(f"**Expected action:** {case['expected_action']}")
        st.info(case["teaching_point"])


def page_cases():
    st.title("5 Case Scenario Assessment")
    st.markdown(
        """
        Complete all 5 dummy cases in the MyHeartRisk system, then record the pathway, result and NADI action here.
        """
    )

    case_correct, case_total = get_case_score()
    st.progress(case_correct / case_total if case_total else 0)
    st.caption(f"Correct cases saved: {case_correct}/{case_total}")

    tabs = st.tabs([f"Case {c['case_no']}" for c in CASES])
    for tab, case in zip(tabs, CASES):
        with tab:
            case_card(case)

    st.divider()
    if case_correct == case_total:
        mark_section_complete("Case scenarios")
        celebrate_once("all_cases_complete", "All 5 case scenarios completed.")
        st.success("All 5 cases are completed correctly.")
        celebration_banner("5 Case Scenarios Completed", "You have completed all selected FRS + REDISCOVER and ACS scenario checks.")
        go_next_button("Next: Complete Knowledge Check ➜", "4. Knowledge Check", "next_to_knowledge")
    else:
        st.warning("Please complete and save all 5 cases correctly before certification.")
        st.button("Next: Complete Knowledge Check ➜", disabled=True, key="next_to_knowledge_disabled")


def page_knowledge():
    st.title("Knowledge Check")
    st.markdown(f"Answer all questions. Passing mark is **{PASS_MARK}%**.")

    for i, q in enumerate(KNOWLEDGE_QUESTIONS):
        st.markdown(f"### Q{i+1}. {q['question']}")
        current = st.session_state.knowledge_answers.get(i)
        option_index = q["options"].index(current) if current in q["options"] else 0

        selected = st.radio(
            "Choose one answer",
            q["options"],
            index=option_index,
            key=f"knowledge_{i}",
        )
        st.session_state.knowledge_answers[i] = selected

        with st.expander("Show explanation after answering"):
            if selected == q["answer"]:
                st.success(f"Correct. {q['explanation']}")
            else:
                st.error(f"Correct answer: {q['answer']}. {q['explanation']}")

    correct, total, percent = get_knowledge_score()
    st.divider()
    st.metric("Knowledge score", f"{percent}% ({correct}/{total})")

    if percent >= PASS_MARK:
        mark_section_complete("Knowledge check")
        celebrate_once("knowledge_passed", "Knowledge check passed.")
        st.success("Knowledge check passed.")
        celebration_banner("Knowledge Check Passed", f"Your score is {percent}%. You may proceed to the Google Form completion record.")
        go_next_button("Next: Complete Google Form ➜", "5. Google Form", "next_to_google_form")
    else:
        st.error("Knowledge check not yet passed. Please review the answers.")
        st.button("Next: Complete Google Form ➜", disabled=True, key="next_to_google_form_disabled")


def page_google_form():
    st.title("Google Form Completion Record")

    st.markdown(
        """
        Please complete the official Google Form before proceeding.

        **Step 1** — Open and submit the Google Form  
        **Step 2** — Return to this app  
        **Step 3** — Tick the confirmation boxes below  
        **Step 4** — Click **Confirm Google Form Completion**  
        **Step 5** — Continue to the certificate page
        """
    )

    st.link_button("Open Google Form", GOOGLE_FORM_URL)

    st.markdown(
        """
        <div class="warning-box">
        Complete the Google Form first. After submitting it, return here and confirm completion.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("google_form_confirmation_form"):
        google_form_done = st.checkbox(
            "I confirm that I have completed and submitted the Google Form.",
            value=st.session_state.google_form_submitted,
        )

        declaration_done = st.checkbox(
            "I declare that I completed all required case scenarios myself and will follow the MyHeartRisk SOP, including not guessing unknown answers.",
            value=st.session_state.declaration_agreed,
        )

        confirm_google_form = st.form_submit_button(
            "Confirm Google Form Completion",
            type="primary"
        )

    if confirm_google_form:
        st.session_state.google_form_submitted = google_form_done
        st.session_state.declaration_agreed = declaration_done

        if google_form_done and declaration_done:
            mark_section_complete("Google form")
            celebrate_once("google_form_completed", "Google Form and declaration completed.")
            celebration_banner(
                "Google Form Record Completed",
                "Your completion record has been confirmed. You may now proceed to the certificate page."
            )
            st.success("Google Form completion confirmed.")
        else:
            st.error("Please complete the Google Form and tick both confirmation boxes before continuing.")

    st.divider()

    record = build_completion_record()
    st.download_button(
        "Download completion evidence JSON",
        data=json.dumps(record, indent=2),
        file_name=f"myheartrisk_completion_evidence_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
    )

    if st.session_state.section_completed.get("Google form"):
        go_next_button("Next: View Certificate ➜", "6. Certificate", "next_to_certificate")
    else:
        st.button("Next: View Certificate ➜", disabled=True, key="next_to_certificate_disabled")


def page_certificate():
    st.title("Certificate of Completion")

    if st.session_state.trainee.get("full_name") and st.session_state.trainee.get("email"):
        st.session_state.certificate_id = get_certificate_id(
            st.session_state.trainee.get("full_name", ""),
            st.session_state.trainee.get("email", ""),
        )

    case_correct, case_total = get_case_score()
    _, _, knowledge_percent = get_knowledge_score()

    status_rows = [
        ["Trainee details completed", "Yes" if st.session_state.trainee.get("full_name") and st.session_state.trainee.get("email") else "No"],
        ["All cases correct", f"{case_correct}/{case_total}"],
        ["Knowledge check", f"{knowledge_percent}%"],
        ["Google Form submitted", "Yes" if st.session_state.google_form_submitted else "No"],
        ["Declaration agreed", "Yes" if st.session_state.declaration_agreed else "No"],
    ]
    st.dataframe(pd.DataFrame(status_rows, columns=["Requirement", "Status"]), use_container_width=True, hide_index=True)

    if is_eligible():
        mark_section_complete("Certificate")
        celebrate_once("certificate_unlocked", "Certificate unlocked. Congratulations!")
        st.success("Congratulations. Certificate is unlocked.")
        celebration_banner("Certificate Unlocked", "The trainee has completed all requirements and is now eligible for the certificate.")

        if not SIGNATURE_IMAGE.exists():
            st.warning(f"Signature image not found: {SIGNATURE_IMAGE.name}")
        html = certificate_html()
        components.html(html, height=860, scrolling=True)

        st.download_button(
            "Download certificate HTML",
            data=html,
            file_name=f"MyHeartRisk_Certificate_{st.session_state.certificate_id}.html",
            mime="text/html",
        )

        pdf_bytes = None
        pdf_error = None
        if FPDF_AVAILABLE:
            try:
                pdf_bytes = generate_certificate_pdf()
            except Exception as e:
                pdf_error = str(e)

        if pdf_bytes:
            st.download_button(
                "Download certificate PDF",
                data=pdf_bytes,
                file_name=f"MyHeartRisk_Certificate_{st.session_state.certificate_id}.pdf",
                mime="application/pdf",
            )
        else:
            if not FPDF_AVAILABLE:
                st.info("PDF generation requires fpdf2. Install using: pip install fpdf2")
            elif pdf_error:
                st.error(f"PDF generation failed: {pdf_error}")

        st.markdown(
            """
            <div class="success-box">
            The user is now certified as a MyHeartRisk NADI Screener.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("Certificate is locked. Please complete all requirements first.")


# -----------------------------
# MAIN
# -----------------------------
def main():
    inject_css()
    init_state()
    sidebar()

    if st.session_state.current_step == "1. Training":
        page_training()
    elif st.session_state.current_step == "2. Trainee Details":
        page_trainee_details()
    elif st.session_state.current_step == "3. Case Scenarios":
        page_cases()
    elif st.session_state.current_step == "4. Knowledge Check":
        page_knowledge()
    elif st.session_state.current_step == "5. Google Form":
        page_google_form()
    elif st.session_state.current_step == "6. Certificate":
        page_certificate()


if __name__ == "__main__":
    main()
