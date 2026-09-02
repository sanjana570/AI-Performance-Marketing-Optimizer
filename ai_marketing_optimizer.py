import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from google import genai

# ============================================================
# GEMINI AI PERFORMANCE MARKETING PIPELINE
# ============================================================

INPUT_FILE = "Marketing_Command_Center_COMPLETE_FINAL_Clear(1).xlsx"
OUTPUT_FILE = "AI_Marketing_Recommendations.xlsx"

MAX_RETRIES = 3
RETRY_DELAY = 8

# ------------------------------------------------------------
# GEMINI CONNECTION
# ------------------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")

client = genai.Client(api_key=api_key)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

print("\nLoading campaign data...")

df = pd.read_excel(
    INPUT_FILE,
    sheet_name="Campaign Data"
)

df.columns = df.columns.str.strip()

print(f"Raw records found: {len(df)}")


# ------------------------------------------------------------
# NUMERIC DATA
# ------------------------------------------------------------

for column in ["Spend", "Revenue", "Purchases"]:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0)


# ------------------------------------------------------------
# CAMPAIGN-LEVEL AGGREGATION
# ------------------------------------------------------------

campaigns = (
    df.groupby(
        ["Campaign", "Platform"],
        as_index=False
    )
    .agg({
        "Spend": "sum",
        "Revenue": "sum",
        "Purchases": "sum"
    })
)

campaigns["ROAS (x)"] = (
    campaigns["Revenue"] /
    campaigns["Spend"]
).where(
    campaigns["Spend"] > 0,
    0
)

campaigns["CPA (₹)"] = (
    campaigns["Spend"] /
    campaigns["Purchases"]
).where(
    campaigns["Purchases"] > 0,
    0
)


# ------------------------------------------------------------
# GEMINI ANALYSIS
# ------------------------------------------------------------

def analyze_campaign(row):

    prompt = f"""
You are an expert performance marketing analyst.

Analyze this advertising campaign.

Campaign: {row['Campaign']}
Platform: {row['Platform']}

Current Spend: ₹{row['Spend']:.2f}
Revenue: ₹{row['Revenue']:.2f}
Purchases: {row['Purchases']:.0f}
CPA: ₹{row['CPA (₹)']:.2f}
ROAS: {row['ROAS (x)']:.2f}x

Return ONLY valid JSON.

Use exactly these fields:

{{
    "Performance Status": "",
    "Primary Issue": "",
    "Recommended Action": "",
    "Priority": "",
    "Recommended Budget": 0,
    "Reasoning": ""
}}

Performance Status must be exactly one of:
Scale
Scale Carefully
Maintain / Test
Reduce

Priority must be exactly one of:
High
Medium
Low

Budget guidance:

- Scale: recommend approximately 10%–25% above current spend.
- Scale Carefully: recommend approximately 5%–10% above current spend.
- Maintain / Test: keep approximately the current spend.
- Reduce: recommend approximately 10%–25% below current spend.

Recommended Budget MUST be a single numeric INR value.

Do not use ranges.
Do not write percentages in the budget field.
Do not write "3x" or "5x".

Use ROAS, CPA, revenue and purchases to make the decision.

Give practical performance marketing advice.
Do not invent data.
"""


    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            text = response.text.strip()

            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            return json.loads(text)

        except Exception as error:

            print(
                f"   Gemini attempt "
                f"{attempt}/{MAX_RETRIES} failed: {error}"
            )

            if attempt < MAX_RETRIES:

                print(
                    f"   Retrying in {RETRY_DELAY} seconds..."
                )

                time.sleep(RETRY_DELAY)

            else:

                raise error


# ------------------------------------------------------------
# BUDGET VALIDATION
# ------------------------------------------------------------

