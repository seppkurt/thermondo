import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load both datasets
installation = pd.read_csv('docs/installation_base.csv')
telemetry = pd.read_csv('docs/telemetry_daily.csv')

print("=== COMBINED CLUSTER ANALYSIS ===\n")

# Normalize reference numbers in both files
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

print(f"Combined dataset: {len(combined)} units")
print(f"Units with telemetry data: {combined['reading_count'].notna().sum()}")
print(f"Units without telemetry data: {combined['reading_count'].isna().sum()}\n")

# === CLUSTER 1: HIGH ALERT RATE (Vendor C) ===
print("=== CLUSTER 1: HIGH ALERT RATE UNITS ===")
vendor_c_alerts = combined[(combined['vendor'] == 'C') & (combined['warn_count'] > 0)]
print(f"Vendor C units with alerts: {len(vendor_c_alerts)}")
if len(vendor_c_alerts) > 0:
    print(f"Average warning count: {vendor_c_alerts['warn_count'].mean():.1f}")
    print(f"Average error count: {vendor_c_alerts['error_count'].mean():.1f}")
    print(f"Service tier distribution:")
    print(vendor_c_alerts['service_tier'].value_counts())
    print(f"\nTop 10 units by warning count:")
    top_alerts = vendor_c_alerts.nlargest(10, 'warn_count')[['reference_number', 'customer_name', 'warn_count', 'error_count', 'service_tier', 'connectivity']]
    print(top_alerts.to_string(index=False))

# === CLUSTER 2: FREQUENT ERRORS ===
print("\n=== CLUSTER 2: FREQUENT ERROR UNITS ===")
high_error_units = combined[combined['error_count'] > 5].copy()
print(f"Units with >5 error occurrences: {len(high_error_units)}")
if len(high_error_units) > 0:
    print(f"By vendor:")
    print(high_error_units['vendor'].value_counts())
    print(f"\nTop 10 units by error count:")
    top_errors = high_error_units.nlargest(10, 'error_count')[['reference_number', 'customer_name', 'error_count', 'warn_count', 'vendor', 'service_tier']]
    print(top_errors.to_string(index=False))

# === CLUSTER 3: TEMPERATURE ANOMALIES ===
print("\n=== CLUSTER 3: TEMPERATURE ANOMALY UNITS ===")
# High flow temp or low DHW temp
temp_anomalies = combined[
    ((combined['avg_flow_temp'] > 35) | (combined['avg_flow_temp'].isna() & (combined['avg_return_temp'] > 29))) |
    ((combined['avg_dhw_temp'] < 40) & (combined['avg_dhw_temp'].notna())) |
    (combined['avg_dhw_temp'] == 0)
].copy()
print(f"Units with temperature anomalies: {len(temp_anomalies)}")
if len(temp_anomalies) > 0:
    print(f"By vendor:")
    print(temp_anomalies['vendor'].value_counts())
    print(f"\nSample of temperature anomaly units:")
    sample_temp = temp_anomalies[['reference_number', 'customer_name', 'avg_flow_temp', 'avg_return_temp', 'avg_dhw_temp', 'vendor']].head(10)
    print(sample_temp.to_string(index=False))

# === CLUSTER 4: HIGH ENERGY CONSUMPTION ===
print("\n=== CLUSTER 4: HIGH ENERGY CONSUMPTION UNITS ===")
# Units with unusually high electrical energy
high_energy = combined[combined['avg_electrical_kwh'] > 100].copy()
print(f"Units with avg electrical energy > 100 kWh: {len(high_energy)}")
if len(high_energy) > 0:
    print(f"By vendor:")
    print(high_energy['vendor'].value_counts())
    print(f"Average electrical energy: {high_energy['avg_electrical_kwh'].mean():.1f} kWh")
    print(f"\nTop 10 units by energy consumption:")
    top_energy = high_energy.nlargest(10, 'avg_electrical_kwh')[['reference_number', 'customer_name', 'avg_electrical_kwh', 'avg_thermal_kwh', 'vendor']]
    print(top_energy.to_string(index=False))

# === CLUSTER 5: CONNECTED BUT NO RECENT DATA ===
print("\n=== CLUSTER 5: CONNECTED BUT NO RECENT DATA ===")
connected_no_data = combined[
    (combined['connectivity'] == 'connected') & 
    (combined['reading_count'].isna() | (combined['reading_count'] < 10))
].copy()
print(f"Connected units with limited/no telemetry: {len(connected_no_data)}")
if len(connected_no_data) > 0:
    print(f"By vendor:")
    print(connected_no_data['vendor'].value_counts())
    print(f"By service tier:")
    print(connected_no_data['service_tier'].value_counts())
    print(f"\nSample units:")
    sample_no_data = connected_no_data[['reference_number', 'customer_name', 'connectivity', 'reading_count', 'vendor', 'service_tier']].head(10)
    print(sample_no_data.to_string(index=False))

