from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

# Selenium 옵션값 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# 스타일 최고 인기! 조회 급상승(최근 3일)
driver.get(f'https://kream.co.kr/exhibitions/2575')

# 로딩 대기
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.product_card.exhibition_product')))
time.sleep(3)

#################################################################

results = driver.find_elements(By.CSS_SELECTOR,'.product_card.exhibition_product')
search_result = []

for r in results:
    WebDriverWait(r, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'item_inner')))
    item_inner = r.find_element(By.CLASS_NAME, 'item_inner')
    pid = item_inner.get_attribute('href')
    brand = r.find_element(By.CLASS_NAME,'product_info_brand').text
    product_name = r.find_element(By.CLASS_NAME,'name').text
    product_translated_name = r.find_element(By.CLASS_NAME,'translated_name').text

    try:
        status_value = r.find_element(By.CLASS_NAME,'status_value').text
    except:
        status_value = '0'
    try:
        wish_figure = r.find_element(By.CLASS_NAME,'wish_figure').text
    except:
        wish_figure = '0'
    try:
        review_figure = r.find_element(By.CLASS_NAME,'review_figure').text
    except:
        review_figure = '0'

    # Append the extracted data to search_result
    search_result.append({
        '제품링크': pid,
        '거래량': status_value,
        '브랜드명': brand,
        '제품명_영문': product_name,
        '제품명_한글': product_translated_name,
        '관심상품_등록수': wish_figure,
        '스타일_업로드횟수': review_figure
    })

    # Go back to the main page
    print(f'{len(search_result)} rows collected')

results = driver.find_elements(By.CSS_SELECTOR,'.product_card.exhibition_product')

df = pd.DataFrame(search_result)

#################################################################

# Initialize empty lists to store the scraped data
release_prices = []
model_numbers = []
release_dates = []
primary_colors = []

# Loop through each row in the dataframe to visit the product page and scrape data
for index, row in df.iterrows():
    # Get the product URL from the '제품링크' column
    product_url = row['제품링크']
    
    # Visit the product page
    driver.get(product_url)
    print(f"Visiting: {product_url}")
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'detail-box')))
    time.sleep(2)
    
    info = driver.find_elements(By.CLASS_NAME, 'product_info')
    try:
        # Scrape '발매가' (release price) by class
        release_price = info[0].text  # Replace with actual class name
        print(f"발매가: {release_price}")
    except:
        release_price = None
        print("발매가 not found")
    
    try:
        # Scrape '모델번호' (model number) by class
        model_number = info[1].text  # Replace with actual class name
        print(f"모델번호: {model_number}")
    except:
        model_number = None
        print("모델번호 not found")
    
    try:
        # Scrape '출시일' (release date) by class
        release_date = info[2].text  # Replace with actual class name
        print(f"출시일: {release_date}")
    except:
        release_date = None
        print("출시일 not found")
    
    try:
        # Scrape '대표 색상' (primary color) by class
        primary_color = info[3].text  # Replace with actual class name
        print(f"대표 색상: {primary_color}")
    except:
        primary_color = None
        print("대표 색상 not found")

    # Append the scraped data to the respective lists
    release_prices.append(release_price)
    model_numbers.append(model_number)
    release_dates.append(release_date)
    primary_colors.append(primary_color)

# Add the scraped data as new columns to the dataframe
df['발매가'] = release_prices
df['모델번호'] = model_numbers
df['출시일'] = release_dates
df['대표 색상'] = primary_colors

#################################################################

def clean_transaction_volume(volume):
    # Remove "거래 " if it exists
    volume = volume.replace("거래 ", "")
    
    # Check if the value contains '만' and process it
    if "만" in volume:
        # Convert n.n만 to full number
        volume = re.sub(r'(\d+\.?\d*)만', lambda x: str(int(float(x.group(1)) * 10000)), volume)
    
    # Remove commas from the result
    return volume.replace(",", "")

# 전처리
df['거래량'] = df['거래량'].apply(clean_transaction_volume)
df['관심상품_등록수'] = df['관심상품_등록수'].apply(clean_transaction_volume)
df['스타일_업로드횟수'] = df['스타일_업로드횟수'].apply(clean_transaction_volume)
df['거래량'] = df['거래량'].astype(int)
df['관심상품_등록수'] = df['관심상품_등록수'].astype(int)
df['스타일_업로드횟수'] = df['스타일_업로드횟수'].astype(int)

# 정렬
df_sorted = df.sort_values(by=['거래량', '관심상품_등록수', '스타일_업로드횟수'], ascending=[False, False, False])

# csv로 추출
df.to_csv(f'[{time.strftime("%Y-%m-%d %H.%M.%S", time.localtime(time.time()))}] 스타일 최고 인기! 조회 급상승(최근 3일).csv')
print(f'[{time.strftime("%Y-%m-%d %H.%M.%S", time.localtime(time.time()))}] 스타일 최고 인기! 조회 급상승(최근 3일).csv 추출 완료')