import pandas as pd
import streamlit as st
import numpy as np
import datetime
import seaborn as sns


@st.cache(allow_output_mutation=True)
def load_listing_data():
    return pd.read_excel('dashboard data.xls', header=0)  # this speeds up the reloading process when the user changes the inputs


LA_listings = load_listing_data()
navigation = ["Home", "Air BnB Finder", "Air BnB Profile"]


def homepage():
    st.markdown("<h1 style='text-align: center;'>Welcome to the LA Air BnB Finder!</h1>", unsafe_allow_html=True)
    st.image('Logo.jpeg', width=500)
    st.markdown("<h2 style='text-align: center;'>Find your perfect getaway today!!</h2>", unsafe_allow_html=True)
    st.write('**About this Dashboard:**', 'Welcome to the LA Airbnb finder! Krtin and Liz have created this dashboard so viewers can find an Airbnb in the LA area based on their specifications. Additionally, they can easily read about various details of their rental or host by supplying the ID number. All the data utilized in this dashboard is from the listings and reviews csv files.')
    st.write('**About the Datasets:** We have retrieved a dataset dealing with Los Angeles Airbnb data. The listings dataset gives various details about the Airbnb rental itself along with host information.')
    st.write('**Number of Air BnBs Available: **', len(LA_listings['availability_365'].astype(float) > 0))

# code for page 2


def dates():  # function to determine the check in and check out dates and thus number of nights
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    check_in = st.date_input('Check in', today)
    check_out = st.date_input('Check out', tomorrow)
    if check_in >= check_out:
        st.error('Error: Check out must fall after Check in')  # error message if check out date before check in
    global stay
    stay = check_out-check_in
    if stay.days == 1:  # formatting output for correct syntax
        st.write(f"Number of days: {stay.days} day")
    else:
        st.write(f"Number of days: {stay.days} days")


def room(data):  # function to filter the type of room wanted by the user
    options = LA_listings['room_type'].unique()
    options = np.insert(options, 0, 'Any')
    st.write("Which type of Airbnb would you like to stay in?")
    room_types = st.selectbox("Airbnb Type:", options)
    if room_types == 'Any':
        types = data  # if statement to output all options if all is chosen
    else:
        types = data[data['room_type'] == room_types]  # else choose only the option selected
    return types


def min_nights(data):  # Ensures the number of nights is equal to or greater than the minimum requirement of the Air BnB
    opt = data[stay.days >= data['minimum_nights']][stay.days <= data['maximum_nights']]
    return opt


def price_range(data):  # creates a slider for max price after filtering all criteria and outputing options
    st.write("Price per night")
    if data['price'].empty:
        st.error("No available options. Change criteria")  # if criterias chosen result in no options
    else:
        minimum = int(data['price'].min())
        maximum = int(data['price'].max())
        lower, upper = st.slider("Range", minimum, maximum, (minimum, maximum+1))  # ensures than when min and max is the same, there is no error
        lower = int(lower)
        upper = int(upper)
        global ranges
        ranges = data[data['price'] <= upper][data['price'] >= lower][data['availability_365'] != 0][['id', 'name', 'neighbourhood_cleansed', 'price', 'room_type','availability_365']]  # ensures AirBnB is available
        ranges = ranges.sort_values(by=['price']).reset_index().drop('index', axis=1)  # sorts in terms of  lowest price and resets the index
        # and then drops the original index column that way the options will be numbers from 0 onwards
        st.subheader("Below are the options according to the filters chosen:")
        st.dataframe(ranges)
        st.write('Number of Options:', len(ranges))
        return ranges


def neighborhood(data):
    st.write("Which neighbourhood are you looking for?")
    neighborhoods = list(pd.Series(LA_listings['neighbourhood_cleansed'].unique()).append(pd.Series('All')).sort_values())  # adding an all function for the neighborhood in case user has no preferance
    area = st.selectbox('Neighborhood:', neighborhoods, index=5)  # sets default value to value with index 5 which is 'All'
    if area == 'All':
        neighborhood_data = data
    else:
        neighborhood_data = data[data['neighbourhood_cleansed'] == area]
    return neighborhood_data


