#Importing the required modules

import pandas as pd
import yfinance as yf # A Python library for downloading historical market data from Yahoo! Finance
from bs4 import BeautifulSoup # To parse the html data.
import requests # To get the data from the URL.
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# --------------------------------------------------------------
#     GAMESTOP STOCK DATA USING yfinance API
# --------------------------------------------------------------

gme=yf.Ticker("GME")

# -------------------------------
# CREATE DATASET USING hisotry()
# -------------------------------

gme_data=gme.history(period='max')
gme_data.reset_index(inplace=True)
#reset the index

gme_data=gme_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
# Now the dataset contain the Date, High, Low, Close, Volume data only..

gme_data['Date']=pd.to_datetime(gme_data['Date'])
print(gme_data.tail()) # We have 6094 rows in the gme stock data

# -------------------------------
#  SAVE DATASET AS CSV FILE
# -------------------------------
gme_data.to_csv("gme_stock.csv",index=False)

# --------------------------------------------------------------
#      GameStop REVENUE DATA RETREIVAL USING WEB SCRAPPING
# --------------------------------------------------------------

url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/stock.html"

tables = pd.read_html(url)

# Check tables
print(len(tables))

# Usually GameStop revenue is in one of the tables
gme_revenue = tables[1]   # adjust if needed

print(gme_revenue.head())
gme_revenue.columns = ["Date", "Revenue"]

# Remove $ and commas
gme_revenue["Revenue"] = gme_revenue["Revenue"].astype(str)
gme_revenue["Revenue"] = gme_revenue["Revenue"].str.replace("$", "", regex=False)
gme_revenue["Revenue"] = gme_revenue["Revenue"].str.replace(",", "", regex=False)

# Remove empty rows
gme_revenue = gme_revenue[gme_revenue["Revenue"] != ""]

# Convert types
gme_revenue["Revenue"] = gme_revenue["Revenue"].astype(float)
gme_revenue["Date"] = pd.to_datetime(gme_revenue["Date"])
gme_revenue.to_csv("gme_revenue.csv",index=False)

# --------------------------------------------------------------
#      DATA VISUALISATION USING PLOTLY
# --------------------------------------------------------------

#Features of the dashboard:
#candlestick
#Volumne bars
#Revenue comparison (Secondary axis)
#Range selector (6m, 1y, 5y)
#hover+zoom+toggle


# -------------------------------
# LOAD DATA
# -------------------------------
gme_data = pd.read_csv("gme_stock.csv")
gme_revenue = pd.read_csv("gme_revenue.csv")

# Convert Date
gme_data['Date'] = pd.to_datetime(gme_data['Date'], utc=True).dt.tz_localize(None)
gme_revenue['Date'] = pd.to_datetime(gme_revenue['Date'], utc=True).dt.tz_localize(None)

# Sort
gme_data = gme_data.sort_values("Date")
gme_revenue = gme_revenue.sort_values("Date")

# -------------------------------
# CREATE ADVANCED SUBPLOTS
# -------------------------------
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    specs=[[{"secondary_y": True}], [{}]],
    subplot_titles=("Stock Price + Revenue", "Trading Volume")
)

# Candlestick (PRO)
fig.add_trace(go.Candlestick(
    x=gme_data['Date'],
    open=gme_data['Open'],
    high=gme_data['High'],
    low=gme_data['Low'],
    close=gme_data['Close'],
    name="Stock Price"
), row=1, col=1, secondary_y=False)

#  Revenue (secondary axis)
fig.add_trace(go.Scatter(
    x=gme_revenue['Date'],
    y=gme_revenue['Revenue'],
    mode='lines+markers',
    name='Revenue',
    line=dict(width=3, dash='dot')
), row=1, col=1, secondary_y=True)

#  Volume bars
fig.add_trace(go.Bar(
    x=gme_data['Date'],
    y=gme_data['Volume'],
    name='Volume',
    opacity=0.5
), row=2, col=1)

# -------------------------------
# LAYOUT MAGIC
# -------------------------------
fig.update_layout(
    title=" GameStop Advanced Interactive Dashboard",
    height=850,
    hovermode="x unified",
    template="plotly_dark",   #  Dark theme (looks premium)

    # Range selector
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    )
)

# Axis labels
fig.update_yaxes(title_text="Stock Price", secondary_y=False)
fig.update_yaxes(title_text="Revenue", secondary_y=True)

# -------------------------------
# SHOW + SAVE
# -------------------------------
fig.show()

#  Save as interactive HTML (VERY IMPORTANT)
fig.write_html("gme_dashboard.html")
