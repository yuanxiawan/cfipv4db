import requests
from bs4 import BeautifulSoup

def extract_and_process_data(url, output_file):
    """抓取网页数据，提取指定表格内容，处理并保存到文件"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        start_marker = soup.find(string='')
        end_marker = soup.find('main')

        if not start_marker or not end_marker:
            print("未找到起始或结束标记。")
            return

        table = None
        current = start_marker.find_next()
        while current and current != end_marker:
            if current.name == 'table':
                table = current
                break
            current = current.find_next()

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

                # 处理重复的数据中心名称
                processed_data_center = data_center
                if data_center in data_center_counter:
                    data_center_counter[data_center] += 1
                    processed_data_center = f"{data_center}{data_center_counter[data_center]}"
                else:
                    data_center_counter[data_center] = 1

                extracted_data.append(f"{preferred_ip}#{processed_data_center}")

        # 按照 "IP#数据中心" 排序
        extracted_data.sort()

        with open(output_file, 'w', encoding='utf-8') as f:
            for item in extracted_data:
                f.write(item + "\n")

        print(f"数据已成功提取、处理并保存到 {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"抓取网页数据失败: {e}")
    except IOError as e:
        print(f"写入文件失败: {e}")

if __name__ == "__main__":
    target_url = "https://www.wetest.vip/page/cloudflare/address_v4.html"
    output_filename = "cloudflare_ipv402.txt"
    extract_and_process_data(target_url, output_filename)
