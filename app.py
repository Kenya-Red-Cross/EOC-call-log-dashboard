'''
This is a streamlit dashboard app for visualizing call log data from KRCS EOC centre.
For queries and comments react out to datateam@redcross.or.ke

Created by: hindada.boneya@icha.net
'''


import streamlit as st
import pandas as pd 
from datetime import date
import numpy as np
from PIL import Image
import plotly.express as px
import gspread
from google.oauth2 import service_account
import plotly.graph_objects as go

st.set_page_config(
        page_title="EOC Call log Dashboard",
        page_icon=  Image.open ('resources/krcs-favicon-96x96.png')
    )


scopes=[ "https://www.googleapis.com/auth/spreadsheets",
        'https://www.googleapis.com/auth/drive']


credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes= scopes)


gc = gspread.authorize(credentials)

headers = ["Date", "Time", "Gender","County","Region","Purpose","Intervention","Status"]

sheet_name = st.secrets["sheet_name"]

@st.cache(ttl = 3600)
def get_data ():

    work_sheet = gc.open(sheet_name)
    ws = work_sheet.get_worksheet(0)

    values = ws.get_all_values()


    data = zip(*(e for e in zip(*values) if e[0] in headers))
    df = pd.DataFrame(data)



    df.columns = df.iloc[0]
    df = df.iloc[1:].reset_index(drop=True)
    df = df.mask(df=="")
    df['Date']= pd.to_datetime(df['Date'], errors='coerce')

    return df


#run the get_data function and store the resukts in a df
df = get_data ()





#session state defined if it doesn't exist

if "my_data"  not in st.session_state :
    st.session_state.my_data = ''






#Sidebar content

# Date filter

oldest_date = (df.Date.min())
latest_date =  (df.Date.max())


oldest_date = oldest_date.date()
latest_date = latest_date.date()


st.sidebar.header("Filter by date:")

start_date = st.sidebar.date_input ("Start Date:", value = oldest_date, min_value= oldest_date, max_value = latest_date)

end_date = st.sidebar.date_input ("End Date:", value = latest_date, min_value= oldest_date, max_value = latest_date)


if (start_date and end_date):
    if (start_date == oldest_date) & (end_date == latest_date):
        pass

    elif end_date > start_date:
        
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")


        df = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    else:
        st.sidebar.write("Start date cannot be greater than end date!")  




st.sidebar.subheader ("Filter by Categories:")

# Purpose filter   

opts = (df['Purpose'].unique())
opts = [x for x in opts if pd.isnull(x) == False and x != 'nan']
options = np.append(opts,'All')


index = (len (options))-1

purpose_choice = st.sidebar.selectbox("Purpose", options, index )



if purpose_choice:
    st.session_state.my_data = purpose_choice


    if (st.session_state.my_data) =='All':
        df = df

    else:
        df = df[df['Purpose']==( st.session_state.my_data)]


# Region filter

opts = df['Region'].unique()
opts = [x for x in opts if pd.isnull(x) == False and x != 'nan']
options = np.append(opts,'All')


index = (len (options))-1

region_choice = st.sidebar.selectbox("Region", options , index)




if region_choice:

    st.session_state.my_data= region_choice

    if (st.session_state.my_data) =='All':
        df = df

    else:
        df = df[df['Region']==(st.session_state.my_data)]



#county filter
opts = df['County'].unique()
options = [x for x in opts if pd.isnull(x) == False and x != 'nan']


index = (len (options))-1

county_choice = st.sidebar.multiselect("County", options )





if county_choice:

    st.session_state.my_data= county_choice

    if (st.session_state.my_data) =='All':
        df = df

    else:
        df = df[df['County'].isin(st.session_state.my_data)]



# Intervention filter

opts= (df['Intervention'].unique())
opts = [x for x in opts if pd.isnull(x) == False and x != 'nan']
options = np.append(opts,'All')


index = (len (options))-1

intervention_choice = st.sidebar.selectbox("Interventions", options, index )


if intervention_choice:
    st.session_state.my_data = intervention_choice


    if (st.session_state.my_data) =='All':
        df = df

    else:
        df = df[df['Intervention']==( st.session_state.my_data)]


# Gender filter

opts = df['Gender'].unique()
opts = [x for x in opts if pd.isnull(x) == False and x != 'nan']
options = np.append(opts,'All')
index = (len (options))-1


