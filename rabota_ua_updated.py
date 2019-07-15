from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import pickle
import sqlite3


# connection to db
def conn_db(path):
    connx = sqlite3.connect(path)
    cursorx = connx.cursor()
    return connx, cursorx


# create table
def create_table_db(name):
    create_table = "CREATE TABLE " + name + " (Name_Surname text, Profile_Url text, Email text, Phone_Number text, City text, CV_Url text)"
    try:
        mycursor.execute(create_table)
    except sqlite3.OperationalError:
        drop_table_db(name)
        mycursor.execute(create_table)
        
          
# drop table from db
def drop_table_db(name):
    drop_table = "DROP TABLE " + name
    mycursor.execute(drop_table)
    
    
# insert people info into db
def insert_into_db(Name_surname, Profile_url, Email, Phone_number, City, Cv_url):
    sql = "INSERT INTO employees (Name_Surname, Profile_Url, Email, Phone_Number, City, CV_Url) VALUES (?, ?, ?, ?, ?, ?)"
    val = (Name_surname, Profile_url, Email, Phone_number, City, Cv_url)
    mycursor.execute(sql, val)
    conn.commit()
    
    
# initializing webdriver
def sel_init(path, start_page):
    driverx = webdriver.Firefox(executable_path=path)
    driverx.get(start_page)
    return driverx


# loading cookies to webdriver
def load_cookie(path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
            
            
# parsing people info
def get_people_info(start_page):
    #find last page number
    driver.get(start_page)
    soup_page = BeautifulSoup(driver.page_source, "html.parser")
    num_page = soup_page.find("div", {"id":"ctl00_centerZone_employerResumeList_grVwResume_ctl24_pagerInnerTable"})
    last_page = int(num_page.find_all("dd")[-1].a.get_text())
    #check all pages
    for page in range(1, last_page + 1):
        driver.get(start_page + "&pg=" + str(page))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        #check all profiles
        for profile in soup.find_all("a", class_="rua-p-t_16 rua-p-c-default ga_cv_view_cv"):
            profile_url = profile["href"]
            name_surname = profile.text
            driver.get(profile_url)
            soup_profile = BeautifulSoup(driver.page_source, "html.parser")
            #print(soup_profile.prettify())
            try:
                email = soup_profile.find("span", {"class":"rua-p-t_13", "id":"ctl00_centerZone_BriefResume1_ViewAttachedCV1_cvHeader_lblEmailValue"}).get_text()
            except AttributeError:
                email = soup_profile.find("span", {"class":"rua-p-t_13", "id":"ctl00_centerZone_BriefResume1_CvView1_cvHeader_lblEmailValue"}).get_text()
            try:
                phone_number = soup_profile.find("span", {"class":"rua-p-t_13", "id":"ctl00_centerZone_BriefResume1_CvView1_cvHeader_lblPhoneValue"}).get_text()
            except AttributeError:
                phone_number = ""
            try:
                city = soup_profile.find("span", {"class":"rua-p-t_13", "id":"ctl00_centerZone_BriefResume1_CvView1_cvHeader_lblRegionValue"}).get_text()
            except AttributeError:
                city = ""  
            cv_url = str(soup.find("a", class_="rua-p-t_16")["href"])
            #driver.get(cv_url)
            #print(name_surname + "\n" + profile_url + "\n" + email +"\n"+ phone_number + "\n" + city + "\n" + cv_url)
            #inserting info
            insert_into_db(name_surname, profile_url, email, phone_number, city, cv_url)

                
# show results
def show_table_rows(name):
    sql_select_all = "SELECT * FROM " + name
    mycursor.execute(sql_select_all)
    print(mycursor.fetchall())


#start                        
def start():
    create_table_db(table_name)
    #sleep(30)
    #pickle.dump(driver.get_cookies() , open("cookies.pkl","wb"))
    load_cookie(cookies_path)
    get_people_info(starting_page)
    show_table_rows(table_name)  
    
    
#constants   
database_path = "mydatabase.db"
table_name = "employees"
driver_path = "C:\\Users\\yurak\\Desktop\\test\\geckodriver.exe"
cookies_path = "C:\\Users\\yurak\\Desktop\\test\\cookies.pkl"
starting_page = "https://notebook.rabota.ua/employer/notepad/cvs?vacancyId=-1"
conn, mycursor = conn_db(database_path)
driver = sel_init(driver_path, starting_page)


start()