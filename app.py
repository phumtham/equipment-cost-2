import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from io import BytesIO

# Load the Excel file
df = pd.read_excel("ค่าอุปกรณ์.xlsx", engine="openpyxl")

# Rename columns for easier access
df.columns = ['equipment', 'Code', 'Cost', 'Universal healthcare', 'UCEP', 'Social Security', 'Civil Servant', 'Self pay']

# Set default quantities
default_quantities = {
    'Angiogram': 1,
    'Contrast media': 4,
    'femoral sheath': 1,
    '0.038 Wire': 1
}

# Streamlit UI
st.title("Healthcare Equipment Cost Calculator")

# Select healthcare scheme
schemes = ['Universal healthcare', 'UCEP', 'Social Security', 'Civil Servant', 'Self pay']
selected_scheme = st.selectbox("Select Healthcare Scheme", schemes)

# Input quantities
st.subheader("Enter Equipment Quantities")
quantities = {}
for index, row in df.iterrows():
    equipment = row['equipment']
    default_qty = default_quantities.get(equipment, 0)
    qty = st.number_input(f"{equipment}", min_value=0, value=default_qty, step=1)
    quantities[equipment] = qty

# Filter used equipment
used_equipment = []
for index, row in df.iterrows():
    equipment = row['equipment']
    qty = quantities[equipment]
    if qty > 0:
        cost = row['Cost'] * qty
        reimbursement = row[selected_scheme] * qty
        out_of_pocket = max(cost - reimbursement, 0)
        used_equipment.append({
            'Equipment': equipment,
            'Quantity': qty,
            'Unit Cost': row['Cost'],
            'Total Cost': cost,
            'Reimbursement': reimbursement,
            'Out-of-Pocket': out_of_pocket
        })

# Display summary
if used_equipment:
    st.subheader(f"Summary for {selected_scheme}")
    summary_df = pd.DataFrame(used_equipment)
    st.dataframe(summary_df)

    total_cost = summary_df['Total Cost'].sum()
    total_reimbursement = summary_df['Reimbursement'].sum()
    total_out_of_pocket = summary_df['Out-of-Pocket'].sum()

    st.markdown(f"**Total Cost:** {total_cost:,.2f} THB")
    st.markdown(f"**Total Reimbursement:** {total_reimbursement:,.2f} THB")
    st.markdown(f"**Total Out-of-Pocket:** {total_out_of_pocket:,.2f} THB")

    # Generate PDF
    def generate_pdf(data, scheme):
        pdf = fitz.open()
        page = pdf.new_page()
        text = f"Healthcare Scheme: {scheme}\n\n"
        text += "Equipment Summary:\n"
        for item in data:
            text += (
                f"- {item['Equipment']}: Qty {item['Quantity']}, "
                f"Unit Cost {item['Unit Cost']}, Total Cost {item['Total Cost']}, "
                f"Reimbursement {item['Reimbursement']}, Out-of-Pocket {item['Out-of-Pocket']}\n"
            )
        text += f"\nTotal Cost: {total_cost:,.2f} THB\n"
        text += f"Total Reimbursement: {total_reimbursement:,.2f} THB\n"
        text += f"Total Out-of-Pocket: {total_out_of_pocket:,.2f} THB\n"
        page.insert_text((72, 72), text, fontsize=12)
        pdf_bytes = pdf.write()
        pdf.close()
        return pdf_bytes

    pdf_bytes = generate_pdf(used_equipment, selected_scheme)
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="equipment_cost_report.pdf",
        mime="application/pdf"
    )
else:
    st.info("Please enter quantities greater than 0 for equipment used.")
