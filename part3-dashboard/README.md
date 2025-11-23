# Health Risk Dashboard

Interactive dashboards for health risk monitoring and personal health tracking.

## Overview

This directory contains two Streamlit dashboards:

1. **Authorities Dashboard** (`dashboard/authorities_app.py`) - For health authorities
   - Public-health risk maps
   - Alerts for high-risk areas
   - Aggregated statistics by location
   - Environmental factors analysis
   - Trend monitoring

2. **Citizens Dashboard** (`dashboard/citizens_app.py`) - For individual citizens
   - Personal health alerts
   - Health metrics trends
   - Risk predictions
   - Personalized recommendations
   - Environmental factors

## Installation

Make sure you have installed all dependencies from the main `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Running the Dashboards

### Authorities Dashboard

```bash
streamlit run part3-dashboard/dashboard/authorities_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Citizens Dashboard

```bash
streamlit run part3-dashboard/dashboard/citizens_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Features

### Authorities Dashboard Features

- **Active Alerts**: Real-time alerts for high-risk areas
- **Risk Maps**: Geographic visualization of health risks by city
- **Key Metrics**: Total patients, high-risk counts, average risk percentages
- **Trend Analysis**: Historical trends of risk percentages over time
- **Environmental Analysis**: Correlation between air quality and health risks
- **Detailed Statistics**: Node-by-node breakdown of health metrics

### Citizens Dashboard Features

- **Current Health Status**: Real-time risk assessment
- **Personal Alerts**: Customized alerts based on health metrics
- **Health Trends**: Visualizations of heart rate, steps, sleep, and risk probability
- **Health Metrics Overview**: Summary statistics and comparisons
- **Environmental Factors**: Air quality and weather data
- **Personalized Recommendations**: AI-driven health recommendations
- **Data Export**: Download personal health data

## Usage

### For Health Authorities

1. Launch the authorities dashboard
2. Use sidebar filters to adjust:
   - Number of nodes to monitor
   - Days of historical data
   - High-risk threshold percentage
3. Review active alerts for immediate action
4. Analyze risk maps to identify high-risk areas
5. Monitor trends over time
6. Download data for further analysis

### For Citizens

1. Launch the citizens dashboard
2. Enter your Patient ID in the sidebar
3. Adjust the days of history to view
4. Review your current health status and alerts
5. Explore your health trends over time
6. Check environmental factors affecting your area
7. Follow personalized recommendations
8. Download your health data

## Data Sources

The dashboards use simulated data from:
- Wearable device data (heart rate, steps, sleep, etc.)
- Environmental sensors (air quality, weather)
- Health risk predictions from the federated learning model

## Integration

The dashboards can be integrated with:
- The inference API (`part2-mlops/mlops/inference_server.py`) for real-time predictions
- MLflow for model tracking and versioning
- The federated learning system for model updates

## Customization

You can customize the dashboards by:
- Modifying the data generation functions
- Adjusting risk thresholds
- Adding new visualizations
- Integrating with real data sources
- Connecting to the inference API for live predictions

## Notes

- The dashboards currently use simulated data for demonstration
- In production, connect to real data sources and the inference API
- Consider adding authentication for sensitive health data
- Ensure compliance with health data privacy regulations (HIPAA, GDPR, etc.)

