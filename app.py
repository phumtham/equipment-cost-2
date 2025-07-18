
import streamlit as st
import pandas as pd

# Load the Excel file
df = pd.read_excel("ค่าอุปกรณ์.xlsx", engine="openpyxl")

# Mapping of scheme names to column names
scheme_columns = {
    "Universal healthcare": "Universal healthcare",
    "UCEP": "UCEP",
    "Social Security": "Social Security",
    "Civil Servant": "Civil Servant",
    "Self pay": "Self pay"
}

# Select a healthcare scheme
selected_scheme = st.selectbox("Select Healthcare Scheme", list(scheme_columns.keys()))

# Initialize a dictionary to store quantities
quantities = {}

# Display input fields for each equipment
st.header("Enter Equipment Quantities")
for index, row in df.iterrows():
    equipment = row["equipment"]
    default_qty = 0
    if equipment == "Angiogram":
        default_qty = 1
    elif equipment == "Contrast media":
        default_qty = 4
    elif equipment in ["femoral sheath", "0.038 Wire"]:
        default_qty = 1
    qty = st.number_input(f"{equipment}", min_value=0, value=default_qty, step=1)
    quantities[equipment] = qty

# Filter out equipment with quantity 0
used_equipment = {eq: qty for eq, qty in quantities.items() if qty > 0}

# Calculate costs
summary = []
for eq, qty in used_equipment.items():
    row = df[df["equipment"] == eq].iloc[0]
    cost = row["Cost"] * qty
    reimbursement = row[scheme_columns[selected_scheme]] * qty
    out_of_pocket = max(0, cost - reimbursement)
    summary.append({
        "Equipment": eq,
        "Quantity": qty,
        "Total Cost (THB)": cost,
        "Reimbursement (THB)": reimbursement,
        "Out-of-Pocket (THB)": out_of_pocket
    })

# Display summary
st.header("Cost Summary")
summary_df = pd.DataFrame(summary)
st.dataframe(summary_df)

# Generate PDF
from fpdf import FPDF

if st.button("Generate PDF Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Healthcare Scheme: {selected_scheme}", ln=True)

    for _, row in summary_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Equipment']} (x{row['Quantity']}): Cost={row['Total Cost (THB)']} THB, Reimbursement={row['Reimbursement (THB)']} THB, Out-of-Pocket={row['Out-of-Pocket (THB)']} THB", ln=True)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    st.download_button("Download PDF", data=pdf_output.getvalue(), file_name="cost_summary.pdf", mime="application/pdf")
