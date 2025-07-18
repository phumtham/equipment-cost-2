
import pandas as pd
import streamlit as st

# Load the Excel file
df = pd.read_excel("ค่าอุปกรณ์.xlsx", engine="openpyxl")

# Set page configuration
st.set_page_config(page_title="Healthcare Equipment Cost Calculator", layout="wide")

# Title
st.title("Healthcare Equipment Cost Calculator")

# Select healthcare scheme
scheme = st.selectbox("Select Healthcare Scheme", [
    "Universal healthcare", "UCEP", "Social Security", "Civil Servant", "Self pay"
])

# Input quantities for each equipment
st.subheader("Enter Equipment Quantities")
quantities = {}
for index, row in df.iterrows():
    equipment = row['equipment']
    default_qty = 0
    if equipment == 'Angiogram':
        default_qty = 1
    elif equipment == 'Contrast media':
        default_qty = 4
    elif equipment == 'femoral sheath':
        default_qty = 1
    elif equipment == '0.038 Wire':
        default_qty = 1
    qty = st.number_input(f"{equipment}", min_value=0, value=default_qty, step=1)
    quantities[equipment] = qty

# Filter out equipment with quantity > 0
used_items = df[df['equipment'].isin([k for k, v in quantities.items() if v > 0])].copy()
used_items['Quantity'] = used_items['equipment'].map(quantities)
used_items['Total Cost'] = used_items['Cost'] * used_items['Quantity']
used_items['Reimbursement'] = used_items[scheme] * used_items['Quantity']
used_items['Out-of-pocket'] = used_items['Total Cost'] - used_items['Reimbursement']

# Display summary
st.subheader(f"Summary for {scheme}")
st.dataframe(used_items[['equipment', 'Quantity', 'Total Cost', 'Reimbursement', 'Out-of-pocket']])

# Show totals
total_cost = used_items['Total Cost'].sum()
total_reimbursement = used_items['Reimbursement'].sum()
total_out_of_pocket = used_items['Out-of-pocket'].sum()

st.markdown(f"**Total Cost:** {total_cost:,.2f} THB")
st.markdown(f"**Total Reimbursement:** {total_reimbursement:,.2f} THB")
st.markdown(f"**Patient Out-of-pocket Expense:** {total_out_of_pocket:,.2f} THB")
