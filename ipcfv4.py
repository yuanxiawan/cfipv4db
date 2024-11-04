import requests
import json

def fetch_and_save_cloudflare_ips(api_url, output_file):
    try:
        # 发送请求获取数据
        response = requests.get(api_url)
        response.raise_for_status()  # 确保请求成功

        # 解析 JSON 响应
        data = response.json()

        # 检查状态码和消息
        if data.get("status") and data.get("code") == 200:
            ip_info = data["info"]  # 获取包含 CM、CU、CT 的信息

            # 打开文件并写入数据
            with open(output_file, 'w', encoding='utf-8') as file:
                for provider, entries in ip_info.items():
                    file.write(f"{provider}:\n")  # 写入提供商名称，如 CM、CU、CT
                    for entry in entries:
                        # 提取并格式化每个字段
                        ip = entry.get("ip")
                        line_name = entry.get("line_name")
                        bandwidth = entry.get("bandwidth")
                        speed = entry.get("speed")
                        colo = entry.get("colo")
                        delay = entry.get("delay")
                        uptime = entry.get("uptime")
                        
                        # 写入格式化内容到文件
                        file.write(
                            f"IP: {ip}, Line: {line_name}, Bandwidth: {bandwidth} Mbps, "
                            f"Speed: {speed} Kbps, Colo: {colo}, Delay: {delay} ms, Uptime: {uptime}\n"
                        )
                    file.write("\n")  # 分隔不同提供商的数据

            print(f"数据已成功保存到 {output_file}")
        else:
            print("数据请求失败或格式不正确。")
        
    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except json.JSONDecodeError:
        print("JSON解析错误。请检查API响应格式。")

# 使用API的URL
api_url = "https://www.wetest.vip/api/cf2dns/get_cloudflare_ip"
output_file = "cloudflare_ips.txt"

# 执行数据抓取并保存到文本文件
fetch_and_save_cloudflare_ips(api_url, output_file)
