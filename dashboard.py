import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
import io
from datetime import datetime, timedelta
import calendar

from dahsboard_functions import DashboardCreator
from helper_functions import clean_credit_card, create_file, create_big_df, clean_checking, add_category_column, month_name_to_number, clean_amounts


def main():
    st.set_page_config(layout="wide")
    st.title("Budget")
    df = get_df_ready()
    __dashboard__(df)


def get_df_ready():

    uploaded_file = st.file_uploader("Upload a new Statement", type=["csv"])

    if not os.path.exists('transactions'):
        os.makedirs('transactions')


    if uploaded_file is not None:
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
    
    df['date'] = pd.to_datetime(df['date'])
    return df

def __dashboard__(df):
    dahsboard = DashboardCreator(df)
    dahsboard.select_month_button()
    dahsboard.create_dashboard()
    dahsboard.month_earnings_tool()
    dahsboard.month_spending_tool()

if __name__ == "__main__":
    main()