# === CLUSTER 6: OVERDUE SERVICE ===
print("\n=== CLUSTER 6: OVERDUE SERVICE UNITS ===")
# Units with last service visit > 6 months ago
six_months_ago = datetime.now() - timedelta(days=180)
overdue_service = combined[
    (combined['parsed_last_visit'].notna()) & 
    (combined['parsed_last_visit'] < six_months_ago)
].copy()
print(f"Units with service visit > 6 months ago: {len(overdue_service)}")
if len(overdue_service) > 0:
    print(f"By vendor:")
    print(overdue_service['vendor'].value_counts())
    print(f"By service tier:")
    print(overdue_service['service_tier'].value_counts())
    print(f"\nMost overdue units:")
    most_overdue = overdue_service.nsmallest(10, 'parsed_last_visit')[['reference_number', 'customer_name', 'parsed_last_visit', 'service_tier', 'vendor']]
    most_overdue['days_since_service'] = (datetime.now() - most_overdue['parsed_last_visit']).dt.days
    print(most_overdue[['reference_number', 'customer_name', 'days_since_service', 'service_tier', 'vendor']].to_string(index=False))

# === CLUSTER 7: NEVER SERVICED ===
print("\n=== CLUSTER 7: NEVER SERVICED UNITS ===")
never_serviced = combined[
    (combined['parsed_last_visit'].isna()) & 
    (combined['parsed_commissioning'].notna())
].copy()
print(f"Units never serviced (but have commissioning date): {len(never_serviced)}")
if len(never_serviced) > 0:
    print(f"By vendor:")
    print(never_serviced['vendor'].value_counts())
    print(f"By service tier:")
    print(never_serviced['service_tier'].value_counts())
    # Calculate age
    never_serviced['days_since_commissioning'] = (datetime.now() - never_serviced['parsed_commissioning']).dt.days
    print(f"\nUnits commissioned > 1 year ago never serviced:")
    old_never_serviced = never_serviced[never_serviced['days_since_commissioning'] > 365]
    print(f"Count: {len(old_never_serviced)}")
    if len(old_never_serviced) > 0:
        print(old_never_serviced[['reference_number', 'customer_name', 'days_since_commissioning', 'service_tier', 'vendor']].head(10).to_string(index=False))

# === CLUSTER 8: HIGH COMPRESSOR STARTS ===
print("\n=== CLUSTER 8: HIGH COMPRESSOR START UNITS ===")
high_compressor = combined[
    (combined['avg_compressor_starts'] > 15) & 
    (combined['avg_compressor_starts'].notna())
].copy()
print(f"Units with avg compressor starts > 15: {len(high_compressor)}")
if len(high_compressor) > 0:
    print(f"By vendor:")
    print(high_compressor['vendor'].value_counts())
    print(f"Average compressor starts: {high_compressor['avg_compressor_starts'].mean():.1f}")
    print(f"\nTop 10 units by compressor starts:")
    top_compressor = high_compressor.nlargest(10, 'avg_compressor_starts')[['reference_number', 'customer_name', 'avg_compressor_starts', 'vendor', 'avg_flow_temp']]
    print(top_compressor.to_string(index=False))

# === SUMMARY RECOMMENDATIONS ===
print("\n=== SERVICE PRIORITY RECOMMENDATIONS ===")
print("Based on cluster analysis, here are the recommended priority groups:\n")

print("IMMEDIATE ATTENTION (Next 1-2 days):")
print("1. Vendor C units with high alert rates - potential widespread issues")
print("2. Units with 0°C DHW temperature - no hot water for customers")
print("3. Connected units with no data - potential communication failures\n")

print("HIGH PRIORITY (This week):")
print("4. Units with frequent error codes (>5 occurrences)")
print("5. High compressor start units - potential efficiency issues")
print("6. Temperature anomaly units - flow temp too high or return temp issues\n")

print("MEDIUM PRIORITY (Next 2 weeks):")
print("7. Overdue service units (>6 months since last visit)")
print("8. Never serviced units commissioned >1 year ago")
print("9. High energy consumption units - potential efficiency problems\n")

print("INVESTIGATION NEEDED:")
print("10. Connected but no data units - data quality issues")
print("11. Vendor-specific data discrepancies for root cause analysis")
