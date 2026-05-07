#Importing the required modules

import pandas as pd
import yfinance as yf # A Python library for downloading historical market data from Yahoo! Finance
from bs4 import BeautifulSoup # To parse the html data.
import requests # To get the data from the URL.
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

# --------------------------------------------------------------
#          NETFLIX STOCK DATA USING yfinance API
# --------------------------------------------------------------

netflix=yf.Ticker('NFLX')
netflix_data=netflix.history(period='max')
netflix_data.reset_index(inplace=True)

netflix_data=netflix_data[['Date','Open','High','Low','Close','Volume']]
# Now the dataset contain the Date, High, Low, Close, Volume data only..

netflix_data['Date']=pd.to_datetime(netflix_data['Date'])
print(netflix_data.tail()) #We have 6025 rows in the netflix stock data

# -------------------------------
#    SAVE DATA AS CSV FILE
# -------------------------------

netflix_data.to_csv("netflix_stock.csv",index=False)


# -------------------------------------------------------------------------------------------------------------------------
#----------------------REVENUE DATA OF NETFLIX USING WEB SCRAPPING--------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------

# URL for Netflix revenue
url = "https://www.macrotrends.net/stocks/charts/NFLX/netflix/revenue"

# Headers to avoid 403
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

# Send request
response = requests.get(url, headers=headers)

# Parse HTML
soup = BeautifulSoup(response.text, "html.parser")

# Find all tables
tables = soup.find_all("table")

print("Number of tables found:", len(tables))  # Debug

# Pick correct table safely
target_table = None
for table in tables:
    if "Revenue" in str(table):
        target_table = table
        break

# Create dataframe, initialize as empty
netflix_revenue = pd.DataFrame(columns=["Date", "Revenue"])

if target_table: # Check if target_table was found
    # Extract rows safely
    for row in target_table.tbody.find_all("tr"):
        cols = row.find_all("td")

        if len(cols) < 2:
            continue

        date = cols[0].text.strip()
        revenue = cols[1].text.strip()

        netflix_revenue.loc[len(netflix_revenue)] = [date, revenue]

    # Clean revenue
    netflix_revenue["Revenue"] = netflix_revenue["Revenue"].str.replace(",", "", regex=False)
    netflix_revenue["Revenue"] = netflix_revenue["Revenue"].str.replace("$", "", regex=False)

    # Remove empty rows
    netflix_revenue = netflix_revenue[netflix_revenue["Revenue"] != ""]

    # Convert types
    if not netflix_revenue.empty: # Only convert if there's data after cleaning
        netflix_revenue["Revenue"] = netflix_revenue["Revenue"].astype(float)
        netflix_revenue["Date"] = pd.to_datetime(netflix_revenue["Date"])

    # Sort
    netflix_revenue = netflix_revenue.sort_values(by="Date")

    print(netflix_revenue.head())
else:
    print("Warning: Expected revenue table not found in the scraped content for Netflix.")
    print("Initializing netflix_revenue as an empty DataFrame.")


#-------------------------------------------------------------------------------------------------
#Code to obtain the Netflix revenue data using yfinance (if the web scrapping is not working)
#-------------------------------------------------------------------------------------------------

#-----------------------------------
# LOAD NETFLIX DATA
#-----------------------------------

netflix = yf.Ticker("NFLX")

# Get quarterly financial data
quarterly_financials = netflix.quarterly_financials
# Transpose data (dates become rows)
quarterly_financials = quarterly_financials.T
# Reset index
quarterly_financials.reset_index(inplace=True)
# Rename columns
quarterly_financials.rename(columns={"index": "Date"}, inplace=True)

#-----------------------------------
# EXTRACT REVENUE
#-----------------------------------

# Check available columns
print(quarterly_financials.columns)
# Extract Total Revenue
netflix_revenue = quarterly_financials[['Date', 'Total Revenue']]
# Rename column
netflix_revenue.rename(columns={"Total Revenue": "Revenue"}, inplace=True)


#-----------------------------------
#  DATA CLEANING
#-----------------------------------

#Drop all the duplicate values
netflix_revenue=netflix_revenue.drop_duplicates()
#Drop all the NaN values
netflix_revenue=netflix_revenue.dropna()

#Remove empty space
netflix_revenue = netflix_revenue[netflix_revenue['Revenue'].astype(str).str.strip() != ""]
#Convert Revenue into float
netflix_revenue['Revenue'] = netflix_revenue['Revenue'].astype(float)
#formatting of date using to_datetime()
netflix_revenue['Date'] = pd.to_datetime(netflix_revenue['Date'],utc=True).dt.tz_localize(None)
#Sort the data
netflix_revenue = netflix_revenue.sort_values(by='Date')
#Reset index
netflix_revenue.reset_index(drop=True, inplace=True)
print(netflix_revenue)

#-----------------------------------
# SAVE CSV
#-----------------------------------

netflix_revenue.to_csv("netflix_revenue.csv", index=False)

#---------------------------------------------------------------------------------------------------------
#                   DATA VISUALISATION (NETFLIX STOCK AND REVENUE)
#---------------------------------------------------------------------------------------------------------

# -------------------------------
# LOAD DATA
# -------------------------------

nflx_stock = pd.read_csv("netflix_stock.csv")
nflx_revenue = pd.read_csv("netflix_revenue.csv")

# -------------------------------
# CLEAN DATA
# -------------------------------

nflx_stock['Date'] = pd.to_datetime(
    nflx_stock['Date'],
    utc=True
).dt.tz_localize(None)

nflx_revenue['Date'] = pd.to_datetime(
    nflx_revenue['Date']
)

# -------------------------------
# MOVING AVERAGE
# -------------------------------

nflx_stock['MA_30'] = nflx_stock['Close'].rolling(30).mean()

# -------------------------------
# CREATE INTERACTIVE SUBPLOTS
# -------------------------------

fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    subplot_titles=(
        "Netflix Stock Price + Moving Average",
        "Netflix Revenue Growth",
        "Trading Volume"
    )
)

# -------------------------------
# STOCK PRICE
# -------------------------------

fig.add_trace(
    go.Scatter(
        x=nflx_stock['Date'],
        y=nflx_stock['Close'],
        mode='lines',
        name='Stock Price',
        line=dict(width=2)
    ),
    row=1,
    col=1
)

# -------------------------------
# MOVING AVERAGE
# -------------------------------

fig.add_trace(
    go.Scatter(
        x=nflx_stock['Date'],
        y=nflx_stock['MA_30'],
        mode='lines',
        name='30-Day MA',
        line=dict(dash='dot')
    ),
    row=1,
    col=1
)

# -------------------------------
# REVENUE
# -------------------------------

fig.add_trace(
    go.Scatter(
        x=nflx_revenue['Date'],
        y=nflx_revenue['Revenue'],
        mode='lines+markers',
        name='Revenue'
    ),
    row=2,
    col=1
)

# -------------------------------
# VOLUME
# -------------------------------

fig.add_trace(
    go.Bar(
        x=nflx_stock['Date'],
        y=nflx_stock['Volume'],
        name='Volume',
        opacity=0.5
    ),
    row=3,
    col=1
)

# -------------------------------
# LAYOUT
# -------------------------------

fig.update_layout(
    title=" Netflix Interactive Dashboard",
    height=900,
    hovermode='x unified',
    template='plotly_dark'
)

fig.show()


