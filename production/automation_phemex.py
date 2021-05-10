from selenium import webdriver
import time
from config import PHEMEX_URL

class Automation():
    def __init__(self):
        
        self.driver = webdriver.Chrome()
        #PHEMEX_URL = "https://testnet.phemex.com/spot/trade/BTCUSDT"
        self.driver.get(PHEMEX_URL)
        a = input()
    
    def get_current_price(self):
        price = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[3]/div[1]/div")
        return float(price.get_attribute('innerText'))
    
    def buy(self):

        # 1. buy button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[1]
        buy_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[1]")
        buy_element.click()
        # 2. market button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[2]/div[2]
        market_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[2]/div[2]")
        market_element.click()
        # 3. 100% button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[2]/div[4]
        all_in_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[2]/div[4]")
        all_in_element.click()
        # 4. buy button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[4]/button
        action_buy_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[4]/button")
        action_buy_element.click()

        
    
    def get_balance_usdt(self):
        # 1. buy button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[1]
        buy_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[1]")
        buy_element.click()
        # 2. market button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[2]/div[2]
        market_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[2]/div[2]")
        market_element.click()

        xml_path = "/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[3]/div[2]/span[2]"
        price = self.driver.find_element_by_xpath(xml_path)
        return float(price.get_attribute('innerText').split(" ")[0].replace(',',''))
        
    def get_balance_bitcion(self):
        # 1. sell button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[2]
        sell_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[2]")
        sell_element.click()
        # 2. market button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[2]/div[2]
        market_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[2]/div[2]")
        market_element.click()

        xml_path = "/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[3]/div[2]/span[2]"
        price = self.driver.find_element_by_xpath(xml_path)
        return float(price.get_attribute('innerText').split(" ")[0].replace(',',''))
    
    def sell(self):
        
        # 1. sell button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[2]
        sell_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[2]")
        sell_element.click()
        # 2. market button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[2]/div[2]
        market_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[2]/div[2]")
        market_element.click()
        # 3. 100% button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[2]/div[4]
        all_in_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[2]/div[4]")
        all_in_element.click()
        # 4. sell button
        # /html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[4]/button
        action_sell_element = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[4]/button")
        action_sell_element.click()


'''
buy_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[1]/span[1]")
buy_button.click()


#one_hunder_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[2]/div[4]")
#one_hunder_button.click()

javaScript = "document.querySelector('body > div.wrap.svelte-1w93xk2 > div > div.main.sv.T2.svelte-1w93xk2 > div > div.body.svelte-1w93xk2 > div > div:nth-child(4) > div.df.fdc.wp100.B1 > div.wrap.pr.df.fdc.p16.pb8.svelte-9kakd1 > div.f1.pr > div > div > div.wrap.df.f12.lh20.svelte-1cl6icl > div:nth-child(4)').click()"
driver.execute_script(javaScript)

buy_button = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[1]/div/div[4]/div[1]/div[2]/div[3]/div/div/div[4]/button")
buy_button.click()

if __name__ == "__main__":
    auto = Automation()
    a = input()
    auto.buy()

'''

if __name__ == "__main__":
    auto = Automation()
    a = input()
    print(auto.buy())
    a = input()
    print(auto.sell())
