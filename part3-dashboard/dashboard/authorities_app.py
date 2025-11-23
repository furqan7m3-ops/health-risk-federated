"""
Health Authorities Dashboard
Public-health risk maps, alerts, and aggregated statistics
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add project paths
# Get the directory where this file is located
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
# Go up to project root: part3-dashboard/dashboard -> part3-dashboard -> project root
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
# Add part1-data-model to path
part1_path = os.path.join(project_root, 'part1-data-model')
sys.path.insert(0, part1_path)

from data_simulation.wearables import WearableSimulator
from data_simulation.air_quality import EnvironmentalSimulator

# Page config
st.set_page_config(
    page_title="Health Authorities Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .high-risk {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .medium-risk {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
    }
    .low-risk {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_authorities_data(num_nodes=5, days=7):
    """Generate aggregated health risk data for multiple nodes"""
    wear_sim = WearableSimulator(num_patients=500)
    env_sim = EnvironmentalSimulator(num_sensors=20)
    
    nodes = [f"hospital_{i:02d}" for i in range(1, num_nodes + 1)]
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    
    all_data = []
    current_date = datetime.now()
    
    for day_offset in range(days):
        date = (current_date - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        
        for idx, node in enumerate(nodes):
            # Generate health data
            health_data = wear_sim.generate_daily_data(date, node_id=node)
            
            # Generate environmental data
            env_data = env_sim.generate_sensor_data(node_id=node)
            env_mean = env_data.groupby('node_id').mean().reset_index()
            
            # Merge data
            merged = health_data.merge(env_mean, on='node_id', how='left').fillna(0)
            
            # Calculate aggregated metrics
            total_patients = len(merged)
            high_risk_count = merged['risk_score'].sum()
            high_risk_pct = (high_risk_count / total_patients) * 100
            
            avg_heart_rate = merged['heart_rate'].mean()
            avg_pm25 = merged['pm25'].mean()
            avg_pm10 = merged['pm10'].mean()
            avg_temp = merged['temperature'].mean()
            
            all_data.append({
                'date': date,
                'node_id': node,
                'city': cities[idx % len(cities)],
                'total_patients': total_patients,
                'high_risk_count': high_risk_count,
                'high_risk_percentage': high_risk_pct,
                'avg_heart_rate': avg_heart_rate,
                'avg_pm25': avg_pm25,
                'avg_pm10': avg_pm10,
                'avg_temperature': avg_temp,
                'avg_o3': merged['o3'].mean(),
                'avg_no2': merged['no2'].mean(),
                'avg_humidity': merged['humidity'].mean()
            })
    
    return pd.DataFrame(all_data)

def get_risk_level(risk_pct):
    """Determine risk level based on percentage"""
    if risk_pct >= 20:
        return "High", "🔴"
    elif risk_pct >= 10:
        return "Medium", "🟡"
    else:
        return "Low", "🟢"

def main():
    st.markdown('<h1 class="main-header">🏥 Health Authorities Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Public Health Risk Monitoring & Alerts")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    num_nodes = st.sidebar.slider("Number of Nodes", 3, 10, 5)
    days = st.sidebar.slider("Days of History", 3, 30, 7)
    risk_threshold = st.sidebar.slider("High Risk Threshold (%)", 5, 30, 15)
    
    # Generate data
    with st.spinner("Loading health data..."):
        df = generate_authorities_data(num_nodes=num_nodes, days=days)
    
    # Current date data
    latest_date = df['date'].max()
    latest_data = df[df['date'] == latest_date].copy()
    
    # Alerts Section
    st.header("🚨 Active Alerts")
    
    high_risk_nodes = latest_data[latest_data['high_risk_percentage'] >= risk_threshold]
    
    if len(high_risk_nodes) > 0:
        for _, row in high_risk_nodes.iterrows():
            risk_level, emoji = get_risk_level(row['high_risk_percentage'])
            st.markdown(f"""
                <div class="alert-box high-risk">
                    <h4>{emoji} Alert: {row['city']} ({row['node_id']})</h4>
                    <p><strong>Risk Level:</strong> {risk_level} ({row['high_risk_percentage']:.1f}% high-risk patients)</p>
                    <p><strong>High Risk Patients:</strong> {int(row['high_risk_count'])} / {int(row['total_patients'])}</p>
                    <p><strong>Air Quality (PM2.5):</strong> {row['avg_pm25']:.2f} μg/m³</p>
                    <p><strong>Date:</strong> {row['date']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No high-risk alerts at this time")
    
    # Key Metrics
    st.header("📊 Key Metrics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_patients = latest_data['total_patients'].sum()
        st.metric("Total Patients Monitored", f"{total_patients:,}")
    
    with col2:
        total_high_risk = latest_data['high_risk_count'].sum()
        st.metric("High Risk Patients", f"{total_high_risk:,}", 
                 delta=f"{(total_high_risk/latest_data['total_patients'].sum()*100):.1f}%")
    
    with col3:
        avg_risk_pct = latest_data['high_risk_percentage'].mean()
        st.metric("Average Risk %", f"{avg_risk_pct:.1f}%")
    
    with col4:
        active_nodes = len(latest_data)
        st.metric("Active Nodes", active_nodes)
    
    # Risk Map
    st.header("🗺️ Risk Map by Location")
    
    # Create risk map data
    map_data = latest_data.groupby('city').agg({
        'high_risk_percentage': 'mean',
        'total_patients': 'sum',
        'high_risk_count': 'sum',
        'avg_pm25': 'mean',
        'avg_pm10': 'mean'
    }).reset_index()
    
    # Simulate coordinates for cities (in real app, use actual coordinates)
    city_coords = {
        'New York': {'lat': 40.7128, 'lon': -74.0060},
        'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
        'Chicago': {'lat': 41.8781, 'lon': -87.6298},
        'Houston': {'lat': 29.7604, 'lon': -95.3698},
        'Phoenix': {'lat': 33.4484, 'lon': -112.0740}
    }
    
    map_data['lat'] = map_data['city'].map(lambda x: city_coords.get(x, {}).get('lat', 0))
    map_data['lon'] = map_data['city'].map(lambda x: city_coords.get(x, {}).get('lon', 0))
    
    # Create map visualization
    fig_map = px.scatter_mapbox(
        map_data,
        lat='lat',
        lon='lon',
        size='high_risk_count',
        color='high_risk_percentage',
        hover_name='city',
        hover_data={
            'high_risk_percentage': ':.1f',
            'total_patients': ':d',
            'avg_pm25': ':.2f'
        },
        color_continuous_scale='RdYlGn_r',
        size_max=50,
        zoom=3,
        height=500,
        title="Health Risk Distribution by City"
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Risk Trends Over Time
    st.header("📈 Risk Trends Over Time")
    
    trend_data = df.groupby(['date', 'city']).agg({
        'high_risk_percentage': 'mean',
        'high_risk_count': 'sum',
        'total_patients': 'sum'
    }).reset_index()
    
    fig_trend = px.line(
        trend_data,
        x='date',
        y='high_risk_percentage',
        color='city',
        markers=True,
        title="High Risk Percentage Trend by City",
        labels={'high_risk_percentage': 'High Risk %', 'date': 'Date'}
    )
    fig_trend.update_layout(height=400)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Environmental Factors
    st.header("🌍 Environmental Factors Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PM2.5 vs Risk
        fig_pm = px.scatter(
            latest_data,
            x='avg_pm25',
            y='high_risk_percentage',
            size='total_patients',
            color='city',
            hover_name='node_id',
            title="PM2.5 vs High Risk Percentage",
            labels={'avg_pm25': 'PM2.5 (μg/m³)', 'high_risk_percentage': 'High Risk %'}
        )
        st.plotly_chart(fig_pm, use_container_width=True)
    
    with col2:
        # Air Quality Index
        latest_data['aqi'] = (latest_data['avg_pm25'] + latest_data['avg_pm10']) / 2
        fig_aqi = px.bar(
            latest_data.sort_values('aqi', ascending=False),
            x='city',
            y='aqi',
            color='high_risk_percentage',
            title="Air Quality Index by City",
            labels={'aqi': 'Air Quality Index', 'city': 'City'}
        )
        st.plotly_chart(fig_aqi, use_container_width=True)
    
    # Detailed Node Statistics
    st.header("📋 Detailed Node Statistics")
    
    selected_city = st.selectbox("Select City", options=['All'] + list(latest_data['city'].unique()))
    
    if selected_city == 'All':
        display_data = latest_data
    else:
        display_data = latest_data[latest_data['city'] == selected_city]
    
    # Format display
    display_cols = ['node_id', 'city', 'total_patients', 'high_risk_count', 
                   'high_risk_percentage', 'avg_heart_rate', 'avg_pm25', 
                   'avg_pm10', 'avg_temperature']
    
    display_df = display_data[display_cols].copy()
    display_df.columns = ['Node ID', 'City', 'Total Patients', 'High Risk Count',
                          'High Risk %', 'Avg Heart Rate', 'PM2.5', 'PM10', 'Temperature']
    display_df = display_df.round(2)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Dataset",
        data=csv,
        file_name=f"health_authorities_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()

