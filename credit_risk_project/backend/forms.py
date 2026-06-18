from django import forms


class CreditRiskForm(forms.Form):


    gender = forms.ChoiceField(
        choices=[
            ("M", "Male"),
            ("F", "Female"),
        ]
    )

    income_type = forms.ChoiceField(
        choices=[
            ("Working", "Working"),
            ("Commercial associate", "Commercial Associate"),
            ("Pensioner", "Pensioner"),
            ("State servant", "State Servant"),
            ("Student", "Student"),
        ]
    )

    education = forms.ChoiceField(
        choices=[
            ("Higher education", "Higher Education"),
            ("Incomplete higher", "Incomplete Higher"),
            ("Secondary / secondary special", "Secondary / Secondary Special"),
            ("Lower secondary", "Lower Secondary"),
        ]
    )

    occupation = forms.ChoiceField(
        choices=[
            ("Cleaning staff", "Cleaning Staff"),
            ("Cooking staff", "Cooking Staff"),
            ("Core staff", "Core Staff"),
            ("Drivers", "Drivers"),
            ("HR staff", "HR Staff"),
            ("High skill tech staff", "High Skill Tech Staff"),
            ("IT staff", "IT Staff"),
            ("Laborers", "Laborers"),
            ("Low-skill Laborers", "Low-skill Laborers"),
            ("Managers", "Managers"),
            ("Medicine staff", "Medicine Staff"),
            ("Private service staff", "Private Service Staff"),
            ("Realty agents", "Realty Agents"),
            ("Sales staff", "Sales Staff"),
            ("Secretaries", "Secretaries"),
            ("Security staff", "Security Staff"),
            ("Unknown", "Unknown"),
            ("Waiters/barmen staff", "Waiters/Barmen Staff"),
        ]
    )

    housing_type = forms.ChoiceField(
        choices=[
            ("House / apartment", "House / Apartment"),
            ("Municipal apartment", "Municipal Apartment"),
            ("Office apartment", "Office Apartment"),
            ("Rented apartment", "Rented Apartment"),
            ("With parents", "With Parents"),
        ]
    )

    family_status = forms.ChoiceField(
        choices=[
            ("Married", "Married"),
            ("Single / not married", "Single / Not Married"),
            ("Separated", "Separated"),
            ("Widow", "Widow"),
        ]
    )

    annual_income = forms.FloatField(min_value=0)

    age = forms.IntegerField(
        min_value=18,
        max_value=100
    )

    family_members = forms.IntegerField(
        min_value=1
    )

    children = forms.IntegerField(
        min_value=0
    )

    employment_years = forms.IntegerField(
        min_value=0
    )

    # ==========================
    # Credit Behavioral Analytics
    # ==========================

    history_length = forms.IntegerField(
        min_value=1
    )

    cnt_c = forms.IntegerField(
        min_value=0,
        required=False
    )

    cnt_x = forms.IntegerField(
        min_value=0,
        required=False
    )

    cnt_0 = forms.IntegerField(
        min_value=0,
        required=False
    )

    cnt_1 = forms.IntegerField(
        min_value=0,
        required=False
    )

    cnt_2 = forms.IntegerField(
        min_value=0,
        required=False
    )

    cnt_3 = forms.IntegerField(
        min_value=0,
        required=False
    )

    cnt_4 = forms.IntegerField(
        min_value=0,
        required=False
    )

    cnt_5 = forms.IntegerField(
        min_value=0,
        required=False
    )

    # ==========================
    # Validation
    # ==========================

    def clean(self):

        cleaned = super().clean()

        for col in [
            "cnt_c",
            "cnt_x",
            "cnt_0",
            "cnt_1",
            "cnt_2",
            "cnt_3",
            "cnt_4",
            "cnt_5"
        ]:
            cleaned[col] = cleaned.get(col) or 0

        history = cleaned.get("history_length") or 0

        total_months = (
            cleaned["cnt_c"]
            + cleaned["cnt_x"]
            + cleaned["cnt_0"]
            + cleaned["cnt_1"]
            + cleaned["cnt_2"]
            + cleaned["cnt_3"]
            + cleaned["cnt_4"]
            + cleaned["cnt_5"]
        )

        if history and total_months > history:
            raise forms.ValidationError(
                f"Total repayment months ({total_months}) cannot exceed history length ({history})."
            )

        return cleaned