import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def is_dynamic_page(url):
    """
    判断网页是否动态加载内容，通过查看页面中是否包含明显的动态加载提示。
    这里通过判断是否包含 'script' 标签以及一些常见的动态加载标识（例如 JavaScript、Ajax 等）。
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all('script')
            if scripts:
                # 判断页面中是否包含 JavaScript 标签或常见的动态加载标识
                if any("ajax" in script.get_text().lower() or "javascript" in script.get_text().lower() for script in scripts):
                    return True
        return False
    except Exception as e:
        print(f"无法请求页面: {e}")
        return True  # 如果无法请求页面，默认假设是动态页面


def fetch_and_write_csv_with_selenium(url, filename):
    """使用 Selenium 从动态加载的网页抓取数据并写入 CSV 文件"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--no-sandbox")  # 禁用沙盒
    chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用 /dev/shm 使用，防止内存不足

    # 设置 ChromeDriver 服务
    chrome_service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        print(f"正在使用 Selenium 抓取：{url}")
        driver.get(url)
        time.sleep(5)  # 等待页面加载和JavaScript执行

        # 查找表格元素
        table = driver.find_element(By.TAG_NAME, 'table')
        if not table:
            print("未找到数据表！")
            return

        # 打开 CSV 文件
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # 获取表格头部
            headers = [header.text.strip() for header in table.find_elements(By.TAG_NAME, 'th')]
            writer.writerow(headers)

            # 获取表格数据
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                row_data = [col.text.strip() for col in cols]
                writer.writerow(row_data)

        print(f"CSV文件已成功保存为：{filename}")

    except Exception as e:
        print(f"请求错误: {e}")
    
    finally:
        driver.quit()


def fetch_and_write_csv_with_requests(url, filename):
    """使用 requests 抓取静态网页数据并写入 CSV 文件"""
    try:
        print(f"正在使用 requests 抓取：{url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')

        if table is None:
            print("未找到数据表！")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            headers = []
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if not headers:
                    headers = [col.text.strip() for col in cols]
                    writer.writerow(headers)
                else:
                    row_data = [col.text.strip() for col in cols]
                    writer.writerow(row_data)

        print(f"CSV文件已成功保存为：{filename}")

    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except IOError as e:
        print(f"文件操作错误: {e}")


def process_csv_to_txt(input_filename, txt_filename):
    """处理CSV文件，提取特定列并写入TXT文件"""
    try:
        with open(input_filename, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            with open(txt_filename, mode='w', encoding='utf-8') as outfile:
                for index, row in enumerate(reader, start=1):  # 从1开始计数
                    if row:
                        second_column = row[1]  # 第二列
                        sixth_column = row[5]    # 第六列
                        # 输出第二列和第六列，加入顺序号
                        outfile.write(f"{second_column}#{sixth_column}{index}\n")
                        
        print(f"TXT文件已成功生成为：{txt_filename}")
    except IOError as e:
        print(f"文件操作错误: {e}")


# 定义URL和文件名
URLS = [
    "https://www.wetest.vip/page/cloudflare/address_v4.html",
    "https://stock.hostmonit.com/CloudFlareYes",
    # 你可以添加更多的网址
]
CSV_FILENAME = 'cfip.csv'
TXT_FILENAME = 'cfip4.txt'

# 执行数据抓取和处理
print("开始执行...")

for url in URLS:
    if is_dynamic_page(url):
        fetch_and_write_csv_with_selenium(url, CSV_FILENAME)
    else:
        fetch_and_write_csv_with_requests(url, CSV_FILENAME)

process_csv_to_txt(CSV_FILENAME, TXT_FILENAME)

print("任务已完成。")
