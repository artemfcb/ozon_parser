import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import pprint

def random_delay(min_seconds =1, max_seconds=3):
    time.sleep(random.uniform(min_seconds,max_seconds))

def clean_price(price_text):
    if not price_text:
        return None
    cleaned = re.sub(r'[^\d,]',"", price_text)
    cleaned = cleaned.replace(',' , '.')
    try:
        return float(cleaned)
    except ValueError:
        return None

class OzonParser:
    def __init__(self):
        
        self.url = 'https://www.ozon.ru/'
        self.chrome_options = Options()

        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        self.wait = WebDriverWait(self.driver, 15)

    def get_info(self,target):
        try:
            self.driver.get(self.url) #загрузка главной страницы
            random_delay(3,5) 
            search_selectors = [
                "input[placeholder = 'Искать на Ozon']",
                "input[name='text]",
                ".ns2_29.tsBody500Medium"
            ]
            serch_input = None
            for selector in search_selectors:
                try:
                    search_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,selector)))
                    print(f'найден элемент с селектором {selector}')
                    break
                except:
                    continue
            if search_input is None:
                raise Exception("Не удалось найти поле поиска")
            search_input.clear()
            random_delay(1,2)
            search_input.send_keys(target)
            random_delay(1,2)
            button_selectors = [
                "button[type='submit']",
                "button[class*-'search']",
                ".ns2_2"
            ]
            
            search_button = None
            for selector in button_selectors:
                try:
                    search_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,selector)))
                    break
                except:
                    continue
            if search_button:
                search_button.click()
                print('нажата кнопка поиска')
            else:
                search_input.send_keys(Keys.RETURN)
                print('Использован Enter для поиска')
            random_delay(5,7)
            try:
                self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-widget='searchResultV2]")))
            except:
                print('результаты поиска могут быть не полностью загружены')
                
            html_content = self.driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            products_data = []
            product_cards = soup.select("div[data-widget='searchResultsV2'] div[class*='tile-root']") or \
                        soup.select("div[data-widget='searchResultsV2'] > div > div > div") or \
                        soup.find_all('div', class_=lambda x: x and 'tile-root' in x)
            print(f'найденно карточек товаров{len(product_cards)}')
            
            for i,card in enumerate(product_cards[:25]):
                try:
                    title = None
                    title_selectors = [
                        ".tsBody500Medium",
                        "span[class*='tsBody']",
                        "a[class*='tile-hover']span",
                        "span[data-widget*='webProductHeading']"
                    ]
                    for title_selector in title_selectors:
                        title_elem = card.select_one(title_selector)
                        if title_elem and title_elem.text.strip():
                            title = title_elem.text.strip()
                            break

                        
                    price = None
                    price_selectors = [
                        ".tsHeadline500Medium",  # Основная цена (как в примере)
                        ".c35_3_11-a1",  # Элемент с ценой
                        "span[class*='tsHeadline']",
                        "div[class*='price'] span",
                        "span[class*='price']"
                    ]
                    for price_selector in price_selectors:
                        price_elements = card.select(price_selector)
                        for price_elem in price_elements:
                            if price_elem and price_elem.text.strip():
                                price_text = price_elem.text.strip()
                                print(price_text)
                                if '%' in price_text or '-' in price_text:
                                    continue
                                cleaned_price = clean_price(price_text)
                                if cleaned_price and cleaned_price > 0:
                                    price = cleaned_price
                                    break
                        if price:
                            break
                        
                #  поиск изображений 
                    image = None
                    image_selectors = [
                            'img[loading="eager"][fetchpriority="high"]',
                            'img.ti6_24.b95_3_4-a',
                            '.ti6_24.b95_3_4-a',
                            'img[src*="ir.ozone.ru"]',
                            '.j4x.j4y img',
                            'div[data-widget="webGallery"] img',
                            'picture source',
                            'img[srcset]'
                    ]
                    for image_selector in image_selectors:
                        image_elements = card.select(image_selector)
                        for image_elem in image_elements:
                            print(image_elem)
                            if image_elem and image_elem.get('src'):
                                image = image_elem.get('src')
                        if image:
                            break
                
                    print(image)  
                    if title and price is not None:
                        products_data.append({
                            'title':title,
                            'price':price,
                            'image_url':image
                        })
                    
                    else:
                        if not title:
                            print(f'{i+1} не удалось извлечь название')
                            
                    if price is None:
                        print(f'{i+1} не удалось извлечь цену')
                    
                    with open(f"debug_card_{i+1}.html","w",encoding="utf-8") as file:
                        file.write(card.prettify())
                    
                
                except Exception as e:
                    print(f'ошибка парсинга карточки{i+1}')  
                    continue  
                
                
            if products_data:
                data = products_data.copy()
                df = pd.DataFrame(products_data)
                df_sorted = df.sort_values('price')
                min_price_product = df_sorted.iloc[0]
                
                print("\n" + "=" * 60)
                print("🎯 РЕЗУЛЬТАТЫ ПОИСКА МИНИМАЛЬНОЙ ЦЕНЫ:")
                print("=" * 60)
                print(f"💰 Самый дешевый товар: {min_price_product['title']}")
                print(f"💵 Цена: {min_price_product['price']} руб.")
                print(f"📊 Всего обработано товаров: {len(products_data)}")
                        
                df_sorted.to_csv('ozon_products.csv',index=False,encoding='utf-8-sig')
                message_text = ''
                message_text +=('\n топ 5 самых дешёвых товаров')
                message_text +=('-'*20)
                
                for idx,row in df_sorted.head().iterrows():
                    title_short = row['title'[:70]+"..." if len(row['title'])> 70 else row['title']]
                    message_text +=(f'{row['price']} руб. - {title_short}')
                return message_text
            
            else:
                print("товар не найден") 
                with open("ozon_results_debug.html","w",encoding="utf-8") as file:
                    file.write(self.driver.page_source)       
                return None
            
        except Exception as e:
            print(f'критическая ошибка{e}')
            return None
        
        
        
# ozon_parser = OzonParser()
# # data = ozon_parser.get_info('iphone 17') 
# message = ''
# for idx,row in data.head().iterrows():
#     if idx < 3:
#         title_short = row['title'[:70]+"..." if len(row['title'])> 70 else row['title']]
#         image_url = row['image_url']
#         message += f'{title_short} - {row['price']} руб.'
