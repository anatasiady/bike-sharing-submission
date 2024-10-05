import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import requests

# Set style for seaborn
sns.set(style="dark")

# Function to filter data by date
def count_by_day_df(day_df):
    return day_df.query('dteday >= "2011-01-01" and dteday < "2012-12-31"')

# Function to calculate total registered users
def total_registered_df(day_df):
    reg_df = day_df.groupby(by="dteday").agg({"registered": "sum"}).reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

# Function to calculate total casual users
def total_casual_df(day_df):
    cas_df = day_df.groupby(by="dteday").agg({"casual": "sum"}).reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

# Load datasets
days_df = pd.read_csv("dashboard/day.csv")
hours_df = pd.read_csv("dashboard/hour.csv")

# Convert date columns to datetime
datetime_columns = ["dteday"]
days_df[datetime_columns] = days_df[datetime_columns].apply(pd.to_datetime)
hours_df[datetime_columns] = hours_df[datetime_columns].apply(pd.to_datetime)

# Sidebar with user input
with st.sidebar:
    # Load image from Google Drive
    file_id = "1xj3v1YY8gUrYLJQCeglar4lmXYxAjjUJ"
    url = f"https://drive.google.com/uc?export=view&id={file_id}"
    response = requests.get(url)
    st.image(response.content)

    # Date input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=days_df["dteday"].min(),
        max_value=days_df["dteday"].max(),
        value=[days_df["dteday"].min(), days_df["dteday"].max()],
    )

# Filter main DataFrame based on user input
main_df_days = days_df[
    (days_df["dteday"] >= pd.Timestamp(start_date)) & (days_df["dteday"] <= pd.Timestamp(end_date))
]

# Calculate totals
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)

# Display main header
st.header(":bike: Bike Sharing :bike:")

# Display metrics
st.subheader("Sewa Harian :bar_chart:")
col1, col2, col3 = st.columns(3)
with col1:
    total_orders = day_df_count_2011.cnt.sum()
    st.metric("Total Penyewaan", value=total_orders)
with col2:
    total_registered = reg_df.register_sum.sum()
    st.metric("Total Pengguna Registered", value=total_registered)
with col3:
    total_casual = cas_df.casual_sum.sum()
    st.metric("Total Pengguna Casual", value=total_casual)

# 1. Monthly rental trend
st.subheader("Apa tren jumlah penyewaan sepeda setiap bulannya?")
months_all_years = days_df.groupby(by="mnth").agg({"casual": "sum", "registered": "sum", "cnt": "sum"}).reset_index()
months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
months_all_years["month_labels"] = months_labels

# Plotting monthly rentals
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(months_all_years["month_labels"], months_all_years["cnt"], marker="o", linewidth=2, color="#90CAF9")
ax.set_title("Jumlah Penyewaan Sepeda per Bulan", fontsize=20)
ax.set_ylabel("Jumlah Penyewaan", fontsize=15)
st.pyplot(fig)

# 2. Weather and rental relationship
st.subheader("Bagaimana hubungan antara faktor cuaca dan jumlah penyewaan sepeda di setiap musim?")
filtered_data = days_df[(days_df["dteday"].dt.date >= start_date) & (days_df["dteday"].dt.date <= end_date)]
season_weather_counts = filtered_data.groupby(["season", "weathersit"]).agg({"cnt": "sum"}).reset_index()
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
season_weather_counts["season"] = season_weather_counts["season"].map(season_mapping)

# Plotting season and weather relationship
plt.figure(figsize=(12, 6))
sns.barplot(data=season_weather_counts, x="season", y="cnt", hue="weathersit")
plt.title("Jumlah Penyewaan Sepeda berdasarkan Musim dan Cuaca")
plt.legend(title="Faktor Cuaca")
plt.xticks(rotation=45)
st.pyplot(plt)

# 3. Monthly rentals by user type
st.subheader("Bagaimana tren penyewaan sepeda untuk pengguna casual dan registered dari bulan ke bulan?")
filtered_data = days_df[(days_df["dteday"].dt.date >= start_date) & (days_df["dteday"].dt.date <= end_date)]
months_all_years = filtered_data.groupby(filtered_data["dteday"].dt.month).agg({"casual": "sum", "registered": "sum"}).reset_index()

# Mapping month labels
months_all_years['mnth'] = months_all_years['dteday'].apply(lambda x: months_labels[x-1])

# Plotting user type trends
plt.figure(figsize=(14, 7))
sns.lineplot(data=months_all_years, x="mnth", y="casual", marker="o", label="Pengguna Casual", color="blue")
sns.lineplot(data=months_all_years, x="mnth", y="registered", marker="o", label="Pengguna Registered", color="orange")
plt.title("Tren Penyewaan Sepeda: Pengguna Casual vs Registered per Bulan")
plt.xlabel("Bulan")
plt.ylabel("Jumlah Penyewaan")
plt.grid()
plt.legend()
st.pyplot(plt)

# 4. Clustering: Manual Grouping
st.header("Clustering: Manual Grouping")
st.subheader("Perbandingan pengguna registered dan casual berdasarkan jumlah penyewaan sepeda di tahun 2011 dan 2012") 

# Grouping data by year
years = days_df.groupby('yr').agg(
    casual=('casual', 'sum'),
    registered=('registered', 'sum')
).reset_index()

# Map year values
years['yr'] = years['yr'].map({0: 2011, 1: 2012})
melted_years = years.melt(id_vars='yr', value_vars=['casual', 'registered'], var_name='user_type', value_name='total_users')

# Plotting year comparison
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=melted_years, x='yr', y='total_users', hue='user_type', ax=ax)
ax.set_title('2011 VS 2012', fontsize=16)
ax.set_xlabel('Tahun', fontsize=12)
ax.set_ylabel('Jumlah Total Pengguna', fontsize=12)
ax.legend(title='Tipe Pengguna')
st.pyplot(fig)
