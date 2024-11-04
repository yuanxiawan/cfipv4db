import requests

def fetch_ip_data(url):
    """从指定URL获取IP数据"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.text.strip().splitlines()
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return []

def get_ip_location(ip):
    """查询IP的地理位置"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return f"{ip}#{data['regionName']}"  # 只提取地区名称
            else:
                print(f"无法获取 {ip} 的地理位置: {data['message']}")
                return None
        else:
            print(f"IP查询请求失败: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

def save_to_file(data, filename):
    """将结果保存到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for item in data:
                file.write(f"{item}\n")
        print(f"内容已成功保存到 {filename}")
    except IOError as e:
        print(f"文件操作错误: {e}")

def main():
    url = "https://addressesapi.090227.xyz/ip.164746.xyz"
    ip_lines = fetch_ip_data(url)

    if not ip_lines:
        return

    results = []
    sequence_counter = {}

    for line in ip_lines:
        if line:
            ip, _ = line.split('#')
            location = get_ip_location(ip)
            if location:
                # 检查是否已存在相同的地区，添加序列保证不重名
                region = location.split('#')[1]
                if region in sequence_counter:
                    sequence_counter[region] += 1
                else:
                    sequence_counter[region] = 1

                # 生成不重复的名称
                unique_name = f"{ip}#{region}"
                if sequence_counter[region] > 1:
                    unique_name += str(sequence_counter[region])

                results.append(unique_name)

    save_to_file(results, "cf.txt")

if __name__ == "__main__":
    main()
