import streamlit as st
import pandas as pd
from pathlib import Path


# ============================================================
# FORESIGHT - AI DEMAND & INVENTORY INTELLIGENCE DASHBOARD
# ============================================================

st.set_page_config(
    page_title="FORESIGHT",
    page_icon="📦",
    layout="wide"
)


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

RISK_FILE = Path("outputs/risk/risk_results.csv")
RECOMMENDATION_FILE = Path(
    "outputs/recommendations/recommendations.csv"
)


# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------

@st.cache_data
def load_data():

    if not RISK_FILE.exists():
        return None

    df = pd.read_csv(RISK_FILE)

    return df


df = load_data()


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.title("FORESIGHT")
st.subheader("AI-Powered Demand & Inventory Intelligence")

st.markdown(
    "Monitor inventory risk, identify priority products, "
    "and generate actionable inventory recommendations."
)


# ------------------------------------------------------------
# Check data
# ------------------------------------------------------------

if df is None:

    st.error(
        "Risk data not found. "
        "Run risk_analysis.py first."
    )

    st.stop()


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

st.sidebar.header("Filters")

# Category filter
if "product_category" in df.columns:

    categories = sorted(
        df["product_category"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_category = st.sidebar.selectbox(
        "Product Category",
        ["All"] + categories
    )

else:

    selected_category = "All"


# Product filter
if "product_description" in df.columns:

    products = sorted(
        df["product_description"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_product = st.sidebar.selectbox(
        "Product",
        ["All"] + products
    )

else:

    selected_product = "All"


# ------------------------------------------------------------
# Apply filters
# ------------------------------------------------------------

filtered_df = df.copy()

if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["product_category"]
        == selected_category
    ]


if selected_product != "All":

    filtered_df = filtered_df[
        filtered_df["product_description"]
        == selected_product
    ]


# ------------------------------------------------------------
# KPI calculations
# ------------------------------------------------------------

total_products = filtered_df["product_no"].nunique()

total_units = filtered_df["qty_on_hand"].sum()

inventory_value = filtered_df[
    "inventory_value"
].sum()

risk_products = filtered_df[
    filtered_df["risk_score"] > 0
]["product_no"].nunique()


# ------------------------------------------------------------
# KPI cards
# ------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Products",
        f"{total_products:,}"
    )


with col2:

    st.metric(
        "Units on Hand",
        f"{total_units:,.0f}"
    )


with col3:

    st.metric(
        "Inventory Value",
        f"₹{inventory_value:,.0f}"
    )


with col4:

    st.metric(
        "Products at Risk",
        f"{risk_products:,}"
    )


st.divider()


# ------------------------------------------------------------
# Risk distribution
# ------------------------------------------------------------

st.header("Inventory Risk Overview")

col1, col2 = st.columns(2)


with col1:

    st.subheader("Decision Distribution")

    decision_counts = (
        filtered_df["decision"]
        .value_counts()
    )

    st.bar_chart(decision_counts)


with col2:

    st.subheader("Risk Distribution")

    risk_counts = pd.DataFrame({
        "High Stockout Risk": [
            (
                filtered_df["stockout_risk"]
                == "High"
            ).sum()
        ],

        "High Overstock Risk": [
            (
                filtered_df["overstock_risk"]
                == "High"
            ).sum()
        ]
    })

    st.bar_chart(risk_counts.T)


# ------------------------------------------------------------
# Priority recommendations
# ------------------------------------------------------------

st.header("Priority Actions")

priority_df = filtered_df.copy()

priority_df = priority_df.sort_values(
    "rupee_value_at_stake",
    ascending=False
)


display_columns = [
    "product_no",
    "product_description",
    "product_category",
    "qty_on_hand",
    "stockout_risk",
    "overstock_risk",
    "decision",
    "rupee_value_at_stake"
]


display_columns = [
    column
    for column in display_columns
    if column in priority_df.columns
]


st.dataframe(
    priority_df[display_columns].head(20),
    use_container_width=True,
    hide_index=True
)


# ------------------------------------------------------------
# Recommendations
# ------------------------------------------------------------

st.header("Recommended Actions")

recommendation_file = Path(
    "outputs/recommendations/recommendations.csv"
)


if recommendation_file.exists():

    recommendations = pd.read_csv(
        recommendation_file
    )

    if selected_category != "All":

        recommendations = recommendations[
            recommendations["product_category"]
            == selected_category
        ]

    if selected_product != "All":

        recommendations = recommendations[
            recommendations["product_description"]
            == selected_product
        ]

    recommendation_columns = [
        "product_no",
        "product_description",
        "decision",
        "recommendation",
        "rupee_value_at_stake"
    ]

    recommendation_columns = [
        column
        for column in recommendation_columns
        if column in recommendations.columns
    ]

    st.dataframe(
        recommendations[
            recommendation_columns
        ].head(20),
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "Recommendation file not found. "
        "Run recommendations.py first."
    )


# ------------------------------------------------------------
# Category analysis
# ------------------------------------------------------------

st.header("Inventory by Category")

if "product_category" in filtered_df.columns:

    category_summary = (
        filtered_df
        .groupby("product_category")
        .agg(
            products=("product_no", "nunique"),
            units=("qty_on_hand", "sum"),
            inventory_value=(
                "inventory_value",
                "sum"
            )
        )
        .sort_values(
            "inventory_value",
            ascending=False
        )
    )

    st.dataframe(
        category_summary,
        use_container_width=True
    )


# ------------------------------------------------------------
# Product detail
# ------------------------------------------------------------

st.header("Product Detail")

if selected_product != "All":

    product_data = filtered_df[
        filtered_df["product_description"]
        == selected_product
    ]

    st.dataframe(
        product_data,
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.divider()

st.caption(
    "FORESIGHT | Demand & Inventory Intelligence Platform"
)