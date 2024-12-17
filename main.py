import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Load datasets
def load_data():
    vehicles = pd.read_csv("data/vehicles.csv")
    rates = pd.read_csv("data/rent_rates.csv")
    layout = pd.read_csv("data/parking_layout.csv")
    return vehicles, rates, layout

vehicles, rates, layout = load_data()

# Helper function to calculate rent
def calculate_rent(vehicle_type, entry_time, exit_time):
    rate_per_hour = rates[rates['Type'] == vehicle_type]['RatePerHour'].values[0]
    entry_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M")
    exit_dt = datetime.strptime(exit_time, "%Y-%m-%d %H:%M")
    hours = max(1, (exit_dt - entry_dt).seconds // 3600)  # At least 1 hour
    return rate_per_hour * hours

# Header
st.title("🚗 Parking Lot Management System")

# 1. Vehicle Tracking
st.sidebar.header("🔍 Vehicle Tracking")
search_token = st.sidebar.text_input("Enter Token or License Number:")

if search_token:
    results = vehicles[
        (vehicles['Token'].astype(str) == search_token) | 
        (vehicles['License'] == search_token)
    ]
    if not results.empty:
        st.subheader("Vehicle Details")
        st.table(results)
    else:
        st.warning("No vehicle found for the given input!")

# 2. Add Vehicle Entry
st.sidebar.header("📝 Add Vehicle Entry")
with st.sidebar.form("add_vehicle"):
    token = st.text_input("Token")
    license_number = st.text_input("License Number")
    vehicle_type = st.selectbox("Vehicle Type", rates['Type'].unique())
    entry_time = st.text_input("Entry Time (YYYY-MM-DD HH:MM)", value=str(datetime.now())[:16])
    slot = st.text_input("Slot Number")
    submitted = st.form_submit_button("Add Vehicle")
    
    if submitted:
        new_entry = pd.DataFrame([[token, license_number, vehicle_type, entry_time, "", slot]], 
                                  columns=vehicles.columns)
        vehicles = pd.concat([vehicles, new_entry], ignore_index=True)
        vehicles.to_csv("data/vehicles.csv", index=False)
        st.success("Vehicle Added Successfully!")

# 3. Vehicle Exit and Rent Calculation
st.subheader("🚦 Vehicle Exit & Rent Calculation")
exit_token = st.text_input("Enter Token for Exit:")

if exit_token:
    result = vehicles[vehicles['Token'].astype(str) == exit_token]
    if not result.empty:
        st.write("Vehicle Found:")
        st.table(result)
        exit_time = st.text_input("Exit Time (YYYY-MM-DD HH:MM)", value=str(datetime.now())[:16])
        if st.button("Calculate Rent"):
            rent = calculate_rent(result['Type'].iloc[0], result['EntryTime'].iloc[0], exit_time)
            st.success(f"Total Rent: ₹{rent}")
            vehicles.loc[vehicles['Token'].astype(str) == exit_token, 'ExitTime'] = exit_time
            vehicles.to_csv("data/vehicles.csv", index=False)
    else:
        st.warning("No vehicle found for the given token!")

# 4. Parking Layout Visualization
st.subheader("🗺️ Parking Lot Layout")
st.table(layout)

# 5. Analytics
st.subheader("📊 Analytics")
total_vehicles = len(vehicles)
occupied_slots = layout[layout['Status'] == 'Occupied'].shape[0]
vacant_slots = layout[layout['Status'] == 'Vacant'].shape[0]
st.write(f"**Total Vehicles:** {total_vehicles}")
st.write(f"**Occupied Slots:** {occupied_slots}")
st.write(f"**Vacant Slots:** {vacant_slots}")

st.bar_chart(layout['Status'].value_counts())
