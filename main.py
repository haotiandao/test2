import re
import requests
import logging
from collections import OrderedDict, defaultdict
from datetime import datetime
import subprocess
import os
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("function.log", "w", encoding="utf-8"), logging.StreamHandler()])

def parse_template(template_file):
    template_channels = OrderedDict()
    current_category = None

    with open(template_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "#genre#" in line:
                    current_category = line.split(",")[0].strip()
                    template_channels[current_category] = []
                elif current_category:
                    channel_name = line.split(",")[0].strip()
                    template_channels[current_category].append(channel_name)

    return template_channels

def fetch_channels(url):
    channels = OrderedDict()

    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        lines = response.text.split("\n")
        current_category = None
        is_m3u = any("#EXTINF" in line for line in lines[:15])
        source_type = "m3u" if is_m3u else "txt"
        logging.info(f"url: {url} 获取成功，判断为{source_type}格式")

        if is_m3u:
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF"):
                    match = re.search(r'group-title="(.*?)",(.*)', line)
                    if match:
                        current_category = match.group(1).strip()
                        channel_name = match.group(2).strip()
                        if current_category not in channels:
                            channels[current_category] = []
                elif line and not line.startswith("#"):
                    channel_url = line.strip()
                    if current_category and channel_name:
                        channels[current_category].append((channel_name, channel_url))
        else:
            for line in lines:
                line = line.strip()
                if "#genre#" in line:
                    current_category = line.split(",")[0].strip()
                    channels[current_category] = []
                elif current_category:
                    match = re.match(r"^(.*?),(.*?)$", line)
                    if match:
                        channel_name = match.group(1).strip()
                        channel_url = match.group(2).strip()
                        channels[current_category].append((channel_name, channel_url))
                    elif line:
                        channels[current_category].append((line, ''))
        if channels:
            categories = ", ".join(channels.keys())
            logging.info(f"url: {url} 爬取成功✅，包含频道分类: {categories}")
    except requests.RequestException as e:
        logging.error(f"url: {url} 爬取失败❌, Error: {e}")

    return channels

def match_channels(template_channels, all_channels):
    matched_channels = OrderedDict()

    for category, channel_list in template_channels.items():
        matched_channels[category] = OrderedDict()
        for channel_name in channel_list:
            for online_category, online_channel_list in all_channels.items():
                for online_channel_name, online_channel_url in online_channel_list:
                    if channel_name == online_channel_name:
                        matched_channels[category].setdefault(channel_name, []).append(online_channel_url)

    return matched_channels

def filter_source_urls(template_file):
    template_channels = parse_template(template_file)
    source_urls = ["https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u", "import re
import requests
import logging
from collections import OrderedDict, defaultdict
from datetime import datetime
import subprocess
import os
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("function.log", "w", encoding="utf-8"), logging.StreamHandler()])

