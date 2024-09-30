import csv
import requests
from bs4 import BeautifulSoup

def fetch_and_write_csv(url, filename):
    """从给定的URL抓取数据并写入CSV文件"""
    try:
        print(f"正在请求：{url}")
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
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
                for row in reader:
                    if row:
                        second_column = row[1]  # 第二列
                        sixth_column = row[5]   # 第六列
                        # seventh_column = row[6]  # 第七列
                        outfile.write(f"{second_column}#{sixth_column}\n")

        print(f"TXT文件已成功生成为：{txt_filename}")
    except IOError as e:
        print(f"文件操作错误: {e}")

# 定义URL和文件名
URL = "https://www.182682.xyz/page/cloudflare/ipv4.html"
CSV_FILENAME = '4.csv'
TXT_FILENAME = 'ip4.txt'

# 执行数据抓取和处理
print("开始执行...")
fetch_and_write_csv(URL, CSV_FILENAME)
process_csv_to_txt(CSV_FILENAME, TXT_FILENAME)
print("任务已完成。")
