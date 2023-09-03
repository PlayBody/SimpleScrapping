import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import requests
import time
import threading


data = pd.read_excel("./new_urls.xlsx")


data["website"] = ""
data["full_address"] = ""
data["phone"] = ""

# print(data)

start = time.time()

headers_regular = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,ko;q=0.6",
    "Connection": "keep-alive",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br"
}

headers_special = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,ko;q=0.6",
    "Connection": "keep-alive",
    "Accept": "*/*",
}

name_cases = [
    ">name",
    ">user",
    ">your name",
    'placeholder="your name"',
    'placeholder="name"',
    '> name',
    '> user',
    "> your name",
]

phone_cases = [
    ">phone",
    ">mobile",
    ">number",
    ">office phone",
    'placeholder="phone"',
    'placeholder="mobile"',
    'placeholder="number"',
    '> phone',
    '> mobile',
    "> number",
]

email_cases = [
    ">email",
    ">your email",
    'placeholder="your email"',
    'placeholder="email"',
    '> email',
    '> your email',
]

def get_data(index, url, catched):
    try:
        if "https://" in url:
            response = requests.get(url, headers=headers_regular)
            if response.status_code != 200:
                response = requests.get(url, headers=headers_special)
            soup = BeautifulSoup(response.content, "html.parser")

            add1 = ""
            try:
                for el in soup.find("div", {"class":"address hidden-sm-down"}).find_all("p"):
                    add1 += el.text + " "
            except: add1 = ""         
#                print(add1)

            try: tel = str(soup.find("img", {"alt":"phone icon"}).parent.parent.get("href")).replace("tel:","")
            except: tel = ""
#             print(tel)

            try: website = soup.find("a", string="Website").get("href")
            except: website = ""
#             print(website)

            try: 
                forms = soup.find_all("form")
                for form in forms:
                    str_form = str(form).lower()
                    is_ok = True
                    for name_case in name_cases:
                        if name_case not in str_form:
                            is_ok = False
                    if is_ok == False:
                        continue
                    for phone_case in phone_cases:
                        if phone_case not in str_form:
                            is_ok = False
                    if is_ok == False:
                        continue
                    
                    for email_case in email_cases:
                        if email_case not in str_form:
                            is_ok = False
                    if is_ok == False:
                        continue
                    if is_ok == True:
                        print(form)
                        std_out = "./" + str(index) + "_out.xml"
                        with open(std_out, "w") as file:
                            file.write(str(form))
            except: form = ""

            catched[index] = [website, add1, tel]
        else:
            catched[index] = [url, "", ""]
    except: print("Skipped", index)
    # print(index, website, add1, tel)

index_urls = []

for index, row in data.head(10).iterrows():
    index_urls.append([index, row["Url"]])
    # get_data(index, row["Url"], data)
    # if index % 500:
    #     data.to_excel("merged_file_additional_info.xlsx", index=False)

url_count = len(index_urls)
catched = [None] * url_count

threads = []
for [index, url] in index_urls:
    thread = threading.Thread(target=get_data, args=(index, url, catched))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

# Check if all threads have finished
all_finished = all(not thread.is_alive() for thread in threads)
if all_finished:
    # print(catched)
    i = 0
    for catch in catched:
        data.loc[i, ["website"]] = catch[0]
        data.loc[i, ["full_address"]] = catch[1]
        data.loc[i, ["phone"]] = catch[2]
        i = i + 1
    data.to_excel("scrapped.xlsx", index=False)
    end = time.time()
    print("total time spends", end - start)
else:
    print("Some threads are still running.")

# with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#     # Submit the GET requests concurrently
#     futures = [executor.submit(get_data, index, url, data) for [index, url] in index_urls]

#     # Retrieve the responses as they become available
#     for future in concurrent.futures.as_completed(futures):
#         url_counter = url_counter + 1
#         response = future.result()
#         # Process the response as needed
#         # print(response.status_code)
#         if url_counter == url_count:
#             data.to_excel("merged_file_additional_info.xlsx", index=False)
#             end = time.time()
#             print(end - start)

