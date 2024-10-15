import csv
import requests
from bs4 import BeautifulSoup
import base64

def fetch_and_write_csv(url, filename):
    """从给定的URL抓取数据并写入CSV文件"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"正在请求：{url}")
        response = requests.get(url, headers=headers)
        print(f"HTTP Status Code: {response.status_code}")
        print(f"Response Content Preview: {response.content[:500]}")  # 打印前500个字符
        
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
                for index, row in enumerate(reader, start=1):  # 从1开始计数
                    if row:
                        second_column = row[1]  # 第二列
                        sixth_column = row[5]    # 第六列
                        outfile.write(f"{second_column}#{sixth_column}{index}\n")
                        
        print(f"TXT文件已成功生成为：{txt_filename}")
    except IOError as e:
        print(f"文件操作错误: {e}")

# 编码的 URL
encoded_url = "aHR0cHM6Ly93d3cud2V0ZXN0LnZpcC9wYWdlL2Nsb3VkZmxhcmUvYWRkcmVzc192NC5odG1s"

# 解码 URL
decoded_url = base64.b64decode(encoded_url).decode('utf-8')

# 执行数据抓取和处理
print("开始执行...")
fetch_and_write_csv(decoded_url, 'cfip.csv')
process_csv_to_txt('cfip.csv', 'cfip4.txt')
print("任务已完成。")
