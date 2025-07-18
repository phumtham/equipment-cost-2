
import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# Load the Excel file
df = pd.read_excel("ค่าอุปกรณ์.xlsx", engine="openpyxl")

# Rename columns for easier access
df.columns = ['equipment', 'Code', 'Cost', 'Universal healthcare', 'UCEP', 'Social Security', 'Civil Servant', 'Self pay']

# Set default quantities
default_quantities = {name: 0 for name in df['equipment']}
default_quantities['Angiogram'] = 1
default_quantities['Contrast media'] = 4
default_quantities['femoral sheath'] = 1
default_quantities['0.038 Wire'] = 1

# Streamlit UI
st.title("Healthcare Equipment Cost Calculator")

# Select healthcare scheme
schemes = ['Universal healthcare', 'UCEP', 'Social Security', 'Civil Servant', 'Self pay']
selected_scheme = st.selectbox("Select Healthcare Scheme", schemes)

# Input quantities
st.header("Enter Equipment Quantities")
quantities = {}
for index, row in df.iterrows():
    eq_name = row['equipment']
    default_qty = default_quantities.get(eq_name, 0)
    qty = st.number_input(f"{eq_name}", min_value=0, value=default_qty, step=1)
    quantities[eq_name] = qty

# Filter used equipment
used_equipment = df[df['equipment'].isin([k for k, v in quantities.items() if v > 0])].copy()
used_equipment['Quantity'] = used_equipment['equipment'].map(quantities)
used_equipment['Total Cost'] = used_equipment['Cost'] * used_equipment['Quantity']
used_equipment['Reimbursement'] = used_equipment[selected_scheme] * used_equipment['Quantity']
used_equipment['Out of Pocket'] = used_equipment['Total Cost'] - used_equipment['Reimbursement']
used_equipment['Out of Pocket'] = used_equipment['Out of Pocket'].apply(lambda x: max(x, 0))

# Display summary
st.header("Cost Summary")
st.dataframe(used_equipment[['equipment', 'Quantity', 'Total Cost', 'Reimbursement', 'Out of Pocket']])

# Generate PDF
def generate_pdf(data, scheme):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Healthcare Scheme: {scheme}", ln=True, align='L')
    pdf.ln(5)
    pdf.cell(40, 10, "Equipment", 1)
    pdf.cell(20, 10, "Qty", 1)
    pdf.cell(30, 10, "Cost", 1)
    pdf.cell(40, 10, "Reimbursement", 1)
    pdf.cell(40, 10, "Out of Pocket", 1)
    pdf.ln()
    for _, row in data.iterrows():
        pdf.cell(40, 10, str(row['equipment']), 1)
        pdf.cell(20, 10, str(row['Quantity']), 1)
        pdf.cell(30, 10, f"{row['Total Cost']:.2f}", 1)
        pdf.cell(40, 10, f"{row['Reimbursement']:.2f}", 1)
        pdf.cell(40, 10, f"{row['Out of Pocket']:.2f}", 1)
        pdf.ln()
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Download PDF
if st.button("Generate PDF Report"):
    pdf_file = generate_pdf(used_equipment, selected_scheme)
    st.download_button(label="Download PDF", data=pdf_file, file_name="cost_summary.pdf", mime="application/pdf")
