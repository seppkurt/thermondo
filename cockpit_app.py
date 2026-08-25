import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processor import load_and_clean_data, get_prepared_action, get_communication_template

# Page configuration
st.set_page_config(
    page_title="Service Cockpit",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .critical {
        color: #dc2626;
        font-weight: bold;
    }
    .high {
        color: #ea580c;
        font-weight: bold;
    }
    .medium {
        color: #ca8a04;
        font-weight: bold;
    }
    .normal {
        color: #16a34a;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    return load_and_clean_data()

# Main application
def main():
    # Header
    st.title("🔧 Service Cockpit")
    st.markdown("---")
    
    # Load data
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    
    # Calculate key metrics
    total_units = len(df)
    connected_units = df[df['connectivity'] == 'connected'].shape[0]
    critical_count = df[df['priority_level'] == 'Critical'].shape[0]
    high_count = df[df['priority_level'] == 'High'].shape[0]
    medium_count = df[df['priority_level'] == 'Medium'].shape[0]
    normal_count = df[df['priority_level'] == 'Normal'].shape[0]
    
    # Key metrics dashboard - First row
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Units", total_units)
    
    with col2:
        st.metric("Connected", f"{connected_units} ({connected_units/total_units*100:.0f}%)")
    
    # Key metrics dashboard - Second row (priority counts)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔴 Critical", critical_count, delta_color="inverse")
    
    with col2:
        st.metric("🟡 High", high_count)
    
    with col3:
        st.metric("🟠 Medium", medium_count)
    
    with col4:
        st.metric("🟢 Normal", normal_count)
    
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    view = st.sidebar.selectbox(
        "Select View",
        ["Priority Action List", "Unit Status Dashboard", "Trend Analysis", "Communication Center"]
    )
    
    # Filters in sidebar
    st.sidebar.title("Filters")
    
    vendor_filter = st.sidebar.multiselect(
        "Filter by Vendor",
        options=['All'] + sorted(df['vendor'].unique()),
        default=['All']
    )
    
    priority_filter = st.sidebar.multiselect(
        "Filter by Priority",
        options=['All', 'Critical', 'High', 'Medium', 'Normal'],
        default=['All']
    )
    
    connectivity_filter = st.sidebar.multiselect(
        "Filter by Connectivity",
        options=['All', 'connected', 'not_connected', 'unknown'],
        default=['All']
    )
    
    service_tier_filter = st.sidebar.multiselect(
        "Filter by Service Tier",
        options=['All'] + sorted(df['service_tier'].unique()),
        default=['All']
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if 'All' not in vendor_filter:
        filtered_df = filtered_df[filtered_df['vendor'].isin(vendor_filter)]
    
    if 'All' not in priority_filter:
        filtered_df = filtered_df[filtered_df['priority_level'].isin(priority_filter)]
    
    if 'All' not in connectivity_filter:
        filtered_df = filtered_df[filtered_df['connectivity'].isin(connectivity_filter)]
    
    if 'All' not in service_tier_filter:
        filtered_df = filtered_df[filtered_df['service_tier'].isin(service_tier_filter)]
    
    # Main content based on selected view
    if view == "Priority Action List":
        display_priority_list(filtered_df)
    elif view == "Unit Status Dashboard":
        display_unit_status(filtered_df)
    elif view == "Trend Analysis":
        display_trend_analysis(df)
    elif view == "Communication Center":
        display_communication_center(filtered_df)

def display_priority_list(df):
    """Display the priority action list"""
    st.header("🚨 Priority Action List")
    
    # Search functionality
    search_term = st.text_input("🔍 Search by customer name or reference number")
    
    # Sort by priority score
    df_sorted = df.sort_values('priority_score', ascending=False)
    
    # Apply search filter
    if search_term:
        df_sorted = df_sorted[
            df_sorted['customer_name'].str.contains(search_term, case=False, na=False) |
            df_sorted['reference_number'].str.contains(search_term, case=False, na=False)
        ]
    
    st.markdown("---")
    
    # Detailed table with actions
    st.subheader("Detailed Priority List")
    
    # Select columns to display
    display_columns = [
        'reference_number', 'customer_name', 'service_tier', 'vendor', 'priority_level', 'priority_score', 
        'priority_reasons', 'connectivity'
    ]
    
    # Rename columns for display
    column_renames = {
        'reference_number': 'Reference',
        'customer_name': 'Customer',
        'service_tier': 'Service Tier',
        'vendor': 'Vendor',
        'priority_level': 'Priority',
        'priority_score': 'Score',
        'priority_reasons': 'Reasons',
        'connectivity': 'Connectivity'
    }
    
    display_df = df_sorted[display_columns].copy()
    display_df.columns = [column_renames.get(col, col) for col in display_df.columns]
    
    # Add action column with colored rectangles
    def get_action_color(priority):
        if priority == 'Critical':
            return '🟥 Call'
        elif priority == 'High':
            return '🟧 Schedule'
        elif priority == 'Medium':
            return '🟨 Monitor'
        else:
            return '🟩 OK'
    
    display_df['Action'] = display_df['Priority'].apply(get_action_color)
    
    # Reorder columns to put Action first
    cols = display_df.columns.tolist()
    cols = ['Action'] + [col for col in cols if col != 'Action']
    display_df = display_df[cols]
    
    # Color coding for priority
    def color_priority(val):
        if val == 'Critical':
            return 'background-color: #fee2e2'
        elif val == 'High':
            return 'background-color: #ffedd5'
        elif val == 'Medium':
            return 'background-color: #fef9c3'
        else:
            return 'background-color: #dcfce7'
    
    # Color coding for service tier
    def color_service_tier(val):
        if val == 'care_plus':
            return 'background-color: #e0e7ff; color: #1e1b4b'
        elif val == 'care':
            return 'background-color: #f3e8ff; color: #581c87'
        elif val == 'optimize':
            return 'background-color: #dbeafe; color: #1e3a8a'
        else:  # free
            return 'background-color: #f1f5f9; color: #475569'
    
    # Color coding for connectivity
    def color_connectivity(val):
        if val == 'connected':
            return 'background-color: #dcfce7; color: #166534'
        elif val == 'not_connected':
            return 'background-color: #fee2e2; color: #991b1b'
        else:  # unknown
            return 'background-color: #fef9c3; color: #854d0e'
    
    styled_df = display_df.style.map(color_priority, subset=['Priority'])
    styled_df = styled_df.map(color_service_tier, subset=['Service Tier'])
    styled_df = styled_df.map(color_connectivity, subset=['Connectivity'])
    
    st.dataframe(styled_df, width='stretch', hide_index=True)
    
    # Customer selection for details
    st.markdown("---")
    st.subheader("Customer Details")
    
    if len(df_sorted) > 0:
        # Select customer to view details
        selected_customer = st.selectbox(
            "Select customer to view details (from table above)",
            options=df_sorted['customer_name'].tolist(),
            index=0 if len(df_sorted) > 0 else None
        )
        
        if selected_customer:
            customer_data = df_sorted[df_sorted['customer_name'] == selected_customer].iloc[0]
            
            # Show customer details
            with st.expander("🔍 Customer Details", expanded=True):
                st.markdown(f"**Customer:** {customer_data['customer_name']}")
                st.markdown(f"**Reference:** {customer_data['reference_number']}")
                st.markdown(f"**Vendor:** {customer_data['vendor']}")
                st.markdown(f"**Address:** {customer_data['street_address']}")
                st.markdown(f"**Phone:** {customer_data['contact_phone']}")
                st.markdown(f"**Postcode:** {customer_data['postcode_region']}")
                st.markdown(f"**Connectivity:** {customer_data['connectivity']}")
                st.markdown(f"**Service Tier:** {customer_data['service_tier']}")
                
                if pd.notna(customer_data['parsed_commissioning']):
                    st.markdown(f"**Commissioning Date:** {customer_data['parsed_commissioning'].strftime('%Y-%m-%d')}")
                
                if pd.notna(customer_data['parsed_last_visit']):
                    st.markdown(f"**Last Service Visit:** {customer_data['parsed_last_visit'].strftime('%Y-%m-%d')}")
                
                st.markdown("---")
                st.markdown("### Telemetry Data")
                
                if pd.notna(customer_data['avg_outdoor_temp']):
                    st.markdown(f"**Outdoor Temperature:** {customer_data['avg_outdoor_temp']:.1f}°C")
                
                if pd.notna(customer_data['avg_flow_temp']):
                    st.markdown(f"**Flow Temperature:** {customer_data['avg_flow_temp']:.1f}°C")
                
                if pd.notna(customer_data['avg_return_temp']):
                    st.markdown(f"**Return Temperature:** {customer_data['avg_return_temp']:.1f}°C")
                
                if pd.notna(customer_data['avg_dhw_temp']):
                    st.markdown(f"**DHW Temperature:** {customer_data['avg_dhw_temp']:.1f}°C")
                
                if pd.notna(customer_data['avg_electrical_kwh']):
                    st.markdown(f"**Electrical Energy:** {customer_data['avg_electrical_kwh']:.2f} kWh")
                
                if pd.notna(customer_data['avg_thermal_kwh']):
                    st.markdown(f"**Thermal Energy:** {customer_data['avg_thermal_kwh']:.2f} kWh")
                
                if pd.notna(customer_data['avg_compressor_starts']):
                    st.markdown(f"**Compressor Starts:** {customer_data['avg_compressor_starts']:.1f}")
                
                if pd.notna(customer_data['error_count']):
                    st.markdown(f"**Error Count:** {customer_data['error_count']:.0f}")
                
                if pd.notna(customer_data['warn_count']):
                    st.markdown(f"**Warning Count:** {customer_data['warn_count']:.0f}")
                
                if pd.notna(customer_data['reading_count']):
                    st.markdown(f"**Data Points:** {customer_data['reading_count']:.0f}")
            
            # Handle actions
            st.markdown("---")
            st.markdown("### Select Action")
            
            action = st.radio(
                "Choose action:",
                ["📞 Call Customer", "📅 Schedule Visit", "✉️ Send Monitor Email"]
            )
            
            if action == "📞 Call Customer":
                st.markdown("### 📞 Call Details")
                st.markdown(f"**Customer:** {customer_data['customer_name']}")
                st.markdown(f"**Reference:** {customer_data['reference_number']}")
                st.markdown(f"**Issue:** {customer_data['priority_reasons']}")
                st.markdown(f"**Vendor:** {customer_data['vendor']}")
                st.markdown(f"**Service Tier:** {customer_data['service_tier']}")
                st.success(f"Call initiated to {customer_data['customer_name']}")
                st.info("In production, this would integrate with your phone system")
            
            elif action == "📅 Schedule Visit":
                st.markdown("### 📅 Schedule Service Visit")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    visit_date = st.date_input("Select visit date")
                    visit_time = st.time_input("Select visit time")
                
                with col2:
                    st.markdown(f"**Customer:** {customer_data['customer_name']}")
                    st.markdown(f"**Reference:** {customer_data['reference_number']}")
                    st.markdown(f"**Issue:** {customer_data['priority_reasons']}")
                    st.markdown(f"**Vendor:** {customer_data['vendor']}")
                    st.markdown(f"**Service Tier:** {customer_data['service_tier']}")
                
                if st.button("📅 Confirm Schedule"):
                    st.success(f"Visit scheduled for {visit_date} at {visit_time}")
                    st.info("Call dialog would open with customer details")
            
            elif action == "✉️ Send Monitor Email":
                st.markdown("### ✉️ Send Monitoring Email")
                
                # Adapt email template based on priority
                if customer_data['priority_level'] == 'Critical':
                    email_template = f"""Subject: URGENT: Heat pump issue detected - Immediate attention required

Dear {customer_data['customer_name']},

Our monitoring system has detected a critical issue with your heat pump that requires immediate attention.

Issue: {customer_data['priority_reasons']}
Priority: CRITICAL
Reference: {customer_data['reference_number']}
Vendor: {customer_data['vendor']}

Please contact our service hotline immediately to schedule an emergency visit, or we will proactively reach out to you within 24 hours.

Your service team
"""
                elif customer_data['priority_level'] == 'High':
                    email_template = f"""Subject: Heat pump issue detected - Attention required this week

Dear {customer_data['customer_name']},

Our monitoring system has detected an issue with your heat pump that should be addressed soon.

Issue: {customer_data['priority_reasons']}
Priority: HIGH
Reference: {customer_data['reference_number']}
Vendor: {customer_data['vendor']}

We recommend scheduling a preventive maintenance visit this week to prevent potential problems. Would you like us to schedule this for you?

Your service team
"""
                elif customer_data['priority_level'] == 'Medium':
                    email_template = f"""Subject: Heat pump maintenance reminder

Dear {customer_data['customer_name']},

This is a friendly reminder that your heat pump is due for scheduled maintenance.

Issue: {customer_data['priority_reasons']}
Priority: MEDIUM
Reference: {customer_data['reference_number']}
Vendor: {customer_data['vendor']}

Regular maintenance helps ensure reliable operation and prevents unexpected issues. Would you like to schedule a visit?

Your service team
"""
                else:  # Normal
                    email_template = f"""Subject: Your heat pump status update

Dear {customer_data['customer_name']},

Our monitoring system shows your heat pump is operating normally.

Current status: All systems functioning correctly
Temperature readings: Within expected range
No alerts detected
Reference: {customer_data['reference_number']}
Vendor: {customer_data['vendor']}

No action is required at this time. We'll continue monitoring your system and will reach out if any issues arise.

Your service team
"""
                
                st.text_area("Email Template", email_template, height=200)
                
                if st.button("✉️ Send Email"):
                    st.success(f"Email sent to {customer_data['customer_name']}")
                    st.info("In production, this would integrate with your email system")

def display_unit_status(df):
    """Display unit status dashboard"""
    st.header("📊 Unit Status Dashboard")
    
    # Search functionality
    search_term = st.text_input("Search by customer name or reference number")
    
    if search_term:
        df = df[
            df['customer_name'].str.contains(search_term, case=False, na=False) |
            df['reference_number'].str.contains(search_term, case=False, na=False)
        ]
    
    # Unit status table
    display_columns = [
        'reference_number', 'customer_name', 'vendor', 'connectivity',
        'avg_flow_temp', 'avg_return_temp', 'avg_dhw_temp',
        'avg_electrical_kwh', 'avg_thermal_kwh',
        'error_count', 'warn_count', 'priority_level'
    ]
    
    # Filter out columns that might not exist
    available_columns = [col for col in display_columns if col in df.columns]
    
    if available_columns:
        display_df = df[available_columns].copy()
        
        # Rename columns
        column_renames = {
            'reference_number': 'Reference',
            'customer_name': 'Customer',
            'vendor': 'Vendor',
            'connectivity': 'Connectivity',
            'avg_flow_temp': 'Flow Temp (°C)',
            'avg_return_temp': 'Return Temp (°C)',
            'avg_dhw_temp': 'DHW Temp (°C)',
            'avg_electrical_kwh': 'Electrical (kWh)',
            'avg_thermal_kwh': 'Thermal (kWh)',
            'error_count': 'Errors',
            'warn_count': 'Warnings',
            'priority_level': 'Priority'
        }
        
        display_df.columns = [column_renames.get(col, col) for col in display_df.columns]
        
        st.dataframe(display_df, width='stretch')
    else:
        st.warning("No data available to display")

def display_trend_analysis(df):
    """Display trend analysis charts"""
    st.header("📈 Trend Analysis")
    
    # Priority distribution
    st.subheader("Priority Distribution")
    
    priority_counts = df['priority_level'].value_counts()
    
    fig_pie = px.pie(
        values=priority_counts.values,
        names=priority_counts.index,
        title="Units by Priority Level",
        color_discrete_map={
            'Critical': '#dc2626',
            'High': '#ea580c',
            'Medium': '#ca8a04',
            'Normal': '#16a34a'
        }
    )
    st.plotly_chart(fig_pie, use_container_width=False)
    
    # Vendor distribution
    st.subheader("Issues by Vendor")
    
    vendor_priority = df.groupby(['vendor', 'priority_level']).size().unstack(fill_value=0)
    
    fig_vendor = px.bar(
        vendor_priority,
        title="Priority Levels by Vendor",
        barmode='stack',
        color_discrete_map={
            'Critical': '#dc2626',
            'High': '#ea580c',
            'Medium': '#ca8a04',
            'Normal': '#16a34a'
        }
    )
    st.plotly_chart(fig_vendor, use_container_width=False)
    
    # Temperature analysis (for units with data)
    st.subheader("Temperature Analysis")
    
    temp_df = df[df['avg_flow_temp'].notna()].copy()
    
    if len(temp_df) > 0:
        fig_temp = px.scatter(
            temp_df,
            x='avg_flow_temp',
            y='avg_return_temp',
            color='vendor',
            size='priority_score',
            hover_data=['customer_name'],
            title="Flow vs Return Temperature (size = priority score)",
            labels={
                'avg_flow_temp': 'Flow Temperature (°C)',
                'avg_return_temp': 'Return Temperature (°C)'
            }
        )
        st.plotly_chart(fig_temp, use_container_width=False)
    else:
        st.info("No temperature data available for analysis")

def display_communication_center(df):
    """Display communication center with templates"""
    st.header("✉️ Communication Center")
    
    # Select customer
    if len(df) > 0:
        selected_customer = st.selectbox(
            "Select customer for communication",
            options=df['customer_name'].tolist(),
            index=0 if len(df) > 0 else None
        )
        
        if selected_customer:
            customer_data = df[df['customer_name'] == selected_customer].iloc[0]
            
            # Display customer info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Priority", customer_data['priority_level'])
            
            with col2:
                st.metric("Vendor", customer_data['vendor'])
            
            with col3:
                st.metric("Connectivity", customer_data['connectivity'])
            
            st.markdown("---")
            
            # Communication template
            st.subheader("Prepared Communication")
            
            template = get_communication_template(
                customer_data['priority_level'],
                customer_data['customer_name'],
                customer_data
            )
            
            st.text_area(
                "Message Template",
                template,
                height=200,
                key="message_template"
            )
            
            # Suggested actions
            st.subheader("Suggested Actions")
            
            actions = get_prepared_action(
                customer_data['priority_level'],
                customer_data['priority_reasons']
            )
            
            for action in actions:
                st.checkbox(action, key=f"action_{action}")
            
            # Send button
            if st.button("📤 Send Communication"):
                st.success(f"Communication prepared for {selected_customer}")
                st.info("In production, this would integrate with email/SMS systems")
    else:
        st.warning("No customers available for communication")

if __name__ == "__main__":
    main()