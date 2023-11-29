import pandas as pd
import os
from datetime import datetime, timedelta
import calendar

from categories import store_categories, overall_categories

def clean_checking(df):
    df['date'] = pd.to_datetime(df['Date'])
    df.drop(columns=['Date', 'Running Bal.'], inplace=True)
    df.rename(columns={'Description': 'description', 'Amount': 'amount'}, inplace=True)
    df['account'] = "checking"
    return df

def clean_credit_card(df):
    df['date'] = pd.to_datetime(df['Posted Date'])
    df.drop(columns=['Posted Date', 'Reference Number', 'Address'], inplace=True)
    df.rename(columns={'Payee': 'description', 'Amount': 'amount'}, inplace=True)
    df['account'] = "credit card"
    return df

def create_file(df):
    if df['account'][0] == 'credit card':
        file_name = "transactions." + df['date'].min().strftime('%Y-%m-%d') + "_to_" + df['date'].max().strftime('%Y-%m-%d') + ".csv"
    else:
        file_name = "checking." + df['date'].min().strftime('%Y-%m-%d') + "_to_" + df['date'].max().strftime('%Y-%m-%d') + ".csv"

    # Save the uploaded file to the uploads folder
    df.to_csv("transactions/" + file_name, index=False)

def create_big_df():
    df = pd.DataFrame()
    
    # delete files over 2 years old and combine all of them into one dataset
    files = os.listdir('transactions')
    for file_name in files:
        # Print or perform actions on each file
        if (pd.to_datetime(file_name.split(".")[1].split("_")[0]) - datetime.today()) > timedelta(days=365 * 2):
            os.remove(file_name)
        
        df1 = pd.read_csv("transactions/"+ file_name)
        df = pd.concat([df, df1])
    df = df.dropna(axis=0)
    df = df.drop_duplicates()
    # df.to_csv('transactions/all.csv')

    return df


def add_category_column(df):
    def __mapStoreToCat__(vendor_name):
        vendor_name = vendor_name.replace("-", " ")
        for store_name, category in store_categories.items():
            if store_name in vendor_name:
                return category
        return 'Other'
    
    def __mapCatToMain__(input_category):
        for sub_category, category in overall_categories.items():
            if sub_category in input_category:
                return category
            
        return input_category
    
    df['subcategory'] = df['description'].apply(lambda x: __mapStoreToCat__(x))
    df['category'] = df['subcategory'].apply(lambda x: __mapCatToMain__(x))
    df.loc[(df['amount'] > 0) & (~df['subcategory'].isin(['Credit Card Payment','Transfer'])), 'category'] = 'Income'
    return df

def month_name_to_number(month_name):
    # Get the month number from the calendar module
    month_number = list(calendar.month_name).index(month_name)
    return month_number

def clean_amounts(df):
    df = df.copy()
    df['amount'] = pd.to_numeric(df['amount'].dropna().astype(str).str.replace(",", "", regex = False))
    df['amount'] = round(df['amount'], 2)
    return df