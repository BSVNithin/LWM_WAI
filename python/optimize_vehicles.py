import pandas as pd
from ortools.linear_solver import pywraplp
import os

# ============================================================
# LOGIOPT AI - VEHICLE ALLOCATION OPTIMIZER
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SHIPMENTS_FILE = os.path.join(
    BASE_DIR, "data", "current_shipments.csv"
)

VEHICLES_FILE = os.path.join(
    BASE_DIR, "data", "vehicles.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR, "data", "optimized_shipments.csv"
)


# ============================================================
# 1. LOAD DATA
# ============================================================

shipments = pd.read_csv(SHIPMENTS_FILE)
vehicles = pd.read_csv(VEHICLES_FILE)

print("=" * 60)
print("LOGIOPT AI - VEHICLE ALLOCATION OPTIMIZATION")
print("=" * 60)

print("\nShipments loaded:", len(shipments))
print("Vehicles available:", len(vehicles))


# ============================================================
# 2. CREATE OPTIMIZATION MODEL
# ============================================================

solver = pywraplp.Solver.CreateSolver("SCIP")

if not solver:
    raise RuntimeError("OR-Tools solver could not be created.")


# Decision variables:
# x[i,j] = 1 if shipment i is assigned to vehicle j

x = {}

for i in range(len(shipments)):
    for j in range(len(vehicles)):

        shipment_load = shipments.iloc[i]["Load_KG"]
        vehicle_capacity = vehicles.iloc[j]["Capacity_KG"]

        # Only create a variable when vehicle has enough capacity
        if shipment_load <= vehicle_capacity:

            x[i, j] = solver.BoolVar(
                f"x_{i}_{j}"
            )


# ============================================================
# 3. CONSTRAINT
# EACH SHIPMENT MUST HAVE EXACTLY ONE VEHICLE
# ============================================================

for i in range(len(shipments)):

    valid_variables = [
        x[i, j]
        for j in range(len(vehicles))
        if (i, j) in x
    ]

    if not valid_variables:

        shipment_id = shipments.iloc[i]["Shipment_ID"]
        load = shipments.iloc[i]["Load_KG"]

        raise ValueError(
            f"No vehicle can carry shipment {shipment_id} "
            f"with load {load} KG."
        )

    solver.Add(
        sum(valid_variables) == 1
    )


# ============================================================
# 4. OBJECTIVE
# MINIMIZE TOTAL TRANSPORTATION COST
#
# Cost = Fixed Cost + Distance × Cost Per KM
# ============================================================

objective_terms = []

for (i, j), variable in x.items():

    distance = shipments.iloc[i]["Distance_KM"]

    fixed_cost = vehicles.iloc[j]["Fixed_Cost"]

    cost_per_km = vehicles.iloc[j]["Cost_Per_KM"]

    transportation_cost = (
        fixed_cost +
        distance * cost_per_km
    )

    objective_terms.append(
        transportation_cost * variable
    )


solver.Minimize(
    sum(objective_terms)
)


# ============================================================
# 5. SOLVE
# ============================================================

print("\nSolving optimization model...")

status = solver.Solve()


if status != pywraplp.Solver.OPTIMAL:
    raise RuntimeError(
        "Optimal solution could not be found."
    )


print("Optimization completed successfully!")


# ============================================================
# 6. CURRENT ALLOCATION COST
# ============================================================

current_costs = []

for _, shipment in shipments.iterrows():

    vehicle_id = shipment["Vehicle_ID"]

    vehicle_match = vehicles[
        vehicles["Vehicle_ID"] == vehicle_id
    ]

    if vehicle_match.empty:

        current_costs.append(None)

    else:

        vehicle = vehicle_match.iloc[0]

        cost = (
            vehicle["Fixed_Cost"]
            +
            shipment["Distance_KM"]
            * vehicle["Cost_Per_KM"]
        )

        current_costs.append(cost)


shipments["Current_Cost"] = current_costs


# ============================================================
# 7. EXTRACT OPTIMIZED SOLUTION
# ============================================================

optimized_vehicle_ids = []
optimized_costs = []
vehicle_utilization = []

for i in range(len(shipments)):

    selected_vehicle = None
    selected_cost = None
    selected_capacity = None

    for j in range(len(vehicles)):

        if (i, j) in x and x[i, j].solution_value() > 0.5:

            vehicle = vehicles.iloc[j]

            selected_vehicle = vehicle["Vehicle_ID"]

            selected_capacity = vehicle["Capacity_KG"]

            selected_cost = (
                vehicle["Fixed_Cost"]
                +
                shipments.iloc[i]["Distance_KM"]
                * vehicle["Cost_Per_KM"]
            )

            break

    optimized_vehicle_ids.append(
        selected_vehicle
    )

    optimized_costs.append(
        selected_cost
    )

    utilization = (
        shipments.iloc[i]["Load_KG"]
        / selected_capacity
    ) * 100

    vehicle_utilization.append(
        round(utilization, 2)
    )


shipments["Optimized_Vehicle"] = optimized_vehicle_ids

shipments["Optimized_Cost"] = optimized_costs

shipments["Vehicle_Utilization_%"] = vehicle_utilization


# ============================================================
# 8. CALCULATE SAVINGS
# ============================================================

shipments["Cost_Saving"] = (
    shipments["Current_Cost"]
    -
    shipments["Optimized_Cost"]
)


shipments["Saving_%"] = (
    shipments["Cost_Saving"]
    /
    shipments["Current_Cost"]
    * 100
)


# ============================================================
# 9. SAVE RESULTS
# ============================================================

shipments.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 10. SUMMARY
# ============================================================

total_current_cost = shipments["Current_Cost"].sum()

total_optimized_cost = shipments["Optimized_Cost"].sum()

total_saving = (
    total_current_cost
    -
    total_optimized_cost
)

saving_percentage = (
    total_saving
    /
    total_current_cost
    * 100
)


print("\n" + "=" * 60)
print("OPTIMIZATION RESULTS")
print("=" * 60)

print(
    f"\nCurrent Transportation Cost : "
    f"{total_current_cost:.2f}"
)

print(
    f"Optimized Transportation Cost: "
    f"{total_optimized_cost:.2f}"
)

print(
    f"Total Cost Saving            : "
    f"{total_saving:.2f}"
)

print(
    f"Cost Saving %                : "
    f"{saving_percentage:.2f}%"
)


# ============================================================
# 11. VEHICLE ALLOCATION SUMMARY
# ============================================================

print("\nVehicle Allocation:")

allocation = (
    shipments["Optimized_Vehicle"]
    .value_counts()
    .sort_index()
)

print(allocation)


# ============================================================
# 12. DISPLAY SAMPLE RESULTS
# ============================================================

print("\nSample Optimized Shipments:")

print(
    shipments[
        [
            "Shipment_ID",
            "Load_KG",
            "Distance_KM",
            "Vehicle_ID",
            "Optimized_Vehicle",
            "Current_Cost",
            "Optimized_Cost",
            "Cost_Saving"
        ]
    ].head(10).to_string(index=False)
)


print("\n" + "=" * 60)
print("RESULT FILE SAVED")
print("=" * 60)

print(OUTPUT_FILE)