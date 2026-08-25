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

## Part 3: Read the data

### 1. How many heat pumps are actually in this dataset?

It depends on how you count:
- **Unique reference numbers in installation base**: 412 + 3 with missing reference number
- **Units with both installation and telemetry data**: 259
- **Units in installation base with no telemetry**: 156

### 2. Which units would you put on a technician's list for tomorrow morning?

**In general:** care_plus before care, priority critical, score above 100.

**Specific:** 3 units: TH-02398, TH-02312, TH-02322
- Because they are care_plus, critical, and only limited time available during tomorrow morning.

**Quiet sure because:**
- High alert rate
- care_plus service tier
- Overdue service

### 3. For each of these four questions, say whether the data answers it, partly answers it, or does not answer it, and why

**How efficiently is a unit running?**
Partly. Temperatures are only reported for parts of the units or even show wrong/not plausible values. No defrost status reported. Electrical kWh reporting is quite ok, thermal kWh reporting is not reliable. Flow temp is 14 or 15 degrees, quite cold, return temp 26, which does not make sense.

**Is a unit delivering hot water?**
Partly. About half of the units send this value as DHW_actual_c.

**Is a unit heating at all?**
Partly, for those with numbers reported.

**Is a fault recurring or a one off?**
Partly. A third of the data has errors recurring up to 30 times.

### 4. Which fault signals occur most often? Which of them would you keep off the front page of the cockpit, and what made you decide that?

Fault 6021 occurs 2,475 times. None of them should be on the front page as long as it is not recurring and the meaning is not known.

## Part 4: What you need from other people

### Which field or access is missing that would change the product most?

**The meaning of error codes.** This would change the product most because it would allow the cockpit to make meaningful decisions and show actionable information instead of cryptic vendor codes.

### Who has to deliver it, and what is your read on how hard that will be?

The vendors have to deliver it. Not too hard as it should be in the manuals—at least for the more often recurring faults.

### Write the actual message you would send in your first week to get it

Dear service team,

Can you help me finding the meaning behind error code 6021 from vendor B? I would like to evaluate if this is something our in development cockpit needs to take into consideration or not. If you cannot find it, drop me a short notice. I would follow up on this until Tuesday next week 10 AM.

Regards, Sebastian

