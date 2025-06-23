import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="UN Country Profiles Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/country_profile_variables.csv")
    return df

df = load_data()

# Sidebar
st.sidebar.title("🌍 UN Country Profiles")
selected_country = st.sidebar.selectbox("Select a country", sorted(df['country'].unique()))
numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
selected_metric = st.sidebar.selectbox("📊 View Top 10 Countries by:", numeric_columns)

# Main Title
st.title("UN Country Profiles Dashboard")

# --- Country Profile Display ---
st.subheader(f"📌 Country Profile: {selected_country}")
country_data = df[df['country'] == selected_country].T
country_data = country_data.reset_index()
country_data.columns = ['Indicator', 'Value']
country_data = country_data[1:]  # skip the first row (country name)

# Download button
st.markdown("### 📥 Download Profile")
csv = country_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Country Profile as CSV",
    data=csv,
    file_name=f"{selected_country}_profile.csv",
    mime='text/csv'
)

# Display in two columns
left_col, right_col = st.columns(2)
mid = len(country_data) // 2
with left_col:
    for i in range(mid):
        st.markdown(f"- **{country_data.iloc[i, 0]}**: {country_data.iloc[i, 1]}")
with right_col:
    for i in range(mid, len(country_data)):
        st.markdown(f"- **{country_data.iloc[i, 0]}**: {country_data.iloc[i, 1]}")

# --- Top 10 Chart by Population ---
st.markdown("---")
st.subheader("📊 Top 10 Countries by Selected Metric")
st.markdown("---")
st.subheader("⚖️ Compare Two Countries by a Metric")

# Country selectors
col1, col2 = st.columns(2)
with col1:
    country1 = st.selectbox("Select First Country", sorted(df['country'].unique()), key='country1')
with col2:
    country2 = st.selectbox("Select Second Country", sorted(df['country'].unique()), key='country2')

# Metric selector
compare_metric = st.selectbox("📊 Choose a metric to compare", numeric_columns, key='compare_metric')

# Extract data
compare_df = df[df['country'].isin([country1, country2])][['country', compare_metric]].copy()
compare_df[compare_metric] = pd.to_numeric(compare_df[compare_metric], errors='coerce')
st.markdown("---")
st.subheader("🌍 Global Metric Map")

# Select metric
map_metric = st.selectbox("🗺️ Select a metric to display on world map", numeric_columns, key='map_metric')

# Clean and prepare data
map_df = df[['country', map_metric]].copy()
map_df[map_metric] = pd.to_numeric(map_df[map_metric], errors='coerce')

# Plot choropleth
fig_map = px.choropleth(
    map_df,
    locations='country',
    locationmode='country names',
    color=map_metric,
    color_continuous_scale='Viridis',
    title=f"World Map: {map_metric}",
    labels={map_metric: map_metric}
)
fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})


# Plot side-by-side bar
fig_compare = px.bar(
    compare_df,
    x='country',
    y=compare_metric,
    color='country',
    title=f"{compare_metric} Comparison: {country1} vs {country2}",
    labels={compare_metric: compare_metric}
)
st.plotly_chart(fig_compare, use_container_width=True)

# Clean and sort selected metric
df[selected_metric] = pd.to_numeric(df[selected_metric], errors='coerce')
top10 = df.sort_values(by=selected_metric, ascending=False).head(10)

# Plot
fig = px.bar(
    top10,
    x='country',
    y=selected_metric,
    title=f"Top 10 Countries by {selected_metric}",
    labels={selected_metric: selected_metric},
    color='country'
)
st.plotly_chart(fig, use_container_width=True)
