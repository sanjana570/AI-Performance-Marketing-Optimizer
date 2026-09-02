import os
import json
import time

import streamlit as st
from dotenv import load_dotenv
from google import genai


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Performance Marketing Optimizer",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# GEMINI SETUP
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "GEMINI_API_KEY was not found. "
        "Please check your .env file."
    )
    st.stop()

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# HEADER
# ============================================================

st.title("🤖 AI-Powered Performance Marketing Optimizer")

st.write(
    "Enter campaign performance metrics and generate "
    "AI-powered marketing optimization recommendations."
)

st.divider()


# ============================================================
# CAMPAIGN INFORMATION
# ============================================================

st.subheader("📌 Campaign Information")

campaign_options = [
    "Google Brand Search",
    "Google Generic Search",
    "Google High-Intent Search",
    "Google Shopping",
    "Meta Broad Prospecting",
    "Meta Creative Test",
    "Meta Interest Prospecting",
    "Meta Retargeting"
]

col1, col2 = st.columns(2)

with col1:

    campaign_name = st.selectbox(
        "Campaign Name",
        campaign_options
    )

with col2:

    platform = st.selectbox(
        "Platform",
        [
            "Google Ads",
            "Meta Ads",
            "LinkedIn Ads",
            "Other"
        ]
    )


objective = st.selectbox(
    "Campaign Objective",
    [
        "Sales",
        "Leads",
        "Traffic",
        "Awareness"
    ]
)


st.divider()


# ============================================================
# CAMPAIGN PERFORMANCE INPUTS
# ============================================================

st.subheader("📊 Campaign Performance Metrics")

st.caption(
    "Change any value below. The calculated KPIs "
    "will update automatically."
)


# ------------------------- ROW 1 ----------------------------

col1, col2, col3 = st.columns(3)

with col1:

    spend = st.number_input(
        "Spend (₹)",
        min_value=0.0,
        value=1000.0,
        step=100.0
    )

with col2:

    revenue = st.number_input(
        "Revenue (₹)",
        min_value=0.0,
        value=5000.0,
        step=500.0
    )

with col3:

    purchases = st.number_input(
        "Purchases / Conversions",
        min_value=0,
        value=10,
        step=1
    )


# ------------------------- ROW 2 ----------------------------

col1, col2, col3 = st.columns(3)

with col1:

    impressions = st.number_input(
        "Impressions",
        min_value=0,
        value=50000,
        step=1000
    )

with col2:

    clicks = st.number_input(
        "Clicks",
        min_value=0,
        value=2500,
        step=100
    )

with col3:

    product_views = st.number_input(
        "Product Views",
        min_value=0,
        value=1200,
        step=50
    )


# ------------------------- ROW 3 ----------------------------

col1, col2 = st.columns(2)

with col1:

    add_to_carts = st.number_input(
        "Add to Carts",
        min_value=0,
        value=150,
        step=10
    )

with col2:

    checkouts = st.number_input(
        "Checkouts",
        min_value=0,
        value=50,
        step=5
    )


st.divider()


# ============================================================
# AUTOMATIC KPI CALCULATIONS
# ============================================================

st.subheader("📈 Calculated Performance KPIs")


# ROAS
if spend > 0:
    roas = revenue / spend
else:
    roas = 0.0


# CPA
if purchases > 0:
    cpa = spend / purchases
else:
    cpa = 0.0


# CTR
if impressions > 0:
    ctr = (clicks / impressions) * 100
else:
    ctr = 0.0


# CPC
if clicks > 0:
    cpc = spend / clicks
else:
    cpc = 0.0


# Conversion Rate
if clicks > 0:
    conversion_rate = (purchases / clicks) * 100
else:
    conversion_rate = 0.0


# Add-to-Cart Rate
if product_views > 0:
    add_to_cart_rate = (
        add_to_carts / product_views
    ) * 100
else:
    add_to_cart_rate = 0.0


# Checkout Rate
if add_to_carts > 0:
    checkout_rate = (
        checkouts / add_to_carts
    ) * 100