def validate_budget(
    ai_budget,
    status,
    current_spend
):

    try:
        ai_budget = float(ai_budget)

    except:
        ai_budget = current_spend


    if status == "Scale":

        minimum = current_spend * 1.10
        maximum = current_spend * 1.25

    elif status == "Scale Carefully":

        minimum = current_spend * 1.05
        maximum = current_spend * 1.10

    elif status == "Maintain / Test":

        minimum = current_spend * 0.90
        maximum = current_spend * 1.10

    else:

        minimum = current_spend * 0.75
        maximum = current_spend * 0.90


    return round(
        max(
            minimum,
            min(ai_budget, maximum)
        ),
        2
    )


# ------------------------------------------------------------
# PROCESS ALL CAMPAIGNS
# ------------------------------------------------------------

results = []

total = len(campaigns)

print("\n======================================")
print("GEMINI AI MARKETING ANALYSIS")
print("======================================")

print(
    f"Unique campaigns to analyze: {total}"
)

print()


for index, (_, row) in enumerate(
    campaigns.iterrows(),
    start=1
):

    print(
        f"[{index}/{total}] "
        f"{row['Campaign']} "
        f"({row['Platform']})"
    )

    try:

        ai_result = analyze_campaign(row)

        status = ai_result.get(
            "Performance Status",
            "Maintain / Test"
        )

        final_budget = validate_budget(
            ai_result.get(
                "Recommended Budget",
                row["Spend"]
            ),
            status,
            row["Spend"]
        )


        results.append({

            "Campaign":
                row["Campaign"],

            "Platform":
                row["Platform"],

            "Spend":
                round(row["Spend"], 2),

            "Revenue":
                round(row["Revenue"], 2),

            "Purchases":
                row["Purchases"],

            "CPA (₹)":
                round(row["CPA (₹)"], 2),

            "ROAS (x)":
                round(row["ROAS (x)"], 2),

            "AI Performance Status":
                status,

            "AI Primary Issue":
                ai_result.get(
                    "Primary Issue",
                    ""
                ),

            "AI Recommended Action":
                ai_result.get(
                    "Recommended Action",
                    ""
                ),

            "AI Priority":
                ai_result.get(
                    "Priority",
                    ""
                ),

            "AI Recommended Budget":
                final_budget,

            "AI Reasoning":
                ai_result.get(
                    "Reasoning",
                    ""
                )
        })


    except Exception as error:

        print(
            f"   ⚠️ Final failure: {error}"
        )

        results.append({

            "Campaign":
                row["Campaign"],

            "Platform":
                row["Platform"],

            "Spend":
                round(row["Spend"], 2),

            "Revenue":
                round(row["Revenue"], 2),

            "Purchases":
                row["Purchases"],

            "CPA (₹)":
                round(row["CPA (₹)"], 2),

            "ROAS (x)":
                round(row["ROAS (x)"], 2),

            "AI Performance Status":
                "Analysis Failed",

            "AI Primary Issue":
                "Temporary Gemini API failure",

            "AI Recommended Action":
                "Review campaign manually",

            "AI Priority":
                "Medium",

            "AI Recommended Budget":
                round(row["Spend"], 2),

            "AI Reasoning":
                str(error)
        })


    # Delay between campaigns
    time.sleep(3)


# ------------------------------------------------------------
# SAVE FINAL OUTPUT
# ------------------------------------------------------------

result_df = pd.DataFrame(results)

result_df.to_excel(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

successful = (
    result_df["AI Performance Status"]
    != "Analysis Failed"
).sum()

failed = total - successful


print("\n======================================")
print("GEMINI AI PIPELINE COMPLETE")
print("======================================")

print(
    f"Raw records: {len(df)}"
)

print(
    f"Unique campaigns: {total}"
)

print(
    f"Successful AI analyses: {successful}"
)

print(
    f"Failed analyses: {failed}"
)

print(
    f"\nFinal output saved as:"
    f"\n{OUTPUT_FILE}"
)

print("\nAI Status Summary:")

print(
    result_df[
        "AI Performance Status"
    ].value_counts()
)

print("\nFinal recommendations:")

print(
    result_df[
        [
            "Campaign",
            "Platform",
            "ROAS (x)",
            "CPA (₹)",
            "AI Performance Status",
            "AI Priority",
            "AI Recommended Budget"
        ]
    ].to_string(index=False)
)