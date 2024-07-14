import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objs as go
from collections import Counter

# Set page layout to Wide
st.set_page_config(layout="wide")

# Define the time frame choices and corresponding time deltas
timeFrameChoices = {
    '1D': timedelta(days=1),
    '1W': timedelta(days=5),
    '1M': timedelta(days=30),
    '3M': timedelta(days=90),
    '6M': timedelta(days=180),
    'YTD': None,  # Special case handled separately
    '1Y': timedelta(days=365),
    '2Y': timedelta(days=2 * 365),
    '5Y': timedelta(days=5 * 365),
    '10Y': timedelta(days=10 * 365),
    'MAX': None  # Special case handled separately
}

# Load the ticker symbols from a CSV file
tickersFile = pd.read_csv('constituents.csv')
tickerList = tickersFile.iloc[:, 0].tolist()

# Function to determine the start date based on the selected timeframe
def get_start_date(timeframe):
    today = datetime.now()
    if timeframe == 'YTD':
        return datetime(today.year, 1, 1)
    elif timeframe == 'MAX':
        return datetime(1900, 1, 1)  # Arbitrary old date for maximum data
    else:
        return today - timeFrameChoices[timeframe]

# Formatting function for displaying options
def format_func(option):
    return option

# Main Streamlit app
st.title('Stock Details')
stock = st.selectbox('Choose a stock', tickerList, placeholder="...", index=39)

