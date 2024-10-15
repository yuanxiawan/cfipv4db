# ip42.py

import asyncio
import base64
from playwright.async_api import async_playwright
import pandas as pd

async def fetch_data(url):
    """从给定的 URL 抓取数据"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(2000)  # 等待页面加载

        # 选择要抓取的数据
        # 假设数据在一个特定的 div 中
        # 你可以根据需要调整选择器
        data_divs = await page.query_selector_all("tbody")  # 替换为实际的类名

        data = []
        for div in data_divs:
            # 假设每个 div 中有多个需要抓取的字段
            # 修改以提取实际数据
            title = await div.query_selector("tr")  # 假设每个 div 中有一个 h2 元素
            description = await div.query_selector("td")  # 假设有一个 p 元素
            
            title_text = await title.inner_text() if title else "N/A"
            description_text = await description.inner_text() if description else "N/A"

            data.append({
                "Title": title_text,
                "Description": description_text,
            })

        await browser.close()
        return data

def save_to_csv(data, filename):
    """将数据保存为 CSV 文件"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"CSV文件已成功保存为：{filename}")

# 主程序
if __name__ == "__main__":
    # 编码的 URL
    encoded_url = "aHR0cHM6Ly93d3cud2V0ZXN0LnZpcC9wYWdlL2Nsb3VkZmxhcmUvYWRkcmVzc192NC5odG1s"
    decoded_url = base64.b64decode(encoded_url).decode('utf-8')

    # 异步运行抓取数据
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(fetch_data(decoded_url))
    save_to_csv(data, 'output.csv')
