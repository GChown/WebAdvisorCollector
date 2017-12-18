from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Navigator:
    def __init__(self, driver):
        self.__driver = driver

    # Click element
    def click(self, xpath):
        self.__driver.wait.until(EC.visibility_of_element_located((By.XPATH, xpath))).click()

    # Text input
    def fill(self, xpath, text):
        field = self.__driver.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        field.send_keys(text)

    # Option field
    def select(self, xpath, option):
        field = self.__driver.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        field.send_keys(option)

    def tableElements(self, xpath):
        return self.__driver.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def query(self, xpath):
        return self.__driver.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