gender_choice = st.sidebar.selectbox("Gender", options, index)


if gender_choice:

    st.session_state.my_data = gender_choice


    if (st.session_state.my_data) =='All':
        df = df

    else:
        df = df[df['Gender']==(st.session_state.my_data)]


# Status filter

opts = df['Status'].unique()
opts = [x for x in opts if pd.isnull(x) == False and x != 'nan']
options = np.append(opts,'All')
index = (len (options))-1

status_choice = st.sidebar.selectbox("Status", options, index)


if status_choice:

    st.session_state.my_data = status_choice


    if (st.session_state.my_data) =='All':
        df = df

    else:
        df = df[df['Status']==(st.session_state.my_data)]




# infobox
st.sidebar.subheader("Contribute")
st.sidebar.info(
    "You are welcome to contribute your "
    "comments, questions and resources as "
    "[issues](https://github.com/Kenya-Red-Cross/EOC-call-log-dashboard) or "
    "[pull requests](https://github.com/Kenya-Red-Cross/EOC-call-log-dashboard/pulls) "
    "to the [source code](https://github.com/Kenya-Red-Cross/EOC-call-log-dashboard/blob/main/app.py). "
    "You can also reach out to hindada.boneya@icha.net")


# krcs logo

krcs_logo = Image.open ('resources/KRCS_Logo.png')
st.sidebar.image(krcs_logo, width=250)



# calculations that are needed.

tot_calls = len(df.index)

today_date = date.today().strftime("%Y-%m-%dT%H:%M:%S")
calls_today = len (df[(df['Date'] == today_date)])


calls_by_years = df.set_index('Date').resample('Y')["Gender"].count().to_frame('count').reset_index()
calls_this_year = calls_by_years.loc[len(calls_by_years)-1, 'count']


calls_by_months = df.set_index('Date').resample('MS')["Gender"].count().to_frame('Num of calls').reset_index()

calls_this_month = calls_by_months.loc[len(calls_by_months)-1, 'Num of calls']


calls_by_month_days = df.groupby([df['Date'].dt.month.rename("Month"), df['Date'].dt.day_of_week.rename("Day")]).Gender.agg({'count'}).reset_index()
c_b_m_d = calls_by_month_days.pivot(index="Month", columns=["Day"],values="count")




calls_region = df.Region.value_counts().rename_axis("Region").reset_index(name='Num of calls')


calls_county = df.County.value_counts().rename_axis("County").reset_index(name='Num of calls')

calls_purpose = df.Purpose.value_counts().rename_axis("Purpose").reset_index(name='Num of calls')

calls_purpose['percentage'] = ((calls_purpose['Num of calls'] / calls_purpose['Num of calls'].sum())*100).round(2).astype(str) + ' %'

calls_gender =  df.Gender.value_counts().rename_axis("Gender").reset_index(name='Num of calls')

purpose_gender = df.groupby(['Purpose','Gender']).Gender.count()

purpose_gender = purpose_gender.to_frame('Num of calls').reset_index()

purpose_gender['percentage'] = ((purpose_gender['Num of calls'] / purpose_gender['Num of calls'].sum())*100).round(2).astype(str) + ' %'

region_gender = df.groupby(['Region','Gender']).Gender.count()

region_gender = region_gender.to_frame('Num of calls').reset_index()

region_gender['percentage'] = ((region_gender['Num of calls'] / region_gender['Num of calls'].sum())*100).round(2).astype(str) + ' %'

status_dist = df.Status.value_counts().rename_axis("Status").reset_index(name='Num of calls')

calls_intervention = df.Intervention.value_counts().rename_axis("Interventions").reset_index(name='Num of calls')

calls_intervention['percentage'] = ((calls_intervention['Num of calls'] / calls_intervention['Num of calls'].sum())*100).round(2).astype(str) + ' %'

regions_county = df.groupby(['Region','County']).County.count()

regions_county = regions_county.to_frame('Num of calls').reset_index()

regions_county['percentage'] = ((regions_county['Num of calls'] / regions_county['Num of calls'].sum())*100).round(2).astype(str) + ' %'


# main content of the page

st.title ("EOC Call Log Dashboard")
st.write ("This dashboard visualizes incidents reported through the KRCS EOC call centre. Data comes from a Google sheets endpoint.")
st.write("**Developed by: [ICHA Data Team](http://www.icha.net/data)** ")

