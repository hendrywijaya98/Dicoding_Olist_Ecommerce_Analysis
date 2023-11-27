import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

 # frequency unique value 1, 2, 3, 4, 5, 6, 7, 9, 14
def frequency_score(frequency):
    freq_score = None
    # kalau frequency 1, 2, 3
    if frequency <=3:
        freq_score = 1
    elif frequency <=6:
        freq_score = 2
    elif frequency <=9:
        freq_score = 3
    else:
        freq_score = 4
    return freq_score

# defining customer segment
def customer_segment(rfm_score):
    segment = ''
    # High Value Customer, `rfm_score` > 3
    if rfm_score >=3:
        segment = 'High Value Customer'
    # Medium Value Customer, `rfm_score` > 2
    elif rfm_score >=2:
        segment = 'Medium Value Customer'
    # Low Value Customer, `rfm_score` > 1
    else:
        segment = 'Low Value Customer'
    return segment

# rfm data
def rec_freq_mon(df):
    rfm_df = df.groupby('customer_id', as_index=False).agg(
    {'order_approved_at':'max','order_id':'nunique','total_amount':'sum'})
    rfm_df.sort_values(by='total_amount', ascending=False).head(10)

    rfm_df['order_approved_at'] = pd.to_datetime(rfm_df['order_approved_at'])
    rfm_df['order_approved_at'] = rfm_df['order_approved_at'].dt.date

    recent_date = rfm_df['order_approved_at'].max()
    rfm_df['recency'] = rfm_df['order_approved_at'].apply(lambda x: (recent_date - x).days)
    rfm_df.rename(columns={'order_id':'frequency', 'total_amount':'monetary'}, inplace=True)

    # perhitungan nilai dari nilai masing-masign pada recency, frequency dan monetary
    rfm_df['r_score'] = pd.qcut(rfm_df['recency'], 4, labels=[4, 3, 2, 1], duplicates='drop')
    rfm_df['f_score'] = rfm_df['frequency'].apply(frequency_score)
    rfm_df['m_score'] = pd.qcut(rfm_df['monetary'], 4, labels=[1, 2, 3, 4], duplicates='drop')

    # # kemudian masing-msaing nilai dari recency, frequency dan monetary dihitung rata-ratanya
    rfm_df['rfm_score'] = rfm_df['r_score'].astype(int) + rfm_df['f_score'].astype(int) + rfm_df['m_score'].astype(int)
    rfm_df['rfm_score'] = (rfm_df['rfm_score']/3).round(2)

    rfm_df['cust_segment'] = rfm_df['rfm_score'].apply(customer_segment)

    return rfm_df

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
    page_title="Customer Segmentation Analysis", page_icon="📊"
)

# kostumisasi side bar
st.sidebar.header("Customer Segmentation Analysis")

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

rfm_df = rec_freq_mon(main_df)
st.header('Olist Customer Segmentation Analysis With RFM')

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df['recency'].mean(), 1)
    st.metric('Average Recency (days)', value=avg_recency)

with col2:
    avg_frequency = round(rfm_df['frequency'].mean(), 1)
    st.metric('Average Frequency', value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df['monetary'].mean(), 1)
    st.metric('Average Monetary', value=avg_monetary)

# buat 3 kolom visualisasi
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(36, 6))

# color palette

# mencari tahu terakhir kali melakukan transaksi
sns.barplot(y='recency', x='customer_id', palette=["#031fd5", "#0323d7", "#3454e8", "#72bcd4", "#72bcd4"], ax=ax[0],
            data=rfm_df.sort_values(by='recency', ascending=False).head(5))
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title('Recency of Last Transaction', loc='center', fontsize=18)
ax[0].tick_params(axis='x', labelsize=15, rotation=45)

# menghitung frequenci pelanggan melakukan transaksi pada bulan terakhir
sns.barplot(y='frequency', x='customer_id', palette=["#0323d7", "#0323d7", "#0323d7", "#0323d7", "#72bcd4"], ax=ax[1],
            data=rfm_df.sort_values(by='frequency', ascending=False).head(5))
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title('Number of Transaction since last month', loc='center', fontsize=18)
ax[1].tick_params(axis='x', labelsize=15, rotation=45)

# mengitung banyaknya uang yang dihabiskan customer
sns.barplot(y='monetary', x='customer_id', palette=["#0323d7", "#6075e5", "#6075e5", "#72bcd4", "#72bcd4"], ax=ax[2],
            data=rfm_df.sort_values(by='monetary', ascending=False).head(5))
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title('Number of Money Spent', loc='center', fontsize=18)
ax[2].tick_params(axis='x', labelsize=15, rotation=45)

st.pyplot(fig)

st.subheader('Number of Customer by Segment')
fig, ax = plt.subplots(figsize=(10,7))
aux = rfm_df.groupby('cust_segment')['customer_id'].nunique().reset_index()
sbar = sns.barplot(data=aux, x='cust_segment', y='customer_id', palette=['#72bcd4', '#031fd5', '#6075e5'])

# bar plot annotation
for p in sbar.patches:
    sbar.annotate(format(p.get_height(), '.0f'), (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha = 'center', va = 'center', xytext = (0, 6), textcoords = 'offset points')
st.pyplot(fig)

st.subheader('Customer Segment by Recency, Frequency and Monetary Analysis')
col1, col2 = st.columns(2)
with col1:
    # customer segment by recency distribution
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='recency', y='cust_segment', data=rfm_df, 
            palette={"High Value Customer": "skyblue", "Medium Value Customer": "lightblue", "Low Value Customer":"blue"})
    ax.set_title('Segment of Customer by Recency', fontsize=14)
    st.pyplot(fig)
with col2:
    # recency vs frequency
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(x='recency', y='frequency', data=rfm_df, hue='cust_segment', palette=['#031fd5', '#6075e5', '#72bcd4'])
    ax.set_title('Recency vs Frequency', fontsize=14)
    ax.legend(loc='upper left', title='Customer Segment', bbox_to_anchor=(1,0.6))
    st.pyplot(fig)

col1, col2 = st.columns(2)
with col1:
    # customer segment by monetary distribution
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='monetary', y='cust_segment', data=rfm_df, 
            palette={"High Value Customer": "skyblue", "Medium Value Customer": "lightblue", "Low Value Customer":"blue"})
    ax.set_title('Segment of Customer by Monetary', fontsize=14)
    st.pyplot(fig)
with col2:
    # recency vs monetary
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(x='recency', y='monetary', data=rfm_df, hue='cust_segment', palette=['#031fd5', '#6075e5', '#72bcd4'])
    ax.set_title('Recency vs Monetary', fontsize=14)
    ax.legend(loc='upper left', title='Customer Segment', bbox_to_anchor=(1,0.6))
    st.pyplot(fig)

col1, col2 = st.columns(2)
with col1:
    # customer segment by frequency distribution
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='frequency', y='cust_segment', data=rfm_df, 
            palette={"High Value Customer": "skyblue", "Medium Value Customer": "lightblue", "Low Value Customer":"blue"})
    ax.set_title('Segment of Customer by Frequency', fontsize=14)
    st.pyplot(fig)
with col2:
    # frequency vs monetary
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(x='frequency', y='monetary', data=rfm_df, hue='cust_segment', palette=['#031fd5', '#6075e5', '#72bcd4'])
    ax.set_title('Frequency vs Monetary', fontsize=14)
    ax.legend(loc='upper left', title='Customer Segment', bbox_to_anchor=(1,0.6))
    st.pyplot(fig)

st.caption('Copyright (c) Data Analyst Project - Hendry Wijaya - Dicoding 2023')