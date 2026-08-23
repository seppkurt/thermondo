import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

# Load the data
df = pd.read_csv('docs/installation_base.csv')

print("=== INSTALLATION BASE ANALYSIS ===\n")

# 1. Vendor representation
print("1. VENDOR REPRESENTATION:")
vendor_counts = df['vendor'].value_counts()
print(vendor_counts)
print(f"\nTotal unique vendors: {len(vendor_counts)}")
print(f"Total records: {len(df)}\n")

# 2. Connectivity ratio
print("2. CONNECTIVITY RATIO:")
connectivity_counts = df['connectivity'].value_counts()
print(connectivity_counts)
print(f"\nConnected ratio: {connectivity_counts.get('connected', 0) / len(df) * 100:.1f}%")
print(f"Not connected ratio: {connectivity_counts.get('not_connected', 0) / len(df) * 100:.1f}%")
print(f"Unknown ratio: {connectivity_counts.get('unknown', 0) / len(df) * 100:.1f}%\n")

# 3. Commission months analysis
print("3. COMMISSIONING MONTHS:")
# Clean and standardize dates
def parse_date(date_str):
    if pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    # Try different formats
    for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d.%m.%y']:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

df['parsed_commissioning'] = df['commissioning_date'].apply(parse_date)
valid_dates = df[df['parsed_commissioning'].notna()]

# Extract year-month
valid_dates['commission_year_month'] = valid_dates['parsed_commissioning'].dt.to_period('M')
monthly_counts = valid_dates['commission_year_month'].value_counts().sort_index()

print("Monthly commissioning counts:")
for period, count in monthly_counts.items():
    print(f"{period}: {count}")

print(f"\nTotal with valid commissioning dates: {len(valid_dates)} out of {len(df)}")

# Create a bar chart for commissioning months
plt.figure(figsize=(12, 6))
monthly_counts.plot(kind='bar')
plt.title('Heat Pump Commissioning by Month')
plt.xlabel('Month')
plt.ylabel('Number of Units Commissioned')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('commissioning_months.png', dpi=100, bbox_inches='tight')
print("\nChart saved as 'commissioning_months.png'")

# 4. Service tier representation
print("\n4. SERVICE TIER REPRESENTATION:")
service_tier_counts = df['service_tier'].value_counts()
print(service_tier_counts)
print(f"\nTotal unique service tiers: {len(service_tier_counts)}")

# Calculate percentages
for tier, count in service_tier_counts.items():
    print(f"{tier}: {count} ({count/len(df)*100:.1f}%)")

# 5. Service visits by months (DESC)
print("\n5. SERVICE VISITS BY MONTH (DESC):")
df['parsed_last_visit'] = df['last_service_visit'].apply(parse_date)
valid_visits = df[df['parsed_last_visit'].notna()]

valid_visits['visit_year_month'] = valid_visits['parsed_last_visit'].dt.to_period('M')
visit_monthly_counts = valid_visits['visit_year_month'].value_counts().sort_index(ascending=False)

print("Monthly service visit counts (most recent first):")
for period, count in visit_monthly_counts.items():
    print(f"{period}: {count}")

print(f"\nTotal with valid last service visit dates: {len(valid_visits)} out of {len(df)}")

# Additional interesting stats
print("\n=== ADDITIONAL INSIGHTS ===")
print(f"Records with missing reference numbers: {df['reference_number'].isna().sum()}")
print(f"Records with missing vendor: {df['vendor'].isna().sum()}")
print(f"Records with missing commissioning date: {df['commissioning_date'].isna().sum()}")
print(f"Records with missing connectivity: {df['connectivity'].isna().sum()}")
print(f"Records with missing service tier: {df['service_tier'].isna().sum()}")
print(f"Records with missing last service visit: {df['last_service_visit'].isna().sum()}")

# Reference number analysis
print("\n=== REFERENCE NUMBER ANALYSIS ===")
ref_numbers = df['reference_number'].dropna()
print(f"Total reference numbers: {len(ref_numbers)}")
print(f"Unique reference numbers: {ref_numbers.nunique()}")
print(f"Duplicate reference numbers: {len(ref_numbers) - ref_numbers.nunique()}")

# Show some examples of different formats
print("\nSample reference number formats:")
sample_refs = ref_numbers.head(10)
for ref in sample_refs:
    print(f"  '{ref}'")
