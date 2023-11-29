import pandas as pd

from categories import store_categories

class Cleaner:
    def __init__(self, checking_df, credit_card_df):
        self.checking_df = checking_df
        self.credit_card_df = credit_card_df
        self.accounts_df = pd.DataFrame()


    def getAccountsDf(self):
        return self.accounts_df
    


    def clean(self):
        self.__cleanCreditCardTransactions__()
        self.__cleanBankTransactions__()
        self.__addCategoryColumn__()
        self.__combineDfs__()
        self.__sortDates__()
        self.accounts_df.drop(columns=['balance'], inplace=True)
        self.accounts_df.reset_index(drop=True, inplace=True)




    def __cleanCreditCardTransactions__(self):
        self.__dropUnusedColumns__()
        self.__renameColumns__()
        self.__dropUnusedRows__()
        self.__cleanDescription__()
        self.__convertDateToDateObject__()
        self.__convertMoneyToNumber__()
        self.credit_card_df['account'] = 'Credit Card'
        
        self.credit_card_df.reset_index(inplace=True, drop = True)

        
    def __dropUnusedColumns__(self):
        self.credit_card_df.drop(self.credit_card_df.columns[2], axis=1, inplace= True)

    def __renameColumns__(self):
        self.credit_card_df.rename(columns={'sort by Posting Date  in chronological order  ↓': 'date', 
                                        'sort by Description in alphabetical order': 'description', 
                                        'sort by Amount in ascending order':'amount', 
                                        'Balance':'balance'}, inplace=True)
    def __dropUnusedRows__(self):
        self.credit_card_df = self.credit_card_df.copy()
        self.credit_card_df.drop(self.credit_card_df.loc[self.credit_card_df['date'] == 'There are no transactions to display for the filter you selected. Try changing your selection in the Type filter.'].index, inplace=True)
        self.credit_card_df.drop(self.credit_card_df.loc[self.credit_card_df['date'].str.contains('Beginning balance as of')].index, inplace=True)
        self.credit_card_df.drop(self.credit_card_df.loc[self.credit_card_df['date'].str.contains('link not applicable for screen reader users')].index, inplace=True)
        self.credit_card_df.drop(self.credit_card_df.loc[self.credit_card_df['date'] == "Pending"].index, inplace=True)
    
    def __cleanDescription__(self):
        self.credit_card_df = self.credit_card_df.copy()
        self.credit_card_df['description'] = self.credit_card_df['description'].str.split('transaction').str.get(1).str.strip('for Transaction date: ').str.split('Add this deal').str.get(0).str.replace(r'(\d{2}\/\d{2}\/\d{4}.)', '', regex=True)

    def __convertDateToDateObject__(self):
        self.credit_card_df = self.credit_card_df.copy()
        self.credit_card_df['date'] = pd.to_datetime(self.credit_card_df['date'])

    def __convertMoneyToNumber__(self):
        self.credit_card_df = self.credit_card_df.copy()
        self.credit_card_df['amount'] = pd.to_numeric(self.credit_card_df['amount'].str.replace('$', "",regex=False).str.replace(",", '', regex=False))
        self.credit_card_df['balance'] = pd.to_numeric(self.credit_card_df['balance'].str.replace('$', "",regex=False).str.replace(",",'',regex=False))





    def __cleanBankTransactions__(self):
        self.checking_df = self.checking_df.copy()
        self.checking_df.rename(columns={'Posting date' : 'date', 'Description':'description', 'Amount':'amount', 'Available balance':'balance', 'Type':'category'}, inplace=True)
        self.checking_df.drop(columns=['Reconcile', 'Unnamed: 6'], inplace=True)
        desired_order = ['date', 'description', 'amount', 'balance', 'category']
        self.checking_df = self.checking_df[desired_order]
        self.checking_df.drop(self.checking_df.loc[self.checking_df['date'].str.contains('Statement')].index, inplace=True)
        self.checking_df['description'] = self.checking_df['description'].str.replace('View/Edit', '')
        self.checking_df['amount'] = pd.to_numeric(self.checking_df['amount'].str.replace('$', "",regex=False).str.replace(",", '',regex=False))
        self.checking_df['balance'] = pd.to_numeric(self.checking_df['balance'].str.replace('$', "",regex=False).str.replace(",",'',regex=False))
        self.checking_df.drop(self.checking_df.loc[self.checking_df['date'] == 'Processing'].index, inplace=True)
        self.checking_df['date'] = pd.to_datetime(self.checking_df['date'])
        self.checking_df['account'] = 'Checking'




    def __addCategoryColumn__(self):
        def __mapStoreToCat__(vendor_name):
            vendor_name = vendor_name.replace("-", " ")
            for store_name, category in store_categories.items():
                if store_name in vendor_name:
                    return category
                
            return 'Other'
        self.credit_card_df['category'] = self.credit_card_df['description'].apply(lambda x: __mapStoreToCat__(x))




    def __combineDfs__(self):
        self.accounts_df = pd.concat([self.credit_card_df, self.checking_df])   

    def __sortDates__(self):
        self.accounts_df.sort_values(by='date', ascending=False, inplace=True)