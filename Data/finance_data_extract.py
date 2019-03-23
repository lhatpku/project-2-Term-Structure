import quandl
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from datetime import datetime
import datetime
import bs4 as bs
import urllib.request
import time
import monthdelta
import sqlite3
from sqlite3 import Error
from config import quandl_API, sql_Password


def get_treasury_yield():

    quandl.ApiConfig.api_key = quandl_API

    # Extract US Treasury Data
    teasury_yield_raw = quandl.get("USTREASURY/YIELD")

    # Display the extracted data in 
    teasury_yield_raw_df = pd.DataFrame(teasury_yield_raw)
    teasury_yield_df = teasury_yield_raw_df.reset_index()

    # Change the column name to import to data base
    old_column_name = teasury_yield_df.columns
    new_column_name = ['_'.join(name.split(' ')[::-1]) for name in old_column_name]
    teasury_yield_df.rename(columns=dict(zip(old_column_name,new_column_name)),inplace=True)
    teasury_yield_df.head()

    # Update id
    teasury_yield_df.index.name = 'id'
    teasury_yield_df.index += 1

    conn = sqlite3.connect('treasury_yield.db')

    teasury_yield_df.to_sql(name='treasury_yield', con=conn, if_exists='replace')

    conn.close()

def get_historical_price(ticker, date1, date2, frequency='1d',display=True):
 
    format_string='%Y-%m-%d %H:%M:%S'
 
    # One day (86400 second) adjustment required to get dates printed to match web site manual output
    _date1 = date1.strftime("%Y-%m-%d 00:00:00")
    date1_epoch = str(int(time.mktime(time.strptime(_date1, format_string)))- 86400)
    
    if display == True: 
        print("")
        print(date1, date1_epoch, " + 86,400 = ", str(int(date1_epoch) + 86400))
 
    _date2 = date2.strftime("%Y-%m-%d 00:00:00")
    date2_epoch = str(int(time.mktime(time.strptime(_date2, format_string))))
    
    if display == True:
        print(date2, date2_epoch)
 
    url = 'https://finance.yahoo.com/quote/' + ticker + '/history?period1=' + date1_epoch + '&period2=' + date2_epoch + '&interval='+frequency+'&filter=history&frequency='+frequency
    source = urllib.request.urlopen(url).read()      
    soup = bs.BeautifulSoup(source,'lxml')
    table_rows = soup.find_all('tr')
      
    extract_table = []
      
    for table_row in table_rows:
        table_row_values = table_row.find_all('td')
        extract_row = [i.text for i in table_row_values]
        extract_table.append(extract_row)        
      
    column_names = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
  
    #extract_table = extract_table[1:-2]
    extract_table_df = pd.DataFrame(extract_table)
    extract_table_df.columns = column_names
    extract_table_df.set_index(column_names[0], inplace=True)
    extract_table_df = extract_table_df.convert_objects(convert_numeric=True)
    extract_table_df = extract_table_df.iloc[::-1]
    extract_table_df.dropna(inplace=True)
      
    return extract_table_df

def get_long_historical_price(ticker, start_date, end_date, frequency='1d',display=True):

    date1 = start_date
    iteration_number = 1

    dfall = {}
    
    while date1 <= end_date:

        if frequency == '1d':      
            month_delta = 3         
        else:          
            if frequency == '1wk':            
                month_delta = 12            
            else:            
                month_delta = 48
                                
        # Create 'date2' in a 60 day Window or less
        date2 = date1 + monthdelta.monthdelta(month_delta)
        date2 = datetime.date(date2.year, date2.month, 1)
        date2 = date2 - datetime.timedelta(days = 1)

        # Do not allow 'date2' to go beyond the 'End Date'
        if date2 > end_date:
            date2 = end_date
            
        # print(f"Processing {date1} thru {date2}.")

        try: 
        
            df = get_historical_price(ticker, date1, date2, frequency, display)  

            if len(df) > 0: 
                
                if iteration_number == 1:
                    dfall = df.copy()
                else:
                    frames = [dfall, df]
                    dfall = pd.concat(frames) 

                iteration_number += 1 
                
            date1 = date1 + monthdelta.monthdelta(month_delta)
            date1 = datetime.date(date1.year, date1.month, 1)
            
        except:
            
            date1 = date1 + monthdelta.monthdelta(month_delta)
            date1 = datetime.date(date1.year, date1.month, 1)
            
    return dfall

def get_bond_price():

    Short_TR_Tickers = ['IEF','DTYL','EDV','TLH']
    Long_TR_Tickers = ['SHV','VGSH','SCHR']

    Short_TR_Data_Dict = {}

    for ticker in Short_TR_Tickers:
        
        # Set up start and end date
        start_date = datetime.date(2000, 1, 2)
        end_date = datetime.date.today()
    
        ticker_df = get_long_historical_price(ticker, start_date, end_date, '1d', False)
        
        Short_TR_Data_Dict = {**Short_TR_Data_Dict,**{ticker:ticker_df}}

    Long_TR_Data_Dict = {}

    for ticker in Long_TR_Tickers:
        
        # Set up start and end date
        start_date = datetime.date(2000, 1, 2)
        end_date = datetime.date.today()
        
        ticker_df = get_long_historical_price(ticker, start_date, end_date, '1d', False)
        
        Long_TR_Data_Dict = {**Long_TR_Data_Dict,**{ticker:ticker_df}}

    total_Data_Dict = {**Short_TR_Data_Dict,**Long_TR_Data_Dict}
    for key,table in total_Data_Dict.items():
        table.rename(columns={'Adj Close':'Adj_Close'},inplace=True)
        table_name = table.columns
        for name in table_name:
            table[name] = table[name].apply(lambda x: float(x.replace(',','').replace('-','0')) if isinstance(x,str) else x)
        table = table.reset_index()
        table['Ticker'] = key
        table['Date'] = table['Date'].apply(lambda x: datetime.datetime.strptime(x,'%b %d, %Y').date())
        total_Data_Dict[key] = table

    iteration = 1
    for key,table in total_Data_Dict.items():
        if iteration == 1:
            agg_table = table.copy()
        else:
            agg_table = pd.concat([agg_table,table],ignore_index=True)
        iteration += 1

    agg_table.index.name = 'id'
    agg_table.index += 1

    conn = sqlite3.connect('bond_prices.db')
    agg_table.to_sql(name='bond_prices', con=conn, if_exists='replace')
    conn.close()







