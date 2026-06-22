import pandas as pd
from sqlalchemy import create_engine
import pymysql
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import numpy as np

print("Processing started")

# ------------------
# Loading data set
# ------------------
df=pd.read_csv('ONLINE_FOOD_DELIVERY_ANALYSIS (1).csv')
df1=df.copy()

print("Data Set loading to dataframe completed")

# -----------------------------------------
# Changing data type to respective columns
# ------------------------------------------

df1['Customer_Gender']=df1['Customer_Gender'].astype('category')
df1['Customer_Age']=df1['Customer_Age'].astype('float')
df1['City']=df1['City'].astype('category')
df1['Area']=df1['Area'].astype('category')
df1['Cuisine_Type']=df1.Cuisine_Type.astype('category')
# df1['Order_Time']=pd.to_datetime(df1['Order_Time'].dt.time
df1['Payment_Mode']=df1['Payment_Mode'].astype('category')
df1['Order_Status']=df1['Order_Status'].astype('category')
df1['Cancellation_Reason']=df1['Cancellation_Reason'].astype('category')
df1['Order_Day']=df1['Order_Day'].astype('category')
df1['Peak_Hour']=df1['Peak_Hour'].astype('category')

# ---------------------------------------------------------
# Formatting mixed date formats into uniform format'%d-%m-%Y'
# ----------------------------------------------------------
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='mixed', dayfirst=False)
df1['Order_Date'] = df1['Order_Date'].dt.strftime('%d-%m-%Y')
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'])

# ---------------------------------------------------------
# Identifying the Columns and segregating Numerical and other data types
# ----------------------------------------------------------

numerical_columns=[]
categorical_columns=[]
for i in df1.columns:
    if df1[i].dtype in['float64','int']:
        numerical_columns.append(i)
    else:
        categorical_columns.append(i)
print(f"Columns in Dataset: {df.columns}\n\n")
print("Categorical Columns:", categorical_columns,"\n")
print("Numerical Columns:", numerical_columns,"\n")
print(f"Number of Categorical Columns: {len(categorical_columns)}")
print(f"Number of Numerical Columns: {len(numerical_columns)}")

# ---------------------------------------------------------
# Identifying the correlation
# ----------------------------------------------------------
df_en=df1.copy()
for i in df1.columns:

  if df1[i].dtype in ["category", "object"]:
    le = LabelEncoder()
    df_en[i] = le.fit_transform(df1[i])

corr=df_en.corr()
fig = px.imshow(corr,text_auto='.2f',color_continuous_scale='RdBu_r',width=1200, height=1200)
fig.show()

print("Correlation of datas completed")
# ----------------------------------------------------------
#outlier detection
# Calculate IQR bounds
# ----------------------------------------------------------
for i in df1.columns:
    if df1[i].dtype in ['float64', 'int64']:
        print(f"Column name: ***{i}***")
        Q1 = df1[i].quantile(0.25)
        Q3 = df1[i].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df1[(df1[i] < lower_bound) | (df1[i] > upper_bound)]
        print(f"Number of Outliers in {i} column: ***{outliers.shape[0]}***")
        # Visualization: Boxplot with custom dimensions
        print(f"Visualization for outlier detection in column: {i}")
        fig = px.box(df1, y=i, title=f"{i} Outlier Detection", width=900, height=600)

        fig.add_hline(y=lower_bound, line_color="red", line_dash="dash", annotation_text=f"Lower Bound: {lower_bound:.2f}", annotation_position="top left")
        fig.add_hline(y=upper_bound, line_color="green", line_dash="dash", annotation_text=f"Upper Bound: {upper_bound:.2f}", annotation_position="top right")
        # fig.show()
        print(f"____________________________________________________________________________________________________________________________________________________\n")

print("Outlier detection of Data Set values completed")
# ----------------------------------------------------------
#Null Value Imputation:
# ----------------------------------------------------------
#In order to fill null values proportionately, eventhough the datatype is numerical in discount_applied column, the discount values falls into 5 types(0,20,50,100,300) which is type of categorical data. 
# hence we are filling up Null of Discount_applied columns with mode based on each category of order_status 
discount_split = df1.groupby('Order_Status')['Discount_Applied']

delivered_mode = df1[df1['Order_Status'] == 'Delivered']['Discount_Applied'].mode()[0]
cancelled_mode = df1[df1['Order_Status'] == 'Cancelled']['Discount_Applied'].mode()[0]
df1.loc[(df1['Order_Status'] == 'Cancelled') & (df1['Discount_Applied'].isnull()),'Discount_Applied'] = cancelled_mode
df1.loc[(df1['Order_Status'] == 'Delivered') & (df1['Discount_Applied'].isnull()),'Discount_Applied'] = delivered_mode

