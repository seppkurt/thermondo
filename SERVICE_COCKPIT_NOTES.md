# Service Cockpit Case Study - Notes & Documentation

## Part 1: Decide what the cockpit is for

### What is this cockpit for, in one or two sentences, and who is the primary user?

The Service Cockpit is a unified technical investigation dashboard that enables Second Level Support to identify systematic equipment patterns across different manufacturers, determine root causes of alerts and errors, and prepare evidence-based communications with vendor technical teams. The primary user is Second Level Support / Technical Service Engineers who need to move beyond individual unit troubleshooting to address widespread issues like Vendor C's 31.9% alert rate and Vendor B's systematic error code patterns.

### Which requirements do you take from the raw material above? List them in the order you would build them.

1. **Data unification and reference resolution** - Normalize inconsistent reference numbers, vendor names, and date formats across installation_base and telemetry_daily files to create a single coherent dataset.
2. **Vendor-specific error code timeline visualization** - Show error code trends by vendor over time to distinguish systematic issues (Vendor B's 6021 code pattern) from random faults.
3. **Alert severity matrix** - Cross-tabulation of vendor × alert type × frequency to quickly identify which vendor has which types of issues and prioritize investigations.
4. **Unit deep-dive with historical context** - Time-series charts for problem units compared to peer group averages to validate whether alerts represent real equipment issues versus threshold/sensor problems.
5. **Temperature relationship analysis** - Flow temp vs return temp vs outdoor temp scatter plots to determine if high-alert units have abnormal operating characteristics.
6. **Energy consumption distribution by vendor** - Comparative histograms to investigate Vendor B's 15,000 kWh vs Vendor A's 2-6 kWh measurement discrepancy.
7. **Data quality dashboard** - Monitor connected units with no data, missing fields by vendor, and data freshness to identify communication failures versus integration issues.

### What did you deliberately leave out, and why?

Left out the broader service planning features (morning list for technicians, customer communication tools, subcontractor access) because the analysis reveals that Second Level Support needs to first solve the systematic vendor-specific issues before the service organization can effectively use unit-level data for dispatch decisions. Also omitted advanced remote actions (restart, settings changes) as these require resolving the current data quality and interpretation challenges—particularly the unclear error codes and measurement unit differences between vendors. The cockpit must first establish what "normal" operation looks like for each manufacturer before enabling remote interventions.

