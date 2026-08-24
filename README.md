# Service Cockpit - Heat Pump Monitoring Dashboard

A proactive customer communication tool for heat pump service management, built with Streamlit.

## Features

- **Priority Action List**: Identifies units needing immediate attention based on alert patterns, temperature anomalies, and maintenance schedules
- **Unit Status Dashboard**: Real-time view of all connected units with key metrics
- **Trend Analysis**: Visual charts showing priority distribution, vendor patterns, and temperature relationships
- **Communication Center**: Pre-built message templates for proactive customer outreach

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
streamlit run cockpit_app.py
```

The application will open in your browser at `http://localhost:8501`

## System Requirements

- Python 3.8 or higher
- Internet connection (for loading Plotly charts)
- The `docs/` folder containing:
  - `installation_base.csv`
  - `telemetry_daily.csv`

## Data Processing

The application automatically handles data quality issues:
- Normalizes reference numbers (TH-02085 → 02085)
- Standardizes vendor names (OEM_A, oem a, A → A)
- Unifies date formats (DD.MM.YYYY → YYYY-MM-DD)
- Handles missing values (-999 → NaN)
- Calculates priority scores based on risk factors

## Priority Scoring Logic

Units are scored based on:
- **Critical (50+ points)**: High alert rates (Vendor C), low hot water temp, frequent errors
- **High (40-59 points)**: Multiple warning factors, overdue service
- **Medium (20-39 points)**: Service due, connected but no data
- **Normal (<20 points)**: Operating normally

## Usage

1. **Priority Action List**: Start here to see which customers need immediate attention
2. **Unit Status Dashboard**: Search and view detailed status of specific units
3. **Trend Analysis**: Understand patterns across your installation base
4. **Communication Center**: Prepare and send proactive customer messages

## Known Limitations

- Vendor B energy consumption readings appear to use different units (15,000 kWh vs 2-6 kWh for other vendors)
- Error codes are vendor-specific without complete documentation
- Some "connected" units have no telemetry data (likely communication failures)
- Reference number matching between files may have some inconsistencies

## Case Study Context

This prototype was built for the thermondo Service Cockpit case study to demonstrate:
- Proactive customer service using real-time equipment data
- Handling messy, multi-vendor data programmatically
- Prioritizing service actions based on predictive risk scoring
- Standardizing communications for scale

## Contact

For questions about this prototype or the case study, please refer to the accompanying documentation.