if stock:
    timeframe = st.selectbox('Choose a timeframe', options=list(timeFrameChoices.keys()), format_func=format_func, index=5)
    end_time = datetime.now()
    start_time = get_start_date(timeframe)

    ticker = yf.download(stock, start=start_time, end=end_time)
    tickerInfo = yf.Ticker(stock)

    # Create a stock price chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ticker.index, y=ticker['Close'], mode='lines', name=f'{stock} Close'))

    stock2 = st.selectbox('Choose a stock to compare with', tickerList, placeholder="...", index=None)

    if stock2:
        ticker2 = yf.download(stock2, start=start_time, end=end_time)
        tickerInfo2 = yf.Ticker(stock2)
        fig.add_trace(go.Scatter(x=ticker2.index, y=ticker2['Close'], mode='lines', name=f'{stock2} Close', line=dict(color='crimson')))

    fig.update_layout(
        title=f'{stock} Stock Price' + (f' vs {stock2} Stock Price' if stock2 else ''),
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_tickformat='%d %b %y'  # Format x-axis ticks as Day Month Year (e.g., 01 Jan 20)
    )

    st.plotly_chart(fig)

    if timeframe == '1D':
        st.markdown(''':gray[Please note that if Market is closed, 1D will show nothing]''')

    # Sidebar information
    # Dataset 1 - Company Name, Symbol, Exchange Type, Sector, and Industry
    informationSetData = pd.DataFrame(
        [tickerInfo.info['longName'], tickerInfo.info['symbol'], tickerInfo.info['exchange'], tickerInfo.info['sector'], tickerInfo.info['industry']],
        index=["Company Name", "Ticker", "Exchange", "Sector", "Industry"],
        columns=[""])
    informationSet = pd.DataFrame(data=informationSetData, index=["Company Name", "Ticker", "Exchange", "Sector", "Industry"])

    # Dataset 2 - Stock Opening Price, Closing Price, 24/hr High & Low, 52/week High & Low, Volume, & Market Cap
    metricsSetData = pd.DataFrame(
        [tickerInfo.info['open'], tickerInfo.info['previousClose'], tickerInfo.info['dayHigh'], tickerInfo.info['dayLow'], tickerInfo.info['fiftyTwoWeekHigh'], tickerInfo.info['fiftyTwoWeekLow'], tickerInfo.info['volume'], tickerInfo.info['marketCap']],
        index=["Open", "Previous Close", "Day High", "Day Low", "52-Week High", "52-Week Low", "Volume", "Market Cap"],
        columns=[""])
    metricsSet = pd.DataFrame(data=metricsSetData, index=["Open", "Previous Close", "Day High", "Day Low", "52-Week High", "52-Week Low", "Volume", "Market Cap"])

    # Dataset 3 - Firm Name, Grade Dates, and Grades Formed
    predictionSet = tickerInfo.upgrades_downgrades.rename(columns={'GradeDate': 'Date Graded', 'ToGrade': 'Current Grade', 'FromGrade': 'Previous Grade'}).drop(columns=['Action'])

    completeDataSet = [informationSet, metricsSet]
    completeDataSetTile = pd.concat(completeDataSet)

    with st.sidebar:
        st.title(f"{tickerInfo.info['symbol']} - {tickerInfo.info['shortName']}")
        st.write(completeDataSetTile)
        st.write(predictionSet)

        # Extract the 'Current Grade' column as a list of strings
        grades = predictionSet['Current Grade'].head(15).tolist()

        # Tokenize the words in the column
        words = [word for grade in grades for word in grade.split()]

        # Count the occurrences of each word
        word_counts = Counter(words)

        # Find the most common word
        most_common_word, most_common_count = word_counts.most_common(1)[0]

        st.write(f"The current consensus between experts is '{most_common_word}' with {most_common_count} occurrences out of the most recent 15.")

        if stock2:
            st.title(f"{stock2} - {tickerInfo2.info['shortName']}")

            # Sidebar Datasets for second stock
            # Dataset 1 - Company Name, Symbol, Exchange Type, Sector, and Industry
            informationSetData2 = pd.DataFrame(
                [tickerInfo2.info['longName'], tickerInfo2.info['symbol'], tickerInfo2.info['exchange'], tickerInfo2.info['sector'], tickerInfo2.info['industry']],
                index=["Company Name", "Ticker", "Exchange", "Sector", "Industry"],
                columns=[""])
            informationSet2 = pd.DataFrame(data=informationSetData2, index=["Company Name", "Ticker", "Exchange", "Sector", "Industry"])

            # Dataset 2 - Stock Opening Price, Closing Price, 24/hr High & Low, 52/week High & Low, Volume, & Market Cap
            metricsSetData2 = pd.DataFrame(
                [tickerInfo2.info['open'], tickerInfo2.info['previousClose'], tickerInfo2.info['dayHigh'], tickerInfo2.info['dayLow'], tickerInfo2.info['fiftyTwoWeekHigh'], tickerInfo2.info['fiftyTwoWeekLow'], tickerInfo2.info['volume'], tickerInfo2.info['marketCap']],
                index=["Open", "Previous Close", "Day High", "Day Low", "52-Week High", "52-Week Low", "Volume", "Market Cap"],
                columns=[""])
            metricsSet2 = pd.DataFrame(data=metricsSetData2, index=["Open", "Previous Close", "Day High", "Day Low", "52-Week High", "52-Week Low", "Volume", "Market Cap"])

            # Dataset 3 - Firm Name, Grade Dates, and Grades Formed
            predictionSet2 = tickerInfo2.upgrades_downgrades.rename(columns={'GradeDate': 'Date Graded', 'ToGrade': 'Current Grade', 'FromGrade': 'Previous Grade'}).drop(columns=['Action'])

            completeDataSet2 = [informationSet2, metricsSet2]
            completeDataSetTile2 = pd.concat(completeDataSet2)

            st.write(completeDataSetTile2)
            st.write(predictionSet2)

            # Extract the 'Current Grade' column as a list of strings
            grades = predictionSet2['Current Grade'].head(15).tolist()

            # Tokenize the words in the column
            words = [word for grade in grades for word in grade.split()]

            # Count the occurrences of each word
            word_counts = Counter(words)

            # Find the most common word
            most_common_word, most_common_count = word_counts.most_common(1)[0]

            st.write(f"The current consensus between experts is '{most_common_word}' with {most_common_count} occurrences out of the most recent 15.")
