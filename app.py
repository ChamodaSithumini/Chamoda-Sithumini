
# cd C:\Users\ACER\Desktop\MySQL_Project
# streamlit run app.py


# Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# Connect to MySQL and load the data
username = "root"
password = "ASPIREE15mysql"
database_name = "customer_orders_data1"

connection_string = f"mysql+mysqlconnector://{username}:{password}@localhost/{database_name}"
engine = create_engine(connection_string)

# Query to fetch data from MySQL database
with engine.connect() as connection:
    customers = connection.execute(text("SELECT * FROM customers")).fetchall()
    orders = connection.execute(text("SELECT * FROM orders")).fetchall()

# Convert data to DataFrame
df_customers = pd.DataFrame(customers, columns=['customer_id', 'name', 'email'])
df_orders = pd.DataFrame(orders, columns=['id', 'display_order_id', 'total_amount', 'created_at', 'customer_id'])

# Drop unnecessary columns
df_customers = df_customers.drop(columns=['email'])
df_orders = df_orders.drop(columns=['display_order_id'])

# Merge the DataFrames on customer_id
merged_df = pd.merge(df_orders, df_customers, on='customer_id', how='left')



merged_df['created_at'] = pd.to_datetime(merged_df['created_at'], errors='coerce')



# Sidebar Filters
st.sidebar.header("Filters")

# Date Range Filter
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime(merged_df['created_at']).min())
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(merged_df['created_at']).max())
filtered_df = merged_df[
    (merged_df['created_at'] >= pd.to_datetime(start_date)) & 
    (merged_df['created_at'] <= pd.to_datetime(end_date))
]

# Total Amount Slider Filter
total_amount_filter = st.sidebar.slider(
    "Total Amount Spent", 
    min_value=int(merged_df['total_amount'].min()), 
    max_value=int(merged_df['total_amount'].max()), 
    value=int(1000)
)
filtered_df = filtered_df[filtered_df['total_amount'] >= total_amount_filter]

# Order Count Dropdown Filter
order_counts = merged_df.groupby('customer_id')['id'].count()
min_orders = st.sidebar.selectbox("Minimum Number of Orders", options=[5, 10, 20, 50])
customers_with_min_orders = order_counts[order_counts > min_orders].index
filtered_df = filtered_df[filtered_df['customer_id'].isin(customers_with_min_orders)]



# Main Dashboard
st.title("Customer Orders Dashboard")

# Display filtered data in a table
st.subheader("Filtered Data")
st.dataframe(filtered_df)
# Top 10 Customers by Total Revenue
top_customers = filtered_df.groupby('customer_id')['total_amount'].sum().nlargest(10).reset_index()
top_customers = top_customers.merge(df_customers[['customer_id', 'name']], on='customer_id', how='left')
fig_bar = px.bar(top_customers, x='name', y='total_amount', title="Top 10 Customers by Revenue")
st.plotly_chart(fig_bar)
# Total Revenue Over Time (grouped by month)
filtered_df['created_at'] = pd.to_datetime(filtered_df['created_at'])
revenue_over_time = filtered_df.resample('M', on='created_at')['total_amount'].sum().reset_index()
fig_line = px.line(revenue_over_time, x='created_at', y='total_amount', title="Total Revenue Over Time")
st.plotly_chart(fig_line)


# Summary Metrics
st.subheader("Key Metrics")
total_revenue = filtered_df['total_amount'].sum()
unique_customers = filtered_df['customer_id'].nunique()
total_orders = filtered_df['id'].nunique()

st.write(f"**Total Revenue:** ${total_revenue}")
st.write(f"**Number of Unique Customers:** {unique_customers}")
st.write(f"**Number of Orders:** {total_orders}")