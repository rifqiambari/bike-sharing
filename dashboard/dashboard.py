import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set(style="dark")


def count_by_day_df(day_df):
    day_df_count = day_df.query(
        str('datetime >= "2011-01-01" and datetime < "2012-12-31"')
    )
    return day_df_count


def total_registered_df(day_df):
    reg_df = day_df.groupby(by="datetime").agg({"registered": "sum"})
    reg_df = reg_df.reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df


def total_casual_df(day_df):
    cas_df = day_df.groupby(by="datetime").agg({"casual": ["sum"]})
    cas_df = cas_df.reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df


def season_type(day_df):
    season_df = day_df.groupby(by="season").total_count.sum().reset_index()
    return season_df


def create_weather_rent_df(df):
    weather_rent_df = df.groupby(by="weather_condition").agg({"total_count": "sum"})
    return weather_rent_df


def create_season_rent_df(df):
    season_rent_df = (
        df.groupby(by="season")
        .agg({"registered": "sum", "casual": "sum"})
        .reset_index()
    )
    return season_rent_df


def create_rfm_df(df):

    current_date = max(days_df["datetime"])
    rfm_df = (
        days_df.groupby("registered")
        .agg(
            {
                "datetime": lambda x: (current_date - x.max()).days,  # Recency
                "rec_id": "count",  # Frequency
                "total_count": "sum",  # Monetary
            }
        )
        .reset_index()
    )

    rfm_df.columns = ["registered", "recency", "frequency", "monetary"]
    return rfm_df


days_df = pd.read_csv("day_data.csv")
hours_df = pd.read_csv("hour_data.csv")

datetime_columns = ["datetime"]
days_df.sort_values(by="datetime", inplace=True)
days_df.reset_index(inplace=True)

hours_df.sort_values(by="datetime", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["datetime"].min()
max_date_days = days_df["datetime"].max()

min_date_hour = hours_df["datetime"].min()
max_date_hour = hours_df["datetime"].max()

with st.sidebar:
    # Add Logo
    st.image("logo.jpg", width=200)

    # Get start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label="Range Date",
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days],
    )

main_df_days = days_df[
    (days_df["datetime"] >= str(start_date)) & (days_df["datetime"] <= str(end_date))
]

main_df_hour = hours_df[
    (hours_df["datetime"] >= str(start_date)) & (hours_df["datetime"] <= str(end_date))
]


day_df_count = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
weather_rent_df = create_weather_rent_df(main_df_hour)
season_df = season_type(main_df_days)
season_rent_df = create_season_rent_df(main_df_days)
rfm_df = create_rfm_df(main_df_days)

# Complete Dashboard with Data Visualization
st.header("Bike Sharing :sparkles:")

st.subheader("Daily Sharing")
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = day_df_count.total_count.sum()
    st.metric("Total Sharing Bike", value=total_orders)

with col2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total Registered User", value=total_sum)

with col3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total Casual User", value=total_sum)

##Bike rentals performance
st.subheader("Bike Rentals Performance Comparison")
main_df_days["month"] = pd.Categorical(
    main_df_days["month"],
    categories=[
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],
    ordered=True,
)

monthly_counts = (
    main_df_days.groupby(by=["year", "month"]).agg({"total_count": "sum"}).reset_index()
)

# Set the style
fig_bike_rentals, ax = plt.subplots(figsize=(25, 10))
sns.lineplot(
    data=monthly_counts,
    x="month",
    y="total_count",
    hue="year",
    palette="Set2",
    marker="o",
)
plt.xlabel(None)
plt.ylabel(None)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.title(f"Bike Rental Trends ({start_date} to {end_date})", fontsize=21)
plt.legend(title="Year", loc="upper right", fontsize=17)
plt.gca().xaxis.grid(False)
st.pyplot(fig_bike_rentals)


st.subheader("Most Rented each Season")
# colors setting
colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]

# create a subplot with 1 row and 1 column, with size (20, 10)
fig_season, ax = plt.subplots(figsize=(20, 10))

sns.barplot(
    y="total_count",
    x="season",
    data=main_df_days.sort_values(by="season", ascending=False),
    palette=colors,
    ax=ax,
)
# sets the title, y and x labels, and tick params for the subplot
ax.set_title("Inter-Seasonal Chart", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="x", labelsize=35)
ax.tick_params(axis="y", labelsize=30)
st.pyplot(fig_season)


st.subheader("Number of Registered and Casual per Season")
# Groups data by season and counts the number of registered and unregistered uses
seasonal_usage = (
    season_rent_df.groupby("season")[["registered", "casual"]].sum().reset_index()
)

# Create a subplot with 1 row and 1 column, with size (20, 10)
fig1, ax = plt.subplots(figsize=(20, 10))

# Create bar plot
sns.barplot(
    x="season",
    y="registered",
    data=seasonal_usage,
    label="registered",
    color="tab:blue",
)

sns.barplot(
    x="season", y="casual", data=seasonal_usage, label="Casual", color="tab:gray"
)

plt.xlabel(None)
plt.ylabel(None)
plt.title("Number of bicycle rentals based on season")
plt.legend()
st.pyplot(fig1)

st.subheader("Best Customer Based on RFM Parameters")

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(
    y="recency",
    x="registered",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis="x", labelsize=15)

sns.barplot(
    y="frequency",
    x="registered",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis="x", labelsize=15)

sns.barplot(
    y="monetary",
    x="registered",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    palette=colors,
    ax=ax[2],
)
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis="x", labelsize=15)

plt.suptitle("Best Customer Based on RFM Parameters (registered)", fontsize=20)
st.pyplot(fig)

st.caption("Created by: Rifqi Ambari")
