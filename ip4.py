import csv
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def fetch_and_write_csv_with_requests(url, filename, is_first_run):
    """使用 requests 抓取静态网页数据并追加到 CSV 文件"""
    try:
        print(f"正在使用 requests 抓取：{url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')

        if table is None:
            print("未找到数据表！")
            return

        # 打开 CSV 文件并追加内容
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # 获取表格头部，只在文件的第一次写入时添加头部
            if is_first_run and file.tell() == 0:
                headers = [col.text.strip() for col in table.find_all('th')]
                writer.writerow(['Source'] + headers)  # 添加数据来源列

            # 获取表格数据
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                row_data = [col.text.strip() for col in cols]
                if row_data:  # 过滤空行
                    writer.writerow([url] + row_data)

        print(f"CSV文件已成功保存为：{filename}")

    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except IOError as e:
        print(f"文件操作错误: {e}")

def fetch_and_write_csv_with_selenium(url, filename, is_first_run):
    """使用 Selenium 从动态加载的网页抓取数据并追加到 CSV 文件"""
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

        # 打开 CSV 文件并追加内容
        with open(filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # 获取表格头部，只在文件的第一次写入时添加头部
            if is_first_run and file.tell() == 0:
                headers = [header.text.strip() for header in table.find_elements(By.TAG_NAME, 'th')]
                writer.writerow(['Source'] + headers)  # 添加数据来源列

            # 获取表格数据
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                row_data = [col.text.strip() for col in cols]
                if row_data:  # 过滤空行
                    writer.writerow([url] + row_data)

        print(f"CSV文件已成功保存为：{filename}")

    except Exception as e:
        print(f"请求错误: {e}")
    
    finally:
        driver.quit()

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
                        # 将顺序数字加在 sixth_column 后面
                        outfile.write(f"{second_column}#{sixth_column}{index}\n")
                        
        print(f"TXT文件已成功生成为：{txt_filename}")
    except IOError as e:
        print(f"文件操作错误: {e}")

# 定义URL和文件名
URLS = {
    "https://www.wetest.vip/page/cloudflare/address_v4.html": "requests",
    "https://stock.hostmonit.com/CloudFlareYes": "selenium",  # 使用Selenium抓取
}

CSV_FILENAME = 'cfip.csv'
TXT_FILENAME = 'cfip4.txt'

# 执行数据抓取和处理
print("开始执行...")
is_first_run = True

# 遍历 URL 列表
for url, method in URLS.items():
    if method == "requests":
        fetch_and_write_csv_with_requests(url, CSV_FILENAME, is_first_run)
    elif method == "selenium":
        fetch_and_write_csv_with_selenium(url, CSV_FILENAME, is_first_run)
    is_first_run = False  # 只在第一次运行时写入头部

# 处理 CSV 文件并生成 TXT 文件
process_csv_to_txt(CSV_FILENAME, TXT_FILENAME)

print("任务已完成。")