def parse_template(template_file):
    template_channels = OrderedDict()
    current_category = None

    with open(template_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "#genre#" in line:
                    current_category = line.split(",")[0].strip()
                    template_channels[current_category] = []
                elif current_category:
                    channel_name = line.split(",")[0].strip()
                    template_channels[current_category].append(channel_name)

    return template_channels

def fetch_channels(url):
    channels = OrderedDict()

    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        lines = response.text.split("\n")
        current_category = None
        is_m3u = any("#EXTINF" in line for line in lines[:15])
        source_type = "m3u" if is_m3u else "txt"
        logging.info(f"url: {url} 获取成功，判断为{source_type}格式")

        if is_m3u:
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF"):
                    match = re.search(r'group-title="(.*?)",(.*)', line)
                    if match:
                        current_category = match.group(1).strip()
                        channel_name = match.group(2).strip()
                        if current_category not in channels:
                            channels[current_category] = []
                elif line and not line.startswith("#"):
                    channel_url = line.strip()
                    if current_category and channel_name:
                        channels[current_category].append((channel_name, channel_url))
        else:
            for line in lines:
                line = line.strip()
                if "#genre#" in line:
                    current_category = line.split(",")[0].strip()
                    channels[current_category] = []
                elif current_category:
                    match = re.match(r"^(.*?),(.*?)$", line)
                    if match:
                        channel_name = match.group(1).strip()
                        channel_url = match.group(2).strip()
                        channels[current_category].append((channel_name, channel_url))
                    elif line:
                        channels[current_category].append((line, ''))
        if channels:
            categories = ", ".join(channels.keys())
            logging.info(f"url: {url} 爬取成功✅，包含频道分类: {categories}")
    except requests.RequestException as e:
        logging.error(f"url: {url} 爬取失败❌, Error: {e}")

    return channels

def match_channels(template_channels, all_channels):
    matched_channels = OrderedDict()

    for category, channel_list in template_channels.items():
        matched_channels[category] = OrderedDict()
        for channel_name in channel_list:
            for online_category, online_channel_list in all_channels.items():
                for online_channel_name, online_channel_url in online_channel_list:
                    if channel_name == online_channel_name:
                        matched_channels[category].setdefault(channel_name, []).append(online_channel_url)

    return matched_channels

def filter_source_urls(template_file):
    template_channels = parse_template(template_file)
    source_urls = ["http://example.com/channels.m3u", "http://example.com/channels.txt"]  # Placeholder URLs

    all_channels = OrderedDict()
    for url in source_urls:
        fetched_channels = fetch_channels(url)
        for category, channel_list in fetched_channels.items():
            if category in all_channels:
                all_channels[category].extend(channel_list)
            else:
                all_channels[category] = channel_list

    matched_channels = match_channels(template_channels, all_channels)

    return matched_channels, template_channels

def is_ipv6(url):
    return re.match(r'^http:\/\/\[[0-9a-fA-F:]+\]', url) is not None

def updateChannelUrlsM3U(channels, template_channels):
    written_urls = set()

    current_date = datetime.now().strftime("%Y-%m-%d")
    announcements = [
        {
            'channel': 'Announcement',
            'entries': [{'name': current_date, 'logo': '', 'url': ''}]
        }
    ]

    with open("live.m3u", "w", encoding="utf-8") as f_m3u:
        f_m3u.write(f"""#EXTM3U x-tvg-url={",".join(f'"{epg_url}"' for epg_url in ["http://example.com/epg.xml"])}\n""")

        with open("live.txt", "w", encoding="utf-8") as f_txt:
            for group in announcements:
                f_txt.write(f"{group['channel']},#genre#\n")
                for announcement in group['entries']:
                    f_m3u.write(f"""#EXTINF:-1 tvg-id="1" tvg-name="{announcement['name']}" tvg-logo="{announcement['logo']}" group-title="{group['channel']}",{announcement['name']}\n""")
                    f_m3u.write(f"{announcement['url']}\n")
                    f_txt.write(f"{announcement['name']},{announcement['url']}\n")

            for category, channel_list in template_channels.items():
                f_txt.write(f"{category},#genre#\n")
                if category in channels:
                    for channel_name in channel_list:
                        if channel_name in channels[category]:
                            sorted_urls = sorted(channels[category][channel_name], key=lambda url: not is_ipv6(url) if True == "ipv6" else is_ipv6(url))
                            filtered_urls = []
                            for url in sorted_urls:
                                if url and url not in written_urls and not any(blacklist in url for blacklist in []):
                                    filtered_urls.append(url)
                                    written_urls.add(url)

                            total_urls = len(filtered_urls)
                            for index, url in enumerate(filtered_urls, start=1):
                                if is_ipv6(url):
                                    url_suffix = f"$LR•IPV6" if total_urls == 1 else f"$LR•IPV6『线路{index}』"
                                else:
                                    url_suffix = f"$LR•IPV4" if total_urls == 1 else f"$LR•IPV4『线路{index}』"
                                if '$' in url:
                                    base_url = url.split('$', 1)[0]
                                else:
                                    base_url = url

                                new_url = f"{base_url}{url_suffix}"

                                f_m3u.write(f"#EXTINF:-1 tvg-id=\"{index}\" tvg-name=\"{channel_name}\" tvg-logo=\"https://gcore.jsdelivr.net/gh/yuanzl77/TVlogo@master/png/{channel_name}.png\" group-title=\"{category}\",{channel_name}\n")
                                f_m3u.write(new_url + "\n")
                                f_txt.write(f"{channel_name},{new_url}\n")

            f_txt.write("\n")

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
    start_time = time.time()
    try:
        subprocess.run(command, check=True)
        end_time = time.time()
        download_time = end_time - start_time
        print(f"视频已成功下载到 {output_path}，耗时 {download_time:.2f} 秒")
        return download_time
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
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
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"获取视频信息失败: {result.stderr}")
        return None
    
    width, height, size = result.stdout.strip().split('x')
    resolution = f"{width}x{height}"
    file_size = int(size)
    return {'resolution': resolution, 'file_size': file_size}

