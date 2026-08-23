import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('docs/telemetry_daily.csv')

print("=== TELEMETRY DAILY ANALYSIS ===\n")

# Basic info
print(f"Total records: {len(df)}")
print(f"Date range: {df['reading_date'].min()} to {df['reading_date'].max()}")
print(f"Unique units: {df['reference_number'].nunique()}\n")

# 1. Alert status analysis by manufacturer
print("1. ALERT STATUS BY MANUFACTURER:")
# Check status_raw values
status_values = df['status_raw'].value_counts()
print("Status value distribution:")
print(status_values)
print()

# Normalize vendor names for analysis
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

df['normalized_vendor'] = df['vendor'].apply(normalize_vendor)

# Count alerts by vendor (assuming status contains 'warn', 'error', 'alert', etc.)
alert_keywords = ['warn', 'error', 'alert', 'fault', 'critical', 'emergency']
df['is_alert'] = df['status_raw'].str.lower().str.contains('|'.join(alert_keywords), na=False)

alert_by_vendor = df[df['is_alert']].groupby('normalized_vendor').size()
total_by_vendor = df.groupby('normalized_vendor').size()

print("Alerts by manufacturer:")
for vendor in ['A', 'B', 'C']:
    total = total_by_vendor.get(vendor, 0)
    alerts = alert_by_vendor.get(vendor, 0)
    alert_rate = (alerts / total * 100) if total > 0 else 0
    print(f"Vendor {vendor}: {alerts} alerts out of {total} records ({alert_rate:.1f}%)")

print(f"\nTotal alerts: {df['is_alert'].sum()} out of {len(df)} records ({df['is_alert'].sum()/len(df)*100:.1f}%)\n")

# 2. Temperature outliers analysis
print("2. TEMPERATURE OUTLIERS ANALYSIS:")

temp_columns = ['outdoor_temp_c', 'flow_temp_c', 'return_temp_c', 'dhw_actual_c']

for col in temp_columns:
    # Filter out -999 (missing values) and NaN
    valid_data = df[(df[col].notna()) & (df[col] != -999)][col]
    
    if len(valid_data) > 0:
        print(f"\n{col}:")
        print(f"  Valid records: {len(valid_data)} out of {len(df)}")
        print(f"  Min: {valid_data.min():.1f}°C")
        print(f"  Max: {valid_data.max():.1f}°C")
        print(f"  Mean: {valid_data.mean():.1f}°C")
        print(f"  Median: {valid_data.median():.1f}°C")
        print(f"  Std: {valid_data.std():.1f}°C")
        
        # IQR method for outliers
        Q1 = valid_data.quantile(0.25)
        Q3 = valid_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = valid_data[(valid_data < lower_bound) | (valid_data > upper_bound)]
        print(f"  Outliers (IQR method): {len(outliers)} values ({len(outliers)/len(valid_data)*100:.1f}%)")
        
        if len(outliers) > 0:
            print(f"  Outlier range: {outliers.min():.1f}°C to {outliers.max():.1f}°C")
            print(f"  Sample outliers: {outliers.head(5).tolist()}")

# 3. Energy outliers analysis
print("\n3. ENERGY OUTLIERS ANALYSIS:")

energy_columns = ['electrical_energy_kwh', 'thermal_energy_kwh']

for col in energy_columns:
    # Filter out NaN and invalid values
    valid_data = df[(df[col].notna()) & (df[col] != -999)][col]
    
    if len(valid_data) > 0:
        print(f"\n{col}:")
        print(f"  Valid records: {len(valid_data)} out of {len(df)}")
        print(f"  Min: {valid_data.min():.2f} kWh")
        print(f"  Max: {valid_data.max():.2f} kWh")
        print(f"  Mean: {valid_data.mean():.2f} kWh")
        print(f"  Median: {valid_data.median():.2f} kWh")
        
        # Check for extreme values
        if valid_data.max() > 10000:
            print(f"  WARNING: Very high maximum value detected!")
            
        # IQR method for outliers
        Q1 = valid_data.quantile(0.25)
        Q3 = valid_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = valid_data[(valid_data < lower_bound) | (valid_data > upper_bound)]
        print(f"  Outliers (IQR method): {len(outliers)} values ({len(outliers)/len(valid_data)*100:.1f}%)")
        
        if len(outliers) > 0:
            print(f"  Outlier range: {outliers.min():.2f} kWh to {outliers.max():.2f} kWh")

# 4. Error code analysis
print("\n4. ERROR CODE ANALYSIS:")
error_codes = df[df['error_code_raw'].notna() & (df['error_code_raw'] != '')]['error_code_raw']
print(f"Total records with error codes: {len(error_codes)}")
print(f"Unique error codes: {error_codes.nunique()}")
print("\nMost common error codes:")
print(error_codes.value_counts().head(10))

# 5. Data completeness by vendor
print("\n5. DATA COMPLETENESS BY VENDOR:")
for vendor in ['A', 'B', 'C']:
    vendor_data = df[df['normalized_vendor'] == vendor]
    print(f"\nVendor {vendor} ({len(vendor_data)} records):")
    
    for col in temp_columns + energy_columns:
        valid_count = vendor_data[(vendor_data[col].notna()) & (vendor_data[col] != -999)][col].count()
        completeness = (valid_count / len(vendor_data)) * 100
        print(f"  {col}: {valid_count}/{len(vendor_data)} ({completeness:.1f}%)")

# 6. Time series analysis - daily patterns
print("\n6. DAILY PATTERNS:")
df['reading_date'] = pd.to_datetime(df['reading_date'])
daily_records = df.groupby('reading_date').size()
print(f"Records per day - Min: {daily_records.min()}, Max: {daily_records.max()}, Mean: {daily_records.mean():.1f}")

# Check for missing days
date_range = pd.date_range(start=df['reading_date'].min(), end=df['reading_date'].max())
missing_days = date_range.difference(df['reading_date'].unique())
print(f"Missing days in date range: {len(missing_days)}")

# 7. Compressor starts and defrost cycles
print("\n7. OPERATIONAL METRICS:")
operational_cols = ['compressor_starts', 'defrost_cycles']
for col in operational_cols:
    valid_data = df[df[col].notna()][col]
    if len(valid_data) > 0:
        print(f"\n{col}:")
        print(f"  Valid records: {len(valid_data)}")
        print(f"  Min: {valid_data.min()}")
        print(f"  Max: {valid_data.max()}")
        print(f"  Mean: {valid_data.mean():.1f}")
