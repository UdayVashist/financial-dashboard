import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Financial Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Load Data ────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('data/superstore.csv', encoding='latin-1')
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed')
    df['Ship Date']  = pd.to_datetime(df['Ship Date'],  format='mixed')
    df['Order Year']    = df['Order Date'].dt.year
    df['Order Month']   = df['Order Date'].dt.to_period('M').astype(str)
    df['Order Quarter'] = df['Order Date'].dt.quarter.apply(lambda q: f"Q{q}")
    df['Profit Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
    df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days
    return df

# ── Sidebar Filters ──────────────────────────────────
st.sidebar.title("Filters")
years      = st.sidebar.multiselect("Year",     sorted(df['Order Year'].unique()),    default=sorted(df['Order Year'].unique()))
regions    = st.sidebar.multiselect("Region",   df['Region'].unique(),                default=list(df['Region'].unique()))
categories = st.sidebar.multiselect("Category", df['Category'].unique(),              default=list(df['Category'].unique()))

filtered = df[
    df['Order Year'].isin(years) &
    df['Region'].isin(regions) &
    df['Category'].isin(categories)
]

# ── KPI Cards ────────────────────────────────────────
st.title("📊 Financial Performance Dashboard")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue",  f"${filtered['Sales'].sum():,.0f}")
col2.metric("Net Profit",     f"${filtered['Profit'].sum():,.0f}")
col3.metric("Total Orders",   f"{filtered['Order ID'].nunique():,}")
col4.metric("Avg Profit Margin", f"{filtered['Profit Margin'].mean():.1f}%")

st.markdown("---")

# ── Row 1: Revenue Trend + Category Profit ───────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Monthly Revenue Trend")
    monthly = (filtered.groupby('Order Month')
               .agg(Revenue=('Sales','sum'))
               .reset_index()
               .sort_values('Order Month'))
    fig1 = px.line(monthly, x='Order Month', y='Revenue',
                   markers=True, color_discrete_sequence=['#636EFA'])
    fig1.update_layout(xaxis_tickangle=-45, height=320)
    st.plotly_chart(fig1, use_container_width=True)

with col_r:
    st.subheader("Profit by Category")
    cat = (filtered.groupby('Category')
           .agg(Profit=('Profit','sum'))
           .reset_index())
    fig2 = px.bar(cat, x='Category', y='Profit',
                  color='Category', height=320)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Sub-category Margin + State Map ───────────
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("Profit Margin by Sub-Category")
    sub = (filtered.groupby('Sub-Category')
           .agg(Revenue=('Sales','sum'), Profit=('Profit','sum'))
           .reset_index())
    sub['Margin %'] = (sub['Profit'] / sub['Revenue'] * 100).round(1)
    sub = sub.sort_values('Margin %')
    fig3 = px.bar(sub, x='Margin %', y='Sub-Category',
                  orientation='h', height=420,
                  color='Margin %',
                  color_continuous_scale='RdYlGn',
                  color_continuous_midpoint=0)
    st.plotly_chart(fig3, use_container_width=True)

with col_r2:
    st.subheader("Sales by State")
    state_sales = (filtered.groupby('State')
                   .agg(Sales=('Sales','sum'))
                   .reset_index())
    fig4 = px.choropleth(state_sales, locations='State',
                         locationmode='USA-states',
                         color='Sales', scope='usa',
                         color_continuous_scale='Blues',
                         height=420)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Raw Data Table ────────────────────────────
st.markdown("---")
st.subheader("Raw Data Explorer")
st.dataframe(
    filtered[['Order Date','Region','Category','Sub-Category',
              'Product Name','Sales','Profit','Profit Margin']]
    .sort_values('Order Date', ascending=False),
    use_container_width=True,
    height=300
)