def test_live_stream(urls, output_dir='temp_videos'):
    """
    测试多个直播源地址，下载2秒的视频并检查分辨率和文件大小，并按速度排序。
    
    :param urls: 直播源地址列表
    :param output_dir: 临时视频文件保存目录
    :return: 排序后的直播源地址列表
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []

    for index, url in enumerate(urls):
        output_path = os.path.join(output_dir, f'temp_{index}.ts')
        print(f"正在测试 URL: {url}")
        
        # 下载视频并记录下载时间
        download_time = download_video(url, output_path)
        
        # 获取视频信息
        info = get_video_info(output_path)
        if info:
            print(f"分辨率: {info['resolution']}, 文件大小: {info['file_size']} bytes")
            
            # 判断是否满足条件（这里可以根据需要调整判断标准）
            if info['file_size'] > 0 and info['resolution']:
                results.append((url, download_time))
        
        # 删除临时文件
        os.remove(output_path)
    
    if not results:
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



"]  # Placeholder URLs

    all_channels = OrderedDict()
    for url in source_urls:
        fetched_channels = fetch_channels(url)
        for category, channel_list in fetched_channels.items():
            if category in all_channels:
                all_channels[category].extend(channel_list)
            else:
                all_channels[category] = channel_list

    matched_channels = match_channels(template_channels, all_channels)

    return matched_channels, template_channels

def is_ipv6(url):
    return re.match(r'^http:\/\/\[[0-9a-fA-F:]+\]', url) is not None

def updateChannelUrlsM3U(channels, template_channels):
    written_urls = set()

    current_date = datetime.now().strftime("%Y-%m-%d")
    announcements = [
        {
            'channel': 'Announcement',
            'entries': [{'name': current_date, 'logo': '', 'url': ''}]
        }
    ]

    with open("live.m3u", "w", encoding="utf-8") as f_m3u:
        f_m3u.write(f"""#EXTM3U x-tvg-url={",".join(f'"{epg_url}"' for epg_url in ["http://example.com/epg.xml"])}\n""")

        with open("live.txt", "w", encoding="utf-8") as f_txt:
            for group in announcements:
                f_txt.write(f"{group['channel']},#genre#\n")
                for announcement in group['entries']:
                    f_m3u.write(f"""#EXTINF:-1 tvg-id="1" tvg-name="{announcement['name']}" tvg-logo="{announcement['logo']}" group-title="{group['channel']}",{announcement['name']}\n""")
                    f_m3u.write(f"{announcement['url']}\n")
                    f_txt.write(f"{announcement['name']},{announcement['url']}\n")

            for category, channel_list in template_channels.items():
                f_txt.write(f"{category},#genre#\n")
                if category in channels:
                    for channel_name in channel_list:
                        if channel_name in channels[category]:
                            sorted_urls = sorted(channels[category][channel_name], key=lambda url: not is_ipv6(url) if True == "ipv6" else is_ipv6(url))
                            filtered_urls = []
                            for url in sorted_urls:
                                if url and url not in written_urls and not any(blacklist in url for blacklist in []):
                                    filtered_urls.append(url)
                                    written_urls.add(url)

                            total_urls = len(filtered_urls)
                            for index, url in enumerate(filtered_urls, start=1):
                                if is_ipv6(url):
                                    url_suffix = f"$LR•IPV6" if total_urls == 1 else f"$LR•IPV6『线路{index}』"
                                else:
                                    url_suffix = f"$LR•IPV4" if total_urls == 1 else f"$LR•IPV4『线路{index}』"
                                if '$' in url:
                                    base_url = url.split('$', 1)[0]
                                else:
                                    base_url = url

                                new_url = f"{base_url}{url_suffix}"

                                f_m3u.write(f"#EXTINF:-1 tvg-id=\"{index}\" tvg-name=\"{channel_name}\" tvg-logo=\"https://gcore.jsdelivr.net/gh/yuanzl77/TVlogo@master/png/{channel_name}.png\" group-title=\"{category}\",{channel_name}\n")
                                f_m3u.write(new_url + "\n")
                                f_txt.write(f"{channel_name},{new_url}\n")

            f_txt.write("\n")

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
    start_time = time.time()
    try:
        subprocess.run(command, check=True)
        end_time = time.time()
        download_time = end_time - start_time
        print(f"视频已成功下载到 {output_path}，耗时 {download_time:.2f} 秒")
        return download_time
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
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
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"获取视频信息失败: {result.stderr}")
        return None
    
    width, height, size = result.stdout.strip().split('x')
    resolution = f"{width}x{height}"
    file_size = int(size)
    return {'resolution': resolution, 'file_size': file_size}

def test_live_stream(urls, output_dir='temp_videos'):
    """
    测试多个直播源地址，下载2秒的视频并检查分辨率和文件大小，并按速度排序。
    
    :param urls: 直播源地址列表
    :param output_dir: 临时视频文件保存目录
    :return: 排序后的直播源地址列表
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []

    for index, url in enumerate(urls):
        output_path = os.path.join(output_dir, f'temp_{index}.ts')
        print(f"正在测试 URL: {url}")
        
        # 下载视频并记录下载时间
        download_time = download_video(url, output_path)
        
        # 获取视频信息
        info = get_video_info(output_path)
        if info:
            print(f"分辨率: {info['resolution']}, 文件大小: {info['file_size']} bytes")
            
            # 判断是否满足条件（这里可以根据需要调整判断标准）
            if info['file_size'] > 0 and info['resolution']:
                results.append((url, download_time))
        
        # 删除临时文件
        os.remove(output_path)
    
    if not results:
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



