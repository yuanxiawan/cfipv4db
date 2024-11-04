import requests

def fetch_ip_data(url):
    """获取IP数据"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.text.strip().splitlines()  # 按行分割
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return []  # 返回空列表以防后续代码出错

def fetch_ip_location(ip):
    """查询IP的地理位置"""
    location_api_url = f"http://ip-api.com/json/{ip}"
    try:
        response = requests.get(location_api_url)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        return data.get('region', '未知区域')  # 获取区域，默认为“未知区域”
    except requests.RequestException as e:
        print(f"获取位置错误: {e}")
        return '未知区域'  # 发生错误时返回“未知区域”

def generate_output_file(ip_data, output_filename):
    """生成输出文件"""
    seen = {}  # 用于跟踪已处理的输出行
    with open(output_filename, 'w', encoding='utf-8') as f:
        for ip_entry in ip_data:
            ip = ip_entry.split('#')[0]  # 提取IP部分
            location = fetch_ip_location(ip)  # 获取地理位置
            
            # 处理重复项
            output_line = f"{ip}#{location}"
            if output_line in seen:
                seen[output_line] += 1  # 增加重复计数
                output_line = f"{ip}#{location}{seen[output_line]}"  # 生成新的唯一行
            else:
                seen[output_line] = 1  # 初始化计数为1

            f.write(output_line + '\n')  # 写入文件
    print(f"输出已保存到 {output_filename}")

# 主程序
url = "https://addressesapi.090227.xyz/ip.164746.xyz"  # 目标URL
ip_data = fetch_ip_data(url)  # 获取IP数据
generate_output_file(ip_data, "cf.txt")  # 生成输出文件
