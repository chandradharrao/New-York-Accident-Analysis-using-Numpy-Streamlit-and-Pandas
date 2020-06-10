import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("Motor_Vehicle_Collisions_-_Crashes.csv")
st.title("Motor vehicle collision in New York")
st.markdown("This is a streamlit applictaion used to monitor and analyse  motor vehicle collisions in NYC")


#since we dont want to do this computaion over and over again we use the decorator fucntion:
@st.cache(persist = True)
def load_data(nrows):
    #we need to set the data type of the columns CRASH_DATE and CRASH_TIME as datetype or else it will be stored as string type
    data = pd.read_csv(DATA_URL,nrows = nrows,parse_dates = [['CRASH_DATE','CRASH_TIME']])
     #we use df.dropna(subset,inplace) to drop rows under the columns mentioned in the subset with empty or NaN values for either longitude or latitude
    data.dropna(subset = ['LATITUDE','LONGITUDE'],inplace = True)
    #we want to rename all column names to lower case
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase,axis = 'columns',inplace = True) 
    #we want to rename the long column name into smaller one
    data.rename(columns = {"crash_date_crash_time":"date/time"},inplace = True)
    return data
 
#loading 100K rows in it
data=load_data(100000)
original_data = data
#data manipulation:
st.header("Map showing locaton of injuries based on your choice of count")
max_injury = data["injured_persons"].max()
min_injury = data["injured_persons"].min()
injured_people = st.slider( "Count of injured persons in vehicle collisions",min_injury,max_injury)
#we are using data.query() to get the clatitude and longitude values of columns with injured_persons >= slider value represented by @
st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how = "any"))

st.header("Number of collisions in a time of a day")
hour = st.slider("Which hour of the day?",0,23)
data = data[data['date/time'].dt.hour == hour] #parsing the df by selecting only those columns which have hour of collision same as that mentioned by user
st.markdown("Vehicle collision between {}:00 and {}:00".format(hour,hour+1))

#co-ordinates for the initial view state should be somewhere in Ny ad not the world map
midpoint = np.average(data['latitude']), np.average(data['longitude'])
#creating a pydeck figure(an empty 3D map)
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude":midpoint[0],
        "longitude":midpoint[1],
        "zoom":11,
        "pitch":75#refers to the camera angle of view for a 3D plot
        }, #creating a 3D layer on top of the map/fig
    layers = [pdk.Layer (
        "HexagonLayer",
        data = data[["date/time","longitude","latitude"]],
        get_position = ['longitude','latitude'],
        radius = 100, #radius of the hexagon
        extruded = True, #makes the hexagonal 3D bars
        pickable = True,
        elevation_scale = 4,
        elevation_range = [0,1000]
        )]
    ))

st.header("Breakdown by minute between {}:00 and {}:00".format(hour,hour+1))
#trying to get rows which satisfy both the conditions
filtered = data[(data["date/time"].dt.hour>=hour) & (data["date/time"].dt.hour<(hour+1))]
#creating a histogram
hist = np.histogram(filtered['date/time'].dt.minute,bins = 60,range = (0,60))[0] #this contans the frequency of accidents in each minutes
chart_data = pd.DataFrame({"minute":range(0,60),"crashes":hist})
#creating the bar chart
fig = px.bar(chart_data,x = "minute", y = "crashes",hover_data = ["minute","crashes"],height = 400)
st.write(fig)

st.header("Top 5 dangerous streets affected by type")
select = st.selectbox("Affected type of people",["Pedestrians","Cyclists","Motorists"])
if (select == "Pedestrian"):
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by = ["injured_pedestrians"],ascending = False).dropna(how = "any")[:5])
elif (select == "Cyclists"):
    st.write(original_data.query("injured_cyclists >=1")[["on_street_name","injured_cyclists"]].sort_values(by = ["injured_cyclists"],ascending = False).dropna(how = "any")[:5])
elif (select == "Motorists"):
    st.write(original_data.query("injured_motorists >=1")[["on_street_name","injured_motorists"]].sort_values(by = ["injured_motorists"],ascending = False).dropna(how = "any")[:5])
    
#now displaying the data only if check box is clicked
if (st.checkbox("Show Raw Data",False)):
    st.subheader("Raw Data")
    st.write(data)
