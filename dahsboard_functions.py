import streamlit as st
import seaborn as sns
import calendar
import matplotlib.pyplot as plt 
import pandas as pd
import os

from categories import store_categories
from helper_functions import month_name_to_number, add_category_column

class DashboardCreator:
    def __init__(self, df):
        self.df = df
        self.budget_df = None
        self.income_budget_df = None
    
    def create_dashboard(self):
        budget_tool = BudgetTool()
        budget_tool.create_budget_tool()

    def select_month_button(self):
        self.selected_month = st.selectbox('Select a month', [calendar.month_name[month] for month in self.df['date'].dt.month.unique()])
    
    def month_earnings_tool(self):
        st.subheader(f'Income for the month of {self.selected_month}')
        month_num = month_name_to_number(self.selected_month)
        total =  round(self.df.loc[(self.df['date'].dt.month == month_num) &
                                     (self.df['category'] == 'Income')]['amount'].sum(), 2)
        st.markdown(f"##### Total Income: :green[${total}]")
        col1, col2 = st.columns((1,1.5))

        desc = col1.checkbox("Show Description")

        if desc:
            to_drop = ['category', 'account']
        else:
            to_drop = ['category', 'account','description']
        month_earnings = self.df.loc[(self.df['date'].dt.month == month_num) &
                                     (self.df['category'] == 'Income')].drop(to_drop, axis = 1)
        month_earnings['date'] = month_earnings['date'].dt.date

        cat_order = month_earnings.sort_values(by = 'amount', ascending = False)['subcategory'].unique()
        
        fig, ax = plt.subplots(figsize = (8,3))
        palette = sns.color_palette("Blues_d")
        palette.reverse()
        sns.barplot(data = month_earnings,
                     x = 'amount', 
                     y = 'subcategory', 
                     order=cat_order,
                     estimator='sum',
                     ci = False,
                     palette=palette
                     )
        
        sns.light_palette("#69d", as_cmap=True)
        col1.table(month_earnings)
        col2.pyplot(fig)

        return month_earnings

    def month_spending_tool(self):

        month_num = month_name_to_number(self.selected_month)

        selected_month_df_spending = self.df.loc[(self.df['date'].dt.month == month_num) & (self.df['amount'] <= 0) & (self.df['category'] != "Credit Card Payment") & (self.df['category'] != "Transfer")]
        selected_month_df_spending['amount'] = selected_month_df_spending['amount'] * -1

        self.budget_df = pd.read_csv('budgets/budget.csv', index_col=0)

        spending_budget = pd.concat([selected_month_df_spending, self.budget_df])

        self.__month_spending_graph__(spending_budget, self.selected_month)
        self.__month_spending_cat__(spending_budget, self.selected_month)
        
        

    def __month_spending_graph__(self, df, selected_month):
        df_group = df.groupby('category')[['amount', 'budget']].sum().reset_index()
        df = df.drop(["budget"], axis = 1).dropna()
        df_long = pd.melt(df_group, id_vars='category', var_name='variable', value_name='value')
        df_long = df_long.loc[df_long['value'] > 0]
        category_order = df_group.loc[(df_group['amount'] > 0)].sort_values(by = 'amount', ascending=False)['category']
        total = (str)(df_group['amount'].sum())
        st.write("Total spending for the month of", selected_month, "is :red[$]", f":red[{total}]")
        st.write(f"(from {df['date'].dt.date.min()} to {df['date'].dt.date.max()})")
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize = (8,len(category_order)-4))
        plt.tight_layout()
        sns.barplot(
                    x='value', 
                    y='category', 
                    data=df_long, 
                    color='blue', 
                    hue = 'variable', 
                    palette="rocket", 
                    order=category_order,
                    width=.7
                    )
        for i in ax.containers:
            ax.bar_label(i,fontsize = 10,padding = 1)
        plt.legend(loc='lower right')
        st.pyplot(fig)

    def __month_spending_cat__(self, df, selected_month):
        selected_cat = st.selectbox("Select a category", df['category'].unique())
        total = df[df['category'] == selected_cat]['amount'].sum()
        # selected_month_df_spending.insert(0, "Edit", False)

        st.write("Spending in the month of ", selected_month, " in category ", selected_cat)
        st.write("Total: $", round(total, 2).astype(str))
        df = df.drop(['budget'], axis = 1).dropna()
        df['date'] = df['date'].dt.date
        selected_df = st.data_editor(df[df['category'] == selected_cat], 
                    #    column_config={"Edit": st.column_config.CheckboxColumn(required=True)}, 
                    #    disabled=selected_month_df_spending.drop('Edit', axis=1).columns,
                    hide_index=True)
        
        # selected_rows = selected_df[selected_df.Edit]
        # if selected_rows.size != 0:
        #     sub_cat = st.selectbox("Change selected row(s) subcategory to", set(store_categories.values()))
            
        #     done = st.button("Rename")

        #     if done:
        #         for description in selected_rows['description']:
        #             store_categories[description] = sub_cat
        #         st.rerun()


        #     st.write(selected_rows)

        #     st.write(self.df)

        




class BudgetTool:
    def __init__(self):
        self.income_budget_df = None
        self.budget_df = None

    def create_budget_tool(self):
        st.subheader("Create a budget here")
        self.__budget_expander__()

    def __budget_expander__(self):
        expander = st.expander(label="Expand Budget Tool")
        with expander:
            col1, col2 = st.columns(2)
            self.__income_budget__(col1)
            self.__spending_budget__(col2)

    def __income_budget__(self, col1):
        self.__find_income_budget_df__()

        budget_df = st.session_state.income_budget_df

        col1.markdown("#### Income")

        budget_df = col1.data_editor(budget_df,disabled=budget_df['category'], hide_index=True, use_container_width=True)

        if col1.button("Save", key = 'save_income'):
            budget_df.to_csv("budgets/budget.csv")

        self.income_budget_df = budget_df

    def __find_income_budget_df__(self, income = False):
        if not os.path.exists('budgets/income_budget.csv'):
            if 'income_budget_df' not in st.session_state:
                st.session_state.income_budget_df = pd.DataFrame(columns=['category', 'budget'])

            budget_df = st.session_state.income_budget_df

            budget_df['category'] = self.df[self.df['category'] == 'Income']['subcategory'].unique()
            budget_df['budget'] = 0
            budget_df.to_csv('budgets/income_budget.csv')
        else:
            if 'budget_df' not in st.session_state:
                st.session_state.income_budget_df = pd.read_csv("budgets/income_budget.csv", index_col=0)

    

    def __spending_budget__(self, col2):
        self.__find_spending_budget__()
        budget_df = st.session_state.budget_df
        budget_df = budget_df.loc[~budget_df['category'].isin(['Income','Credit Card Payment','Laundry'])].sort_values(by = 'category')


        col2.markdown("#### Expenses")

        budget_df = col2.data_editor(budget_df,disabled=budget_df['category'], hide_index=True, use_container_width=True)

        if col2.button("Save", key = 'save_expenses'):
            budget_df.to_csv("budgets/budget.csv")

        self.budget_df = budget_df

    def __find_spending_budget__(self):
        if not os.path.exists('budgets/budget.csv'):
            if 'budget_df' not in st.session_state:
                st.session_state.budget_df = pd.DataFrame(columns=['category', 'budget'])

            budget_df = st.session_state.budget_df

            budget_df['category'] = self.df['category'].unique()
            budget_df['budget'] = 0
            budget_df.to_csv('budgets/budget.csv')
        else:
            if 'budget_df' not in st.session_state:
                st.session_state.budget_df = pd.read_csv("budgets/budget.csv", index_col=0)

