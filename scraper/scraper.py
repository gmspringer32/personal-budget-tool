import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options

from cleaner import Cleaner

class BankScraper:
    def __init__(self):
        with open("secure/bankurl.txt") as file:
            self.url = file.read()
        self.driver = None
        self.credit_card_df = pd.DataFrame()
        self.checking_df = pd.DataFrame()
        self.accounts_df = pd.DataFrame()
        with open("secure/creditcardaccount") as file:
            self.credit_card_account = file.read()
        with open("secure/bankaccount") as file:
            self.bank_account = file.read()
        

    def __startDriver__(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.get(self.url)

    def __insertUsername__(self, username):
        username_bar = self.driver.find_element(By.ID, 'onlineId1')
        time.sleep(.5)
        username_bar.click()
        username_bar.send_keys(username)
        time.sleep(.5)

    def __insertPassword__(self, password):
        password_bar = self.driver.find_element(By.ID, "passcode1")
        time.sleep(.5)
        password_bar.click()
        password_bar.send_keys(password)
        time.sleep(.5)

    def __clickLogin__(self):
        signin_bar = self.driver.find_element(By.ID, 'signIn')
        signin_bar.click()

    def login(self, username, password):
        self.__startDriver__()
        self.__insertUsername__(username)
        self.__insertPassword__(password)
        self.__clickLogin__()

    def __openAccount__(self, account_string):
        accounts = self.driver.find_elements(By.CLASS_NAME, "AccountName")
        wanted_account = account_string
        account_element = None
        for account in accounts:
            if account.text == wanted_account:
                account_element = account
        account_element.click()        

    def __scrapeCreditCardTransactions__(self):
        date_input = self.driver.find_element(By.CLASS_NAME, 'select-bofa')
        date_input_elements = date_input.find_elements(By.TAG_NAME, 'option')
        min_num = min(12, len(date_input_elements))
        for i in range(0, min_num):
            date_input = self.driver.find_element(By.CLASS_NAME, 'select-bofa')
            date_input.find_elements(By.TAG_NAME, 'option')[i].click()
            transactions = self.driver.find_element(By.ID, "transactions")
            table_html = transactions.get_attribute('outerHTML')
            df = pd.read_html(table_html)[0]
            self.credit_card_df = pd.concat([self.credit_card_df, df])

    
    def __closeAccount__(self):
        self.driver.find_element(By.LINK_TEXT, 'Accounts').click()

    def __scrapeBankTransactions__(self):
        time.sleep(1.5)
        self.checking_df = pd.read_html(self.driver.find_elements(By.TAG_NAME, 'table')[1].get_attribute('outerHTML'))[0]

    
    

    def getAccountTransactions(self, month = None):
        month_nums = range(1,12) 
        if month not in month_nums and month is not None:
            print("Please input month as a number, Jan = 1")
            return
    
        self.__openAccount__(self.credit_card_account)
        self.__scrapeCreditCardTransactions__()
        self.__closeAccount__()
        self.__openAccount__(self.bank_account)
        self.__scrapeBankTransactions__()
        cleaner = Cleaner(self.checking_df, self.credit_card_df)
        cleaner.clean()
        return cleaner.getAccountsDf()
    
    def logout(self):
        self.driver.quit()