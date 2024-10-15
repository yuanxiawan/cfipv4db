import csv
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import base64

# 手动选择抓取方式
USE_PLAYWRIGHT = {
    "https://www.wetest.vip/page/cloudflare/address_v4.html": True,
    "https://stock.hostmonit.com/CloudFlareYes": True
}

def fetch_data_with_requests(url):
    """使用 requests 抓取静态网页"""
    try:
        print(f"正在使用 requests 抓取：{url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

def fetch_data_with_playwright(url):
    """使用 Playwright 抓取动态加载数据的网页"""
    try:
        print(f"正在使用 Playwright 抓取：{url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        print(f"Playwright 抓取错误: {e}")
        return None

def fetch_and_write_csv(url, filename, use_playwright):
    """根据选择的方式抓取数据并写入CSV文件"""
    content = None
    if use_playwright:
        content = fetch_data_with_playwright(url)
    else:
        content = fetch_data_with_requests(url)

    if not content:
        print(f"抓取 {url} 失败！")
        return

    try:
        soup = BeautifulSoup(content, 'html.parser')
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
    except IOError as e:
        print(f"文件操作错误: {e}")

def process_csv_to_txt(input_filename, txt_filename):
    """处理CSV文件，提取特定列并写入TXT文件"""
    try:
        with open(input_filename, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            with open(txt_filename, mode='w', encoding='utf-8') as outfile:
                for index, row in enumerate(reader, start=1):
                    if row:
                        if len(row) < 6:
                            print(f"行 {index} 没有足够的列数据，跳过该行")
                            continue
                        second_column = row[1]  # 第二列
                        sixth_column = row[5]   # 第六列
                        outfile.write(f"{second_column}#{sixth_column}{index}\n")
        print(f"TXT文件已成功生成为：{txt_filename}")
    except IOError as e:
        print(f"文件操作错误: {e}")

# 编码的 URL 列表
encoded_urls = [
    "aHR0cHM6Ly93d3cud2V0ZXN0LnZpcC9wYWdlL2Nsb3VkZmxhcmUvYWRkcmVzc192NC5odG1s",
    "aHR0cHM6Ly9zdG9jay5ob3N0bW9uaXQuY29tL0Nsb3VkRmxhcmVZZXM="
]

# 解码 URL
decoded_urls = [base64.b64decode(url).decode('utf-8') for url in encoded_urls]

# 执行数据抓取和处理
print("开始执行...")

csv_filename = 'cfip.csv'
txt_filename = 'cfip4.txt'

for url in decoded_urls:
    use_playwright = USE_PLAYWRIGHT.get(url, False)
    fetch_and_write_csv(url, csv_filename, use_playwright)

process_csv_to_txt(csv_filename, txt_filename)
print("任务已完成。")
