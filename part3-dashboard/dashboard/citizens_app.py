"""
Citizens Dashboard
Personal health alerts, trends, and recommendations
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
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(project_root, 'part1-data-model'))

from data_simulation.wearables import WearableSimulator
from data_simulation.air_quality import EnvironmentalSimulator

# Page config
st.set_page_config(
    page_title="Personal Health Dashboard",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2e7d32;
        margin-bottom: 1rem;
    }
    .alert-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    .info-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_personal_data(patient_id, days=30):
    """Generate personal health data for a specific patient"""
    wear_sim = WearableSimulator(num_patients=1)
    env_sim = EnvironmentalSimulator(num_sensors=1)
    
    all_data = []
    current_date = datetime.now()
    
    for day_offset in range(days):
        date = (current_date - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        
        # Generate health data
        health_data = wear_sim.generate_daily_data(date, node_id="hospital_01")
        if len(health_data) > 0:
            patient_data = health_data.iloc[0].copy()
            
            # Generate environmental data
            env_data = env_sim.generate_sensor_data(node_id="hospital_01")
            env_mean = env_data.groupby('node_id').mean().reset_index()
            
            if len(env_mean) > 0:
                # Simulate risk prediction
                risk_score = patient_data['risk_score']
                risk_probability = 0.15 if risk_score == 0 else 0.75
                
                all_data.append({
                    'date': date,
                    'patient_id': patient_id,
                    'heart_rate': patient_data['heart_rate'],
                    'steps': patient_data['steps'],
                    'sleep_hours': patient_data['sleep_hours'],
                    'respiratory_rate': patient_data['respiratory_rate'],
                    'body_temp': patient_data['body_temp'],
                    'pm25': env_mean.iloc[0]['pm25'] if len(env_mean) > 0 else 12,
                    'pm10': env_mean.iloc[0]['pm10'] if len(env_mean) > 0 else 20,
                    'o3': env_mean.iloc[0]['o3'] if len(env_mean) > 0 else 0.035,
                    'no2': env_mean.iloc[0]['no2'] if len(env_mean) > 0 else 18,
                    'temperature': env_mean.iloc[0]['temperature'] if len(env_mean) > 0 else 70,
                    'humidity': env_mean.iloc[0]['humidity'] if len(env_mean) > 0 else 55,
                    'risk_score': risk_score,
                    'risk_probability': risk_probability
                })
    
    return pd.DataFrame(all_data)

def get_risk_level(risk_prob):
    """Determine risk level based on probability"""
    if risk_prob >= 0.7:
        return "High", "🔴", "high-risk"
    elif risk_prob >= 0.3:
        return "Medium", "🟡", "medium-risk"
    else:
        return "Low", "🟢", "low-risk"

def get_recommendations(risk_level, data):
    """Get personalized health recommendations"""
    latest = data.iloc[-1]
    recommendations = []
    
    if risk_level == "High":
        recommendations.append("⚠️ **Immediate Action Recommended**: Consult with your healthcare provider")
        if latest['heart_rate'] > 90:
            recommendations.append("💓 Your heart rate is elevated. Consider rest and relaxation")
        if latest['sleep_hours'] < 6:
            recommendations.append("😴 Prioritize getting 7-9 hours of sleep")
        if latest['pm25'] > 35:
            recommendations.append("🌬️ Air quality is poor. Limit outdoor activities")
        if latest['steps'] < 3000:
            recommendations.append("🚶 Increase daily activity, but avoid high-intensity exercise")
    elif risk_level == "Medium":
        recommendations.append("📊 Monitor your health metrics closely")
        if latest['sleep_hours'] < 7:
            recommendations.append("😴 Aim for 7-9 hours of sleep per night")
        if latest['steps'] < 5000:
            recommendations.append("🚶 Try to reach 5,000-10,000 steps daily")
        if latest['pm25'] > 25:
            recommendations.append("🌬️ Consider wearing a mask if air quality is concerning")
    else:
        recommendations.append("✅ Your health metrics look good!")
        recommendations.append("💪 Keep up the healthy habits")
        if latest['steps'] < 8000:
            recommendations.append("🚶 Consider increasing daily activity for optimal health")
    
    return recommendations

def main():
    st.markdown('<h1 class="main-header">👤 Personal Health Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Your Health Metrics, Alerts & Trends")
    
    # Sidebar - Patient Selection
    st.sidebar.header("Your Profile")
    patient_id = st.sidebar.text_input("Patient ID", value="PT_0001")
    days_history = st.sidebar.slider("Days of History", 7, 90, 30)
    
    # Generate personal data
    with st.spinner("Loading your health data..."):
        df = generate_personal_data(patient_id, days=days_history)
    
    if len(df) == 0:
        st.error("No data available for this patient. Please check the Patient ID.")
        return
    
    # Sort by date
    df = df.sort_values('date')
    latest = df.iloc[-1]
    
    # Current Risk Status
    st.header("🎯 Current Health Status")
    
    risk_level, emoji, risk_class = get_risk_level(latest['risk_probability'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h2 style="margin:0; color: #1f77b4;">{latest['risk_probability']*100:.1f}%</h2>
                <p style="margin:0; color: #666;">Risk Probability</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h2 style="margin:0; color: #2e7d32;">{risk_level}</h2>
                <p style="margin:0; color: #666;">Risk Level</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h2 style="margin:0; color: #ff9800;">{latest['date']}</h2>
                <p style="margin:0; color: #666;">Last Updated</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Personal Alerts
    st.header("🔔 Personal Alerts")
    
    alerts = []
    
    # Health alerts
    if latest['heart_rate'] > 100:
        alerts.append(("High Heart Rate", f"Your heart rate is {latest['heart_rate']:.0f} bpm, which is above normal. Consider rest.", "high-risk"))
    elif latest['heart_rate'] < 50:
        alerts.append(("Low Heart Rate", f"Your heart rate is {latest['heart_rate']:.0f} bpm, which is below normal. Consult a doctor.", "high-risk"))
    
    if latest['sleep_hours'] < 6:
        alerts.append(("Insufficient Sleep", f"You only got {latest['sleep_hours']:.1f} hours of sleep. Aim for 7-9 hours.", "medium-risk"))
    
    if latest['body_temp'] > 99.5:
        alerts.append(("Elevated Body Temperature", f"Your body temperature is {latest['body_temp']:.1f}°F. Monitor for symptoms.", "medium-risk"))
    
    if latest['steps'] < 3000:
        alerts.append(("Low Activity", f"You've only taken {latest['steps']:.0f} steps today. Try to be more active.", "low-risk"))
    
    # Environmental alerts
    if latest['pm25'] > 35:
        alerts.append(("Poor Air Quality", f"PM2.5 level is {latest['pm25']:.1f} μg/m³ (unhealthy). Limit outdoor activities.", "high-risk"))
    elif latest['pm25'] > 25:
        alerts.append(("Moderate Air Quality", f"PM2.5 level is {latest['pm25']:.1f} μg/m³. Sensitive individuals should take caution.", "medium-risk"))
    
    if risk_level == "High":
        alerts.append(("High Health Risk", "Your current health metrics indicate elevated risk. Please consult with healthcare provider.", "high-risk"))
    
    if alerts:
        for title, message, alert_class in alerts:
            st.markdown(f"""
                <div class="alert-box {alert_class}">
                    <h4>{title}</h4>
                    <p>{message}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No active alerts. Your health metrics look good!")
    
    # Health Trends
    st.header("📈 Health Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Heart Rate Trend
        fig_hr = px.line(
            df,
            x='date',
            y='heart_rate',
            title="Heart Rate Trend",
            labels={'heart_rate': 'Heart Rate (bpm)', 'date': 'Date'},
            markers=True
        )
        fig_hr.add_hline(y=72, line_dash="dash", line_color="green", 
                        annotation_text="Normal Range")
        fig_hr.add_hline(y=100, line_dash="dash", line_color="red", 
                        annotation_text="High")
        fig_hr.update_layout(height=300)
        st.plotly_chart(fig_hr, use_container_width=True)
        
        # Sleep Hours Trend
        fig_sleep = px.bar(
            df,
            x='date',
            y='sleep_hours',
            title="Sleep Hours",
            labels={'sleep_hours': 'Hours', 'date': 'Date'},
            color='sleep_hours',
            color_continuous_scale='Blues'
        )
        fig_sleep.add_hline(y=7, line_dash="dash", line_color="green", 
                           annotation_text="Recommended")
        fig_sleep.update_layout(height=300)
        st.plotly_chart(fig_sleep, use_container_width=True)
    
    with col2:
        # Steps Trend
        fig_steps = px.line(
            df,
            x='date',
            y='steps',
            title="Daily Steps",
            labels={'steps': 'Steps', 'date': 'Date'},
            markers=True,
            color_discrete_sequence=['#2e7d32']
        )
        fig_steps.add_hline(y=10000, line_dash="dash", line_color="green", 
                           annotation_text="Goal")
        fig_steps.update_layout(height=300)
        st.plotly_chart(fig_steps, use_container_width=True)
        
        # Risk Probability Trend
        fig_risk = px.area(
            df,
            x='date',
            y='risk_probability',
            title="Health Risk Probability Trend",
            labels={'risk_probability': 'Risk Probability', 'date': 'Date'},
            color_discrete_sequence=['#f44336']
        )
        fig_risk.add_hline(y=0.7, line_dash="dash", line_color="red", 
                          annotation_text="High Risk")
        fig_risk.add_hline(y=0.3, line_dash="dash", line_color="orange", 
                          annotation_text="Medium Risk")
        fig_risk.update_layout(height=300)
        st.plotly_chart(fig_risk, use_container_width=True)
    
    # Health Metrics Overview
    st.header("💪 Health Metrics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_hr = df['heart_rate'].mean()
        st.metric("Avg Heart Rate", f"{avg_hr:.0f} bpm", 
                 delta=f"{latest['heart_rate'] - avg_hr:.0f}")
    
    with col2:
        avg_steps = df['steps'].mean()
        st.metric("Avg Daily Steps", f"{avg_steps:.0f}", 
                 delta=f"{latest['steps'] - avg_steps:.0f}")
    
    with col3:
        avg_sleep = df['sleep_hours'].mean()
        st.metric("Avg Sleep Hours", f"{avg_sleep:.1f} hrs", 
                 delta=f"{latest['sleep_hours'] - avg_sleep:.1f}")
    
    with col4:
        avg_temp = df['body_temp'].mean()
        st.metric("Avg Body Temp", f"{avg_temp:.1f}°F", 
                 delta=f"{latest['body_temp'] - avg_temp:.1f}")
    
    # Environmental Factors
    st.header("🌍 Environmental Factors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Air Quality Trend
        fig_aq = px.line(
            df,
            x='date',
            y=['pm25', 'pm10'],
            title="Air Quality (PM2.5 & PM10)",
            labels={'value': 'Concentration (μg/m³)', 'date': 'Date', 'variable': 'Pollutant'},
            markers=True
        )
        fig_aq.update_layout(height=300)
        st.plotly_chart(fig_aq, use_container_width=True)
    
    with col2:
        # Weather Factors
        fig_weather = go.Figure()
        fig_weather.add_trace(go.Scatter(
            x=df['date'],
            y=df['temperature'],
            name='Temperature',
            yaxis='y',
            line=dict(color='red')
        ))
        fig_weather.add_trace(go.Scatter(
            x=df['date'],
            y=df['humidity'],
            name='Humidity',
            yaxis='y2',
            line=dict(color='blue')
        ))
        fig_weather.update_layout(
            title="Temperature & Humidity",
            xaxis_title="Date",
            yaxis=dict(title="Temperature (°F)", side="left"),
            yaxis2=dict(title="Humidity (%)", side="right", overlaying="y"),
            height=300
        )
        st.plotly_chart(fig_weather, use_container_width=True)
    
    # Recommendations
    st.header("💡 Personalized Recommendations")
    
    recommendations = get_recommendations(risk_level, df)
    
    for rec in recommendations:
        st.markdown(f"• {rec}")
    
    # Download Data
    st.header("📥 Download Your Data")
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Health Data (CSV)",
        data=csv,
        file_name=f"personal_health_data_{patient_id}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Info Box
    st.markdown("""
        <div class="info-box">
            <h4>ℹ️ About Your Data</h4>
            <p>This dashboard shows your personal health metrics collected from wearable devices 
            and environmental sensors. Data is updated daily and used to provide personalized 
            health insights and recommendations.</p>
            <p><strong>Privacy:</strong> Your data is kept private and secure. Only aggregated, 
            anonymized data is shared with health authorities for public health monitoring.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

