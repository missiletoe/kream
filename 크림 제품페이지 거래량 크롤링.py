from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import pandas as pd

# Selenium 옵션값 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

#############################################################

# 로그인
driver.get('https://kream.co.kr/login')
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'wrap')))
driver.find_element(By.CSS_SELECTOR,'input[type="email"]').send_keys(input('아이디 입력 : '))
driver.find_element(By.CSS_SELECTOR,'input[type="password"]').send_keys(input('비밀번호 입력 : '))
driver.find_element(By.CLASS_NAME,'login-btn-box').click()

#############################################################

# 제품 페이지 접속
pid = input('product ID : ')
size = input('size : ')
driver.get(f'https://kream.co.kr/products/{pid}/?size={size}')
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,'wrap')))
print(driver.title)

# 체결 내역 더보기 버튼 클릭
driver.find_element(By.XPATH,'//*[@id="panel1"]/a').click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'price_body')))

#############################################################

# 거래 데이터가 있는 클래스 찾기
price_body = driver.find_element(By.CLASS_NAME,'price_body')

# 페이지 무한스크롤
loaded = 50 # 한번 스크롤에 불러오는 데이터 개수

for i in range(driver.execute_script('return arguments[0].scrollHeight', price_body), int(int(input('로딩할 거래 데이터 수 입력 : ')) / loaded)*1650, 1650):
    # 첫번째만 1658px 스크롤, 나머지는 1650px 스크롤
    if driver.execute_script('return arguments[0].scrollHeight', price_body) == 1658:
        driver.execute_script('arguments[0].scrollTop = arguments[1]', price_body, 1658)
    else:
        driver.execute_script('arguments[0].scrollTop = arguments[1]', price_body, i)
    # 스크롤 후 2~3초 대기
    time.sleep(random.uniform(2,3))

    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, f'//div[@class="body_list"][{loaded}]')))
        loaded += 50
        print(f'{loaded}개 데이터 호출 완료')
    except:
        print('데이터 추가 로딩 실패. 스크롤 반복문 종료')
        break

#############################################################

# 스크롤 후 viewport에 보여지는 데이터를 salesList에 추가
body_list = price_body.find_elements(By.CLASS_NAME,'body_list')
salesList = []
count = 0

for sales in body_list:
    date_sold = sales.find_element(By.XPATH,'./div[3]/span').text
    size_sold = sales.find_element(By.XPATH,'./div[1]/span').text
    price_sold = sales.find_element(By.XPATH,'./div[2]/span').text

    try:
        sales.find_element(By.XPATH,'./div[3]/div/i/span').text
        express = True
    except:
        express = False
    
    salesList.append({
        '거래일': date_sold,
        '옵션': size_sold,
        '거래가': price_sold,
        '빠른배송': express
    })

    count += 1
    print(f'리스트에 {count}개 데이터 추가 완료')

#############################################################

# 최종 데이터 출력
print(f"총 {len(salesList)}개의 거래 데이터가 수집되었습니다.")
tables = pd.DataFrame(salesList)


# csv 추출
tables.to_csv(f'~/Downloads/{driver.title}.csv')
print(f'csv 추출 완료. 파일 경로 : 다운로드 폴더 > {driver.title}.csv')