st.subheader("Snapshot of the dataset")

st.write(df.head(4))


st.subheader("Quick Stats")

col1, col2, col3, col4, col5  = st.columns (5)


col1.metric(label="Total calls to date:", value= tot_calls)
col2.metric(label="Calls today:", value= calls_today)
col3.metric(label="Calls latest month:", value= calls_this_month)
col4.metric(label="Calls latest year:", value= calls_this_year)




# plotly graphing fuctions defined here

def bar_graph (d, x, y,t,c=None,b=None):
    fig = px.bar (d ,x= x, y = y,text_auto='.3s',color= c, title = t, barmode = b, color_discrete_sequence= ['#ed1b2e'])
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(248, 248, 248, 1)',
        })
    fig.update_traces (textfont_size=12, textangle=0, textposition="inside", cliponaxis=False)
    st.plotly_chart(fig)

def group_bar_graph (d, x, y,t,c=None,b=None):
    fig = px.bar (d ,x= x, y = y,text_auto='.3s',color= c, title = t, barmode = b)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(248, 248, 248, 1)',
        })
    fig.update_traces (textfont_size=12, textangle=0, textposition="inside", cliponaxis=False)
    st.plotly_chart(fig)


def pie_chart (d, v, n,t):
    fig = px.pie (d ,values= v,names = n, title = t)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(248, 248, 248, 1)',
        })
    fig.update_traces ( textposition="inside")
    st.plotly_chart(fig)


def line_graph(d,x,y,t):
    fig = px.line(d, x=x, y=y, title=t, markers=True)
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(248, 248, 248, 1)',
        })
    st.plotly_chart(fig)

def heat_map(d):
    
    fig = px.imshow(d,title='Heat map',labels=dict(x="Day of the week", y="Month", color="Volume of calls"),text_auto=True,aspect="auto",
    x=['Mon','Tue','Wed','Thur','Frid','Sat','Sun'],
    y=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    fig.update_xaxes(side="top")
    st.plotly_chart(fig)

def mytable (df, title):
    fig = go.Figure(
            data = [go.Table (
                header = dict(
                 values = list(df.columns),
                 font=dict(size=12, color = 'white'),
                 fill_color = '#ED1B2E',
                 align = 'left',
                 height=20
                 )
              , cells = dict(
                  values = [df[K].tolist() for K in df.columns], 
                  font=dict(size=12),
                  align = 'left',
                  fill_color='#F0F2F6',
                  height=20))]) 

    fig.update_layout(title_text=title,title_font_color = '#264653',title_x=0,margin= dict(l=0,r=10,b=10,t=30), height=480)
    st.plotly_chart(fig, use_container_width=True)
    


# calling graphing functions with appropraite arguements


st.subheader("Graphical visualizations")

line_graph (calls_by_months, x='Date', y = 'Num of calls', t ="Number of calls per month")

try:
    heat_map (c_b_m_d)
except Exception  as e:
    print (e)


with st.expander("View table"):
    mytable(regions_county, title="")

bar_graph (calls_region , x='Region', y = 'Num of calls', t ="Calls per region")

bar_graph (calls_county, x='County', y = 'Num of calls', t ="Calls per county")

with st.expander("View table"):
    mytable(calls_purpose, title="")

pie_chart (calls_purpose, n='Purpose', v = 'Num of calls', t ="Calls by purpose")

pie_chart (calls_gender, v = 'Num of calls',n ='Gender', t= "Calls by gender")

with st.expander("View table"):
    mytable(region_gender, title="")

group_bar_graph (region_gender, x='Region', y = 'Num of calls', t ="Distribution of calls by region and gender", c='Gender',b='group')

with st.expander("View table"):
    mytable(purpose_gender, title="")

group_bar_graph (purpose_gender, x='Purpose', y = 'Num of calls', t ="Distribution of calls by purpose and gender", c='Gender',b='group')

with st.expander("View table"):
    mytable(calls_intervention, title="")

bar_graph (calls_intervention, x='Interventions', y = 'Num of calls', t ="Interventions applied")

pie_chart (calls_intervention, v = 'Num of calls',n ='Interventions', t= "Interventions applied")

pie_chart (status_dist, v = 'Num of calls',n ='Status', t= "Status of calls")