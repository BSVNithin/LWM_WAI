import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LogiOpt AI",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CURRENT_FILE = os.path.join(DATA_DIR, "current_shipments.csv")
HISTORICAL_FILE = os.path.join(DATA_DIR, "historical_shipments.csv")
OPTIMIZED_FILE = os.path.join(DATA_DIR, "optimized_shipments.csv")
OPT_SUMMARY_FILE = os.path.join(DATA_DIR, "optimization_summary.csv")
VEHICLES_FILE = os.path.join(DATA_DIR, "vehicles.csv")
CARRIERS_FILE = os.path.join(DATA_DIR, "carriers.csv")

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    current = pd.read_csv(CURRENT_FILE)
    historical = pd.read_csv(HISTORICAL_FILE)
    optimized = pd.read_csv(OPTIMIZED_FILE)
    optimization_summary = pd.read_csv(OPT_SUMMARY_FILE)
    vehicles = pd.read_csv(VEHICLES_FILE)
    carriers = pd.read_csv(CARRIERS_FILE)

    return (
        current,
        historical,
        optimized,
        optimization_summary,
        vehicles,
        carriers
    )


try:

    (
        current,
        historical,
        optimized,
        optimization_summary,
        vehicles,
        carriers
    ) = load_data()

except Exception as e:

    st.error("Unable to load project data.")
    st.write(e)
    st.stop()


# ============================================================
# DATA PREPARATION
# ============================================================

current["Date"] = pd.to_datetime(
    current["Date"],
    errors="coerce"
)

historical["Date"] = pd.to_datetime(
    historical["Date"],
    errors="coerce"
)

optimized["Date"] = pd.to_datetime(
    optimized["Date"],
    errors="coerce"
)

# Risk score based on operational factors
# Used for dashboard visualization only.
def calculate_risk_score(row):

    score = 0

    # Distance
    if row["Distance_KM"] >= 700:
        score += 25
    elif row["Distance_KM"] >= 500:
        score += 15
    else:
        score += 5

    # Traffic
    traffic = str(row["Traffic"]).lower()

    if traffic == "high":
        score += 25
    elif traffic == "medium":
        score += 15
    else:
        score += 5

    # Weather
    weather = str(row["Weather"]).lower()

    if weather in ["storm", "severe"]:
        score += 25
    elif weather in ["rain", "heavy rain"]:
        score += 15
    else:
        score += 5

    # Priority
    priority = str(row["Priority"]).lower()

    if priority == "critical":
        score += 15
    elif priority == "high":
        score += 10
    else:
        score += 5

    # Delivery window
    if row["Delivery_Window_Hours"] <= 10:
        score += 10
    elif row["Delivery_Window_Hours"] <= 14:
        score += 5

    return min(score, 100)


current["Risk_Score"] = current.apply(
    calculate_risk_score,
    axis=1
)

