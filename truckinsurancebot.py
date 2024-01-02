#baby's first web scraper! (sort of)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import pyautogui
import csv

#creates the initial file
def create_initial_file():
    fields = ["US DOT", "Docket Number", "Legal Name", "Form", "Type", "Insurance Carrier", "Policy/Surety", "Posted Date", "Coverage From", "Coverage To", "Effective Date", "Cancellation Date"]
    filename = "insurance_data.csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)

#saves the data from each page
def save_data(data):
    try:
        #cleans the data
        data = data.split("Active/Pending Insurance")[1]
        data = data.split("Carrier Details")[0]

        basic_data = data.split("Form Type")[0]
        us_dot = basic_data.split()[2]
        docket_number = basic_data.split()[5]

        legal_name = basic_data.split("\n")[2]  
        legal_name = legal_name.split(":")[1]
        legal_name = legal_name[1:]

        table_data = data.split("Cancellation\nDate")[1]
        table_data = table_data.split("\n")
        table_data = table_data[1:]

        #may potentially cause a bug
        '''
        for i in range(len(table_data)):
            if "If a carrier is in compliance, the amount of coverage" in table_data[i]:
                table_data.remove(table_data[i])'''

        #91X, 84, 85, 34
        rows_to_write = []

        #accounts for if there are 3 rows in the table
        if len(table_data) > 16:
            print("table_data > 16")
            indices_list = []
            for i in range(1, len(table_data)):
                print("i in range 1, len(table_data)")
                if "34" in table_data[i] or "84" in table_data[i] or "85" in table_data[i] or "91X" in table_data[i]:
                    indices_list.append(i)
            
            row1 = table_data[:indices_list[0]].copy()
            row2 = table_data[indices_list[0]:indices_list[1]].copy()
            row3 = table_data[indices_list[1]:].copy()

            row1.insert(0, legal_name)
            row1.insert(0, docket_number)
            row1.insert(0, us_dot)
            row2.insert(0, legal_name)
            row2.insert(0, docket_number)
            row2.insert(0, us_dot)
            row3.insert(0, legal_name)
            row3.insert(0, docket_number)
            row3.insert(0, us_dot)
            print(row1)
            print(row2)
            print(row3)
            rows_to_write.append(row1)
            rows_to_write.append(row2)  
            rows_to_write.append(row3)

        #accounts for if there are 2 rows in the table
        elif len(table_data) > 9:
            print("table_data > 9")
            for i in range(1, len(table_data)):
                print("i in range 1, len(table_data)")
                if "34" in table_data[i] or "84" in table_data[i] or "85" in table_data[i] or "91X" in table_data[i]:
                    print("got here")
                    row1 = table_data[:i].copy()
                    row2 = table_data[i:].copy()
                    row1.insert(0, legal_name)
                    row1.insert(0, docket_number)
                    row1.insert(0, us_dot)
                    row2.insert(0, legal_name)
                    row2.insert(0, docket_number)
                    row2.insert(0, us_dot)
                    print(row1)
                    print(row2)

                    rows_to_write.append(row1)
                    rows_to_write.append(row2)

                    break

        #if there is 1 row in the table:
        else:
            row = table_data.copy()
            row.insert(0, legal_name)
            row.insert(0, docket_number)
            row.insert(0, us_dot)

            rows_to_write.append(row)

        #writes the data into the csv file
        filename = "insurance_data.csv"
        with open(filename, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            for row in rows_to_write:
                csvwriter.writerow(row)
    
    #if any exception occurs, skip writing that line and continue with the program
    except:
        return

#creates Firefox window
driver = webdriver.Firefox()
#maximizes window
driver.maximize_window()
#creates initial file
create_initial_file()

driver.get('https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?pv_vpath=LIVIEW')

#inputs state
state_select = driver.find_element(by=By.ID, value="state")
state_select.send_keys("fl")
pyautogui.typewrite("\n")

#wait until captcha has been completed by user
loadedPage = False
while loadedPage == False:
    try:
        table = driver.find_element(by=By.CLASS_NAME, value="g-recaptcha") #waits until captcha element is gone from the page
    except Exception as e:
        loadedPage = True
        break

#how many pages to scrape
for j in range(1000):
    for i in range(10):
        #click "View Details" and ensure action was successful 
        #if you want to switch to selenium clicking, every 5+3*i-th "input" element is a button
        pyautogui.moveTo(1415, 300+(55*i)) 
        loadedPage = False
        while loadedPage == False:
            try:
                time.sleep(0.1)
                pyautogui.click()
                title = driver.find_element(by=By.LINK_TEXT, value="https://www.adobe.com/products/acrobat/readstep2.html") #this link only present on "Search" page
            except Exception as e:
                loadedPage = True
                break
    
        #click Active/Pending Insurance Button and ensure action was successful
        loadedPage = False
        while loadedPage == False:
            try:
                time.sleep(0.5)
                insurance_link = driver.find_elements(by=By.CLASS_NAME, value="information_db")[2]
                insurance_link.click()
                title = driver.find_element(by=By.ID, value="property") #property ID only present on "Details" page
            except Exception as e:
                loadedPage = True
                break
        
        #check if data is available
        try:
            #if no data is available, this code will be successful. if data is available, the code will throw an exception
            data =  driver.find_element(By.XPATH, "//center/strong/font[1]")
        except Exception as e:
            #if data is available, add it to the csv file
            data = driver.find_element(By.TAG_NAME, value="font").text
            save_data(data)

        #go back to main page
        loadedPage = False
        while loadedPage == False:
            try:
                pyautogui.hotkey('command', 'left')
                time.sleep(0.1)
                title = driver.find_element(by=By.LINK_TEXT, value="https://www.adobe.com/products/acrobat/readstep2.html") #this link only present on "Search" page
                loadedPage = True
                break
            except Exception as e:
                continue
    
    #after going through all 10 entries on the page, move onto the next page
            
    #if on 1st page
    if j == 0:
        pyautogui.moveTo(746, 835)
        pyautogui.click()
        time.sleep(2)

    #for every page after the 1st page
    if j > 0:
        pyautogui.moveTo(815, 835)
        pyautogui.click()
        time.sleep(2)

    
#closes the program
driver.quit()


