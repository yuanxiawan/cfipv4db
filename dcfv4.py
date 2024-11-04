import requests

def fetch_ip_data(url):
    """获取IP数据"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip().splitlines()
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return []

def fetch_ip_location(ip):
    """查询IP的地理位置"""
    location_api_url = f"http://ip-api.com/json/{ip}"
    try:
        response = requests.get(location_api_url)
        response.raise_for_status()
        data = response.json()
        return data.get('region', '未知区域')
    except requests.RequestException as e:
        print(f"获取位置错误: {e}")
        return '未知区域'

def generate_output_file(ip_data, output_filename):
    """生成输出文件"""
    seen = set()
    with open(output_filename, 'w', encoding='utf-8') as f:
        for ip_entry in ip_data:
            ip = ip_entry.split('#')[0]  # 提取IP部分
            location = fetch_ip_location(ip)  # 获取地理位置

            # 处理重复项
            output_line = f"{ip}#{location}"
            count = 1
            while output_line in seen:
                count += 1
                output_line = f"{ip}#{location}{count}"
            seen.add(output_line)

            f.write(output_line + '\n')
    print(f"输出已保存到 {output_filename}")

# 主程序
url = "https://addressesapi.090227.xyz/ip.164746.xyz"
ip_data = fetch_ip_data(url)
generate_output_file(ip_data, "cf.txt")
