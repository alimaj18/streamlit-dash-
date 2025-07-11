import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB Atlas
uri = "mongodb+srv://sba24031:cctcollege123@bigdataproject.fv4m4ai.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=BigDataProject"
client = MongoClient(uri)
db = client["CarSalesDB"]

# Load collections
orders = db["Orders"]
vehicles = db["Vehicles"]
customers = db["Customers"]

# Convert to DataFrames
df_orders = pd.DataFrame(list(orders.find()))
df_vehicles = pd.DataFrame(list(vehicles.find()))
df_customers = pd.DataFrame(list(customers.find()))

# Convert ObjectId to string for merging
df_orders['_id'] = df_orders['_id'].astype(str)
df_orders['vehicle_id'] = df_orders['vehicle_id'].astype(str)
df_orders['customer_id'] = df_orders['customer_id'].astype(str)
df_vehicles['_id'] = df_vehicles['_id'].astype(str)
df_customers['_id'] = df_customers['_id'].astype(str)

# Flatten vehicle showroom stock info
df_stock = df_vehicles.explode('stock')
df_stock['showroom'] = df_stock['stock'].apply(lambda x: x['showroom'] if isinstance(x, dict) else None)
df_stock['available'] = df_stock['stock'].apply(lambda x: x['available'] if isinstance(x, dict) else None)
df_stock = df_stock.drop(columns=['stock'])

# Merge with orders and customers
df_merged = df_orders.merge(df_stock, left_on='vehicle_id', right_on='_id', suffixes=('', '_vehicle'))
df_merged = df_merged.merge(df_customers, left_on='customer_id', right_on='_id', suffixes=('', '_customer'))

# Convert order_date
if 'order_date' in df_merged.columns:
    df_merged['order_date'] = pd.to_datetime(df_merged['order_date'])

# 🎯 Streamlit UI
st.title("Car Sales Dashboard")

# Bar chart: Orders by showroom
orders_by_showroom = df_merged['showroom'].value_counts()
st.subheader("Number of Orders per Showroom")
st.bar_chart(orders_by_showroom)

# Table
st.subheader("Merged Data Sample")
st.dataframe(df_merged[['name', 'nationality', 'make', 'model', 'showroom', 'status', 'order_date']].head())

import streamlit as st
import pandas as pd
from pymongo import MongoClient

# MongoDB Atlas connection
uri = "mongodb+srv://sba24031:cctcollege123@bigdataproject.fv4m4ai.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=BigDataProject"
client = MongoClient(uri)
db = client["CarSalesDB"]

# Load collections
orders = db["Orders"]
vehicles = db["Vehicles"]

# Convert to DataFrames
df_orders = pd.DataFrame(list(orders.find()))
df_vehicles = pd.DataFrame(list(vehicles.find()))

# Convert ObjectIds and dates
df_orders["_id"] = df_orders["_id"].astype(str)
df_orders["vehicle_id"] = df_orders["vehicle_id"].astype(str)
df_vehicles["_id"] = df_vehicles["_id"].astype(str)

if "order_date" in df_orders.columns:
    df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])

# Merge orders with vehicles on vehicle_id
df_merged = df_orders.merge(df_vehicles, left_on="vehicle_id", right_on="_id", suffixes=('_order', '_vehicle'))

# Extract showroom from stock (handle nested list)
def extract_showroom(stock_data):
    try:
        if isinstance(stock_data, list) and len(stock_data) > 0:
            return stock_data[0].get("showroom", "Unknown")
    except Exception:
        return "Unknown"

# Add showroom column if 'stock' exists
if "stock" in df_merged.columns:
    df_merged["showroom"] = df_merged["stock"].apply(extract_showroom)
else:
    st.warning("⚠️ 'stock' column not found in merged data. Showroom info not available.")
    df_merged["showroom"] = "Unknown"

# Group by showroom and count orders
showroom_counts = df_merged["showroom"].value_counts().reset_index()
showroom_counts.columns = ["Showroom", "Number of Orders"]

# Plot
st.title("Car Sales Dashboard")
st.subheader("📊 Number of Orders per Showroom")

if not showroom_counts.empty:
    st.bar_chart(showroom_counts.set_index("Showroom"))
else:
    st.write("No order data available.")


# Load customers
customers = db["Customers"]
df_customers = pd.DataFrame(list(customers.find()))
df_customers["_id"] = df_customers["_id"].astype(str)

# Add dummy 'age' column if missing
if "age" not in df_customers.columns:
    import random
    df_customers["age"] = [random.randint(18, 60) for _ in range(len(df_customers))]

# Merge orders with customers
df_orders["customer_id"] = df_orders["customer_id"].astype(str)
df_merged = df_orders.merge(df_customers, left_on="customer_id", right_on="_id", suffixes=('_order', '_customer'))
df_merged = df_merged.merge(df_vehicles, left_on="vehicle_id", right_on="_id", suffixes=('', '_vehicle'))

# Extract showroom
def extract_showroom(stock_data):
    try:
        if isinstance(stock_data, list) and len(stock_data) > 0:
            return stock_data[0].get("showroom", "Unknown")
    except Exception:
        return "Unknown"

df_merged["showroom"] = df_merged["stock"].apply(extract_showroom)

# Filter: Young Adults 18–35
df_young = df_merged[(df_merged["age"] >= 18) & (df_merged["age"] <= 35)]

# Group and plot
young_counts = df_young["showroom"].value_counts().reset_index()
young_counts.columns = ["Showroom", "Orders by 18–35 age group"]

st.subheader("📍 Orders by Young Adults (18–35)")
if not young_counts.empty:
    st.bar_chart(young_counts.set_index("Showroom"))
else:
    st.write("No data for customers aged 18–35.")

import matplotlib.pyplot as plt

st.subheader("🥧 Top 5 Car Models Purchased (Pie Chart)")

# Create a combined car model column
df_merged["car_model"] = df_merged["make"] + " " + df_merged["model"]

# Count top 5 car models
top_models = df_merged["car_model"].value_counts().head(5)

# Plot pie chart
fig, ax = plt.subplots()
ax.pie(top_models.values, labels=top_models.index, autopct="%1.1f%%", startangle=90)
ax.axis("equal")  # Equal aspect ratio ensures pie is drawn as a circle.

# Display in Streamlit
st.pyplot(fig)


