import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import undetected_chromedriver as uc


data = pd.read_excel("urls.xlsx")

data["website"] = ""
data["full_address"] = ""
data["phone"] = ""

import time

start = time.time()


driver = uc.Chrome(driver_executable_path=r"chromedriver.exe", headless=False, use_subprocess=False)
for index, row in data.head(10).iterrows():
    try:
        if "https://www.toasttab" in row["Url"]:
            driver.get(row["Url"])

            soup = BeautifulSoup(driver.page_source, "html.parser")

            add1 = ""
            for el in soup.find("div", {"class":"address hidden-sm-down"}).find_all("p"):
                add1 += el.text + " "
#             print(add1)

            try: tel = str(soup.find("img", {"alt":"phone icon"}).parent.parent.get("href")).replace("tel:","")
            except: tel = ""
#             print(tel)

            try: website = soup.find("a", string="Website").get("href")
            except: website = ""
#             print(website)

            data.loc[index, ["website"]] = website
            data.loc[index, ["full_address"]] = add1
            data.loc[index, ["phone"]] = tel
        else:
            data.loc[index, ["website"]] = row["Url"]
    except: print("Skipped", index)
    print(index)
    
    if index %500:
        data.to_excel("merged_file_additional_info.xlsx", index=False)
        
end = time.time()
print(end - start)