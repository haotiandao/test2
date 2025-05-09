import re
import requests
import logging
from collections import OrderedDict, defaultdict
from datetime import datetime
import subprocess
import os
import time

# 配置日志记录，输出到控制台和文件
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("function.log", "w", encoding="utf-8"), logging.StreamHandler()])

def parse_template(template_file):
    # 创建一个有序字典来存储模板频道信息
    template_channels = OrderedDict()
    current_category = None

    # 打开模板文件并读取内容
    with open(template_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()  # 去除行首尾空格
            if line and not line.startswith("#"):  # 忽略空行和注释行
                if "#genre#" in line:  # 检查是否为分类行
                    current_category = line.split(",")[0].strip()  # 提取分类名称
                    template_channels[current_category] = []  # 初始化该分类的频道列表
                elif current_category:  # 如果当前分类存在
                    channel_name = line.split(",")[0].strip()  # 提取频道名称
                    template_channels[current_category].append(channel_name)  # 将频道名称添加到当前分类

    return template_channels

def fetch_channels(url):
    # 创建一个有序字典来存储抓取的频道信息
    channels = OrderedDict()

    try:
        response = requests.get(url)  # 发送HTTP GET请求获取数据
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常
        response.encoding = 'utf-8'  # 设置响应编码为UTF-8
        lines = response.text.split("\n")  # 将响应文本按行分割
        current_category = None
        is_m3u = any("#EXTINF" in line for line in lines[:15])  # 判断是否为M3U格式
        source_type = "m3u" if is_m3u else "txt"  # 根据判断结果确定源类型
        logging.info(f"url: {url} 获取成功，判断为{source_type}格式")  # 记录日志

        if is_m3u:  # 如果是M3U格式
            for line in lines:
                line = line.strip()  # 去除行首尾空格
                if line.startswith("#EXTINF"):  # 检查是否为频道信息行
                    match = re.search(r'group-title="(.*?)",(.*)', line)  # 正则表达式提取分类和频道名称
                    if match:
                        current_category = match.group(1).strip()  # 提取分类名称
                        channel_name = match.group(2).strip()  # 提取频道名称
                        if current_category not in channels:  # 如果该分类不存在
                            channels[current_category] = []  # 初始化该分类的频道列表
                elif line and not line.startswith("#"):  # 如果是频道URL行且非注释行
                    channel_url = line.strip()  # 提取频道URL
                    if current_category and channel_name:  # 如果当前分类和频道名称存在
                        channels[current_category].append((channel_name, channel_url))  # 将频道名称和URL添加到当前分类
        else:  # 如果是TXT格式
            for line in lines:
                line = line.strip()  # 去除行首尾空格
                if "#genre#" in line:  # 检查是否为分类行
                    current_category = line.split(",")[0].strip()  # 提取分类名称
                    channels[current_category] = []  # 初始化该分类的频道列表
                elif current_category:  # 如果当前分类存在
                    match = re.match(r"^(.*?),(.*?)$", line)  # 正则表达式提取频道名称和URL
                    if match:
                        channel_name = match.group(1).strip()  # 提取频道名称
                        channel_url = match.group(2).strip()  # 提取频道URL
                        channels[current_category].append((channel_name, channel_url))  # 将频道名称和URL添加到当前分类
                    elif line:  # 如果只有频道名称
                        channels[current_category].append((line, ''))  # 将频道名称和空URL添加到当前分类
        if channels:  # 如果抓取到了频道信息
            categories = ", ".join(channels.keys())  # 获取所有分类名称
            logging.info(f"url: {url} 爬取成功✅，包含频道分类: {categories}")  # 记录日志
    except requests.RequestException as e:  # 捕获请求异常
        logging.error(f"url: {url} 爬取失败❌, Error: {e}")  # 记录错误日志

    return channels

def match_channels(template_channels, all_channels):
    # 创建一个有序字典来存储匹配后的频道信息
    matched_channels = OrderedDict()

    # 遍历模板频道
    for category, channel_list in template_channels.items():
        matched_channels[category] = OrderedDict()  # 初始化该分类的匹配频道列表
        for channel_name in channel_list:  # 遍历每个频道名称
            for online_category, online_channel_list in all_channels.items():  # 遍历所有抓取的频道
                for online_channel_name, online_channel_url in online_channel_list:  # 遍历每个抓取的频道
                    if channel_name == online_channel_name:  # 如果模板频道名称与抓取的频道名称匹配
                        matched_channels[category].setdefault(channel_name, []).append(online_channel_url)  # 将抓取的频道URL添加到匹配频道列表

    return matched_channels

def filter_source_urls(template_file):
    # 解析模板文件获取模板频道信息
    template_channels = parse_template(template_file)
    source_urls = [
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.txt"  # 添加其他源URL
    ]

    all_channels = OrderedDict()  # 创建一个有序字典来存储所有抓取的频道信息
    for url in source_urls:  # 遍历每个源URL
        fetched_channels = fetch_channels(url)  # 抓取频道信息
        for category, channel_list in fetched_channels.items():  # 遍历每个抓取的频道分类
            if category in all_channels:  # 如果该分类已存在于所有频道中
                all_channels[category].extend(channel_list)  # 将新抓取的频道添加到现有分类
            else:
                all_channels[category] = channel_list  # 否则创建新的分类并添加频道

    matched_channels = match_channels(template_channels, all_channels)  # 匹配模板频道和所有抓取的频道

    return matched_channels, template_channels

def is_ipv6(url):
    # 使用正则表达式检查URL是否为IPv6地址
    return re.match(r'^http:\/\/\[[0-9a-fA-F:]+\]', url) is not None

def updateChannelUrlsM3U(channels, template_channels):
    written_urls = set()  # 创建一个集合来存储已写入的URL，避免重复

    current_date = datetime.now().strftime("%Y-%m-%d")  # 获取当前日期
    announcements = [
        {
            'channel': 'Announcement',
            'entries': [{'name': current_date, 'logo': '', 'url': ''}]  # 创建公告条目
        }
    ]

    # 写入M3U文件
    with open("live.m3u", "w", encoding="utf-8") as f_m3u:
        f_m3u.write(f"""#EXTM3U x-tvg-url={",".join(f'"{epg_url}"' for epg_url in ["http://example.com/epg.xml"])}\n""")  # 写入EPG URL

        # 写入TXT文件
        with open("live.txt", "w", encoding="utf-8") as f_txt:
            for group in announcements:  # 遍历公告组
                f_txt.write(f"{group['channel']},#genre#\n")  # 写入公告分类
                for announcement in group['entries']:  # 遍历每个公告条目
                    f_m3u.write(f"""#EXTINF:-1 tvg-id="1" tvg-name="{announcement['name']}" tvg-logo="{announcement['logo']}" group-title="{group['channel']}",{announcement['name']}\n""")  # 写入公告信息
                    f_m3u.write(f"{announcement['url']}\n")  # 写入公告URL
                    f_txt.write(f"{announcement['name']},{announcement['url']}\n")  # 写入公告信息到TXT文件

            for category, channel_list in template_channels.items():  # 遍历模板频道分类
                f_txt.write(f"{category},#genre#\n")  # 写入分类
                if category in channels:  # 如果该分类存在于匹配频道中
                    for channel_name in channel_list:  # 遍历每个频道名称
                        if channel_name in channels[category]:  # 如果该频道名称存在于匹配频道中
                            sorted_urls = sorted(channels[category][channel_name], key=lambda url: not is_ipv6(url) if True == "ipv6" else is_ipv6(url))  # 根据是否为IPv6地址排序URL
                            filtered_urls = []
                            for url in sorted_urls:  # 遍历排序后的URL
                                if url and url not in written_urls and not any(blacklist in url for blacklist in []):  # 过滤无效URL和黑名单URL
                                    filtered_urls.append(url)  # 将有效URL添加到过滤列表
                                    written_urls.add(url)  # 将URL标记为已写入

                            total_urls = len(filtered_urls)  # 获取过滤后URL的数量
                            for index, url in enumerate(filtered_urls, start=1):  # 遍历过滤后的URL
                                if is_ipv6(url):  # 如果URL为IPv6地址
                                    url_suffix = f"$LR•IPV6" if total_urls == 1 else f"$LR•IPV6『线路{index}』"  # 添加后缀标识
                                else:  # 如果URL为IPv4地址
                                    url_suffix = f"$LR•IPV4" if total_urls == 1 else f"$LR•IPV4『线路{index}』"  # 添加后缀标识
                                if '$' in url:  # 如果URL中包含$
                                    base_url = url.split('$', 1)[0]  # 提取基础URL
                                else:
                                    base_url = url  # 否则基础URL即为原URL

                                new_url = f"{base_url}{url_suffix}"  # 构建新的URL

                                f_m3u.write(f"#EXTINF:-1 tvg-id=\"{index}\" tvg-name=\"{channel_name}\" tvg-logo=\"https://gcore.jsdelivr.net/gh/yuanzl77/TVlogo@master/png/{channel_name}.png\" group-title=\"{category}\",{channel_name}\n")  # 写入频道信息
                                f_m3u.write(new_url + "\n")  # 写入新的URL
                                f_txt.write(f"{channel_name},{new_url}\n")  # 写入频道信息到TXT文件

            f_txt.write("\n")  # 写入换行符

def download_video(url, output_path, duration=2):
    """
    使用FFmpeg从指定URL下载指定时长的视频。
    
    :param url: 直播源地址
    :param output_path: 下载视频保存路径
    :param duration: 下载时长（秒）
    :return: 下载时间（秒）
    """
    command = [
        'ffmpeg',
        '-i', url,
        '-t', str(duration),
        '-c', 'copy',
        output_path
    ]
    start_time = time.time()  # 记录开始时间
    try:
        subprocess.run(command, check=True)  # 运行FFmpeg命令
        end_time = time.time()  # 记录结束时间
        download_time = end_time - start_time  # 计算下载时间
        print(f"视频已成功下载到 {output_path}，耗时 {download_time:.2f} 秒")  # 输出下载信息
        return download_time  # 返回下载时间
    except subprocess.CalledProcessError as e:  # 捕获子进程异常
        print(f"下载失败: {e}")  # 输出错误信息
        return float('inf')  # 返回一个很大的值表示下载失败

def get_video_info(video_path):
    """
    使用FFprobe获取视频文件的信息，包括分辨率和文件大小。
    
    :param video_path: 视频文件路径
    :return: 包含分辨率和文件大小的字典
    """
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height;format=size',
        '-of', 'csv=s=x:p=0',
        video_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)  # 运行FFprobe命令
    if result.returncode != 0:  # 如果命令执行失败
        print(f"获取视频信息失败: {result.stderr}")  # 输出错误信息
        return None  # 返回None
    
    width, height, size = result.stdout.strip().split('x')  # 分割输出结果
    resolution = f"{width}x{height}"  # 构建分辨率字符串
    file_size = int(size)  # 转换文件大小为整数
    return {'resolution': resolution, 'file_size': file_size}  # 返回包含分辨率和文件大小的字典