# ----------------------------------------------------------
#from Order_Value, Final_Amount and Discount_Applied columns we can fill the part of the null values in it using this.
# from the excel above, we can able to see that the some of the Final_Amount columns are null aginst values in Order_Value and Discount_Applied columns, so we can fill those null values using the below code.
# ----------------------------------------------------------

final_amount_median=df1['Final_Amount'].median()

condition_1=(df1['Order_Value']>0 & df1['Final_Amount'].isnull())
df1.loc[condition_1,'Final_Amount']=df1.loc[condition_1,'Order_Value']-df1.loc[condition_1,'Discount_Applied']

condition_2=(df1['Order_Value'].isnull()) & (df1['Discount_Applied'] > 0 & df1['Final_Amount'].isnull())
df1.loc[condition_2,'Final_Amount']=df1.loc[condition_2,'Discount_Applied']+final_amount_median

df1['Final_Amount'] = df1['Final_Amount'].fillna(final_amount_median) #to fill na other than 2 conditions

df1['Final_Amount'] = df1['Final_Amount'].clip(lower=0) #to make sure that there is no negative value in the Final_Amount column after substracting discount form order_value as the discount is higher than order value.

# --------------------------------
# Null Value Imputation of Order_Value
# ------------------------------------

condition_order=df1['Order_Value'].isnull()
df1.loc[condition_order,'Order_Value']=df1.loc[condition_order,"Final_Amount"]-df1.loc[condition_order,'Discount_Applied']

# 1. 'Customer_Age': Impute with mean or median as the data is continous data and the imputation is also based on the age based, outlier detection on the distribution of ages in the dataset.
#As mean and median is about 39.00 out of 49.9% data which represents that the data is normally distributed and there is no outliers noticed as per the plotly visualization. Hence filling NA values with median.
df1['Customer_Age']=df1['Customer_Age'].fillna(df1['Customer_Age'].median())
df_cust_age=df1['Customer_Age'].value_counts().sort_values(ascending=False)

#Customer _Gender
non_null = df1['Customer_Gender'].dropna()
null_count = df1['Customer_Gender'].isnull().sum()

fill_values = non_null.sample(n=null_count, replace=True).values
df1.loc[df1['Customer_Gender'].isnull(),'Customer_Gender']=fill_values

#Null imputation of City:
#Grouping by city and area with respect to Restuarant name and Restaurant_ID which is contradactory as Restaurant_1 has been spread across all the cities and areas along with all cuisine types
# 1.Restaurant_ID cannot be used for city imputation because each ID is unique with only one occurrence
# 2.Restaurant_Name cannot be used because all rows share the same name "Restaurant_1" across different cities
# 3.Cuisine_Type also has nulls and overlaps across cities

non_null = df1['City'].dropna()
null_count = df1['City'].isnull().sum()

fill_values = non_null.sample(n=null_count, replace=True).values
df1.loc[df1['City'].isnull(),'City']=fill_values


#Null imputation of Area:
#Grouping by city and area with respect to Restuarant name and Restaurant_ID which is contradactory as Restaurant_1 has been spread across all the cities and areas along with all cuisine types
# 1.Restaurant_ID cannot be used for city imputation because each ID is unique with only one occurrence
# 2.Restaurant_Name cannot be used because all rows share the same name "Restaurant_1" across different cities
# 3.Cuisine_Type also has nulls and overlaps across cities


summary_area = pd.DataFrame({
    'Area': df1['Area'].value_counts().index,
    'count': df1['Area'].value_counts().values,
    'percentage': (df1['Area'].value_counts(normalize=True)*100)
})
# print(f"Before Imputation:\n {summary_area}\n")
non_null_area = df1['Area'].dropna()
null_count_area = df1['Area'].isnull().sum()

fill_values_area = non_null_area.sample(n=null_count_area, replace=True).values
df1.loc[df1['Area'].isnull(),'Area']=fill_values_area

summary_area1 = pd.DataFrame({
    'Area': df1['Area'].value_counts().index,
    'count': df1['Area'].value_counts().values,
    'percentage': (df1['Area'].value_counts(normalize=True)*100)
})
# print (f"After Imputation:\n {summary_area1}\n")

#Null imputation of Cuisine type:
#No strong correlation exists for Cuisine_Type which has nulls and overlaps across all the cities
summary = pd.DataFrame({'Cuisine_Type': df1['Cuisine_Type'].value_counts().index,
    'count': df1['Cuisine_Type'].value_counts().values,
    'percentage': (df1['Cuisine_Type'].value_counts(normalize=True)*100)
})
# print(f"Before Imputation:\n{summary}")

