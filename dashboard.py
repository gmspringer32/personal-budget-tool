import pandas as pd
import streamlit as st
import os
import io

from dahsboard_functions import DashboardCreator
from scraper.helper_functions import clean_credit_card, create_file, create_big_df, clean_checking, add_category_column, clean_amounts


def main():
    st.set_page_config(layout="wide")
    st.title("Budget")
    st.write("Welcome to the Personal Budget Tracker, a user-friendly Streamlit app designed to empower you in managing your finances effectively. This intuitive tool is tailored for individuals seeking a simplified and organized approach to personal budgeting.")
    st.write("Features:")
    st.write("1. Budget Tool - Allows you to input budget amounts for the month")
    st.write("2. Monthly Income - A place for you to look at income for the selected month")
    st.write("3. Monthly Spending - A place for you to look at spending for a specific month and filter by category")
    st.write("4. Month to Month Spending and Income - Visualization of spending and income from month to month over the year")
    st.write("5. Month to Month Spending by Category - Where to see spending in different categories from month to month in specific categories")
    st.write("\nnote that the default values of this dashboard come from dummy data")
    df = get_df_ready()
    __dashboard__(df)


def get_df_ready():

    uploaded_file = st.file_uploader("Upload a new Statement", type=["csv"])

    
    if not os.path.exists('transactions'):
        df = pd.read_csv('dummy_data.csv', index_col=0)
        df = add_category_column(df)
        df.sort_values(by = ['date'], inplace=True, ascending=False)
        df.reset_index(drop = True, inplace=True)


    elif uploaded_file is not None:
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
        df = create_big_df()
        df = clean_amounts(df)
        df = add_category_column(df)
        df.sort_values(by = ['date'], inplace=True, ascending=False)
        df.reset_index(drop = True, inplace=True)

    elif uploaded_file is None:
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
