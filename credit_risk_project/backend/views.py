from django.shortcuts import render
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import shap
from .forms import CreditRiskForm


# =====================================================
# Load model once when Django starts
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "ml" / "credit_risk_model.pkl"
FEATURE_PATH = BASE_DIR / "ml" / "feature_columns.pkl"

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURE_PATH)
explainer = shap.TreeExplainer(model)

# =====================================================
# Home Page
# =====================================================

def home(request):
    form = CreditRiskForm()

    return render(
        request,
        "index.html",
        {
            "form": form
        }
    )


# =====================================================
# Prediction Page
# =====================================================

def predict(request):

    if request.method != "POST":
        return home(request)

    form = CreditRiskForm(request.POST)

    if not form.is_valid():

        return render(
            request,
            "index.html",
            {
                "form": form
            }
        )

    data = form.cleaned_data

    # =================================================
    # Raw Inputs
    # =================================================

    gender = data["gender"]
    income_type = data["income_type"]
    education = data["education"]
    occupation = data["occupation"]
    housing_type = data["housing_type"]
    family_status = data["family_status"]

    annual_income = data["annual_income"]
    age = data["age"]
    family_members = data["family_members"]
    children = data["children"]
    employment_years = data["employment_years"]

    history_length = data["history_length"]

    cnt_c = data["cnt_c"]
    cnt_x = data["cnt_x"]
    cnt_0 = data["cnt_0"]
    cnt_1 = data["cnt_1"]
    cnt_2 = data["cnt_2"]
    cnt_3 = data["cnt_3"]
    cnt_4 = data["cnt_4"]
    cnt_5 = data["cnt_5"]

    # =================================================
    # Engineered Features
    # =================================================

    has_children = int(children > 0)

    income_per_person = annual_income / max(family_members, 1)

    log_income = np.log1p(annual_income)

    is_pensioner = int(income_type == "Pensioner")

    has_ever_been_late = int(
        cnt_1 + cnt_2 + cnt_3 + cnt_4 + cnt_5 > 0
    )

    if cnt_5 > 0:
        max_status_past = 5
    elif cnt_4 > 0:
        max_status_past = 4
    elif cnt_3 > 0:
        max_status_past = 3
    elif cnt_2 > 0:
        max_status_past = 2
    elif cnt_1 > 0:
        max_status_past = 1
    else:
        max_status_past = 0

    # =================================================
    # Build Feature Dictionary
    # =================================================

    row = {}

    for col in feature_columns:
        row[col] = 0

    # =================================================
    # Numerical Features
    # =================================================

    numerical_features = {
        "HISTORY_LENGTH": history_length,
        "CNT_C": cnt_c,
        "CNT_X": cnt_x,
        "CNT_0": cnt_0,
        "CNT_1": cnt_1,
        "CNT_2": cnt_2,
        "CNT_3": cnt_3,
        "CNT_4": cnt_4,
        "CNT_5": cnt_5,
        "MAX_STATUS_PAST": max_status_past,
        "HAS_EVER_BEEN_LATE": has_ever_been_late,
        "CNT_CHILDREN": children,
        "AMT_INCOME_TOTAL": annual_income,
        "CNT_FAM_MEMBERS": family_members,
        "AGE": age,
        "EMPLOYMENT_YEARS": employment_years,
        "IS_PENSIONER": is_pensioner,
        "INCOME_PER_PERSON": income_per_person,
        "LOG_INCOME": log_income,
        "HAS_CHILDREN": has_children
    }

    for col, value in numerical_features.items():
        if col in row:
            row[col] = value

    # =================================================
    # One Hot Encoding
    # =================================================

    gender_col = f"CODE_GENDER_{gender}"

    if gender_col in row:
        row[gender_col] = 1

    income_col = f"NAME_INCOME_TYPE_{income_type}"

    if income_col in row:
        row[income_col] = 1

    education_col = f"NAME_EDUCATION_TYPE_{education}"

    if education_col in row:
        row[education_col] = 1

    occupation_col = f"OCCUPATION_TYPE_{occupation}"

    if occupation_col in row:
        row[occupation_col] = 1

    housing_col = f"NAME_HOUSING_TYPE_{housing_type}"

    if housing_col in row:
        row[housing_col] = 1

    family_col = f"NAME_FAMILY_STATUS_{family_status}"

    if family_col in row:
        row[family_col] = 1

    # =================================================
    # Additional Binary Features
    # =================================================

    # Default assumptions

    if "FLAG_OWN_CAR_Y" in row:
        row["FLAG_OWN_CAR_Y"] = 0

    if "FLAG_OWN_REALTY_Y" in row:
        row["FLAG_OWN_REALTY_Y"] = 0

    # =================================================
    # Prediction DataFrame
    # =================================================

    X = pd.DataFrame([row])

    X = X.reindex(
        columns=feature_columns,
        fill_value=0
    )

    #shap Part Explanable AI


    shap_values = explainer.shap_values(X)
    if isinstance(shap_values, list):
        sample_shap = shap_values[1][0]
    else:
        sample_shap = shap_values[0]


    shap_df = pd.DataFrame({
        "feature": X.columns,
        "impact": sample_shap
    })

    shap_df["abs_impact"] = shap_df["impact"].abs()

    shap_df = shap_df.sort_values(
        "abs_impact",
        ascending=False
    )

    top_features = shap_df.head(5)
    print(top_features)
    # ==============================================

    feature_names = {
        "CNT_1": "Late Payments",
        "CNT_2": "2-Month Delinquencies",
        "CNT_3": "3-Month Delinquencies",
        "CNT_4": "Severe Delinquencies",
        "CNT_5": "Critical Delinquencies",
        "CNT_C": "Closed Accounts",
        "CNT_0": "On-Time Payments",
        "LOG_INCOME": "Income Level",
        "INCOME_PER_PERSON": "Income Per Family Member",
        "MAX_STATUS_PAST": "Maximum Delinquency",
        "HAS_EVER_BEEN_LATE": "Past Late Payment History",
        "HISTORY_LENGTH": "Credit History Length",
        "EMPLOYMENT_YEARS": "Employment Stability",
        "AGE": "Customer Age"
    }

    shap_explanations = []

    for _, row in top_features.iterrows():

        shap_explanations.append({
            "feature": feature_names.get(row["feature"], row["feature"]),
            "impact": round(float(row["impact"]), 4),
            "direction": (
                "risk"
                if row["impact"] > 0
                else "protective"
            )
        })
    

    # =================================================
    # Prediction
    # =================================================

    probability_default = model.predict_proba(X)[0][1]

    print("=" * 50)
    print("PD:", probability_default)
    print("=" * 50)

    credit_score = int(
        round(
            300 + (1-probability_default) * 600
        )
    )

    credit_score = max(
        300,
        min(900, credit_score)
    )

    # =================================================
    # Risk Band
    # =================================================

    if probability_default < 0.10:
        risk_band = "LOW RISK"
        recommendation = "APPROVE"

    elif probability_default < 0.30:
        risk_band = "MEDIUM RISK"
        recommendation = "MANUAL REVIEW"

    elif probability_default < 0.60:
        risk_band = "HIGH RISK"
        recommendation = "MANUAL REVIEW"

    else:
        risk_band = "VERY HIGH RISK"
        recommendation = "REJECT"

    result = {
        "credit_score": credit_score,
        "default_prob": round(
            probability_default * 100,
            2
        ),
        "risk_band": risk_band,
        "recommendation": recommendation
    }

    explanations = []

    # Positive Factors

    if cnt_0 >= 15:
        explanations.append({
            "type": "positive",
            "text": f"Strong repayment history with {cnt_0} on-time payments."
        })

    if annual_income >= 500000:
        explanations.append({
            "type": "positive",
            "text": f"High annual income of ₹{annual_income:,.0f}."
        })

    if employment_years >= 5:
        explanations.append({
            "type": "positive",
            "text": f"Stable employment history ({employment_years} years)."
        })

    if history_length >= 24:
        explanations.append({
            "type": "positive",
            "text": f"Long credit history ({history_length} months)."
        })

    # Negative Factors

    if cnt_1 > 0:
        explanations.append({
            "type": "negative",
            "text": f"{cnt_1} month(s) with late payments detected."
        })

    if cnt_2 > 0:
        explanations.append({
            "type": "negative",
            "text": f"{cnt_2} occurrence(s) of 2-month delinquency."
        })

    if cnt_3 > 0:
        explanations.append({
            "type": "negative",
            "text": f"{cnt_3} occurrence(s) of 3-month delinquency."
        })

    if cnt_4 > 0:
        explanations.append({
            "type": "negative",
            "text": f"{cnt_4} occurrence(s) of severe delinquency."
        })

    if cnt_5 > 0:
        explanations.append({
            "type": "negative",
            "text": f"{cnt_5} occurrence(s) of critical delinquency."
        })

    if income_per_person < 50000:
        explanations.append({
            "type": "negative",
            "text": f"Low income per family member (₹{income_per_person:,.0f})."
        })

    return render(
        request,
        "index.html",
        {
            "form": form,
            "result": result,
            "explanations": explanations,
            "shap_explanations": shap_explanations
        }
    )