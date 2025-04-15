from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def fetch_html_with_selenium(url):
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(url)
        time.sleep(5) # 等待页面加载完成 (根据实际情况调整)
        html_content = driver.page_source
        driver.quit()
        return html_content
    except Exception as e:
        print(f"使用 Selenium 获取 HTML 失败: {e}")
        return None

def extract_and_process_data(html_content, output_file):
    soup = BeautifulSoup(html_content, 'html.parser')
    start_div = soup.find('div', class_='cname-table-wrapper')
    end_div = soup.find('div', class_='container footer-content')

    if not start_div or not end_div:
        print("未找到起始或结束 div 标记。")
        return

    table = start_div.find('table')  # 假设表格在 start_div 内
    if not table:
        print("未找到表格。")
        return

    data_center_counter = {}
    extracted_data = []

    for row in table.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) == 2:
            data_center = columns[0].get_text(strip=True)
            preferred_ip = columns[1].get_text(strip=True)

            processed_data_center = data_center
            if data_center in data_center_counter:
                data_center_counter[data_center] += 1
                processed_data_center = f"{data_center}{data_center_counter[data_center]}"
            else:
                data_center_counter[data_center] = 1

            extracted_data.append(f"{preferred_ip}#{processed_data_center}")

    extracted_data.sort()

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in extracted_data:
            f.write(item + "\n")

    print(f"数据已成功提取、处理并保存到 {output_file}")

if __name__ == "__main__":
    target_url = "https://www.wetest.vip/page/cloudflare/address_v4.html"
    html_content = fetch_html_with_selenium(target_url)
    if html_content:
        extract_and_process_data(html_content, "cloudflare_ipv402.txt")
