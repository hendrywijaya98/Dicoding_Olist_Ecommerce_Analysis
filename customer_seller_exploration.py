import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import seaborn as sns
import streamlit as st
import datetime

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# top rating seller data
def seller_rating(df):
    rating_seller_df = df.groupby('review_rating')['seller_id'].nunique().reset_index()
    rating_seller_df.rename(columns={'seller_id':'seller_count'}, inplace=True)
    return rating_seller_df

# top product category
def product_category(df):
    top_least_category_df = df.groupby('product_category')['order_id'].nunique().sort_values(ascending=False).reset_index()
    top_least_category_df.rename(columns={'order_id':'total_orders'}, inplace=True)
    return top_least_category_df

# customer satisfaction data
def customer_satisfaction(df):
    df['review_creation_date'] = pd.to_datetime(df['review_creation_date'])
    customer_satisfaction_df = df.resample(rule='M', on='review_creation_date').agg(
    {'review_rating':'count', 'review_score':'mean'}).round(2)
    customer_satisfaction_df = customer_satisfaction_df.reset_index()
    customer_satisfaction_df.rename(columns={'review_rating':'rating_count', 'review_score':'average_rating'}, inplace=True)
    customer_satisfaction_df.fillna(0, inplace=True)
    return customer_satisfaction_df

# payment preference data
def payment_preference(df):
    payment_preference_df = df.groupby('payment_type')[['customer_id','order_id']].nunique().reset_index()
    return payment_preference_df

custran_df = pd.read_csv('cust_trans_dataset.csv')
custran_df.sort_values(by='order_approved_at', inplace=True)
custran_df.reset_index(inplace=True)

# transformasi kolom tanggal dari tipe object ke datetime
for date_col in ['order_approved_at', 'order_delivered_customer_date']:
    custran_df[date_col] = pd.to_datetime(custran_df[date_col])

## menambahkan komponen filter pada dashboard
min_date = custran_df['order_approved_at'].min()
max_date = custran_df['order_approved_at'].max()

st.set_page_config(
    page_title="Customer and Merchants", page_icon="📈"
)

# kostumisasi side bar
st.sidebar.header("Customer and Merchants")
# membuat filter date di dalam side bar untuk filter order approve at dari custrans df
with st.sidebar:

    # logo perusahaan
    st.image("https://seeklogo.com/images/O/olist-logo-9DCE4443F8-seeklogo.com.png")
    st.subheader('Olist Customer & Sales Analysis')

    # mengambil start date & end date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value = min_date,
        max_value = max_date, value = [min_date, max_date])


# menyimpan data dari filter start_date dan end_date ke main_df
main_df = custran_df[(custran_df['order_approved_at'] >= str(start_date)) \
                      & (custran_df['order_approved_at'] <= str(end_date))]

seller_rating_df = seller_rating(main_df)
top_least_category_df = product_category(main_df)
customer_satisfaction_df = customer_satisfaction(main_df)
payment_preference_df = payment_preference(main_df)

st.header('Olist Customer and Merchants Exploration')

st.subheader('Customer transaction overviews')
col1, col2 = st.columns(2)
# menampilkan big number total order, revenue, customer dan sellers dengan metrics
with col1:
    total_orders = custran_df['order_id'].nunique()
    st.metric('Total Orders :', value=total_orders)

with col2:
    total_revenue = (custran_df['total_amount'].sum()).round(2)
    st.metric('Total Amount Transactions :', value=total_revenue)

col1, col2 = st.columns(2)
with col1:  
    total_customers = custran_df['customer_id'].nunique()
    st.metric('Total Customers :', value=total_customers)

with col2:
    total_sellers = custran_df['seller_id'].nunique()
    st.metric('Total Merchants :', value=total_sellers)


st.subheader('Best and Worst Performing Products from Number of Sales')
# menggunakan subplots dengan object fig dan ax
fig, ax = plt.subplots(nrows = 1, ncols=2, figsize=(24, 8))

# color pallette
colors = ["#031fd5", "#6075e5", "#6075e5", "#6075e5", "#6075e5"]

# visualisasi produk dengan performa terbaik
sns.barplot(x='total_orders', y='product_category',palette = colors, ax=ax[0], 
            data=top_least_category_df.head(5))
# ax[0] adalah object canvas pertama
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title('Best Performing Product', loc='center', fontsize=15)
ax[0].tick_params(axis='y', labelsize=12)

# visualisasi produk dengan performa terburuk
sns.barplot(x='total_orders', y='product_category', palette = colors, ax=ax[1],
            data=top_least_category_df.sort_values(by='total_orders',
                                        ascending=True).head(5))
# ax[1] adalah object canvas kedua
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].set_title('Worst Performing Product', loc='center', fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)
st.pyplot(fig)

st.subheader('Customer Satisfaction by Rating')
# membuat visualisasi jumlah revenue dengan line chart
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(customer_satisfaction_df['review_creation_date'], customer_satisfaction_df['rating_count'],
         marker='o', linestyle='--', linewidth=2, color="#0323d7")
ax.set_title('Monthly Customer Satisfaction by Total Rating', loc='center', fontsize=20)
ax.set_xticklabels(ax.get_xticks(), rotation = 45)
ax.set_yticklabels(ax.get_yticks(), fontsize=10)
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(customer_satisfaction_df['review_creation_date'], customer_satisfaction_df['average_rating'],
         marker='+', linestyle='-.', linewidth=2, color="#6075e5")
ax.set_title('Monthly Customer Satisfaction by Average Rating', loc='center', fontsize=20)
ax.set_xticklabels(ax.get_xticks(), rotation = 45)
ax.set_yticklabels(ax.get_yticks(), fontsize=10)
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
st.pyplot(fig)

st.subheader('Customer most used Payment Method when order')
fig, ax = plt.subplots(figsize=(16,8))
# left pie chart for number of customers
pie1 = fig.add_subplot(121)
pie1.pie(payment_preference_df['customer_id'], labels=payment_preference_df['payment_type'],
        autopct='%.0f%%', colors=('cyan','turquoise','lightblue', 'aquamarine'))
ax.set_title('most used Payment Method by customers', fontsize=16)

# piechart right for number of orders
pie2 = fig.add_subplot(122)
pie2.pie(payment_preference_df['order_id'], labels=payment_preference_df['payment_type'],
        autopct='%.0f%%', colors=('blue','royalblue','cornflowerblue','dodgerblue'))
plt.title('most used Payment Method from order history', fontsize=16)
st.pyplot(fig)

st.subheader('Overall Merchants Rating')
fig, ax = plt.subplots(figsize=(8,4))
sns.barplot(x='review_rating', y='seller_count', data=seller_rating_df,
            palette= ["#6075e5", "#72bcd4", "#72bcd4", "#6075e5", "#031fd5"])
ax.set_title('Overall Merchant by Rating Given of Customers', loc='center', fontsize=15)
ax.set_ylabel('Number of Merchants')
ax.set_xlabel('Merchants')
st.pyplot(fig)

st.caption('Copyright (c) Data Analyst Project - Hendry Wijaya - Dicoding 2023')