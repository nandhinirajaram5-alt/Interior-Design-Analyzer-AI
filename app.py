import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="InterioAI - Interior Design Assistant",
    page_icon="🏠",
    layout="wide"
)


# =========================================================
# GEMINI API CONFIGURATION
# =========================================================



# GOOGLE_API_KEY = "YOUR_API_KEY"

GOOGLE_API_KEY = "AQ.Ab8RN6LI3Oa9huD0uuhtd2YD7wm-9iuz5rbioJm5iLTEqn_Wsg"

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-3.6-flash")


# =========================================================
# SESSION STATE
# =========================================================

if "room_analysis" not in st.session_state:
    st.session_state.room_analysis = None

if "design_recommendations" not in st.session_state:
    st.session_state.design_recommendations = None

if "budget_analysis" not in st.session_state:
    st.session_state.budget_analysis = None

if "designer_question_answer" not in st.session_state:
    st.session_state.designer_question_answer = None

if "room_image" not in st.session_state:
    st.session_state.room_image = None

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_response(text):

    """
    Removes unnecessary markdown code fences
    if the AI returns them.
    """

    text = text.strip()

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*$",
        "",
        text
    )

    return text.strip()


def extract_json(text):

    """
    Attempts to extract JSON from an AI response.
    """

    text = clean_response(text)

    try:
        return json.loads(text)

    except Exception:

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if match:

            try:
                return json.loads(
                    match.group()
                )

            except Exception:
                return None

    return None


def calculate_budget_total(budget_data):

    """
    Calculates the total budget using Python.
    """

    total = 0

    if isinstance(budget_data, dict):

        for value in budget_data.values():

            if isinstance(value, (int, float)):

                total += value

    return total


# =========================================================
# TITLE
# =========================================================

st.title("🏠 InterioAI")
st.caption("AI-powered interior design assistant for your space.")

# =========================================================
# USER PROFILE
# =========================================================

st.divider()

st.subheader("👤 Tell Us About Your Design Goal")


col1, col2, col3 = st.columns(3)


with col1:

    room_type = st.selectbox(
        "🏠 Room Type",
        [
            "Living Room",
            "Bedroom",
            "Kitchen",
            "Dining Room",
            "Study Room",
            "Home Office",
            "Kids Room",
            "Balcony",
            "Other"
        ]
    )


with col2:

    preferred_style = st.selectbox(
        "✨ Preferred Interior Style",
        [
            "Modern",
            "Minimalist",
            "Scandinavian",
            "Bohemian",
            "Traditional",
            "Contemporary",
            "Industrial",
            "Luxury",
            "Rustic",
            "Not Sure"
        ]
    )


with col3:

    budget = st.number_input(
        "💰 Maximum Budget (₹)",
        min_value=1000,
        value=25000,
        step=5000
    )


# =========================================================
# DESIGN PREFERENCES
# =========================================================

with st.expander("🎨 Design Preferences", expanded=True):

    col1, col2 = st.columns(2)

    with col1:
        preferred_colors = st.text_input(
            "🎨 Preferred Colors",
            placeholder="Beige, white and light brown"
        )

    with col2:
        room_requirements = st.text_input(
            "💡 What would you like to improve?",
            placeholder="More storage, brighter, cozy atmosphere..."
        )


# =========================================================
# LIFESTYLE PREFERENCES
# =========================================================

with st.expander("🏠 Lifestyle Preferences", expanded=False):

    col1, col2, col3 = st.columns(3)

    with col1:
        maintenance_preference = st.selectbox(
            "🧹 Maintenance",
            [
                "Low Maintenance",
                "Moderate Maintenance",
                "High Maintenance is Fine"
            ]
        )

    with col2:
        lighting_preference = st.selectbox(
            "💡 Lighting",
            [
                "Bright",
                "Warm & Cozy",
                "Balanced",
                "Natural Light Focus"
            ]
        )

    with col3:
        furniture_preference = st.selectbox(
            "🪑 Furniture",
            [
                "Keep Existing Furniture",
                "Mix Existing & New",
                "Mostly New Furniture"
            ]
        )

# =========================================================
# ROOM IMAGE UPLOAD
# =========================================================

st.divider()

st.subheader("📷 Upload Your Room")


room_file = st.file_uploader(
    "Upload a clear image of your room",
    type=[
        "jpg",
        "jpeg",
        "png"
    ],
    key="room_upload"
)