non_null_CT = df1['Cuisine_Type'].dropna()
null_count_CT = df1['Cuisine_Type'].isnull().sum()

fill_values_CT = non_null_CT.sample(n=null_count_CT, replace=True).values
df1.loc[df1['Cuisine_Type'].isnull(),'Cuisine_Type']=fill_values_CT

summary1 = pd.DataFrame({'Cuisine_Type': df1['Cuisine_Type'].value_counts().index,
    'count': df1['Cuisine_Type'].value_counts().values,
    'percentage': (df1['Cuisine_Type'].value_counts(normalize=True)*100)
})
# print(f"After Imputation:\n{summary1}")


#Null Imputation of Distance_km and Delivery_Time_Min

deliver_out=df1.groupby('Order_Status')[['Delivery_Time_Min','Distance_km']].describe()

df1['Delivery_Time_Min'] = df1['Delivery_Time_Min'].clip(upper=160)

df1['Distance_km'] = df1['Distance_km'].fillna(df1['Distance_km'].mean())
df1['Distance_km']=df1['Distance_km'].round(2)

#Null imputation for Delivery_time_min with respect to distance_km and order status group by distance km

# Condition 1
condition1 = ((df1['Order_Status'] == 'Delivered') & (df1['Distance_km'].between(1.00, 5.99)) & (df1['Delivery_Time_Min'].isna()))
df1.loc[condition1, 'Delivery_Time_Min'] = 40

# Condition 2
condition2 = ((df1['Order_Status'] == 'Delivered') & (df1['Distance_km'].between(6.00, 10.99)) & (df1['Delivery_Time_Min'].isna()))
df1.loc[condition2, 'Delivery_Time_Min'] = 60

# Condition 3
condition3 = ((df1['Order_Status'] == 'Delivered') & (df1['Distance_km'].between(11.00, 15.99)) & (df1['Delivery_Time_Min'].isna()))
df1.loc[condition3, 'Delivery_Time_Min'] = 90

# Condition 4
condition4 = ((df1['Order_Status'] == 'Delivered') & (df1['Distance_km'].between(16.00, 25.99)) & (df1['Delivery_Time_Min'].isna()))
df1.loc[condition4, 'Delivery_Time_Min'] = 120

condition4 = ((df1['Order_Status'] == 'Delivered') & (df1['Distance_km'].between(26.00, 40.00)) & (df1['Delivery_Time_Min'].isna()))
df1.loc[condition4, 'Delivery_Time_Min'] = 150


# Condition 5
condition5 = ((df1['Order_Status'] == 'Cancelled') & (df1['Delivery_Time_Min'].isna()))
df1.loc[condition5, 'Delivery_Time_Min'] = 20



#Null Imputation of Cancellation_Reason
# filtering cancelled orders:
order_cancelled = df1[df1['Order_Status'] == 'Cancelled']
null_reason = order_cancelled[order_cancelled['Cancellation_Reason'].isnull()]
order_delivered = df1[df1['Order_Status'] == 'Delivered']
null_reason_delivered = order_delivered[order_delivered['Cancellation_Reason'].isnull()]
# print(f"\n1.Total cancelled orders: {len(order_cancelled)}")
# print(f"\n {order_cancelled[['Order_Status', 'Cancellation_Reason']]}")
# print(f" Cancelled but no reason given: ***{len(null_reason)}***\n")
# print(f"\n2.Total delivered orders: {len(order_delivered)}")
# print(f"\n order_delivered[['Order_Status', 'Cancellation_Reason']]\n ")
# print(f" Delivered but no reason given: ***{len(null_reason_delivered)}***\n")


summary_CR = pd.DataFrame({
    'Cancellation_Reason': df1['Cancellation_Reason'].value_counts().index,
    'count': df1['Cancellation_Reason'].value_counts().values,
    'percentage': (df1['Cancellation_Reason'].value_counts(normalize=True) * 100).round(2).values
})
# print(f"Before Imputation:\n{summary_CR}")
# Adding new categories before filling 
df1['Cancellation_Reason'] = df1['Cancellation_Reason'].cat.add_categories(['Delivered'])

# condition_1: Delivered orders does not have cancellation reason hence, For 84,964 delivered orders filling it with Delivered.
df1.loc[(df1['Order_Status'] == 'Delivered') & (df1['Cancellation_Reason'].isnull()),'Cancellation_Reason'] = 'Delivered'

#condition_2:For 6,005 cancelled orders with no reason → fill with 'Late Delivery'
df1.loc[(df1['Order_Status'] == 'Cancelled') & (df1['Cancellation_Reason'].isnull()) & (df1['Delivery_Time_Min']>75),'Cancellation_Reason'] = 'Late Delivery'

