import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# customer by domicile
def customer_domicile(df):
    cust_domicile_df = df.groupby(by=['customer_state', 'customer_city'])['customer_id'].nunique().reset_index()
    cust_domicile_df.rename(columns={'customer_id':'customer_count'}, inplace=True)
    return cust_domicile_df

# seller by domicile
def seller_domicile(df):
    seller_domicile_df = df.groupby(by=['seller_state', 'seller_city'])['seller_id'].nunique().reset_index()
    seller_domicile_df.rename(columns={'seller_id':'seller_count'}, inplace=True)
    return seller_domicile_df

# domicile order process
def domicile_by_process(df):
    domicile_process_df = df.groupby(by=['customer_state','customer_city'], as_index=False).agg(
            total_order_process = ('order_process_time','sum'), 
            average_order_process = ('order_process_time','mean'))
    return domicile_process_df

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
    page_title="Customer Domiciles Demographic", page_icon="🌍"
)

# kostumisasi side bar
st.sidebar.header("Customer Domiciles Demographic")
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

cust_domicile_df = customer_domicile(main_df)
seller_domicile_df = seller_domicile(main_df)
domicile_process_df = domicile_by_process(main_df)

st.header('Olist Customer and Merchants Demography')

st.subheader('Number of Customers by States and Cities')
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_ = ["#72bcd4", "#0323d7", "#6075e5", "#3454e8", "#72bcd4","#6075e5","#6075e5", "#72bcd4","#72bcd4", "#72bcd4",
            "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3","#d3d3d3", "#d3d3d3", "#d3d3d3"]
    sns.barplot(x='customer_count', y='customer_state', palette=colors_,
                data=cust_domicile_df[['customer_state','customer_count']].sort_values(
                    by='customer_count', ascending=False).head(40))
    ax.set_title('Number of Customer by States', loc='center', fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_ = ["#0323d7", "#6075e5", "#6075e5", "#6075e5", "#6075e5", "#72bcd4" ,"#72bcd4", "#72bcd4", "#72bcd4", "#72bcd4",
            "#72bcd4", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3"]
    sns.barplot(x='customer_count', y='customer_city', palette=colors_,
                data=cust_domicile_df.sort_values(by='customer_count', ascending=False).head(20))
    ax.set_title('Number of Customer by Cities', loc='center', fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

st.subheader('Number of Merchants by States and Cities')
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_ = ["#6075e5", "#6075e5","#6075e5", "#72bcd4", "#0323d7", "#72bcd4", "#72bcd4","#72bcd4","#72bcd4", "#D3D3D3", "#72bcd4",
           "#72bcd4","#72bcd4", "#d3d3d3", "#d3d3d3", "#d3d3d3","#d3d3d3", "#d3d3d3", "#d3d3d3","#d3d3d3", "#d3d3d3", "#d3d3d3"]
    sns.barplot(x='seller_count', y='seller_state', palette=colors_,
                data=seller_domicile_df.sort_values(by='seller_count', ascending=False))
    ax.set_title('Number of Merchants by States', loc='center', fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_ = ["#0323d7", "#6075e5", "#6075e5", "#6075e5", "#6075e5", "#72bcd4" ,"#72bcd4", "#72bcd4", "#72bcd4", "#72bcd4",
           "#72bcd4", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3"]
    sns.barplot(x='seller_count', y='seller_city', palette=colors_,
                data=seller_domicile_df.sort_values(by='seller_count', ascending=False).head(20))
    ax.set_title('Number of Merchants by Cities', loc='center', fontsize=15)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

st.subheader('Times of Order processing elapsed to Customer by states')
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_ = ["#72bcd4", "#3454e8", "#d3d3d3", "#0323d7", "#d3d3d3","#d3d3d3","#d3d3d3", "#d3d3d3","#d3d3d3", "#d3d3d3",
           "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3","#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3",
           "#d3d3d3","#72bcd4", "#d3d3d3", "#d3d3d3", "#72bcd4", "#d3d3d3", "#72bcd4"]
    sns.barplot(x='total_order_process', y='customer_state', palette=colors_,
                data=domicile_process_df.sort_values(by='total_order_process', ascending=False))
    ax.set_title('Total Time of Order processing elapsed to Customer by States', size=14)
    ax.set_ylabel('Customer States', size=12)
    ax.set_xlabel('Total of Order Processing Times', size=12)
    st.pyplot(fig)
    
with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_ = ["#72bcd4", "#6075e5", "#72bcd4", "#d3d3d3", "#72bcd4", "#6075e5" ,"#6075e5", "#0323d7", "#d3d3d3", "#d3d3d3",
           "#6075e5", "#72bcd4", "#72bcd4", "#0323d7", "#6075e5", "#72bcd4", "#d3d3d3", "#d3d3d3", "#6075e5", "#72bcd4",
           "#0323d7", "#6075e5", "#72bcd4", "#72bcd4", "#d3d3d3", "#6075e5", "#d3d3d3"]
    sns.barplot(x='average_order_process', y='customer_state', palette=colors_,
            data=domicile_process_df.sort_values(by='average_order_process', ascending=False))
    ax.set_title('Average Time of Order processing elapsed to Customer by States', size=14)
    ax.set_ylabel('Customer States', size=12)
    ax.set_xlabel('Average of Order Processing Times', size=12)
    st.pyplot(fig)

st.subheader('Longest and shortest of order processint times to customers by cities')
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_ = ["#0323d7", "#6075e5", "#6075e5", "#6075e5", "#6075e5", "#6075e5" ,"#72bcd4", "#72bcd4", "#72bcd4", "#72bcd4",
           "#72bcd4", "#72bcd4", "#72bcd4", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3"]
    sns.barplot(x='total_order_process', y='customer_city', palette=colors_,
                data=domicile_process_df.sort_values(by='total_order_process', ascending=False).head(20))
    ax.set_title('Top 17 Longest Time of Order processing elapsed to Customer by Cities', size=14)
    ax.set_ylabel('Customer Cities', size=12)
    ax.set_xlabel('Total of Order Processing Times', size=12)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10, 8))
    colors_ = ["#0323d7", "#6075e5", "#6075e5", "#6075e5", "#6075e5", "#6075e5" ,"#72bcd4", "#72bcd4", "#72bcd4", "#72bcd4",
           "#72bcd4", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3", "#d3d3d3"]
    sns.barplot(x='total_order_process', y='customer_city', palette=colors_,
                data=domicile_process_df.sort_values(by='total_order_process', ascending=True).head(20))
    ax.set_title('Top 17 Shortest Time of Order processing elapsed to Customer by Cities', size=14)
    ax.set_ylabel('Customer Cities', size=12)
    ax.set_xlabel('Total of Order Processing Times', size=12)
    st.pyplot(fig)

st.caption('Copyright (c) Data Analyst Project - Hendry Wijaya - Dicoding 2023')