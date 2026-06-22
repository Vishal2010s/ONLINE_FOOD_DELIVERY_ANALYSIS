import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Food Delivery Analytics Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 18px;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 32px;
        font-weight: bold;
        margin: 5px 0;
    }
    .kpi-label {
        font-size: 14px;
        opacity: 0.9;
    }
    .metric-card-1 { background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); }
    .metric-card-2 { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .metric-card-3 { background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%); }
    .metric-card-4 { background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); }
    .metric-card-5 { background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%); }
    .metric-card-6 { background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%); }
    .metric-card-7 { background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); }
    .query-section {
        background-color: #252324;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        border-left: 5px solid #FF6B35;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #252324;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-size: 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6B35 !important;
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('FOOD_DELIVERY_ANALYSIS_final.csv')
    return df

df = load_data()

# ============ SIDEBAR FILTERS ============
st.sidebar.markdown("## Filters")

# City filter
cities = ['All'] + sorted([x for x in df['City'].dropna().unique() if str(x) != 'nan'])
selected_city = st.sidebar.selectbox("Select City", cities)

# Cuisine filter
cuisines = ['All'] + sorted([x for x in df['Cuisine_Type'].dropna().unique() if str(x) != 'nan'])
selected_cuisine = st.sidebar.selectbox("Select Cuisine", cuisines)

# Month filter
months = ['All'] + sorted([x for x in df['Order_month'].dropna().unique() if str(x) != 'nan'])
selected_month = st.sidebar.selectbox("Select Month", months)

# Payment Mode filter
payments = ['All'] + sorted([x for x in df['Payment_Mode'].dropna().unique() if str(x) != 'nan'])
selected_payment = st.sidebar.selectbox("Payment Mode", payments)

# Apply filters
filtered_df = df.copy()
if selected_city != 'All':
    filtered_df = filtered_df[filtered_df['City'] == selected_city]
if selected_cuisine != 'All':
    filtered_df = filtered_df[filtered_df['Cuisine_Type'] == selected_cuisine]
if selected_month != 'All':
    filtered_df = filtered_df[filtered_df['Order_month'] == selected_month]
if selected_payment != 'All':
    filtered_df = filtered_df[filtered_df['Payment_Mode'] == selected_payment]

# ============ SIDEBAR ANALYTICS DROPDOWN ============
st.sidebar.markdown("---")
st.sidebar.markdown("## Food Delivery & Sales Analytics")

query_options = [
    "Select a query...",
    "1. Top Spending Customers by Gender",
    "2. Age Group vs Order Value",
    "3. Weekend vs Weekday Order Patterns",
    "4. Monthly Revenue Trends",
    "5. Impact of Discounts on Profit",
    "6. High-Revenue Cities & Cuisine Intensity",
    "7. Average Delivery Time by City",
    "8. Distance vs Delivery Delay",
    "9. Delivery Rating vs Delivery Time",
    "10. Top-Rated Restaurants",
    "11. Cancellation Rate by Restaurant",
    "12. Cuisine-wise Performance",
    "13. Peak Hour Demand Analysis",
    "14. Payment Mode Preferences",
    "15. Cancellation Reason Analysis"
]
selected_query = st.sidebar.selectbox("Select Analysis Query", query_options)

# ============ HEADER ============
st.markdown('<div class="main-header">Food Delivery Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Analyzing {len(filtered_df):,} orders | Data Period: Jan 2024 - Dec 2024</div>', unsafe_allow_html=True)

# ============ KPI CARDS ============
total_orders = len(filtered_df)
total_revenue = filtered_df['Final_Amount'].sum()
avg_order_value = filtered_df['Order_Value'].mean()
avg_delivery_time = filtered_df['Delivery_Time_Min'].mean()
cancellation_rate = (filtered_df[filtered_df['Order_Status'] == 'Cancelled'].shape[0] / total_orders) * 100 if total_orders > 0 else 0
avg_delivery_rating = filtered_df['Delivery_Rating'].mean()
avg_profit_margin = filtered_df['Profit_Margin_Percentage'].mean()

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    st.markdown(f'<div class="kpi-card metric-card-1"><div class="kpi-label">Total Orders</div><div class="kpi-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card metric-card-2"><div class="kpi-label">Total Revenue</div><div class="kpi-value">Rs.{total_revenue/1e6:.2f}M</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card metric-card-3"><div class="kpi-label">Avg Order Value</div><div class="kpi-value">Rs.{avg_order_value:,.0f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="kpi-card metric-card-4"><div class="kpi-label">Avg Delivery Time</div><div class="kpi-value">{avg_delivery_time:.0f}m</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="kpi-card metric-card-5"><div class="kpi-label">Cancellation Rate</div><div class="kpi-value">{cancellation_rate:.1f}%</div></div>', unsafe_allow_html=True)
with col6:
    st.markdown(f'<div class="kpi-card metric-card-6"><div class="kpi-label">Avg Delivery Rating</div><div class="kpi-value">{avg_delivery_rating:.2f}</div></div>', unsafe_allow_html=True)
with col7:
    st.markdown(f'<div class="kpi-card metric-card-7"><div class="kpi-label">Profit Margin %</div><div class="kpi-value">{avg_profit_margin:.1f}%</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============ TABS ============
tab1, tab2 = st.tabs(["📊 Main Dashboard", "🔍 Food Delivery & Sales Analytics"])

# ==================== TAB 1: MAIN DASHBOARD ====================
with tab1:
    # CHARTS ROW 1
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Monthly Order Trends")
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly = filtered_df.groupby('Order_month').agg({
            'Order_ID': 'count',
            'Final_Amount': 'sum'
        }).reset_index()
        monthly['Order_month'] = pd.Categorical(monthly['Order_month'], categories=month_order, ordered=True)
        monthly = monthly.sort_values('Order_month', ascending=True)
        monthly.columns = ['Month', 'Orders', 'Revenue']

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=monthly['Month'], y=monthly['Orders'], name='Orders', 
                   marker_color='#FF6B35', opacity=0.8),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=monthly['Month'], y=monthly['Revenue']/1000, name='Revenue (K)', 
                       mode='lines+markers', line=dict(color='#11998e', width=3)),
            secondary_y=True
        )
        fig.update_layout(
            height=400,
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        fig.update_xaxes(title_text="Month", dtick=1)
        fig.update_yaxes(title_text="Number of Orders", secondary_y=False)
        fig.update_yaxes(title_text="Revenue (Rs. Thousands)", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### City-wise Performance")
        city_data = filtered_df.groupby('City').agg({
            'Order_ID': 'count',
            'Final_Amount': 'sum',
            'Profit_Margin_Percentage': 'mean'
        }).reset_index()
        city_data.columns = ['City', 'Orders', 'Revenue', 'Profit_Margin']

        fig = px.scatter(city_data, x='Orders', y='Revenue', size='Profit_Margin',
                         color='City', hover_name='City',
                         size_max=60,
                         color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(height=400, template='plotly_white',
                          margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # CHARTS ROW 2
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown("### Cuisine Type Analysis")
        cuisine_data = filtered_df.groupby('Cuisine_Type').agg({
            'Order_ID': 'count',
            'Delivery_Rating': 'mean',
            'Profit_Margin_Percentage': 'mean'
        }).reset_index()
        cuisine_data.columns = ['Cuisine', 'Orders', 'Avg_Rating', 'Profit_Margin']

        fig = px.bar(cuisine_data, x='Cuisine', y='Orders', 
                     color='Avg_Rating', color_continuous_scale='RdYlGn',
                     text='Orders')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, template='plotly_white',
                          margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col_right2:
        st.markdown("### Peak vs Non-Peak Hour Performance")
        peak_data = filtered_df.groupby('Peak_Hour_Indicator').agg({
            'Order_ID': 'count',
            'Delivery_Time_Min': 'mean',
            'Delivery_Rating': 'mean',
            'Profit_Margin_Percentage': 'mean'
        }).reset_index()
        peak_data.columns = ['Peak_Hour', 'Orders', 'Avg_Delivery_Time', 'Avg_Rating', 'Profit_Margin']

        fig = go.Figure(data=[
            go.Bar(name='Orders', x=peak_data['Peak_Hour'], y=peak_data['Orders'], 
                   marker_color=['#FF6B35', '#11998e']),
        ])
        fig.update_layout(height=400, template='plotly_white',
                          margin=dict(l=20, r=20, t=50, b=20),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # CHARTS ROW 3
    col_left3, col_right3 = st.columns(2)

    with col_left3:
        st.markdown("### Delivery Performance Distribution")
        perf_data = filtered_df['Delivery_Performance_Category'].value_counts().reset_index()
        perf_data.columns = ['Category', 'Count']

        colors = ['#11998e', '#F7931E', '#FF416C']
        fig = px.pie(perf_data, values='Count', names='Category', 
                     color_discrete_sequence=colors,
                     hole=0.4)
        fig.update_layout(height=400, template='plotly_white',
                          margin=dict(l=20, r=20, t=50, b=20))
        fig.update_traces(textinfo='percent+label', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col_right3:
        st.markdown("### Payment Mode Analysis")
        payment_data = filtered_df.groupby('Payment_Mode').agg({
            'Order_ID': 'count',
            'Final_Amount': 'sum'
        }).reset_index()
        payment_data.columns = ['Payment_Mode', 'Orders', 'Revenue']

        fig = px.bar(payment_data, x='Payment_Mode', y='Orders',
                     color='Revenue', color_continuous_scale='Viridis',
                     text='Orders')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, template='plotly_white',
                          margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # BOTTOM SECTION
    st.markdown("---")
    st.markdown("### Detailed Metrics Table")

    detailed = filtered_df.groupby(['City', 'Cuisine_Type']).agg({
        'Order_ID': 'count',
        'Final_Amount': 'sum',
        'Order_Value': 'mean',
        'Delivery_Time_Min': 'mean',
        'Delivery_Rating': 'mean',
        'Profit_Margin_Percentage': 'mean'
    }).reset_index()
    detailed.columns = ['City', 'Cuisine', 'Orders', 'Revenue', 'Avg_Order_Value', 'Avg_Delivery_Time', 'Avg_Rating', 'Profit_Margin_Pct']

    
    st.dataframe(detailed.style.format({
        'Revenue': 'Rs.{:,.0f}', 
        'Avg_Order_Value': 'Rs.{:.2f}', 
        'Avg_Delivery_Time': '{:.1f}m', 
        'Avg_Rating': '{:.2f}', 
        'Profit_Margin_Pct': '{:.1f}%', 
    }),
    use_container_width=True, height=400)


# ==================== TAB 2: QUERY ANALYTICS ====================
with tab2:
    if selected_query == "Select a query...":
        st.info("👈 Please select a query from the sidebar dropdown under 'Food Delivery & Sales Analytics' to view analysis results.")
        st.markdown("---")
        st.markdown("### Available Queries:")
        for q in query_options[1:]:
            st.markdown(f"- {q}")
    else:
        st.markdown(f'<div class="query-section"><h3>📊 {selected_query}</h3></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Query 1: Top Spending Customers by Gender
        if selected_query == "1. Top Spending Customers by Gender":
            df_q = filtered_df.groupby('Customer_Gender')['Final_Amount'].sum().reset_index()
            df_q.columns = ['Customer_Gender', 'Total_Amount']
            df_q = df_q.sort_values('Total_Amount', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Total_Amount': '₹{:,.2f}'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='Customer_Gender', y='Total_Amount', text='Total_Amount',
                            title='Top Spending Customers by Gender', color='Customer_Gender',
                            color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 2: Age Group vs Order Value
        elif selected_query == "2. Age Group vs Order Value":
            df_q = filtered_df.groupby('Customer_Age_Group')['Order_Value'].sum().reset_index()
            df_q.columns = ['Customer_Age_Group', 'Total_Amount']
            df_q = df_q.sort_values('Total_Amount', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Total_Amount': '₹{:,.0f}'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.pie(df_q, values='Total_Amount', names='Customer_Age_Group',
                            title='Age Group vs Order Value', hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(textinfo='percent+label', textposition='outside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 3: Weekend vs Weekday Order Patterns
        elif selected_query == "3. Weekend vs Weekday Order Patterns":
            df_q = filtered_df.groupby(['Order_Day', 'Cuisine_Type'])['Final_Amount'].sum().reset_index()
            df_q.columns = ['Order_Day', 'Cuisine_Type', 'Total_Amount']
            df_q = df_q.sort_values('Total_Amount', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Total_Amount': '₹{:,.0f}'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='Order_Day', y='Total_Amount', color='Cuisine_Type',
                            barmode='relative', title='Weekend vs Weekday Order Patterns',
                            text='Total_Amount', color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(texttemplate='₹%{text:.3s}', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 4: Monthly Revenue Trends
        elif selected_query == "4. Monthly Revenue Trends":
            df_q = filtered_df.groupby('Order_month')['Final_Amount'].sum().reset_index()
            df_q.columns = ['Order_month', 'Total_Amount']
            month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            df_q['Order_month'] = pd.Categorical(df_q['Order_month'], categories=month_order, ordered=True)
            df_q = df_q.sort_values('Order_month', ascending=True)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                display_df = df_q[['Order_month', 'Total_Amount']].copy()
                display_df.columns = ['Order_month', 'Total_Amount']
                st.dataframe(display_df.style.format({'Total_Amount': '₹{:,.0f}'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.line(df_q, x='Order_month', y='Total_Amount', markers=True,
                             title='Monthly Revenue Trend', text='Total_Amount',
                             labels={'Order_month': 'Month', 'Total_Amount': 'Total Revenue'})
                fig.update_traces(texttemplate='₹%{text:,.4s}', textposition='top center')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 5: Impact of Discounts on Profit
        elif selected_query == "5. Impact of Discounts on Profit":
            df_q = filtered_df.groupby('Discount_Applied')['Profit_Margin_Percentage'].mean().reset_index()
            df_q.columns = ['Discount_Applied', 'Avg_Profit_Margin_Percentage']
            df_q = df_q.sort_values('Discount_Applied')

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Avg_Profit_Margin_Percentage': '{:.2f}%'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.line(df_q, x='Discount_Applied', y='Avg_Profit_Margin_Percentage',
                             markers=True, title='Impact of Discounts on Profit',
                             labels={'Discount_Applied': 'Discount', 'Avg_Profit_Margin_Percentage': 'Profit Margin %'})
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 6: High-Revenue Cities & Cuisine Intensity
        elif selected_query == "6. High-Revenue Cities & Cuisine Intensity":
            df_city = filtered_df.groupby('City')['Final_Amount'].sum().reset_index()
            df_city.columns = ['City', 'Total_Amount']
            df_city = df_city.sort_values('Total_Amount', ascending=False)

            df_city_cus = filtered_df.groupby(['City', 'Cuisine_Type'])['Final_Amount'].sum().reset_index()
            df_city_cus.columns = ['City', 'Cuisine_Type', 'Total_Amount']
            df_city_cus = df_city_cus.sort_values('Total_Amount', ascending=False)

            st.markdown("#### City-wise Revenue")
            col_t1, col_c1 = st.columns(2)
            with col_t1:
                st.dataframe(df_city.style.format({'Total_Amount': '₹{:,.0f}'}), use_container_width=True)
            with col_c1:
                fig = px.bar(df_city, x='City', y='Total_Amount', title='City-wise Revenue', 
                            text='Total_Amount', color='City', color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(texttemplate='₹%{text:.4s}', textposition='inside')
                fig.update_layout(height=400, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### Revenue Intensity: City vs. Cuisine Type")
            col_t2, col_c2 = st.columns(2)
            with col_t2:
                st.dataframe(df_city_cus.style.format({'Total_Amount': '₹{:,.0f}'}), use_container_width=True)
            with col_c2:
                fig = px.bar(df_city_cus, x='City', y='Total_Amount', color='Cuisine_Type',
                            barmode='group', title='Revenue Intensity: City vs. Cuisine Type',
                            text='Total_Amount', color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(texttemplate='₹%{text:.3s}', textposition='inside')
                fig.update_layout(height=400, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 7: Average Delivery Time by City
        elif selected_query == "7. Average Delivery Time by City":
            df_q = filtered_df.groupby('City')['Delivery_Time_Min'].mean().reset_index()
            df_q.columns = ['City', 'Avg_Delivery_Time_Min']
            df_q = df_q.sort_values('Avg_Delivery_Time_Min', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Avg_Delivery_Time_Min': '{:.1f} min'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='City', y='Avg_Delivery_Time_Min', title='Average Delivery Time by City',
                            text='Avg_Delivery_Time_Min', color='City', color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(texttemplate='%{text:.1f} min', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 8: Distance vs Delivery Delay
        elif selected_query == "8. Distance vs Delivery Delay":
            df_q = filtered_df.groupby('Delivery_Performance_Category').agg({
                'Distance_km': 'mean',
                'Order_ID': 'count'
            }).reset_index()
            df_q.columns = ['Delivery_Performance_Category', 'Avg_Distance', 'Total_Orders']

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Avg_Distance': '{:.2f} km'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='Delivery_Performance_Category', y='Avg_Distance',
                            title='Distance vs Delivery Delay Analysis', text='Total_Orders',
                            color='Delivery_Performance_Category', color_discrete_sequence=['#11998e', '#F7931E', '#FF416C'])
                fig.update_traces(texttemplate='%{text} orders', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 9: Delivery Rating vs Delivery Time
        elif selected_query == "9. Delivery Rating vs Delivery Time":
            df_q = filtered_df.groupby('Delivery_Rating')['Delivery_Time_Min'].mean().reset_index()
            df_q.columns = ['Delivery_Rating', 'Avg_Delivery_Time_Min']
            df_q = df_q.sort_values('Avg_Delivery_Time_Min', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Avg_Delivery_Time_Min': '{:.1f} min'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='Delivery_Rating', y='Avg_Delivery_Time_Min',
                            title='Delivery Rating vs Delivery Time', text='Avg_Delivery_Time_Min',
                            color='Delivery_Rating', color_continuous_scale='RdYlGn_r')
                fig.update_traces(texttemplate='%{text:.1f} min', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 10: Top-Rated Restaurants
        elif selected_query == "10. Top-Rated Restaurants":
            rest_stats = filtered_df.groupby('Restaurant_Name').agg({
                'Restaurant_Rating': 'mean',
                'Order_ID': 'count'
            }).reset_index()
            rest_stats = rest_stats[rest_stats['Order_ID'] > 50].sort_values('Restaurant_Rating', ascending=False).head(10)
            rest_stats.columns = ['Restaurant_Name', 'Avg_Restaurant_Rating', 'Total_orders']

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(rest_stats.style.format({'Avg_Restaurant_Rating': '{:.2f}'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(rest_stats, x='Restaurant_Name', y='Avg_Restaurant_Rating',
                            title='Top-Rated Restaurants (Min 50 Orders)', text='Avg_Restaurant_Rating',
                            color='Avg_Restaurant_Rating', color_continuous_scale='RdYlGn')
                fig.update_traces(texttemplate='%{text:.2f}★', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 11: Cancellation Rate by Restaurant
        elif selected_query == "11. Cancellation Rate by Restaurant":
            rest_stats = filtered_df.groupby('Restaurant_Name').agg({
                'Order_ID': 'count',
                'Order_Status': lambda x: (x == 'Cancelled').sum()
            }).reset_index()
            rest_stats.columns = ['Restaurant_Name', 'Total_Orders', 'Cancelled_Orders']
            rest_stats['Cancellation_Rate'] = (rest_stats['Cancelled_Orders'] / rest_stats['Total_Orders'] * 100).round(2)
            rest_stats = rest_stats.sort_values('Cancellation_Rate', ascending=False).head(10)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(rest_stats.style.format({'Cancellation_Rate': '{:.2f}%'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(rest_stats, x='Restaurant_Name', y='Cancellation_Rate',
                            title='Cancellation Rate by Restaurant', text='Cancellation_Rate',
                            color='Cancellation_Rate', color_continuous_scale='Reds')
                fig.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 12: Cuisine-wise Performance
        elif selected_query == "12. Cuisine-wise Performance":
            df_q = filtered_df.groupby('Cuisine_Type').agg({
                'Order_ID': 'count',
                'Order_Value': 'sum'
            }).reset_index()
            df_q.columns = ['Cuisine_Type', 'Total_Orders', 'Total_Value']
            df_q = df_q.sort_values('Total_Value', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Total_Value': '₹{:,.0f}'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='Cuisine_Type', y='Total_Value',
                            title='Cuisine-wise Performance', text='Total_Value',
                            color='Cuisine_Type', color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(texttemplate='₹%{text:.4s}', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 13: Peak Hour Demand Analysis
        elif selected_query == "13. Peak Hour Demand Analysis":
            df_q = filtered_df.groupby('Peak_Hour_Indicator').agg({
                'Order_ID': 'count',
                'Order_Value': 'sum'
            }).reset_index()
            df_q.columns = ['Peak_Hour_Indicator', 'Total_Orders', 'Total_Value']
            df_q = df_q.sort_values('Total_Value', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Total_Value': '₹{:,.0f}'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='Peak_Hour_Indicator', y='Total_Value',
                            title='Peak Hour Demand Analysis', text='Total_Value',
                            color='Peak_Hour_Indicator', color_discrete_sequence=['#FF6B35', '#11998e'])
                fig.update_traces(texttemplate='₹%{text:.4s}', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 14: Payment Mode Preferences
        elif selected_query == "14. Payment Mode Preferences":
            df_q = filtered_df.groupby('Payment_Mode').agg({
                'Order_ID': 'count',
                'Order_Value': 'sum'
            }).reset_index()
            df_q.columns = ['Payment_Mode', 'Total_Orders', 'Total_Value']
            df_q = df_q.sort_values('Total_Value', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style.format({'Total_Value': '₹{:,.0f}'}), use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='Payment_Mode', y='Total_Value',
                            title='Payment Mode Preferences', text='Total_Value',
                            color='Payment_Mode', color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(texttemplate='₹%{text:.4s}', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

        # Query 15: Cancellation Reason Analysis
        elif selected_query == "15. Cancellation Reason Analysis":
            df_q = filtered_df[filtered_df['Cancellation_Reason'].isin(['Restaurant Issue', 'Customer Cancelled', 'Late Delivery'])]
            df_q = df_q.groupby('Cancellation_Reason')['Order_ID'].count().reset_index()
            df_q.columns = ['Cancellation_Reason', 'Total_Orders']
            df_q = df_q.sort_values('Total_Orders', ascending=False)

            col_t, col_c = st.columns(2)
            with col_t:
                st.markdown("#### Data Table")
                st.dataframe(df_q.style, use_container_width=True)
            with col_c:
                st.markdown("#### Visualization")
                fig = px.bar(df_q, x='Cancellation_Reason', y='Total_Orders',
                            title='Cancellation Reason Analysis', text='Total_Orders',
                            color='Cancellation_Reason', color_discrete_sequence=['#FF416C', '#F7931E', '#FF6B35'])
                fig.update_traces(texttemplate='%{text}', textposition='inside')
                fig.update_layout(height=450, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
    

st.markdown("---")
st.markdown("<center><small>Food Delivery Analytics Dashboard | Built with Streamlit & Plotly</small></center>", unsafe_allow_html=True)