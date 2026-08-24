# Service Cockpit Case Study - Notes & Documentation

## Part 1: Decide what the cockpit is for

### What is this cockpit for, in one or two sentences, and who is the primary user?

The Service Cockpit is a proactive customer communication tool that identifies units likely to become critical situations, triggers maintenance reminders, and provides reassurance when systems are operating normally—transforming reactive service calls into preventive customer care. The primary user is Second Level Support and Service Technicians who need to reach out to customers before problems escalate, using real-time equipment data to prioritize communications.

### Which requirements do you take from the raw material above? List them in the order you would build them.

1. **Data unification and reference resolution** - Normalize inconsistent reference numbers, vendor names, and date formats across installation_base and telemetry_daily files to create a single coherent dataset for customer-specific monitoring.
2. **Critical situation identification** - Flag units with immediate issues like Vendor C's high alert rate (31.9%), low domestic hot water temperatures (<40°C), or frequent error codes for proactive customer outreach.
3. **Predictive risk scoring** - Identify units likely to become critical based on patterns like high compressor starts, temperature anomalies, or declining performance trends to enable preventive communication.
4. **Maintenance scheduling queue** - Generate prioritized lists for customers overdue for service (>6 months) or never serviced, with automatic reminder scheduling based on service tier and commissioning date.
5. **Customer communication templates** - Pre-written, personalized messages for different scenarios (critical alerts, maintenance reminders, normal operation reassurance) with unit-specific data automatically inserted.
6. **Unit status dashboard** - Simple view showing customer name, current equipment status, key metrics (temperatures, energy consumption), and recommended action for quick communication decisions.
7. **Communication history tracking** - Log all customer interactions, link communications to subsequent service visits, and track effectiveness in preventing emergency calls.

### What did you deliberately leave out, and why?

Left out deep technical investigation features like vendor-specific error code analysis and energy consumption distribution studies because the primary goal is customer communication, not root cause analysis. Also omitted advanced remote actions (restart, settings changes) as these require resolving current data quality challenges first. The focus is on using available data to identify which customers need attention now, not solving the underlying vendor data standardization issues—that can come later once the customer communication workflow is proven.

