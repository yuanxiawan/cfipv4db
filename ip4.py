import csv
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import base64

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

def fetch_and_write_csv(url, filename, use_playwright, div_class, table_id, columns_per_row):
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
        
        # 找到指定的 div class="layui-card-body"
        target_div = soup.find('div', class_=div_class)
        if target_div is None:
            print("未找到包含目标表格的DIV！")
            return

        # 在目标 div 内部查找表格
        table = target_div.find('table', id=table_id)
        
        if table is None:
            print("未找到数据表！")
            return

        # 找到 <tbody>，然后直接获取 <td> 元素
        tbody = table.find('tbody')
        if tbody is None:
            print("未找到 <tbody> 元素！")
            return

        # 打开CSV文件写入数据
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            row_data = []
            
            # 遍历每个 <td>，按每行数据的列数划分
            for index, td in enumerate(tbody.find_all('td')):
                row_data.append(td.text.strip())
                if (index + 1) % columns_per_row == 0:
                    writer.writerow(row_data)
                    row_data = []

            # 检查是否有剩余未写入的列
            if row_data:
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
    "aHR0cHM6Ly93d3cud2V0ZXN0LnZpcC9wYWdlL2Nsb3VkZmxhcmUvYWRkcmVzc192NC5odG1s"
]

# 解码 URL
decoded_urls = [base64.b64decode(url).decode('utf-8') for url in encoded_urls]

# 手动指定每个URL是否使用Playwright和目标表格的id
use_playwright = [True]  # 如果需要使用 Playwright 抓取
div_class = 'layui-card-body'  # 目标 div 的 class
table_id = 'data-table'  # 目标表格的id
columns_per_row = 6  # 每行的数据列数

# 执行数据抓取和处理
print("开始执行...")

csv_filename = 'cfip.csv'
txt_filename = 'cfip4.txt'

for url, use_pw in zip(decoded_urls, use_playwright):
    fetch_and_write_csv(url, csv_filename, use_pw, div_class, table_id, columns_per_row)

process_csv_to_txt(csv_filename, txt_filename)
print("任务已完成。")
