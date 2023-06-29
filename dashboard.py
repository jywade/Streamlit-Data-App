import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import openpyxl
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Welcome to my data science project!")
st.markdown("### Sample Superstore EDA")

# Adding CSS style to streamlit page (shifting title to top left)

st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))

if fl is not None:
    # Save the uploaded file locally
    file_path = os.path.join("uploads", fl.name)  # Save the file in a directory named "uploads"
    with open(file_path, "wb") as f:
        f.write(fl.getbuffer())

    # Read the file using pandas
    df = pd.read_excel(file_path)
else:
    ss = os.path.join(r"C:\Users\ZION\Downloads\Sample - Superstore(new).xlsx")
    df = pd.read_excel(ss)

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])


# Getting the min and max date for customization in streamlit dashboard

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1: 
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

### Filter the data based on region, state, and city

st.sidebar.header("Choose your filter: ")
region = st.sidebar.multiselect("Choose Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else: 
    df2 = df[df["Region"].isin(region)]

# State

state = st.sidebar.multiselect("Choose State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# City

city  = st.sidebar.multiselect("Choose City", df3["City"].unique())
if not city:
    df4 = df3.copy()
else:
    df4 = df3[df3["City"].isin(city)]

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif state and region:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else: 
    filtered_df =  df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

# Create bar chart for category 

category_df = filtered_df.groupby(by = ["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category by Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = "plotly")
    st.plotly_chart(fig, use_container_width=True, height = 200)

# Create pie chart for region

with col2:
    st.subheader("Sales by Region")
    fig = px.pie(filtered_df, values = "Sales", names="Region", hole=0.5, template= "plotly_dark")
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

# Create dropdown to download the data

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap = "Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name= "Category.csv", mime= "text/csv",
                           help= 'Click here to download the data as a CSV file')

with cl1:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap = "Greens"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name= "Region.csv", mime= "text/csv",
                           help= 'Click here to download the data as a CSV file')
        
# Create Time Series Analysis Line Chart

filtered_df["Month & Year "] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["Month & Year "].dt.strftime(" %Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x= "Month & Year ", y= "Sales", labels= {"Sales" : "Amount "}, height= 500, width= 1000, template="plotly")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Time Series:"):
    st.write(linechart.T.style.background_gradient(cmap = "Blues"))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name= "TimeSeries.csv", mime='text/csv',
                       help= "Click here to download the data as a CSV file") 
    
# Create a treemap based on Region, category, sub-category

st.subheader("Hierarchical View of Sales Using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region", "Category", "Sub-Category"], values= "Sales", hover_data= ["Sales"],
                  color = "Sub-Category", template="plotly_dark")
fig3.update_layout(width = 800, height =650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)
with chart1: 
    st.subheader("Sales by Segment")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template= "plotly")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2: 
    st.subheader("Sales by Category")
    fig = px.pie(filtered_df, values="Sales", names="Category", template= "plotly_white")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)
#-----------------------------------------------------------------------------------------
import plotly.figure_factory as ff
st.subheader(":point_right: Sub-Category Sales by Month Summary")
with st.expander("Summary Table"):
    df_sample = df[:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Sub-Category by Month Table")
    filtered_df["Month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index=["Sub-Category"], columns="Month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

    # Create a scatter plot

data1 = px.scatter(filtered_df, x = "Sales", y="Profit", size= "Quantity", template="plotly")
data1['layout'].update(title="Relationship Between Sales & Profits",
                           titlefont= dict(size=20), xaxis= dict(title="Sales", titlefont=dict(size=17)),
                           yaxis = dict(title="Profit", titlefont = dict(size=17)))
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Greens"))

# Download original dataset

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Original Dataset", data=csv, file_name= "Dataset.csv", mime='text/csv',
                   help="Click here to download the original dataset as a CSV file")