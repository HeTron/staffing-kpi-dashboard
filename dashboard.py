import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('staffing_data.csv')

st.set_page_config(page_title="Staffing KPI Dashboard", layout="wide")

# Title
st.title("📊 Staffing KPI Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
departments = st.sidebar.multiselect("Select Departments", df['Department'].unique(), default=df['Department'].unique())
months = st.sidebar.multiselect("Select Months", df['Month'].unique(), default=df['Month'].unique())

# Filtered data
filtered_df = df[(df['Department'].isin(departments)) & (df['Month'].isin(months))]

# KPI cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Applicants", int(filtered_df['Applicants'].sum()))
col2.metric("Total Hires", int(filtered_df['Hires'].sum()))
col3.metric("Avg Time to Fill (days)", round(filtered_df['Avg Time to Fill (days)'].mean(), 1))

st.markdown("---")

# Visualization 1: Avg Time to Fill by Department
st.subheader("Average Time to Fill by Department")
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(data=filtered_df, x='Department', y='Avg Time to Fill (days)', ax=ax1, ci=None)
st.pyplot(fig1)

# Visualization 2: Offer Acceptance Rate
st.subheader("Offer Acceptance Rate by Department")
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.boxplot(data=filtered_df, x='Department', y='Offer Acceptance Rate', ax=ax2)
st.pyplot(fig2)

st.subheader("Hiring Funnel Breakdown")
funnel = filtered_df[['Applicants', 'Interviews', 'Offers', 'Hires']].sum()
funnel_fig, funnel_ax = plt.subplots(figsize=(8, 4))
sns.barplot(x=funnel.index, y=funnel.values, ax=funnel_ax)
funnel_ax.set_title("Total Hiring Funnel")
st.pyplot(funnel_fig)

st.subheader("Average Time to Fill Over Time")
monthly = filtered_df.groupby('Month')['Avg Time to Fill (days)'].mean().reset_index()
fig3, ax3 = plt.subplots(figsize=(10, 4))
sns.lineplot(data=monthly, x='Month', y='Avg Time to Fill (days)', marker='o', ax=ax3)
ax3.tick_params(axis='x', rotation=45)
st.pyplot(fig3)
