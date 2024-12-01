"""
bitcoin_etl
DAG auto-generated by Astro Cloud IDE.
"""

from airflow.decorators import dag
from astro import sql as aql
import pandas as pd
import pendulum

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook


@aql.dataframe(task_id="python_1")
def python_1_func():
    from airflow.operators.python import get_current_context
    
    
    context = get_current_context()
    start_date = context['dag'].start_date
    print(f"DAG start date: {start_date}")
    
    
    # Define the time range for yesterday
    end_time = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=1)
    
    # Convert to Unix timestamps in milliseconds
    start_timestamp = int(start_time.timestamp() * 1000)
    end_timestamp = int(end_time.timestamp() * 1000)
    
    # CoinCap API endpoint for Bitcoin historical data
    url = 'https://api.coincap.io/v2/assets/bitcoin/history'
    
    # Parameters for the API request
    params = {
        'interval': 'h1',  # Hourly data
        'start': start_timestamp,
        'end': end_timestamp
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()
    
    # Check if data is available
    if 'data' in data:
        # Convert data to pandas DataFrame
        df = pd.DataFrame(data['data'])
        # Convert time column to datetime
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        # Set time as index
        df.set_index('time', inplace=True)
        # Display the DataFrame
        print(df)
    else:
        print("No data available for the specified date range.")
    
    #### Load
    pg_hook = PostgresHook(postgres_conn_id='postgres')
    engine = pg_hook.get_sqlalchemy_engine()
    df.to_sql('bitcoin_history', con=engine, if_exists='append', index=False)
    
    

default_args={
    "email_on_failure": True,
    "owner": "Alex Lopes,Open in Cloud IDE",
}

@dag(
    default_args=default_args,
    schedule="0 0 * * *",
    start_date=pendulum.from_format("2024-11-17", "YYYY-MM-DD").in_tz("UTC"),
    catchup=True,
    owner_links={
        "Alex Lopes": "mailto:alexlopespereira@gmail.com",
        "Open in Cloud IDE": "https://cloud.astronomer.io/cm3webulw15k701npm2uhu77t/cloud-ide/cm42rbvn10lqk01nlco70l0b8/cm44gkosq0tof01mxajutk86g",
    },
)
def bitcoin_etl():
    python_1 = python_1_func()

dag_obj = bitcoin_etl()
