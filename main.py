import re
import requests
import logging
from collections import OrderedDict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import config
import yt_dlp

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("function.log", "w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def parse_template(template_file):
    """
    解析模板文件，提取频道分类和频道名称。
    
    :param template_file: 模板文件路径
    :return: 包含频道分类和频道名称的有序字典
    """
    template_channels = OrderedDict()
    current_category = None

    with open(template_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "#genre#" in line:
                    # 提取频道分类
                    current_category = line.split(",")[0].strip()
                    template_channels[current_category] = []
                elif current_category:
                    # 提取频道名称
                    channel_name = line.split(",")[0].strip()
                    template_channels[current_category].append(channel_name)

    return template_channels

def fetch_channels(url):
    """
    从给定的URL获取频道信息，并解析为有序字典。
    
    :param url: 频道信息的URL
    :return: 包含频道分类和频道URL的有序字典
    """
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
                        # 提取频道分类和频道名称
                        current_category = match.group(1).strip()
                        channel_name = match.group(2).strip()
                        if current_category not in channels:
                            channels[current_category] = []
                elif line and not line.startswith("#"):
                    # 提取频道URL
                    channel_url = line.strip()
                    if current_category and channel_name:
                        channels[current_category].append((channel_name, channel_url))
        else:
            for line in lines:
                line = line.strip()
                if "#genre#" in line:
                    # 提取频道分类
                    current_category = line.split(",")[0].strip()
                    channels[current_category] = []
                elif current_category:
                    match = re.match(r"^(.*?),(.*?)$", line)
                    if match:
                        # 提取频道名称和频道URL
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

def measure_speed_with_ytdlp(url):
    """
    使用 yt-dlp 测量给定URL的响应时间。
    
    :param url: 要测量速度的URL
    :return: 响应时间（秒），如果请求失败则返回无穷大
    """
    ydl_opts = {
        'quiet': True,
        'simulate': True,
        'dump_single_json': True,
        'no_warnings': True,
    }
    try:
        start_time = datetime.now()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
        end_time = datetime.now()
        return (end_time - start_time).total_seconds()
    except Exception:
        return float('inf')  # 如果请求失败，返回无穷大以确保其排在最后

def sort_and_filter_channels(channels):
    """
    对频道URL进行测速并排序，筛选出最快的前20个URL。
    
    :param channels: 包含频道分类和频道URL的有序字典
    :return: 排序并筛选后的频道URL
    """
    sorted_channels = OrderedDict()
    max_workers = 10  # 最大线程数

    def get_timed_urls(urls):
        """
        并发测量多个URL的速度。
        
        :param urls: URL列表
        :return: 包含响应时间和URL的元组列表
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            timed_urls = list(executor.map(measure_speed_with_ytdlp, urls))
        return [(time, url) for time, url in zip(timed_urls, urls)]

    for category, channel_list in channels.items():
        sorted_channels[category] = {}
        for channel_name, online_channel_urls in channel_list.items():
            urls = [url for _, url in online_channel_urls]
            # 并发测速
            timed_urls = get_timed_urls(urls)
            timed_urls.sort(key=lambda x: x[0])  # 按响应时间排序
            # 取前20个最快的URL
            top_20_urls = [url for _, url in timed_urls[:20]]
            sorted_channels[category][channel_name] = top_20_urls
    return sorted_channels

def match_channels(template_channels, all_channels):
    """
    根据模板频道匹配所有获取到的频道。
    
    :param template_channels: 模板频道
    :param all_channels: 所有获取到的频道
    :return: 匹配后的频道
    """
    matched_channels = OrderedDict()

    for category, channel_list in template_channels.items():
        matched_channels[category] = OrderedDict()
        for channel_name in channel_list:
            for online_category, online_channel_list in all_channels.items():
                for online_channel_name, online_channel_urls in online_channel_list.items():
                    if channel_name == online_channel_name:
                        matched_channels[category].setdefault(channel_name, []).extend(online_channel_urls)

    return matched_channels

def filter_source_urls(template_file):
    """
    过滤源URL并匹配频道。
    
    :param template_file: 模板文件路径
    :return: 匹配后的频道和模板频道
    """
    template_channels = parse_template(template_file)
    source_urls = config.source_urls

    all_channels = OrderedDict()
    for url in source_urls:
        fetched_channels = fetch_channels(url)
        for category, channel_list in fetched_channels.items():
            if category in all_channels:
                for channel_name, channel_url in channel_list:
                    all_channels[category].setdefault(channel_name, []).append(channel_url)
            else:
                all_channels[category] = {channel_name: [channel_url] for channel_name, channel_url in channel_list}

    matched_channels = match_channels(template_channels, all_channels)

    # 对匹配到的渠道进行测速和筛选
    sorted_matched_channels = sort_and_filter_channels(matched_channels)

    return sorted_matched_channels, template_channels

def is_ipv6(url):
    """
    判断URL是否为IPv6地址。
    
    :param url: 要检查的URL
    :return: 如果是IPv6地址返回True，否则返回False
    """
    return re.match(r'^http:\/\/\[[0-9a-fA-F:]+\]', url) is not None

def updateChannelUrlsM3U(channels, template_channels):
    """
    更新M3U和TXT文件中的频道URL。
    
    :param channels: 匹配并筛选后的频道
    :param template_channels: 模板频道
    """
    written_urls = set()

    current_date = datetime.now().strftime("%Y-%m-%d")
    for group in config.announcements:
        for announcement in group['entries']:
            if announcement['name'] is None:
                announcement['name'] = current_date

    with open("live.m3u", "w", encoding="utf-8") as f_m3u:
        f_m3u.write(f"""#EXTM3U x-tvg-url={",".join(f'"{epg_url}"' for epg_url in config.epg_urls)}\n""")

        with open("live.txt", "w", encoding="utf-8") as f_txt:
            for group in config.announcements:
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
                            sorted_urls = sorted(
                                channels[category][channel_name],
                                key=lambda url: not is_ipv6(url) if config.ip_version_priority == "ipv6" else is_ipv6(url)
                            )
                            filtered_urls = []
                            for url in sorted_urls:
                                if url and url not in written_urls and not any(blacklist in url for blacklist in config.url_blacklist):
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



