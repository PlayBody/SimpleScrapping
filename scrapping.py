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


data = pd.read_excel("./urls.xlsx")

data["website"] = ""
data["full_address"] = ""
data["phone"] = ""

# print(data)

start = time.time()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,ko;q=0.6",
    "Connection": "keep-alive",
    "Accept": "*/*"
}

def get_data(index, url, catched):
    try:
        if "https://www.toasttab" in url:
            response = requests.get(url, headers=headers)
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

