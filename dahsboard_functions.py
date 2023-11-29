import streamlit as st
import seaborn as sns
import calendar
import matplotlib.pyplot as plt 
import pandas as pd
import os

from scraper.helper_functions import month_name_to_number

class DashboardCreator:
    def __init__(self, df):
        self.df = df
        self.budget_df = None
        self.income_budget_df = None
        self.selected_month = None
    
    def create_dashboard(self):
        self.selected_month = self.select_month_button()
        budget_tool = BudgetTool(self.df)
        budget_tool.create_budget_tool()

        income_tool = IncomeTool(self.selected_month, self.df)
        income_tool.create_month_earnings_tool()

        spending_tool = SpendingTool(self.selected_month, self.df)
        spending_tool.month_spending_tool()

    def select_month_button(self):
        return st.selectbox('Select a month', [calendar.month_name[month] for month in self.df['date'].dt.month.unique()], key='month')
    


        




class BudgetTool:
    def __init__(self, df):
        self.df = df
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

        income_budget_df = st.session_state.income_budget_df

        col1.markdown("#### Income")

        income_budget_df = col1.data_editor(income_budget_df,disabled=income_budget_df['category'], hide_index=True, use_container_width=True)

        if col1.button("Save", key = 'save_income'):
            income_budget_df.to_csv("budgets/income_budget.csv")

        self.income_budget_df = income_budget_df

    def __find_income_budget_df__(self):
        if not os.path.exists('budgets/income_budget.csv'):
            if 'income_budget_df' not in st.session_state:
                st.session_state.income_budget_df = pd.DataFrame(columns=['category', 'budget'])

            income_budget_df = st.session_state.income_budget_df

            income_budget_df['category'] = self.df[self.df['category'] == 'Income']['subcategory'].unique()
            income_budget_df['budget'] = 0
            income_budget_df.to_csv('budgets/income_budget.csv')
        else:
            if 'income_budget_df' not in st.session_state:
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






class IncomeTool:
    def __init__(self, selected_month, df):
        self.selected_month = selected_month
        self.df = df
        self.month_num = month_name_to_number(self.selected_month)
        self.col1, self.col2 = [None, None]
        self.budget = pd.read_csv('budgets/income_budget.csv', index_col=0)

    def create_month_earnings_tool(self):
        st.subheader(f'Income for the month of {self.selected_month}')

        selected_month_df_income = self.df.loc[(self.df['date'].dt.month == self.month_num)]
        
        total =  round(self.df.loc[(self.df['date'].dt.month == self.month_num) &
                                     (self.df['category'] == 'Income')]['amount'].sum(), 2)
        st.markdown(f"##### Total Income: :green[${total}]")
        st.write(f"(from {selected_month_df_income['date'].dt.date.min()} to {selected_month_df_income['date'].dt.date.max()})")
        
        self.col1, self.col2 = st.columns((1,2))

        month_earnings = self.__calc_month_earnings__()
        fig = self.__month_earnings_graph__(month_earnings)

        header_style = {'selector': 'thead th', 'props': [('background-color', '#3f668f'), ('color', 'white')]}
        

        # Apply the styles
        styled_df = month_earnings.style.set_table_styles([header_style]).set_properties(**{'background-color': '#92b3e8', 'color':'black'}).format(precision=2)
        
        self.col1.table(styled_df)
        self.col2.pyplot(fig)

    
    def __calc_month_earnings__(self):
        desc = self.col1.checkbox("Show Description")
        if desc:
            to_drop = ['category', 'account']
        else:
            to_drop = ['category', 'account','description']
        month_earnings = self.df.loc[(self.df['date'].dt.month == self.month_num) &
                                     (self.df['category'] == 'Income')].drop(to_drop, axis = 1)
        month_earnings['date'] = month_earnings['date'].dt.date
    
        return month_earnings
    
    def __month_earnings_graph__(self, month_earnings):
        cat_order = month_earnings.sort_values(by = 'amount', ascending = False)['subcategory'].unique()
        month_earnings_copy = month_earnings.rename(columns = {'subcategory':'category'})
        earnings_budget = pd.concat([month_earnings_copy, self.budget])
        earnings_budget_group = earnings_budget.groupby('category')[['amount', 'budget']].sum().reset_index()
        earnings_budget_long = earnings_budget_group.melt(id_vars='category')
        
        fig, ax = plt.subplots(figsize = (8,3))
        palette = sns.color_palette("Blues_d")
        custom_palette = ["#3f668f","#92b3e8"]

        # Use your custom palette in a Seaborn plot
        sns.set_palette(custom_palette)
        palette.reverse()
        sns.barplot(data = earnings_budget_long,
                     x = 'value', 
                     y = 'category', 
                     hue = 'variable',
                     order=cat_order,
                     estimator='sum',
                     ci = False,
                     palette=custom_palette
                     )
        
        return fig
    



