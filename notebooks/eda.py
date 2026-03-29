import pandas as pd
import numpy as np
import plotly.express as px

# ── Load Data ──────────────────────────────────────────────
data_path = r'C:\Users\Chitrank Vaishist\PycharmProjects\PythonProject4\Financial-Dashboard\data\superstore.csv'

df = pd.read_csv('../data/superstore.csv', encoding='latin-1')
print("Loaded! Shape:", df.shape)
print(df.dtypes)
print(df.isnull().sum())

# ── Fix Dates ──────────────────────────────────────────────
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed')
df['Ship Date']  = pd.to_datetime(df['Ship Date'],  format='mixed')

# ── Feature Engineering ────────────────────────────────────
df['Order Year']    = df['Order Date'].dt.year
df['Order Month']   = df['Order Date'].dt.to_period('M').astype(str)
df['Order Quarter'] = df['Order Date'].dt.quarter.apply(lambda q: f"Q{q}")
df['Profit Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days

# ── Summary Stats ──────────────────────────────────────────
print("\n=== Summary ===")
print(f"Total Revenue  : ${df['Sales'].sum():,.0f}")
print(f"Total Profit   : ${df['Profit'].sum():,.0f}")
print(f"Total Orders   : {df['Order ID'].nunique():,}")
print(f"Avg Margin     : {df['Profit Margin'].mean():.1f}%")

# ── Charts (will open in browser) ─────────────────────────
monthly = (df.groupby('Order Month')
             .agg(Revenue=('Sales','sum'))
             .reset_index()
             .sort_values('Order Month'))
px.line(monthly, x='Order Month', y='Revenue', title='Monthly Revenue Trend', markers=True).show()

cat = (df.groupby('Category')
         .agg(Revenue=('Sales','sum'), Profit=('Profit','sum'))
         .reset_index())
px.bar(cat, x='Category', y='Profit', color='Category', title='Profit by Category').show()

sub = (df.groupby('Sub-Category')
         .agg(Revenue=('Sales','sum'), Profit=('Profit','sum'))
         .reset_index())
sub['Margin %'] = (sub['Profit'] / sub['Revenue'] * 100).round(1)
sub = sub.sort_values('Margin %')
px.bar(sub, x='Margin %', y='Sub-Category', orientation='h',
       color='Margin %', color_continuous_scale='RdYlGn',
       color_continuous_midpoint=0,
       title='Profit Margin by Sub-Category').show()

region = (df.groupby('Region')
            .agg(Revenue=('Sales','sum'), Profit=('Profit','sum'))
            .reset_index())
px.bar(region, x='Region', y=['Revenue','Profit'], barmode='group',
       title='Revenue vs Profit by Region').show()

# ── Save Clean CSV ─────────────────────────────────────────
save_path = r'C:\Users\Chitrank Vaishist\PycharmProjects\PythonProject4\Financial-Dashboard\data\superstore_clean.csv'
df.to_csv('../data/superstore_clean.csv', index=False)
print("Clean file saved!")