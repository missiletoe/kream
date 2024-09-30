from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--window-size=1920,1080')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

# 검색 키워드를 입력받아 url 연결
keyword = input('검색하고자 하는 논문의 주제를 입력하세요 : ')
url = f'https://www.dbpia.co.kr/search/topSearch?searchOption=all&query={keyword}'
driver.get(url)

# method 2. 하단의 다음 10페이지로 넘어가는 숫자 클릭

link_list = []

# 정렬 방식에서 100개씩 보기로 전환 (ViewPort가 mobile size일때 에러)
driver.find_element(By.CLASS_NAME, 'thesisAll__selectWrap').click()
driver.find_element(By.ID,'get100PerPage').click()
time.sleep(2) # 웹페이지 렌더링 대기

# list에 value 추가
link_list = []

# 하단의 다음 10페이지로 넘어가는 숫자 클릭
for i in range(2,12): # list에 url을 100개씩 10번 저장
    links = driver.find_elements(By.CLASS_NAME, 'thesis__link')
    for l in links:
        link_list.append(l.get_attribute('href'))
    if i < 11: # 페이지 번호에 따라 XPath가 바뀌는 패턴, 10페이지까지만 조회 (검색결과가 900개 이하일 때 에러)
        xpath = f'//*[@id="pageList"]/a[{i}]'
        driver.find_element(By.XPATH, xpath).click()
        time.sleep(2)

#  list에 key와 value 추가를 links_list번 반복
data = []
for link in link_list:
    driver.get(link)
    thesisTitle = driver.find_element(By.CLASS_NAME,'thesisDetail__tit').text
    thesisAuthor = driver.find_element(By.CLASS_NAME, 'authorList').text
    useCount = driver.find_element(By.ID,'showUsageChartButton').text
    try:
        abstract = driver.find_element(By.CLASS_NAME,'abstractTxt').text
    except: # 초록이 없을 경우 에러 처리 방법
        abstract = ''

    data.append({
        '제목': thesisTitle,
        '저자': thesisAuthor,
        '이용수': useCount,
        '초록': abstract
    })
    print(f'{len(data)}개 추가 완료')
    time.sleep(0.5)

tables = pd.DataFrame(data) # Pandas의 DataFrame을 이용하여 tables에 data 추가
tables.to_csv(f'DBPIA - {keyword}.csv') # csv 파일로 추출