current["Risk_Level"] = pd.cut(
    current["Risk_Score"],
    bins=[-1, 35, 65, 100],
    labels=[
        "Low Risk",
        "Medium Risk",
        "High Risk"
    ]
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🚚 LogiOpt AI")

st.sidebar.markdown(
    "**AI-Powered Delivery Risk & Logistics Cost Optimization**"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Dashboard",
    [
        "Executive Overview",
        "Shipment Intelligence",
        "Fleet Optimization",
        "Carrier Analysis",
        "Shipment Explorer"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### Project")

st.sidebar.write(
    """
    **Company:** Delhivery Limited

    **Course:** Logistics and Warehousing Management

    **Project:** LogiOpt AI
    """
)

st.sidebar.divider()

st.sidebar.caption(
    "Academic prototype using simulated logistics data."
)

# ============================================================
# HEADER
# ============================================================

st.title("🚚 LogiOpt AI")

st.markdown(
    "### AI-Powered Delivery Risk & Logistics Cost Optimization"
)

st.caption(
    "Logistics decision-support dashboard for shipment risk, "
    "fleet utilization, carrier performance and transportation cost."
)

st.divider()


# ============================================================
# 1. EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.header("📊 Executive Overview")

    # --------------------------------------------------------
    # KPI VALUES
    # --------------------------------------------------------

    total_shipments = int(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Total Shipments",
            "Value"
        ].iloc[0]
    )

    current_cost = float(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Current Cost",
            "Value"
        ].iloc[0]
    )

    optimized_cost = float(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Optimized Cost",
            "Value"
        ].iloc[0]
    )

    total_saving = float(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Total Saving",
            "Value"
        ].iloc[0]
    )

    saving_percentage = float(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Saving Percentage",
            "Value"
        ].iloc[0]
    )

    high_risk = int(
        (current["Risk_Level"] == "High Risk").sum()
    )

    avg_utilization = optimized[
        "Vehicle_Utilization_%"
    ].mean()

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Shipments",
        f"{total_shipments}"
    )

    col2.metric(
        "High-Risk Shipments",
        f"{high_risk}"
    )

    col3.metric(
        "Current Cost",
        f"${current_cost:,.2f}"
    )

    col4.metric(
        "Optimized Cost",
        f"${optimized_cost:,.2f}"
    )

    col5.metric(
        "Cost Saving",
        f"${total_saving:,.2f}",
        f"{saving_percentage:.2f}%"
    )

    st.divider()

    # --------------------------------------------------------
    # RISK DISTRIBUTION + VEHICLE UTILIZATION
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Shipment Risk Distribution")

        risk_data = (
            current["Risk_Level"]
            .value_counts()
            .reset_index()
        )

        risk_data.columns = [
            "Risk Level",
            "Shipments"
        ]

        fig = px.pie(
            risk_data,
            names="Risk Level",
            values="Shipments",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.subheader("Vehicle Utilization")

        utilization = (
            optimized
            .groupby("Optimized_Vehicle")
            ["Vehicle_Utilization_%"]
            .max()
            .reset_index()
        )

        utilization.columns = [
            "Vehicle",
            "Utilization"
        ]

        fig = px.bar(
            utilization,
            x="Vehicle",
            y="Utilization",
            text="Utilization",
            labels={
                "Utilization": "Utilization (%)"
            }
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%"
        )

        fig.update_yaxes(
            range=[0, 100]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # COST COMPARISON
    # --------------------------------------------------------

    st.subheader("Transportation Cost Optimization")

    cost_data = pd.DataFrame({
        "Scenario": [
            "Current Cost",
            "Optimized Cost"
        ],
        "Cost": [
            current_cost,
            optimized_cost
        ]
    })

    fig = px.bar(
        cost_data,
        x="Scenario",
        y="Cost",
        text="Cost",
        labels={
            "Cost": "Transportation Cost ($)"
        }
    )

    fig.update_traces(
        texttemplate="$%{text:,.2f}"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.success(
        f"Vehicle optimization reduced simulated transportation "
        f"cost by ${total_saving:,.2f}, representing a "
        f"{saving_percentage:.2f}% reduction."
    )

    # --------------------------------------------------------
    # TOP RISK SHIPMENTS
    # --------------------------------------------------------

    st.subheader("Top Risk Shipments")

    risk_display = current.sort_values(
        "Risk_Score",
        ascending=False
    ).head(5)

    st.dataframe(
        risk_display[
            [
                "Shipment_ID",
                "Origin",
                "Destination",
                "Distance_KM",
                "Traffic",
                "Weather",
                "Priority",
                "Risk_Score",
                "Risk_Level"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 2. SHIPMENT INTELLIGENCE
# ============================================================

elif page == "Shipment Intelligence":

    st.header("🔍 Shipment Intelligence")

    st.markdown(
        "Identify shipments that may require early operational intervention."
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        risk_filter = st.multiselect(
            "Risk Level",
            [
                "Low Risk",
                "Medium Risk",
                "High Risk"
            ],
            default=[
                "Low Risk",
                "Medium Risk",
                "High Risk"
            ]
        )

    with col2:

        traffic_filter = st.multiselect(
            "Traffic",
            sorted(
                current["Traffic"]
                .dropna()
                .unique()
            ),
            default=sorted(
                current["Traffic"]
                .dropna()
                .unique()
            )
        )

    with col3:

        weather_filter = st.multiselect(
            "Weather",
            sorted(
                current["Weather"]
                .dropna()
                .unique()
            ),
            default=sorted(
                current["Weather"]
                .dropna()
                .unique()
            )
        )

    filtered = current[
        current["Risk_Level"]
        .astype(str)
        .isin(risk_filter)
    ]

    filtered = filtered[
        filtered["Traffic"]
        .isin(traffic_filter)
    ]

    filtered = filtered[
        filtered["Weather"]
        .isin(weather_filter)
    ]

    st.divider()

    # --------------------------------------------------------
    # RISK KPIs
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Filtered Shipments",
        len(filtered)
    )

    col2.metric(
        "Average Risk Score",
        f"{filtered['Risk_Score'].mean():.1f}"
        if len(filtered) > 0
        else "0"
    )

    col3.metric(
        "High-Risk Shipments",
        int(
            (filtered["Risk_Level"] == "High Risk")
            .sum()
        )
    )

    # --------------------------------------------------------
    # RISK BY TRAFFIC
    # --------------------------------------------------------

    st.subheader("Risk Score by Traffic Condition")

    traffic_risk = (
        filtered
        .groupby("Traffic")["Risk_Score"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        traffic_risk,
        x="Traffic",
        y="Risk_Score",
        text="Risk_Score",
        labels={
            "Risk_Score": "Average Risk Score"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.1f}"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # RISK BY WEATHER
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Risk by Weather")

        weather_risk = (
            filtered
            .groupby("Weather")["Risk_Score"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            weather_risk,
            x="Weather",
            y="Risk_Score",
            text="Risk_Score",
            labels={
                "Risk_Score":
                    "Average Risk Score"
            }
        )

        fig.update_traces(
            texttemplate="%{text:.1f}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.subheader("Risk by Priority")

        priority_risk = (
            filtered
            .groupby("Priority")["Risk_Score"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            priority_risk,
            x="Priority",
            y="Risk_Score",
            text="Risk_Score",
            labels={
                "Risk_Score":
                    "Average Risk Score"
            }
        )

        fig.update_traces(
            texttemplate="%{text:.1f}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # HIGH RISK TABLE
    # --------------------------------------------------------

    st.subheader("🚨 Shipments Requiring Attention")

    high_risk = filtered.sort_values(
        "Risk_Score",
        ascending=False
    )

    st.dataframe(
        high_risk[
            [
                "Shipment_ID",
                "Origin",
                "Destination",
                "Distance_KM",
                "Load_KG",
                "Traffic",
                "Weather",
                "Priority",
                "Delivery_Window_Hours",
                "Risk_Score",
                "Risk_Level"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 3. FLEET OPTIMIZATION
# ============================================================

elif page == "Fleet Optimization":

    st.header("🚛 Fleet Optimization")

    st.markdown(
        "OR-Tools based vehicle allocation and transportation-cost analysis."
    )

    # --------------------------------------------------------
    # COST VALUES
    # --------------------------------------------------------

    current_cost = float(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Current Cost",
            "Value"
        ].iloc[0]
    )

    optimized_cost = float(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Optimized Cost",
            "Value"
        ].iloc[0]
    )

    total_saving = float(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Total Saving",
            "Value"
        ].iloc[0]
    )

    saving_percentage = float(
        optimization_summary.loc[
            optimization_summary["Metric"] == "Saving Percentage",
            "Value"
        ].iloc[0]
    )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Cost",
        f"${current_cost:,.2f}"
    )

    col2.metric(
        "Optimized Cost",
        f"${optimized_cost:,.2f}"
    )

    col3.metric(
        "Cost Saving",
        f"${total_saving:,.2f}"
    )

    col4.metric(
        "Saving %",
        f"{saving_percentage:.2f}%"
    )

    st.divider()

    # --------------------------------------------------------
    # VEHICLE ALLOCATION
    # --------------------------------------------------------

    st.subheader("Vehicle Allocation")

    allocation = (
        optimized
        .groupby("Optimized_Vehicle")
        ["Shipment_ID"]
        .count()
        .reset_index()
    )

    allocation.columns = [
        "Vehicle",
        "Shipments"
    ]

    fig = px.bar(
        allocation,
        x="Vehicle",
        y="Shipments",
        text="Shipments",
        labels={
            "Shipments":
                "Number of Shipments"
        }
    )

    fig.update_traces(
        texttemplate="%{text}"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # UTILIZATION
    # --------------------------------------------------------

    st.subheader("Vehicle Utilization")

    vehicle_utilization = (
        optimized
        .groupby("Optimized_Vehicle")
        ["Vehicle_Utilization_%"]
        .max()
        .reset_index()
    )

    vehicle_utilization.columns = [
        "Vehicle",
        "Utilization"
    ]

    fig = px.bar(
        vehicle_utilization,
        x="Vehicle",
        y="Utilization",
        text="Utilization",
        labels={
            "Utilization":
                "Vehicle Utilization (%)"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%"
    )

    fig.update_yaxes(
        range=[0, 100]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # VEHICLE CAPACITY INFORMATION
    # --------------------------------------------------------

    st.subheader("Vehicle Capacity & Cost Structure")

    vehicle_display = vehicles.copy()

    vehicle_display.columns = [
        "Vehicle ID",
        "Capacity (KG)",
        "Fixed Cost",
        "Cost per KM"
    ]

    st.dataframe(
        vehicle_display,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # OPTIMIZATION MESSAGE
    # --------------------------------------------------------

    st.success(
        f"Optimization reduced transportation cost from "
        f"${current_cost:,.2f} to ${optimized_cost:,.2f}, "
        f"saving ${total_saving:,.2f}."
    )


# ============================================================
# 4. CARRIER ANALYSIS
# ============================================================

elif page == "Carrier Analysis":

    st.header("🚚 Carrier Performance Analysis")

    st.markdown(
        "Comparison of carrier reliability and transportation cost."
    )

    # --------------------------------------------------------
    # CARRIER TABLE
    # --------------------------------------------------------

    carrier_display = carriers.copy()

    carrier_display["Historical_Delay_Rate"] *= 100
    carrier_display["On_Time_Rate"] *= 100

    carrier_display = carrier_display.rename(
        columns={
            "Carrier": "Carrier",
            "Historical_Delay_Rate":
                "Historical Delay Rate (%)",
            "On_Time_Rate":
                "On-Time Rate (%)",
            "Cost_Per_KM":
                "Cost per KM"
        }
    )

    st.dataframe(
        carrier_display,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --------------------------------------------------------
    # DELAY RATE
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Historical Delay Rate")

        fig = px.bar(
            carrier_display,
            x="Carrier",
            y="Historical Delay Rate (%)",
            text="Historical Delay Rate (%)"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.subheader("On-Time Delivery Rate")

        fig = px.bar(
            carrier_display,
            x="Carrier",
            y="On-Time Rate (%)",
            text="On-Time Rate (%)"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # COST COMPARISON
    # --------------------------------------------------------

    st.subheader("Carrier Cost per KM")

    fig = px.bar(
        carrier_display,
        x="Carrier",
        y="Cost per KM",
        text="Cost per KM"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # BEST CARRIER
    # --------------------------------------------------------

    best_on_time = carrier_display.loc[
        carrier_display["On-Time Rate (%)"].idxmax()
    ]

    lowest_cost = carrier_display.loc[
        carrier_display["Cost per KM"].idxmin()
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            f"**Highest On-Time Rate:** "
            f"{best_on_time['Carrier']} "
            f"({best_on_time['On-Time Rate (%)']:.1f}%)"
        )

    with col2:

        st.info(
            f"**Lowest Cost per KM:** "
            f"{lowest_cost['Carrier']} "
            f"({lowest_cost['Cost per KM']:.2f})"
        )


# ============================================================
# 5. SHIPMENT EXPLORER
# ============================================================

elif page == "Shipment Explorer":

    st.header("📦 Shipment Explorer")

    st.markdown(
        "Explore current shipments and their operational characteristics."
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        origin = st.multiselect(
            "Origin",
            sorted(
                current["Origin"]
                .dropna()
                .unique()
            ),
            default=sorted(
                current["Origin"]
                .dropna()
                .unique()
            )
        )

    with col2:

        destination = st.multiselect(
            "Destination",
            sorted(
                current["Destination"]
                .dropna()
                .unique()
            ),
            default=sorted(
                current["Destination"]
                .dropna()
                .unique()
            )
        )

    with col3:

        priority = st.multiselect(
            "Priority",
            sorted(
                current["Priority"]
                .dropna()
                .unique()
            ),
            default=sorted(
                current["Priority"]
                .dropna()
                .unique()
            )
        )

    # --------------------------------------------------------
    # APPLY FILTER
    # --------------------------------------------------------

    explorer = current[
        current["Origin"].isin(origin)
    ]

    explorer = explorer[
        explorer["Destination"].isin(destination)
    ]

    explorer = explorer[
        explorer["Priority"].isin(priority)
    ]

    st.divider()

    st.metric(
        "Matching Shipments",
        len(explorer)
    )

    # --------------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------------

    columns = [
        "Shipment_ID",
        "Date",
        "Origin",
        "Destination",
        "Distance_KM",
        "Carrier",
        "Vehicle_ID",
        "Load_KG",
        "Traffic",
        "Weather",
        "Priority",
        "Delivery_Window_Hours",
        "Risk_Score",
        "Risk_Level"
    ]

    columns = [
        c for c in columns
        if c in explorer.columns
    ]

    st.dataframe(
        explorer[columns],
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    csv = explorer.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Shipments",
        data=csv,
        file_name="logiopt_filtered_shipments.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "LogiOpt AI | Logistics and Warehousing Management | "
    "Academic Project Prototype"
)