# Nhập thư viện và gói cho dự án
import csv
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait     
from selenium.webdriver.common.by import By     
from selenium.webdriver.support import expected_conditions as EC

number_second = 0.5

# Mở Firefox và truy cập trang đăng nhập Linkedin
driver = webdriver.Firefox()
url = 'https://www.linkedin.com'
driver.get(url)
sleep(number_second)

# Nhập tên người dùng (email) và mật khẩu
credential = open('tai_khoan.txt')
line = credential.readlines()
email = line[0]
password = line[1]
sleep(number_second)

# email
email_field = driver.find_element_by_id('session_key')

# send_keys () để mô phỏng các thao tác gõ phím
email_field.send_keys(email)
sleep(number_second)

# password 
password_field = driver.find_element_by_id('session_password')

# send_keys () để mô phỏng các thao tác gõ phím
password_field.send_keys(password)
sleep(number_second)

# xác định vị trí nút gửi đăng nhập
log_in_button = driver.find_element_by_class_name('sign-in-form__submit-button')

# .click () để bắt chước nhấp vào nút đăng nhập
log_in_button.click()
sleep(number_second)


# phương thức driver.get () sẽ điều hướng đến một trang được cung cấp bởi địa chỉ URL
driver.get('https://www.google.com')
sleep(number_second)

# Nhập từ khóa tìm kiếm
search = open('tim_kiem.txt')
line = search.readlines()
skill = line[0]
local = line[1]
page_number = line[2]
keyword = f'site:linkedin.com/in/ AND "{skill}" AND "{local}"'
search_query = driver.find_element_by_name('q')

# send_keys () để mô phỏng các thao tác gõ phím
search_query.send_keys(keyword)
sleep(number_second)

# .send_keys () để mô phỏng khóa trả về
search_query.send_keys(Keys.RETURN)
sleep(number_second)

# thu thập thông tin URL của các cấu hình. viết một hàm để trích xuất các URL của một trang
def GetURL():
    page_source = BeautifulSoup(driver.page_source, 'html.parser')
    sleep(1)
    profiles = page_source.find_all('div', class_ = 'yuRUbf')
    
    all_profile_URL = []
    for profile in profiles:
        for a in profile.find_all('a'):
            sleep(1)
            profile_URL = a.get('href').replace('vn.','')
            if profile_URL not in all_profile_URL:
                all_profile_URL.append(profile_URL)
    return all_profile_URL

# Điều hướng qua nhiều trang và trích xuất URL hồ sơ của mỗi trang
URLs_all_page = []
for page in range(int(page_number)):
    URLs_one_page = GetURL()
    if len(URLs_one_page) == 0:
        print('''Vui long nhap lai
        ''')
        break
    sleep(number_second)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    sleep(number_second)
    next_button = driver.find_element_by_xpath('//*[@id="pnnext"]')
    sleep(number_second)
    driver.execute_script("arguments[0].click();", next_button)
    URLs_all_page = URLs_all_page + URLs_one_page
    sleep(number_second)

# thu thập dữ liệu của 1 hồ sơ Linkedin và ghi dữ liệu vào tệp .CSV
with open('profile_output.csv', 'w',  newline = '', encoding='utf-8') as file_output:
    headers = ['Tên ứng viên', 'Học vấn', 'Công việc hiện tại', 'Công ty hiện tại', 'Thời gian làm việc', 'Nơi làm việc', 'Link tài khoản']
    writer = csv.DictWriter(file_output, delimiter=',', lineterminator='\n',fieldnames=headers)
    writer.writeheader()
    for linkedin_URL in URLs_all_page:
        driver.get(linkedin_URL)
        print('- Truy cập hồ sơ: ', linkedin_URL)
        sleep(number_second)
        page_source = BeautifulSoup(driver.page_source, "html.parser")
        info = page_source.find('div',{'class':'display-flex justify-space-between pt2'})
        info_company = page_source.find('h2',{'class':'text-heading-small align-self-center flex-1'})
        info_college = page_source.find('div',{'class':'pv-entity__degree-info'})
        info_experience = page_source.find('div', {'class':'pv-entity__summary-info pv-entity__summary-info--background-section'})
        try:
            name_people = info.find('h1', class_='text-heading-xlarge inline t-24 v-align-middle break-words').get_text().strip()
            print('--- Tên ứng viên: ', name_people)
            college = info_college.find('h3', class_='pv-entity__school-name t-16 t-black t-bold').get_text().strip()
            print('--- Học vấn: ', college)
            position = info_experience.find('h3', class_='t-16 t-black t-bold').get_text().strip()
            print('--- Công việc hiện tại: ', position)
            # company = info_company.find('div', class_='inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp').get_text().strip()
            # print('--- Công ty hiện tại: ', company)
            # experience
            company = info_experience.find('p', class_='pv-entity__secondary-title t-14 t-black t-normal').get_text().strip()
            print('--- Công ty hiện tại: ', company)
            time_work_at_company = info_experience.find('span', class_='pv-entity__bullet-item-v2').get_text().strip()
            print('--- Thời gian làm việc: ', time_work_at_company)   
            location = info.find('span', class_='text-body-small inline t-black--light break-words').get_text().strip()
            print('--- Nơi làm việc: ', location)

            writer.writerow({
                    headers[0]:name_people,
                    headers[1]:college,
                    headers[2]:position,
                    headers[3]:company,
                    headers[4]:time_work_at_company,
                    headers[5]:location,
                    headers[6]:linkedin_URL
                })

            print('\n')
        except:
            pass

# nhiệm vụ hoàn thành
print('Xong!')
