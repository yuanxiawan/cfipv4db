import csv
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import base64
import logging
import subprocess

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_data_with_requests(url):
    """使用 requests 抓取静态网页"""
    try:
        logging.info(f"正在使用 requests 抓取：{url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"请求错误: {e}")
        return None

def fetch_data_with_playwright(url):
    """使用 Playwright 抓取动态加载数据的网页"""
    try:
        logging.info(f"正在使用 Playwright 抓取：{url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        logging.error(f"Playwright 抓取错误: {e}")
        return None

def fetch_and_write_csv(url, filename, use_playwright, div_class, table_id):
    """根据选择的方式抓取数据并写入CSV文件"""
    try:
        content = None
        if use_playwright:
            content = fetch_data_with_playwright(url)
        else:
            content = fetch_data_with_requests(url)

        if not content:
            logging.error(f"抓取 {url} 失败！")
            return

        soup = BeautifulSoup(content, 'html.parser')

        # 找到 class 为 "cname-table-wrapper" 的 div 元素
        target_div = soup.find('div', class_=div_class)
        if target_div is None:
            logging.error(f"未找到 class 为 '{div_class}' 的 DIV 元素！")
            return

        # 在目标 div 内部查找表格
        table = target_div.find('table')
        if table is None:
            logging.error("在目标 DIV 中未找到数据表！")
            return

        # 找到 <tbody>，然后直接获取 <tr> 元素
        tbody = table.find('tbody')
        if tbody is None:
            logging.error("未找到 <tbody> 元素！")
            return

        # 提取表头
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.text.strip() for th in header_row.find_all('th')]

        # 打开CSV文件写入数据
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if headers:
                writer.writerow(headers)  # 写入表头
            # 遍历每个 <tr>，然后获取每行中的 <td>
            for tr in tbody.find_all('tr'):
                cols = tr.find_all('td')
                if cols:  # 仅处理包含 <td> 的行
                    row_data = [col.text.strip() for col in cols]
                    writer.writerow(row_data)

        logging.info(f"CSV文件已成功保存为：{filename}")
    except Exception as e:
        logging.error(f"抓取或写入CSV文件时发生错误: {e}")

def process_csv_to_txt(input_filename, txt_filename):
    """处理CSV文件，提取特定列并写入TXT文件"""
    try:
        with open(txt_filename, mode='w', encoding='utf-8') as outfile:  # 修改: 'w' 模式，重新写入
            outfile.write("127.0.0.1:1234#cnat\n") # 在文件开头写入
            with open(input_filename, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                for index, row in enumerate(reader, start=1):
                    if row:
                        if len(row) < 6:
                            logging.warning(f"行 {index} 没有足够的列数据，跳过该行")
                            continue
                        second_column = row[1]  # 第二列
                        sixth_column = row[5]  # 第六列
                        line_content = f"{second_column}#{sixth_column}{index}"

                        # 跳过包含 "优选地址#数据中心1" 的行
                        if line_content == "优选地址#数据中心1":
                            logging.info(f"跳过行 {index}: {line_content}")
                            continue

                        outfile.write(line_content + "\n")
        logging.info(f"TXT文件已成功生成为：{txt_filename}")
    except IOError as e:
        logging.error(f"文件操作错误: {e}")

def git_add_and_commit(csv_filename, txt_filename):
    """将生成的文件添加到 Git 并提交"""
    try:
        # 添加文件到 Git
        subprocess.run(["git", "add", csv_filename, txt_filename], check=True)
        logging.info(f"已将 {csv_filename} 和 {txt_filename} 添加到 Git")

        # 提交更改
        commit_message = "Auto-update CSV and TXT files"
        result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)
        if "nothing to commit" in result.stdout:
            logging.info("没有更改需要提交")
        else:
            logging.info(f"已提交更改：{commit_message}")

        # 推送到远程仓库
        subprocess.run(["git", "push"], check=True)
        logging.info("已推送到远程仓库")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git 操作失败: {e}")

# 编码的 URL 列表
encoded_urls = [
    "aHR0cHM6Ly93d3cud2V0ZXN0LnZpcC9wYWdlL2Nsb3VkZmxhcmUvYWRkcmVzc192NC5odG1s"
]

# 解码 URL
decoded_urls = [base64.b64decode(url).decode('utf-8') for url in encoded_urls]

# 手动指定每个URL是否使用Playwright和目标表格的class
use_playwright = [True]  # 如果需要使用 Playwright 抓取
div_class = 'cname-table-wrapper'  # 目标 div 的 class
table_id = None  # 我们直接在找到的 div 内查找表格，不再依赖 id

# 执行数据抓取和处理
logging.info("开始执行...")

# 固定文件名
csv_filename = 'cfip.csv'
txt_filename = 'cfip.txt'

for i, (url, use_pw) in enumerate(zip(decoded_urls, use_playwright)):
    fetch_and_write_csv(url, csv_filename, use_pw, div_class, table_id)
    process_csv_to_txt(csv_filename, txt_filename)
    git_add_and_commit(csv_filename, txt_filename)

logging.info("任务已完成。")