#condition_3: for the remaining nulls
non_null_CR = df1[df1['Cancellation_Reason'].isin(['Customer Cancelled', 'Restaurant Issue'])]['Cancellation_Reason'] #already null values has been imputed accordingly with "Late delivery "as per condition _2, hence filtering with other two
null_count_CR = df1['Cancellation_Reason'].isnull().sum()

fill_values_CR = non_null_CR.sample(n=null_count_CR, replace=True).values
df1.loc[df1['Cancellation_Reason'].isnull(),'Cancellation_Reason']=fill_values_CR

summary_CR1 = pd.DataFrame({
    'Cancellation_Reason': df1['Cancellation_Reason'].value_counts().index,
    'count': df1['Cancellation_Reason'].value_counts().values,
    'percentage': (df1['Cancellation_Reason'].value_counts(normalize=True) * 100).round(2).values
})
# print(f"After Imputation:\n{summary_CR1}")

#null impution of Payment_Mode  

not_null_PM=df1['Payment_Mode'].dropna()
null_PM_count=df1['Payment_Mode'].isna().sum()

fill_PM_values=not_null_PM.sample(n=null_PM_count, replace=True).values
df1.loc[df1['Payment_Mode'].isna(), 'Payment_Mode']= fill_PM_values

#Null imputation of peak hour

non_null_PH = df1['Peak_Hour'].dropna() 
null_count_PH = df1['Peak_Hour'].isnull().sum()

fill_values_PH = non_null_PH.sample(n=null_count_PH, replace=True).values
df1.loc[df1['Peak_Hour'].isnull(),'Peak_Hour']=fill_values_PH

#null impution of Order_Date and Order_Time
df1['Order_Time']=df1['Order_Time'].fillna(df1['Order_Time'].ffill())
df1['Order_Date']=df1['Order_Date'].fillna(df1['Order_Date'].ffill())

#null impution of Delivery_Rating
df1['Delivery_Rating']=df1['Delivery_Rating'].fillna(df1['Delivery_Rating'].median())


print("Null Imputation completed")

# Feature Engineering
# Derived analytical columns:
# --------------------------------------------
# ●	Order day type (Weekday / Weekend)
# --------------------------------------------
df1['Order_Day_Type'] = df1['Order_Day']

# --------------------------------------------
# ●	Peak hour indicator
# --------------------------------------------

df1['Peak_Hour_Indicator'] = df1['Peak_Hour'].map({True: 'Peak Hour', False: 'Non-Peak Hour'})
                                                
# --------------------------------------------
# ●	Profit margin percentage
# --------------------------------------------

df1['Profit_Margin_Percentage'] = (df1['Profit_Margin'] * 100).round(2)

# --------------------------------------------
# ●	Delivery performance categories
# --------------------------------------------
def category (delivery_time):
    if delivery_time <= 45:
        return 'On-Time / Fast (<45 mins)'
    elif delivery_time <= 90:
        return 'Moderate Delay (45-90 mins)'
    else:
        return 'Severe Delay (>90 mins)'

df1['Delivery_Performance_Category'] = df1['Delivery_Time_Min'].apply(category)

# --------------------------------------------
# ●	Customer age groups
# --------------------------------------------
def categorise_age(age):
    if age <= 30:
        return 'Young (18-30)'
    elif age <= 50:
        return 'Middle-Aged (31-50)'
    else:
        return 'Old Adults (51-60)'

df1['Customer_Age_Group'] = df1['Customer_Age'].apply(categorise_age)


#Segregating month to fnd out the monthly revenue trends.

df1['Order_month'] = df1['Order_Date'].dt.month_name()
df1['Order_month']=df1['Order_month'].str[:3]

df1['Order_year']=df1['Order_Date'].dt.year
df1['Order_year']=df1['Order_year'].astype('Int64')

# ----------------------------------------------------
# Exporting th processed dataset into csv file and storing in DB
# --------------------------------------------------- 

df1.to_csv("FOOD_DELIVERY_ANALYSIS_final.csv", index=False)
print("Final CSV export completed")

# --- Create database ---
print("Starting data upload to SQL database...")

try:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Mwin@2028')
    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS Online_food")
    cursor.execute("CREATE DATABASE Online_food")
    cursor.close()
    conn.close()
    print("Database EQ1 created successfully, uploading the data from csv to SQL DB...")
except Exception as e:
    print(" Error while creating DB:", e)


engine = create_engine('mysql+pymysql://root:Mwin%402028@127.0.0.1:3306/Online_food')
df2 = pd.read_csv("FOOD_DELIVERY_ANALYSIS_final.csv")
df2.to_sql("OFD", engine, if_exists='replace', index=False)
print("Data upload to SQL completed")