# =========================================================
# DISPLAY UPLOADED IMAGE
# =========================================================

if room_file is not None:

    try:

        image = Image.open(room_file)

        st.session_state.room_image = image

        col1, col2 = st.columns([2, 1])

        with col1:

            st.image(
                image,
                caption="Uploaded Room",
                use_container_width=True
            )

        with col2:

            st.info(
                """
                📌 For better analysis:

                • Use a clear image
                • Capture most of the room
                • Avoid extremely dark images
                • Keep major furniture visible
                """
            )

        st.success(
            "✅ Room image uploaded successfully!"
        )

    except Exception:

        st.error(
            "❌ Unable to read the uploaded image."
        )


# =========================================================
# ANALYZE ROOM BUTTON
# =========================================================

if st.session_state.room_image is not None:

    st.divider()

    analyze_button = st.button(
        "🚀 Analyze My Room",
        use_container_width=True
    )


    if analyze_button:

        with st.spinner(
            "🤖 AI is analyzing your room..."
        ):

            try:

                # =================================================
                # ROOM ANALYSIS PROMPT
                # =================================================

                analysis_prompt = f"""

You are an expert AI Interior Design Assistant.

Analyze the uploaded room image and provide a detailed,
practical and personalized interior design assessment.

========================================================
USER INFORMATION
========================================================

Room Type:
{room_type}

Preferred Interior Style:
{preferred_style}

Maximum Budget:
₹{budget}

Preferred Colors:
{preferred_colors if preferred_colors else "Not specified"}

Room Requirements:
{room_requirements if room_requirements else "Not specified"}

Maintenance Preference:
{maintenance_preference}

Lighting Preference:
{lighting_preference}

Furniture Preference:
{furniture_preference}


========================================================
VISUAL ANALYSIS
========================================================

Carefully analyze the uploaded image.

Identify only things that are reasonably visible.

Analyze:

1. Existing furniture
2. Furniture arrangement
3. Wall colors
4. Floor appearance
5. Lighting
6. Windows
7. Doors
8. Storage
9. Decor
10. Empty/unused visible space
11. Overall visual style
12. Possible design improvements


========================================================
IMPORTANT RULES
========================================================

- Do not invent objects that are not visible.
- Do not claim exact room dimensions.
- Do not claim exact measurements from the image.
- Clearly state when something cannot be determined.
- Do not provide structural safety conclusions.
- Budget amounts are approximate estimates.
- Recommendations should be realistic.
- Consider the user's stated budget.
- Prefer practical improvements over unnecessary purchases.


========================================================
ROOM DESIGN SCORE
========================================================

Give estimated scores from 0 to 100 for:

Space Utilization
Color Harmony
Lighting
Furniture Arrangement
Storage
Decor
Overall Design

These are subjective AI-based design scores,
not professional architectural measurements.


========================================================
OUTPUT FORMAT
========================================================

Return the analysis in the following format:

# 🏠 Current Room Analysis

Provide a concise description of the room.

# 🪑 Existing Furniture

List visible furniture and their condition/usefulness.

# 🎨 Color Analysis

Describe the current color palette.

# 💡 Lighting Analysis

Describe visible lighting and natural light.

# ✨ Current Style

Identify the apparent current interior style.

# 📊 Design Scores

| Category | Score / 100 | Explanation |
|---|---:|---|
| Space Utilization | | |
| Color Harmony | | |
| Lighting | | |
| Furniture Arrangement | | |
| Storage | | |
| Decor | | |
| Overall Design | | |

# ⚠️ Design Problems

List the main visible areas that could be improved.

# 🌟 Main Strengths

List the strongest aspects of the current room.

"""

                analysis_response = model.generate_content(
                    [
                        analysis_prompt,
                        st.session_state.room_image
                    ]
                )


                st.session_state.room_analysis = (
                    analysis_response.text
                )


                # =================================================
                # DESIGN RECOMMENDATION PROMPT
                # =================================================

                recommendation_prompt = f"""

You are an expert AI Interior Designer.

Create a personalized redesign plan using:

1. The uploaded room image
2. User preferences
3. Room analysis

========================================================
USER PREFERENCES
========================================================

Room:
{room_type}

Preferred Style:
{preferred_style}

Budget:
₹{budget}

Preferred Colors:
{preferred_colors if preferred_colors else "Not specified"}

Requirements:
{room_requirements if room_requirements else "Not specified"}

Maintenance:
{maintenance_preference}

Lighting:
{lighting_preference}

Furniture:
{furniture_preference}


========================================================
ROOM ANALYSIS
========================================================

{st.session_state.room_analysis}


========================================================
TASK
========================================================

Create a practical interior design plan.

Include:

1. Furniture recommendations
2. Furniture rearrangement
3. Decor recommendations
4. Lighting recommendations
5. Storage improvements
6. Color palette
7. Textiles
8. Wall decoration
9. Space optimization
10. Low-cost alternatives


========================================================
DESIGN PRINCIPLES
========================================================

Prioritize:

- Functionality
- User preferences
- Budget
- Existing furniture
- Visual balance
- Practicality
- Low maintenance when requested


========================================================
OUTPUT FORMAT
========================================================

# ✨ Personalized Design Plan

## 🎨 Recommended Style

Explain the recommended style.

## 🎨 Recommended Color Palette

### Primary Color
...

### Secondary Color
...

### Accent Color
...

## 🪑 Furniture Recommendations

| Item | Action | Priority | Reason |
|---|---|---|---|

Action must be one of:

Keep
Rearrange
Replace
Add

## 💡 Lighting Recommendations

...

## 🪴 Decor Recommendations

...

## 📦 Storage Recommendations

...

## 🧵 Textile Recommendations

...

## 📐 Space Optimization

...

## 💸 Low-Budget Alternatives

...

## 🏠 Final Design Concept

Describe how the completed room should look and feel.

"""

                recommendation_response = model.generate_content(
                    [
                        recommendation_prompt,
                        st.session_state.room_image
                    ]
                )


                st.session_state.design_recommendations = (
                    recommendation_response.text
                )


                # =================================================
                # BUDGET PROMPT
                # =================================================

                budget_prompt = f"""

You are an interior design budget planning assistant.

Create an approximate budget allocation for this room.

========================================================
ROOM
========================================================

{room_type}

========================================================
DESIGN STYLE
========================================================

{preferred_style}

========================================================
TOTAL AVAILABLE BUDGET
========================================================

₹{budget}

========================================================
RECOMMENDATIONS
========================================================

{st.session_state.design_recommendations}


========================================================
RULES
========================================================

- Keep the estimated total within approximately the user's budget.
- Use realistic approximate amounts.
- Clearly label estimates as approximate.
- Do not claim these are exact market prices.
- Prioritize essential improvements.


========================================================
OUTPUT FORMAT
========================================================

Return ONLY valid JSON.

Example:

{{
    "Furniture": 0,
    "Lighting": 0,
    "Decor": 0,
    "Storage": 0,
    "Textiles": 0,
    "Wall_Improvements": 0,
    "Miscellaneous": 0
}}

"""

                budget_response = model.generate_content(
                    budget_prompt
                )

                budget_data = extract_json(
                    budget_response.text
                )


                if budget_data:

                    total_budget = calculate_budget_total(
                        budget_data
                    )

                    st.session_state.budget_analysis = {
                        "categories": budget_data,
                        "total": total_budget
                    }

                else:

                    st.session_state.budget_analysis = None


                st.session_state.analysis_complete = True

                st.session_state.designer_question_answer = None


                st.success(
                    "🎉 Room analysis completed successfully!"
                )


            except Exception as e:

                st.error(
                    "❌ Something went wrong while analyzing "
                    "the room."
                )

                st.exception(e)