def test_live_stream(urls, output_dir='temp_videos'):
    """
    测试多个直播源地址，下载2秒的视频并检查分辨率和文件大小，并按速度排序。
    
    :param urls: 直播源地址列表
    :param output_dir: 临时视频文件保存目录
    :return: 排序后的直播源地址列表
    """
    if not os.path.exists(output_dir):  # 如果临时目录不存在
        os.makedirs(output_dir)  # 创建临时目录
    
    results = []  # 创建一个列表来存储测试结果

    for index, url in enumerate(urls):  # 遍历每个直播源地址
        output_path = os.path.join(output_dir, f'temp_{index}.ts')  # 构建临时文件路径
        print(f"正在测试 URL: {url}")
        
        # 下载视频并记录下载时间
        download_time = download_video(url, output_path)
        
        # 获取视频信息
        info = get_video_info(output_path)
        if info:  # 如果获取到视频信息
            print(f"分辨率: {info['resolution']}, 文件大小: {info['file_size']} bytes")
            
            # 判断是否满足条件（这里可以根据需要调整判断标准）
            if info['file_size'] > 0 and info['resolution']:
                results.append((url, download_time))  # 将URL和下载时间添加到结果列表
        
        # 删除临时文件
        os.remove(output_path)
    
    if not results:  # 如果没有找到可用的直播源
        print("没有找到可用的直播源")
        return []
    
    # 按下载时间升序排序
    results.sort(key=lambda x: x[1])
    
    # 提取排序后的URL列表
    sorted_urls = [url for url, _ in results]
    print(f"排序后的直播源地址是: {sorted_urls}")
    return sorted_urls

if __name__ == "__main__":
    template_file = "demo.txt"
    channels, template_channels = filter_source_urls(template_file)
    
    # 示例直播源地址列表
    live_urls = [
        "http://example.com/live/stream1.m3u8",
        "http://example.com/live/stream2.m3u8"
    ]  # 替换为实际的直播源地址
    
    sorted_live_urls = test_live_stream(live_urls)
    
    # 更新频道URLs时使用排序后的第一个URL
    if sorted_live_urls:
        first_available_url = sorted_live_urls[0]
        print(f"最终选择的直播源地址是: {first_available_url}")
        
        # 假设我们只使用第一个可用的URL来更新频道URLs
        updated_channels = {}
        for category, channel_list in channels.items():
            updated_channels[category] = [(channel_name, first_available_url) for channel_name, _ in channel_list]
        
        updateChannelUrlsM3U(updated_channels, template_channels)
    else:
        print("没有找到可用的直播源，无法更新频道URLs")



