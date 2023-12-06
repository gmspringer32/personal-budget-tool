import pandas as pd
import streamlit as st
import os
import io

from dahsboard_functions import DashboardCreator
from scraper.helper_functions import clean_credit_card, create_file, create_big_df, clean_checking, add_category_column, clean_amounts


def main():
    st.set_page_config(layout="wide")
    st.title("Budget")
    df = get_df_ready()
    __dashboard__(df)


def get_df_ready():

    uploaded_file = st.file_uploader("Upload a new Statement", type=["csv"])

    if uploaded_file is not None:
        if not os.path.exists('transactions'):
            os.makedirs('transactions')

        st.info("File uploaded successfully!")

        file_contents = uploaded_file.read()

        # Use io.BytesIO to create a virtual file-like object
        virtual_file = io.BytesIO(file_contents)

        # Convert the virtual file to a pandas DataFrame
        if file_contents.decode('utf-8')[:11] == "Description":
            df = pd.read_csv(virtual_file, skiprows=6)
            df = clean_checking(df)
        else:
            df = pd.read_csv(virtual_file)
            df = clean_credit_card(df)

        create_file(df)

    elif not os.path.exists('transactions'):
        df = pd.read_csv('dummy_data.csv')

    df = create_big_df()
    df = clean_amounts(df)
    df = add_category_column(df)
    df.sort_values(by = ['date'], inplace=True, ascending=False)
    df.reset_index(drop = True, inplace=True)
    
    df['date'] = pd.to_datetime(df['date'])
    return df

def __dashboard__(df):
    dahsboard = DashboardCreator(df)
    dahsboard.create_dashboard()

if __name__ == "__main__":
    main()