# =========================================================
# DISPLAY ROOM ANALYSIS
# =========================================================

# =========================================================
# DISPLAY AI RESULTS
# =========================================================

# =========================================================
# DISPLAY AI RESULTS
# =========================================================

# AI Results
# ---------------------------------------

if (
    st.session_state.room_analysis
    or st.session_state.design_recommendations
):

    st.divider()

    # Subtle colored tabs
    st.markdown(
        """
        <style>

        div[data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #faf8f5;
            padding: 6px;
            border-radius: 12px;
        }

        button[data-baseweb="tab"] {
            background-color: #f1eee9;
            border-radius: 9px;
            padding: 9px 18px;
            font-weight: 600;
            color: #55504a;
            border: none;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #ded6ca;
            color: #3f3a35;
        }

        div[data-baseweb="tab-highlight"] {
            background-color: transparent;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(
        ["🔍 Room Analysis", "✨ Design Plan"]
    )

    with tab1:
        if st.session_state.room_analysis:
            st.markdown(st.session_state.room_analysis)

    with tab2:
        if st.session_state.design_recommendations:
            st.markdown(st.session_state.design_recommendations)


# =========================================================
# DISPLAY BUDGET ANALYSIS
# =========================================================



# ---------------------------------------
# Budget Analysis
# ---------------------------------------

if st.session_state.budget_analysis:

    st.divider()

    st.subheader("💰 Budget Overview")

    # Get the actual budget structure
    budget_info = st.session_state.budget_analysis
    budget_categories = budget_info.get("categories", {})
    estimated_total = budget_info.get("total", 0)

    # ---------------------------------------------------------
    # BUDGET METRICS
    # ---------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💰 Maximum Budget",
            f"₹{budget:,.0f}"
        )

    with col2:
        st.metric(
            "📊 Estimated Cost",
            f"₹{estimated_total:,.0f}"
        )

    with col3:
        remaining = budget - estimated_total

        st.metric(
            "💵 Remaining Budget",
            f"₹{remaining:,.0f}"
        )

    # ---------------------------------------------------------
    # BUDGET BREAKDOWN
    # ---------------------------------------------------------

    with st.expander("📊 View Budget Breakdown", expanded=True):

        for category, amount in budget_categories.items():

            st.write(
                f"**{category.replace('_', ' ')}:** "
                f"₹{amount:,.0f}"
            )

    # ---------------------------------------------------------
    # BUDGET STATUS
    # ---------------------------------------------------------

    if estimated_total > budget:

        st.warning(
            "⚠️ The AI-generated estimate exceeds your "
            "maximum budget. Consider using the low-budget "
            "alternatives."
        )

    else:

        st.success(
            "✅ The estimated design fits within your "
            "selected budget."
        )



# =========================================================
# FOLLOW-UP AI DESIGNER
# =========================================================

if (
    st.session_state.room_analysis
    and st.session_state.design_recommendations
):

    st.divider()

    st.subheader(
        "💬 Ask Your AI Interior Designer"
    )

    st.write(
        "Ask questions about your room, furniture, "
        "colors, budget, layout, or design style."
    )


    with st.form(
        "designer_question_form"
    ):

        user_question = st.text_input(
            "Your Question",
            placeholder=(
                "Example: How can I redesign this room "
                "within ₹10,000?"
            )
        )


        ask_button = st.form_submit_button(
            "🤖 Ask AI Designer",
            use_container_width=True
        )


    # =====================================================
    # PROCESS QUESTION
    # =====================================================

    if ask_button:

        if user_question.strip() == "":

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "🤖 Your AI Interior Designer is thinking..."
            ):

                try:

                    question_prompt = f"""

You are a personalized AI Interior Designer.

Answer the user's question using the room analysis,
design recommendations, and user preferences.

==================================================
ROOM INFORMATION
==================================================

Room:
{room_type}

Preferred Style:
{preferred_style}

Budget:
₹{budget}

Preferred Colors:
{preferred_colors if preferred_colors else "Not specified"}

Requirements:
{room_requirements if room_requirements else "Not specified"}

==================================================
ROOM ANALYSIS
==================================================

{st.session_state.room_analysis}

==================================================
DESIGN RECOMMENDATIONS
==================================================

{st.session_state.design_recommendations}

==================================================
USER QUESTION
==================================================

{user_question}

==================================================
INSTRUCTIONS
==================================================

Provide a practical and personalized answer.

Do not invent room features.

Do not claim exact measurements.

Do not claim exact product prices.

If the question requires information that cannot
be determined from the image, clearly say so.

Whenever possible provide:

1. Direct answer
2. Reasoning
3. Recommended action
4. Budget consideration

Keep the answer useful and easy to understand.

"""

                    question_response = (
                        model.generate_content(
                            question_prompt
                        )
                    )


                    st.session_state.designer_question_answer = (
                        question_response.text
                    )


                except Exception:

                    st.error(
                        "❌ Unable to generate an answer."
                    )


# =========================================================
# DISPLAY AI DESIGNER ANSWER
# =========================================================

if st.session_state.designer_question_answer:

    st.divider()

    st.subheader(
        "🤖 AI Interior Designer"
    )

    st.markdown(
        st.session_state.designer_question_answer
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "InterioAI • AI-powered interior design assistance. "
    "Recommendations are AI-generated estimates and should "
    "not replace professional architectural or structural advice."
)