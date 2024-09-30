from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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

#############################################################

# Retry logic for waiting until the page fully loads
def wait_for_element(driver, by_method, selector, timeout=10, retries=3):
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt+1} to load the element: {selector}")
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by_method, selector))
            )
            print("Element loaded successfully")
            return element
        except TimeoutException:
            print(f"TimeoutException: Element {selector} did not load within {timeout} seconds. Retrying...")
            time.sleep(2)  # Wait for a moment before retrying
    print(f"Failed to load the element {selector} after {retries} attempts.")
    return None

#############################################################

# 키워드 검색해서 제품링크 찾기
a = input('키워드 입력 : ')
driver.get(f'https://kream.co.kr/search?keyword={a}&tab=products')

# 정렬방식 선택
while True:
    try:
        # Get user input and convert it to an integer
        sort_options_input = input('''
검색결과 정렬 방식을 선택하세요.
1. 인기순
2. 남성 인기순
3. 여성 인기순
4. 관심 많은순
5. 스타일 많은순
''')      
        if int(sort_options_input) == 1:
            sort_options = '인기순'
            break
        elif int(sort_options_input) in range(2,6):
            sort_options_input = int(sort_options_input)
            if sort_options_input in (2,3):
                sort_options_input -= 1
            if sort_options_input in (4,5):
                sort_options_input += 3
            driver.find_element(By.XPATH, f'//button[@class="sorting_title"]').click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//ul[@class="sorting_list"]')))
            sort_options = driver.find_element(By.XPATH, f'//li[@class="sorting_item"][{sort_options_input}]/a/div/p').text
            driver.find_element(By.XPATH, f'//li[@class="sorting_item"][{sort_options_input}]').click()
            break
        else:
            print("1에서 5 사이의 숫자만 입력하세요.")
    except ValueError:
        print("정수만 입력 가능합니다. 숫자만 입력하세요.")

time.sleep(5)
results = driver.find_elements(By.CSS_SELECTOR, '.search_result_item.product')
search_result = []

for r in results:
    item_inner = r.find_element(By.CLASS_NAME, 'item_inner')
    pid = item_inner.get_attribute('href')
    brand = r.find_element(By.CLASS_NAME, 'product_info_brand').text
    product_name = r.find_element(By.CLASS_NAME, 'name').text
    product_translated_name = r.find_element(By.CLASS_NAME, 'translated_name').text
    
    try:
        status_value = r.find_element(By.CLASS_NAME, 'status_value').text
        if status_value == '':
            status_value = '0'
    except:
        status_value = '0'
    try:
        wish_figure = r.find_element(By.CLASS_NAME, 'wish_figure').text
        if wish_figure == '':
            wish_figure = '0'
    except:
        wish_figure = '0'
    try:
        review_figure = r.find_element(By.CLASS_NAME, 'review_figure').text
        if review_figure == '':
            review_figure = '0'
    except:
        review_figure = '0'
    
    search_result.append({
        '제품링크': pid,
        '거래량': status_value,
        '브랜드명': brand,
        '제품명_영문': product_name,
        '제품명_한글': product_translated_name,
        '관심상품_등록수': wish_figure,
        '스타일_업로드횟수': review_figure
    })
    print(f'리스트에 {len(search_result)}개 데이터 추가 완료')

df = pd.DataFrame(search_result)
print('리스트 데이터프레임화 완료. 각 제품의 부가 정보 추가 중')

#############################################################

# Initialize empty lists to store the scraped data
release_prices = []
model_numbers = []
release_dates = []
primary_colors = []

# Loop through each row in the dataframe to visit the product page and scrape data
for index, row in df.iterrows():
    # Get the product URL from the '제품링크' column
    product_url = row['제품링크'].replace('?fetchRelated=true','')
    
    # Visit the product page
    driver.get(product_url)
    print(f"\nVisiting: {product_url}")
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,'detail-box')))
    
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

# Save results to CSV
df.to_csv(f'"{a}" KREAM 검색결과 | {sort_options} | 50개.csv')
print(f'"{a}" KREAM 검색결과 | {sort_options} | 50개.csv 추출 완료')