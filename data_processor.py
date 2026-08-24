import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_and_clean_data():
    """Load and clean the installation and telemetry data"""
    
    # Load raw data
    installation = pd.read_csv('docs/installation_base.csv')
    telemetry = pd.read_csv('docs/telemetry_daily.csv')
    
    # Normalize reference numbers
    def normalize_reference(ref):
        if pd.isna(ref):
            return None
        ref = str(ref).strip().upper()
        # Remove common prefixes and normalize
        ref = ref.replace('TH-', '').replace('TH', '')
        # Handle suffixes like -1, -2
        if '-' in ref:
            ref = ref.split('-')[0]
        return ref.zfill(5)  # Pad to 5 digits for consistency

    installation['normalized_ref'] = installation['reference_number'].apply(normalize_reference)
    telemetry['normalized_ref'] = telemetry['reference_number'].apply(normalize_reference)
    
    # Normalize vendor names
    def normalize_vendor(vendor):
        if pd.isna(vendor):
            return 'Unknown'
        vendor = str(vendor).upper().strip()
        if 'A' in vendor and 'B' not in vendor and 'C' not in vendor:
            return 'A'
        elif 'B' in vendor:
            return 'B'
        elif 'C' in vendor:
            return 'C'
        return vendor

    installation['normalized_vendor'] = installation['vendor'].apply(normalize_vendor)
    telemetry['normalized_vendor'] = telemetry['vendor'].apply(normalize_vendor)
    
    # Parse dates
    def parse_date(date_str):
        if pd.isna(date_str):
            return None
        date_str = str(date_str).strip()
        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d.%m.%y']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    installation['parsed_commissioning'] = installation['commissioning_date'].apply(parse_date)
    installation['parsed_last_visit'] = installation['last_service_visit'].apply(parse_date)
    telemetry['parsed_reading_date'] = pd.to_datetime(telemetry['reading_date'])
    
    # Calculate recent telemetry metrics (last 7 days)
    recent_date = telemetry['parsed_reading_date'].max() - timedelta(days=7)
    recent_telemetry = telemetry[telemetry['parsed_reading_date'] >= recent_date]
    
    # Aggregate telemetry by unit
    telemetry_agg = telemetry.groupby('normalized_ref').agg({
        'normalized_vendor': 'first',
        'outdoor_temp_c': 'mean',
        'flow_temp_c': 'mean',
        'return_temp_c': 'mean',
        'dhw_actual_c': 'mean',
        'electrical_energy_kwh': 'mean',
        'thermal_energy_kwh': 'mean',
        'compressor_starts': 'mean',
        'error_code_raw': lambda x: x.notna().sum(),
        'status_raw': lambda x: x.str.lower().str.contains('warn', na=False).sum(),
        'parsed_reading_date': 'count'
    }).reset_index()

    telemetry_agg.columns = ['normalized_ref', 'telemetry_vendor', 'avg_outdoor_temp', 'avg_flow_temp', 
                            'avg_return_temp', 'avg_dhw_temp', 'avg_electrical_kwh', 
                            'avg_thermal_kwh', 'avg_compressor_starts', 'error_count',
                            'warn_count', 'reading_count']
    
    # Join datasets
    combined = installation.merge(telemetry_agg, on='normalized_ref', how='left')
    
    # Use installation vendor as primary, fallback to telemetry vendor
    combined['vendor'] = combined['normalized_vendor'].combine_first(combined['telemetry_vendor'])
    
    # Calculate priority scores
    combined = calculate_priority_scores(combined)
    
    return combined

def calculate_priority_scores(df):
    """Calculate priority scores for each unit based on risk factors"""
    
    now = datetime.now()
    
    def get_priority_score(row):
        score = 0
        reasons = []
        priority = "Normal"
        
        # Critical issues
        if row['vendor'] == 'C' and pd.notna(row['warn_count']) and row['warn_count'] > 15:
            score += 50
            reasons.append("High alert rate (Vendor C)")
        
        if pd.notna(row['avg_dhw_temp']) and row['avg_dhw_temp'] < 40:
            score += 40
            reasons.append("Low hot water temperature")
        
        if pd.notna(row['error_count']) and row['error_count'] > 5:
            score += 30
            reasons.append("Frequent error codes")
        
        # Maintenance needs
        if pd.notna(row['parsed_last_visit']):
            days_since_service = (now - row['parsed_last_visit']).days
            if days_since_service > 365:
                score += 20
                reasons.append(f"Overdue service ({days_since_service} days)")
            elif days_since_service > 180:
                score += 10
                reasons.append(f"Service due ({days_since_service} days)")
        else:
            # Never serviced
            if pd.notna(row['parsed_commissioning']):
                days_since_commissioning = (now - row['parsed_commissioning']).days
                if days_since_commissioning > 365:
                    score += 25
                    reasons.append("Never serviced (>1 year)")
        
        # Connected but no data
        if row['connectivity'] == 'connected' and (pd.isna(row['reading_count']) or row['reading_count'] < 10):
            score += 15
            reasons.append("Connected but no recent data")
        
        # Determine priority level
        if score >= 60:
            priority = "Critical"
        elif score >= 40:
            priority = "High"
        elif score >= 20:
            priority = "Medium"
        else:
            priority = "Normal"
        
        return pd.Series([score, ', '.join(reasons) if reasons else 'Operating normally', priority])
    
    df[['priority_score', 'priority_reasons', 'priority_level']] = df.apply(get_priority_score, axis=1)
    
    return df

def get_prepared_action(priority_level, priority_reasons):
    """Get suggested action based on priority level and reasons"""
    
    actions = {
        "Critical": [
            "Call customer immediately - potential system failure",
            "Schedule emergency technician visit", 
            "Send critical alert notification"
        ],
        "High": [
            "Schedule preventive maintenance visit this week",
            "Send warning notification with monitoring data",
            "Customer outreach recommended"
        ],
        "Medium": [
            "Add to maintenance scheduling queue",
            "Send maintenance reminder",
            "Monitor for 7 days"
        ],
        "Normal": [
            "Send normal operation reassurance",
            "Add to routine maintenance schedule", 
            "No action needed"
        ]
    }
    
    return actions.get(priority_level, ["Review status"])

def get_communication_template(priority_level, customer_name, unit_data):
    """Generate communication template based on priority"""
    
    templates = {
        "Critical": f"""Dear {customer_name},

Our monitoring system has detected a critical issue with your heat pump that requires immediate attention.

Issue: {unit_data.get('priority_reasons', 'System alert')}

Please contact our service hotline immediately to schedule an emergency visit, or we will proactively reach out to you within 24 hours.

Your service team""",
        
        "High": f"""Dear {customer_name},

Our monitoring system has detected an issue with your heat pump that should be addressed soon.

Issue: {unit_data.get('priority_reasons', 'System warning')}

We recommend scheduling a preventive maintenance visit this week to prevent potential problems. Would you like us to schedule this for you?

Your service team""",
        
        "Medium": f"""Dear {customer_name},

This is a friendly reminder that your heat pump is due for scheduled maintenance.

{unit_data.get('priority_reasons', 'Routine maintenance due')}

Regular maintenance helps ensure reliable operation and prevents unexpected issues. Would you like to schedule a visit?

Your service team""",
        
        "Normal": f"""Dear {customer_name},

Good news! Our monitoring shows your heat pump is operating within normal parameters.

Current status: All systems functioning normally
Temperature readings: Within expected range
No alerts detected

No action is required at this time. We'll continue monitoring your system and will reach out if any issues arise.

Your service team"""
    }
    
    return templates.get(priority_level, "Please review your system status.")