class SpendingTool:
    def __init__(self, selected_month, df):
        self.selected_month = selected_month
        self.df = df
        self.budget_df = pd.read_csv('budgets/budget.csv', index_col=0)
        self.col1, self.col2 = [None, None]

    def month_spending_tool(self):
        st.subheader(f'Spending for the month of {self.selected_month}')
        month_num = month_name_to_number(self.selected_month)
        selected_month_df_spending = self.df.loc[(self.df['date'].dt.month == month_num) & (self.df['amount'] <= 0) & (self.df['category'] != "Credit Card Payment") & (self.df['category'] != "Transfer")]
        selected_month_df_spending['amount'] = selected_month_df_spending['amount'] * -1

        total = round(selected_month_df_spending['amount'].sum(),2)
        st.markdown(f"##### Total Spending: :red[${total}]")
        st.write(f"(from {selected_month_df_spending['date'].dt.date.min()} to {selected_month_df_spending['date'].dt.date.max()})")
        
        self.col1, self.col2 = st.columns((1,2))

        spending_budget = pd.concat([selected_month_df_spending, self.budget_df])

        self.__month_spending_graph__(spending_budget, self.selected_month)
        self.__month_spending_cat__(spending_budget, self.selected_month)
        
        

    def __month_spending_graph__(self, df, selected_month):
        df_group = df.groupby('category')[['amount', 'budget']].sum().reset_index()
        df = df.drop(["budget"], axis = 1).dropna()
        df_long = pd.melt(df_group, id_vars='category', var_name='variable', value_name='value')
        df_long = df_long.loc[df_long['value'] > 0]
        category_order = df_group.loc[(df_group['amount'] > 0)].sort_values(by = 'amount', ascending=False)['category']
    
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize = (8,len(category_order)-4))
        plt.tight_layout()
        sns.barplot(
                    x='value', 
                    y='category', 
                    data=df_long, 
                    color='blue', 
                    hue = 'variable', 
                    palette=["#3f668f","#92b3e8"], 
                    order=category_order,
                    width=.7
                    )
        for i in ax.containers:
            ax.bar_label(i,fontsize = 10,padding = 1)
        plt.legend(loc='lower right')
        self.col2.pyplot(fig)

    def __month_spending_cat__(self, df, selected_month):
        selected_cat = self.col1.selectbox("Select a category", df['category'].sort_values().unique())
        total = df[df['category'] == selected_cat]['amount'].sum()

        self.col1.write(f"Spending in the month of {selected_month} in category {selected_cat}")
        self.col1.write(f"Total: ${round(total, 2).astype(str)}")
        df = df.drop(['budget'], axis = 1).dropna()
        df['date'] = df['date'].dt.date

        desc = self.col1.checkbox("Show Description", key = 'desc')
        if desc:
            to_drop = ['category', 'account']
        else:
            to_drop = ['category', 'account','description']

        header_style = {'selector': 'thead th', 'props': [('background-color', '#3f668f'), ('color', 'white')]}
        
        df = df[df['category'] == selected_cat].drop(columns = to_drop)

        # Apply the styles
        styled_df = df.style.set_table_styles([header_style]).set_properties(**{'background-color': '#92b3e8', 'color':'black'}).format(precision=2)


        self.col1.table(styled_df)