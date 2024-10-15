import csv
import asyncio
from playwright.async_api import async_playwright
import base64

async def fetch_and_write_csv(url, filename):
    """使用Playwright从给定的URL抓取数据并写入CSV文件"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            print(f"正在请求：{url}")
            await page.goto(url)
            await page.wait_for_load_state('networkidle')  # 等待页面完全加载

            # 获取表格内容
            table = await page.query_selector('table')

            if table is None:
                print("未找到数据表！")
                await browser.close()
                return

            # 获取表格行内容
            rows = await table.query_selector_all('tr')
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # 遍历每一行
                for row in rows:
                    cols = await row.query_selector_all('td')
                    row_data = [await col.inner_text() for col in cols]
                    writer.writerow(row_data)
                    
            print(f"CSV文件已成功保存为：{filename}")
            await browser.close()

    except Exception as e:
        print(f"请求错误: {e}")

def process_csv_to_txt(input_filename, txt_filename):
    """处理CSV文件，提取特定列并写入TXT文件"""
    try:
        with open(input_filename, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            with open(txt_filename, mode='w', encoding='utf-8') as outfile:
                for index, row in enumerate(reader, start=1):  # 从1开始计数
                    if len(row) >= 6:  # 确保每行有至少6列
                        second_column = row[1]  # 第二列
                        sixth_column = row[5]    # 第六列
                        outfile.write(f"{second_column}#{sixth_column}{index}\n")
                    else:
                        print(f"行 {index} 没有足够的列数据，跳过该行")
                        
        print(f"TXT文件已成功生成为：{txt_filename}")
    except IOError as e:
        print(f"文件操作错误: {e}")

# 编码的 URL
encoded_url = "aHR0cHM6Ly93d3cud2V0ZXN0LnZpcC9wYWdlL2Nsb3VkZmxhcmUvYWRkcmVzc192NC5odG1s"

# 解码 URL
decoded_url = base64.b64decode(encoded_url).decode('utf-8')

# 异步运行 Playwright
print("开始执行...")
asyncio.run(fetch_and_write_csv(decoded_url, 'cfip.csv'))
process_csv_to_txt('cfip.csv', 'cfip4.txt')
print("任务已完成。")
