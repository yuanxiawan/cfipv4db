import requests
import json
import base64

def fetch_data(url):
    """抓取并返回API数据"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

def process_data(data, output_file):
    """处理数据并写入到文本文件中"""
    colo_counter = {}
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            for provider in ['CM', 'CU', 'CT']:
                if provider in data['info']:
                    for entry in data['info'][provider]:
                        ip = entry['ip']
                        colo = entry['colo']

                        # 如果相同colo名称出现多次，为其添加递增编号
                        if colo in colo_counter:
                            colo_counter[colo] += 1
                            formatted_entry = f"{ip}#{colo}{colo_counter[colo]}"
                        else:
                            colo_counter[colo] = 1
                            formatted_entry = f"{ip}#{colo}"

                        file.write(formatted_entry + "\n")
            print(f"数据已保存到 {output_file}")
    except IOError as e:
        print(f"文件写入错误: {e}")

# 隐藏的加密 URL
encoded_url = "aHR0cHM6Ly93d3cud2V0ZXN0LnZpcC9hcGkvY2YyZG5zL2dldF9jbG91ZGZsYXJlX2lw"
decoded_url = base64.b64decode(encoded_url).decode("utf-8")

# 执行数据抓取和处理
data = fetch_data(decoded_url)
if data and data.get("status"):
    process_data(data, "cloudflare_ips.txt")