def room_finder():
    st.title("LET'S FIND THE AIR BNB OF YOUR DREAMS!")
    dates()
    list_data = price_range(neighborhood(room(min_nights(LA_listings))))
    figure = sns.catplot(list_data["room_type"], kind='count',data=list_data, height=9)
    figure.set(xlabel='Type of Room', ylabel='Count of Rooms')
    figure.fig.suptitle('Count of the Types of Rooms Available')
    st.pyplot(figure)
# page 3


def profile(ids, data):
    st.title("Learn more about your Air BnB")

    # choosing which Airbnb ID
    global chosen_id
    st.write('**Choose the AirBnB ID**')
    chosen_id = st.selectbox("", ids)

    # assigning variables
    id_filter = data[data['id'] == chosen_id]  # filters the dataset to simplify the following code
    host_name = id_filter['host_name'].iloc[0]  # obtains host name - we have to use iloc because it returns a series with only 1 object which would have index 0
    host_since = id_filter['host_since'].iloc[0].year
    superhost = id_filter['host_is_superhost'].iloc[0]
    name = id_filter['name'].iloc[0]  # obtains Air BnB name
    neighborhood_name = id_filter['neighbourhood_cleansed'].iloc[0]  # obtains neighborhood
    room_type = id_filter['room_type'].iloc[0]  # obtains room type
    amenities = id_filter['amenities'].iloc[0][2:-2].replace('\", \"',', ')  # obtains the amenities and formats the output
    price = id_filter['price'].iloc[0]  # obtains price per night
    accommodation = int(id_filter['accommodates'].iloc[0])  # obtains the number of people that can stay
    baths = id_filter['bathrooms'].iloc[0]   # obtains the number of bathrooms it has
    beds = int(id_filter['beds'].iloc[0])  # obtains the number of beds it has
    min_night = int(id_filter['minimum_nights'].iloc[0])  # obtains minimum nights
    min_cost = float(price)*float(min_night)  # calculates minimum cost for stay

    # creating output
    st.subheader('***About the Host***')
    st.write(f"**Name of Host:** {host_name}")
    st.write(f"**Host since:** {str(host_since)}")
    if superhost == 't':
        st.write("**Superhost:** Yes")
    elif superhost == 'f':
        st.write("**Superhost:** No")
    else:
        st.write("**Superhost:** Unknown")
    st.subheader('***About the Property***')
    st.write(f"**Air BnB Name:** {name}")
    st.write(f"**Room Type:** {room_type}")
    st.write(f'**Amenities:** {amenities}')
    if beds == 1:
        st.write(f"**Number of Beds:** {beds} bed")
    elif beds == 0:
        st.write(f"**Number of Beds:** Unknown")
    else:
        st.write(f"**Number of Beds:** {beds} beds")
    st.write(f"**Number of Baths:** {baths}")
    if accommodation == 1:
        st.write(f"**Maximum number of guests:** {accommodation} person")
    else:
        st.write(f"**Maximum number of guests:** {accommodation} people")
    st.write(f"**Price Per Night:** ${price:,.2f} per night")
    if min_night == 1:
        st.write(f"**Minimum Number of Nights:** {min_night} night")
    else:
        st.write(f"**Minimum Number of Nights:** {min_night} nights")
    st.write(f"**Neighborhood:** {neighborhood_name}")
    st.subheader(f"**Minimum Cost:** ${min_cost:,.2f}")

# main code


def main():
    page = st.sidebar.radio("Navigation", navigation)
    if page == "Home":
        homepage()
    if page == "Air BnB Finder":
        room_finder()
    if page == "Air BnB Profile":
        profile(LA_listings['id'], LA_listings)


main()