else:
    checkout_rate = 0.0


# ============================================================
# KPI DISPLAY
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "ROAS",
        f"{roas:.2f}x"
    )

with col2:

    st.metric(
        "CPA",
        f"₹{cpa:,.2f}"
    )

with col3:

    st.metric(
        "CTR",
        f"{ctr:.2f}%"
    )

with col4:

    st.metric(
        "CPC",
        f"₹{cpc:,.2f}"
    )


col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Conversion Rate",
        f"{conversion_rate:.2f}%"
    )

with col2:

    st.metric(
        "Add-to-Cart Rate",
        f"{add_to_cart_rate:.2f}%"
    )

with col3:

    st.metric(
        "Checkout Rate",
        f"{checkout_rate:.2f}%"
    )


st.divider()


# ============================================================
# CURRENT CAMPAIGN SUMMARY
# ============================================================

st.subheader("📋 Current Campaign Summary")

col1, col2 = st.columns(2)

with col1:

    st.write(f"**Campaign:** {campaign_name}")
    st.write(f"**Platform:** {platform}")
    st.write(f"**Objective:** {objective}")
    st.write(f"**Spend:** ₹{spend:,.2f}")
    st.write(f"**Revenue:** ₹{revenue:,.2f}")

with col2:

    st.write(f"**Purchases:** {purchases:,}")
    st.write(f"**Impressions:** {impressions:,}")
    st.write(f"**Clicks:** {clicks:,}")
    st.write(f"**Add to Carts:** {add_to_carts:,}")
    st.write(f"**Checkouts:** {checkouts:,}")


st.divider()


# ============================================================
# GEMINI AI ANALYSIS
# ============================================================

st.subheader("🤖 AI Marketing Analysis")

st.write(
    "Gemini will analyze the current campaign values "
    "entered above."
)


analyze_button = st.button(
    "🤖 Generate AI Recommendation",
    type="primary",
    use_container_width=True
)


if analyze_button:

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are an expert performance marketing analyst.

Analyze the following advertising campaign.

IMPORTANT:
Use ONLY the campaign information and metrics provided below.
Do not invent missing data.
Do not assume additional metrics.
Your recommendation must respond to the actual numbers.

CAMPAIGN INFORMATION

Campaign: {campaign_name}
Platform: {platform}
Campaign Objective: {objective}

CAMPAIGN PERFORMANCE

Spend: ₹{spend:,.2f}
Revenue: ₹{revenue:,.2f}
Purchases / Conversions: {purchases}
Impressions: {impressions}
Clicks: {clicks}
Product Views: {product_views}
Add to Carts: {add_to_carts}
Checkouts: {checkouts}

CALCULATED KPIs

ROAS: {roas:.2f}x
CPA: ₹{cpa:,.2f}
CTR: {ctr:.2f}%
CPC: ₹{cpc:,.2f}
Conversion Rate: {conversion_rate:.2f}%
Add-to-Cart Rate: {add_to_cart_rate:.2f}%
Checkout Rate: {checkout_rate:.2f}%

ANALYSIS REQUIREMENTS

Evaluate the campaign's efficiency and conversion performance.

Identify the most important performance issue.

Recommend whether the campaign should be:
- Scale
- Scale Carefully
- Maintain / Test
- Reduce

Priority must be:
- High
- Medium
- Low

Recommended budget rules:

If Scale:
Recommend approximately 10%–25% above current spend.

If Scale Carefully:
Recommend approximately 5%–10% above current spend.

If Maintain / Test:
Recommend approximately the current spend.

If Reduce:
Recommend approximately 10%–25% below current spend.

Recommended Budget MUST be:
- A single numeric value
- In INR
- Based on the current spend
- No currency symbol inside the numeric field
- No budget range
- No dollars
- No USD
- No percentage

Return ONLY valid JSON.

Use exactly this structure:

