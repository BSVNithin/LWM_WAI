import pandas as pd
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "optimized_shipments.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "optimization_summary.csv"
)

df = pd.read_csv(INPUT_FILE)

total_current = df["Current_Cost"].sum()
total_optimized = df["Optimized_Cost"].sum()
total_saving = df["Cost_Saving"].sum()

saving_percentage = (
    total_saving / total_current
) * 100

vehicle_summary = (
    df.groupby("Optimized_Vehicle")
    .agg(
        Shipments=("Shipment_ID", "count"),
        Total_Load_KG=("Load_KG", "sum"),
        Average_Utilization=("Vehicle_Utilization_%", "mean")
    )
    .reset_index()
)

print("\n==========================================")
print("LOGIOPT AI - OPTIMIZATION SUMMARY")
print("==========================================")

print(f"\nTotal Shipments: {len(df)}")

print(
    f"Current Cost: ₹{total_current:,.2f}"
)

print(
    f"Optimized Cost: ₹{total_optimized:,.2f}"
)

print(
    f"Total Saving: ₹{total_saving:,.2f}"
)

print(
    f"Saving Percentage: {saving_percentage:.2f}%"
)

print("\nVehicle Utilization:")

print(
    vehicle_summary.to_string(index=False)
)

summary = pd.DataFrame({
    "Metric": [
        "Total Shipments",
        "Current Cost",
        "Optimized Cost",
        "Total Saving",
        "Saving Percentage"
    ],
    "Value": [
        len(df),
        total_current,
        total_optimized,
        total_saving,
        saving_percentage
    ]
})

summary.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSummary saved to: {OUTPUT_FILE}"
)