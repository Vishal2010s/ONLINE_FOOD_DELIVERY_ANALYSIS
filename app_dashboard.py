import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from sqlalchemy import create_engine, text


engine = create_engine('mysql+pymysql://root:Mwin%402028@127.0.0.1:3306/Online_food')
st.set_page_config(
    page_title="Food Delivery Analytics Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS for styling
st.markdown("""
<style>
    .main-header {font-size: 42px;font-weight: bold;color: #FF6B35;text-align: center;margin-bottom: 10px;}
    .sub-header {font-size: 18px;color: #666;text-align: center;margin-bottom: 30px;}
    .kpi-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);border-radius: 15px;padding: 20px;color: white;text-align: center;box-shadow: 0 4px 15px rgba(0,0,0,0.1);}
    .kpi-value {font-size: 30px;font-weight: bold;margin: 5px 0;}
    .kpi-label {font-size: 14px;opacity: 0.9;}
    .metric-card-1 { background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); }
    .metric-card-2 { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .metric-card-3 { background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%); }
    .metric-card-4 { background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); }
    .metric-card-5 { background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%); }
    .metric-card-6 { background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%); }
    .metric-card-7 { background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); }
    .query-section {background-color: #252324;border-radius: 10px;padding: 20px;margin-top: 20px;border-left: 5px solid #FF6B35;}
    .stTabs [data-baseweb="tab-list"] {gap: 24px;}
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
    .stTabs [aria-selected="true"] {background-color: #FF6B35 !important;color: black !important;}
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
QUERIES = {
    "1. Top Spending Customers by Gender": """
        SELECT Customer_Gender, ROUND(SUM(Final_Amount), 2) AS Total_Amount
        FROM ofd {where_clause}
        GROUP BY Customer_Gender
        ORDER BY Total_Amount DESC
    """,
    "2. Age Group vs Order Value": """
        SELECT Customer_Age_Group, ROUND(SUM(Order_Value), 2) AS Total_Amount
        FROM ofd {where_clause}
        GROUP BY Customer_Age_Group
        ORDER BY Total_Amount DESC
    """,
    "3. Weekend vs Weekday Order Patterns": """
        SELECT Order_Day, Cuisine_Type, ROUND(SUM(Final_Amount), 2) AS Total_Amount
        FROM ofd {where_clause}
        GROUP BY Order_Day, Cuisine_Type
        ORDER BY Total_Amount DESC
    """,
    "4. Monthly Revenue Trends": """
        SELECT Order_month, ROUND(SUM(Final_Amount), 2) AS Total_Amount
        FROM ofd {where_clause}
        GROUP BY Order_month
        ORDER BY FIELD(Order_month, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    """,
    "5. Impact of Discounts on Profit": """
        SELECT Discount_Applied,
               ROUND(AVG(Profit_Margin_Percentage), 2) AS Avg_Profit_Margin_Percentage
        FROM ofd {where_clause}
        GROUP BY Discount_Applied
        ORDER BY Discount_Applied
    """,
    "6. High-Revenue Cities & Cuisine Intensity": (
        """
            SELECT City, ROUND(SUM(Final_Amount), 2) AS Total_Amount
            FROM ofd {where_clause}
            GROUP BY City
            ORDER BY Total_Amount DESC
        """,
        """
            SELECT City, Cuisine_Type, ROUND(SUM(Final_Amount), 2) AS Total_Amount
            FROM ofd {where_clause}
            GROUP BY City, Cuisine_Type
            ORDER BY Total_Amount DESC
        """,
    ),
    "7. Average Delivery Time by City": """
        SELECT City, ROUND(AVG(Delivery_Time_Min), 1) AS Avg_Delivery_Time_Min
        FROM ofd {where_clause}
        GROUP BY City
        ORDER BY Avg_Delivery_Time_Min DESC
    """,
    "8. Distance vs Delivery Delay": """
        SELECT Delivery_Performance_Category,
               ROUND(AVG(Distance_km), 2) AS Avg_Distance,
               COUNT(Order_ID) AS Total_Orders
        FROM ofd {where_clause}
        GROUP BY Delivery_Performance_Category
    """,
    "9. Delivery Rating vs Delivery Time": """
        SELECT Delivery_Rating,
               ROUND(AVG(Delivery_Time_Min), 1) AS Avg_Delivery_Time_Min
        FROM ofd {where_clause}
        GROUP BY Delivery_Rating
        ORDER BY Avg_Delivery_Time_Min DESC
    """,
    "10. Top-Rated Restaurants": """
        SELECT Restaurant_Name,
               ROUND(AVG(Restaurant_Rating), 2) AS Avg_Restaurant_Rating,
               COUNT(Order_ID) AS Total_Orders
        FROM ofd {where_clause}
        GROUP BY Restaurant_Name
        HAVING COUNT(Order_ID) > 50
        ORDER BY Avg_Restaurant_Rating DESC
        LIMIT 10
    """,
    "11. Cancellation Rate by Restaurant": """
        SELECT Restaurant_Name,
               COUNT(Order_ID) AS Total_Orders,
               SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END) AS Cancelled_Orders,
               ROUND(SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END)
                     * 100.0 / COUNT(Order_ID), 2) AS Cancellation_Rate
        FROM ofd {where_clause}
        GROUP BY Restaurant_Name
        ORDER BY Cancellation_Rate DESC
        LIMIT 10
    """,
    "12. Cuisine-wise Performance": """
        SELECT Cuisine_Type, COUNT(Order_ID) AS Total_Orders,
               ROUND(SUM(Order_Value), 2) AS Total_Value
        FROM ofd {where_clause}
        GROUP BY Cuisine_Type
        ORDER BY Total_Value DESC
    """,
    "13. Peak Hour Demand Analysis": """
        SELECT Peak_Hour_Indicator, COUNT(Order_ID) AS Total_Orders,
               ROUND(SUM(Order_Value), 2) AS Total_Value
        FROM ofd {where_clause}
        GROUP BY Peak_Hour_Indicator
        ORDER BY Total_Value DESC
    """,
    "14. Payment Mode Preferences": """
        SELECT Payment_Mode, COUNT(Order_ID) AS Total_Orders,
               ROUND(SUM(Order_Value), 2) AS Total_Value
        FROM ofd {where_clause}
        GROUP BY Payment_Mode
        ORDER BY Total_Value DESC
    """,
    "15. Cancellation Reason Analysis": """
        SELECT Cancellation_Reason, COUNT(Order_ID) AS Total_Orders
        FROM ofd {where_clause}
          AND Cancellation_Reason IN ('Restaurant Issue', 'Customer Cancelled', 'Late Delivery')
        GROUP BY Cancellation_Reason
        ORDER BY Total_Orders DESC
    """,
}
query_options = ["Select a query...", *QUERIES]
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
        conditions = ["1 = 1"]
        sql_params = {}
        if selected_city != "All":
            conditions.append("City = :city")
            sql_params["city"] = selected_city
        if selected_cuisine != "All":
            conditions.append("Cuisine_Type = :cuisine")
            sql_params["cuisine"] = selected_cuisine
        if selected_month != "All":
            conditions.append("Order_month = :month")
            sql_params["month"] = selected_month
        if selected_payment != "All":
            conditions.append("Payment_Mode = :payment")
            sql_params["payment"] = selected_payment
        where_clause = "WHERE " + " AND ".join(conditions)
# Query 1: Top Spending Customers by Gender
        if selected_query == "1. Top Spending Customers by Gender":
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query][0].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_city = pd.read_sql(text(query), connection, params=sql_params)
            query = QUERIES[selected_query][1].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_city_cus = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                rest_stats = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                rest_stats = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
            query = QUERIES[selected_query].format(where_clause=where_clause)
            with engine.connect() as connection:
                df_q = pd.read_sql(text(query), connection, params=sql_params)
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