{{
    "Performance Status": "",
    "Primary Issue": "",
    "Recommended Action": "",
    "Priority": "",
    "Recommended Budget": 0,
    "Reasoning": ""
}}

Give practical performance marketing advice.

Do not invent data.
"""


    # --------------------------------------------------------
    # GEMINI REQUEST WITH RETRIES
    # --------------------------------------------------------

    response = None
    last_error = None

    with st.spinner(
        "🤖 Gemini is analyzing the current campaign..."
    ):

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt
                )

                break

            except Exception as error:

                last_error = error

                if attempt < 2:

                    time.sleep(5)

                else:

                    response = None


    # --------------------------------------------------------
    # IF GEMINI FAILED
    # --------------------------------------------------------

    if response is None:

        st.error(
            "Gemini is temporarily unavailable. "
            "Please try again in a moment."
        )

        st.caption(
            f"Technical details: {last_error}"
        )

        st.stop()


    # --------------------------------------------------------
    # PROCESS GEMINI RESPONSE
    # --------------------------------------------------------

    try:

        text = response.text.strip()

        # Remove Markdown code fences if Gemini adds them
        if text.startswith("```"):

            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()


        result = json.loads(text)


        # ----------------------------------------------------
        # VALIDATE AI OUTPUT
        # ----------------------------------------------------

        performance_status = result.get(
            "Performance Status",
            "Maintain / Test"
        )

        priority = result.get(
            "Priority",
            "Medium"
        )

        primary_issue = result.get(
            "Primary Issue",
            "No issue provided."
        )

        recommended_action = result.get(
            "Recommended Action",
            "Review campaign performance."
        )

        reasoning = result.get(
            "Reasoning",
            "No reasoning provided."
        )

        ai_budget = result.get(
            "Recommended Budget",
            spend
        )


        # Convert AI budget to number
        try:

            ai_budget = float(ai_budget)

        except:

            ai_budget = float(spend)


        # ----------------------------------------------------
        # BUDGET VALIDATION
        # ----------------------------------------------------

        if performance_status == "Scale":

            minimum_budget = spend * 1.10
            maximum_budget = spend * 1.25

        elif performance_status == "Scale Carefully":

            minimum_budget = spend * 1.05
            maximum_budget = spend * 1.10

        elif performance_status == "Maintain / Test":

            minimum_budget = spend * 0.90
            maximum_budget = spend * 1.10

        else:

            minimum_budget = spend * 0.75
            maximum_budget = spend * 0.90


        if spend > 0:

            ai_budget = max(
                minimum_budget,
                min(
                    ai_budget,
                    maximum_budget
                )
            )

        ai_budget = round(
            ai_budget,
            2
        )


        # ----------------------------------------------------
        # SUCCESS MESSAGE
        # ----------------------------------------------------

        st.success(
            "AI analysis completed successfully!"
        )


        # ----------------------------------------------------
        # AI RESULT
        # ----------------------------------------------------

        st.subheader(
            "🤖 Gemini AI Recommendation"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Performance Status",
                performance_status
            )


        with col2:

            st.metric(
                "Priority",
                priority
            )


        with col3:

            st.metric(
                "Recommended Budget",
                f"₹{ai_budget:,.2f}"
            )


        st.markdown(
            "### 🎯 Primary Issue"
        )

        st.write(
            primary_issue
        )


        st.markdown(
            "### 💡 Recommended Action"
        )

        st.write(
            recommended_action
        )


        st.markdown(
            "### 🧠 AI Reasoning"
        )

        st.write(
            reasoning
        )


    # --------------------------------------------------------
    # JSON ERROR
    # --------------------------------------------------------

    except json.JSONDecodeError:

        st.error(
            "Gemini responded, but the response format "
            "was not valid JSON."
        )

        st.write(
            response.text
        )


    # --------------------------------------------------------
    # GENERAL ERROR
    # --------------------------------------------------------

    except Exception as error:

        st.error(
            f"Unable to process the AI response: {error}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Performance Marketing Optimizer • "
    "Interactive campaign analysis powered by Gemini"
)