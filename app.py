
import pandas as pd
import streamlit as st

# Load the Excel file
df = pd.read_excel("ค่าอุปกรณ์.xlsx", engine="openpyxl")

# Set the equipment name column as index for easier access
df.set_index("equipment", inplace=True)

# Create a dictionary to store quantities
quantities = {}

st.title("Healthcare Equipment Cost Calculator")

st.markdown("Enter the quantity for each equipment used in the operation:")

# Input quantities for each equipment
for equipment in df.index:
    if equipment == "Angiogram":
        quantities[equipment] = 1
        st.number_input(equipment, value=1, step=1, disabled=True)
    elif equipment == "Contrast media":
        quantities[equipment] = st.number_input(equipment, min_value=0, step=1, value=4)
    else:
        quantities[equipment] = st.number_input(equipment, min_value=0, step=1, value=0)

# Prepare results
results = []
schemes = ["Universal healthcare", "UCEP", "Social Security", "Civil Servant", "Self pay"]

for scheme in schemes:
    total_cost = 0
    total_reimbursement = 0
    for equipment, qty in quantities.items():
        cost = df.loc[equipment, "Cost"] * qty
        reimbursement = df.loc[equipment, scheme] * qty
        total_cost += cost
        total_reimbursement += reimbursement
    out_of_pocket = total_cost - total_reimbursement
    results.append({
        "Scheme": scheme,
        "Total Cost (THB)": total_cost,
        "Reimbursement (THB)": total_reimbursement,
        "Out-of-Pocket (THB)": out_of_pocket
    })

# Display results
st.subheader("Cost Summary by Healthcare Scheme")
st.dataframe(pd.DataFrame(results))
