import re  # 导入正则表达式模块
import requests  # 导入requests模块用于HTTP请求
import logging  # 导入logging模块用于日志记录
from collections import OrderedDict  # 导入OrderedDict以保持字典顺序
from datetime import datetime  # 导入datetime模块用于日期时间操作
import config  # 导入config模块以获取配置信息

# 配置日志记录，设置日志级别、格式和处理程序
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("function.log", "w", encoding="utf-8"), logging.StreamHandler()])

def parse_template(template_file):
    # 解析模板文件并返回有序字典形式的频道分类
    template_channels = OrderedDict()
    current_category = None

    with open(template_file, "r", encoding="utf-8") as f:  # 打开模板文件进行读取
        for line in f:
            line = line.strip()  # 去除行首尾空白字符
            if line and not line.startswith("#"):  # 忽略空行和注释行
                if "#genre#" in line:  # 检查是否为分类标识
                    current_category = line.split(",")[0].strip()  # 提取分类名称
                    template_channels[current_category] = []  # 初始化该分类的频道列表
                elif current_category:  # 如果当前分类存在
                    channel_name = line.split(",")[0].strip()  # 提取频道名称
                    template_channels[current_category].append(channel_name)  # 将频道名称添加到对应分类

    return template_channels  # 返回解析后的频道分类字典

def fetch_channels(url):
    # 根据给定URL抓取频道信息并返回有序字典形式的频道分类
    channels = OrderedDict()

    try:
        response = requests.get(url)  # 发送GET请求获取数据
        response.raise_for_status()  # 检查响应状态码是否正常
        response.encoding = 'utf-8'  # 设置响应编码为UTF-8
        lines = response.text.split("\n")  # 将响应文本按行分割
        current_category = None  # 初始化当前分类为空
        is_m3u = any("#EXTINF" in line for line in lines[:15])  # 判断是否为M3U格式
        source_type = "m3u" if is_m3u else "txt"  # 设置源类型
        logging.info(f"url: {url} 获取成功，判断为{source_type}格式")  # 记录日志

        if is_m3u:  # 如果是M3U格式
            for line in lines:
                line = line.strip()  # 去除行首尾空白字符
                if line.startswith("#EXTINF"):  # 检查是否为频道信息标识
                    match = re.search(r'group-title="(.*?)",(.*)', line)  # 匹配分类和频道名称
                    if match:
                        current_category = match.group(1).strip()  # 提取分类名称
                        channel_name = match.group(2).strip()  # 提取频道名称
                        if current_category not in channels:  # 如果该分类不存在
                            channels[current_category] = []  # 初始化该分类的频道列表
                elif line and not line.startswith("#"):  # 如果不是注释行且非空
                    channel_url = line.strip()  # 提取频道URL
                    if current_category and channel_name:  # 如果当前分类和频道名称存在
                        channels[current_category].append((channel_name, channel_url))  # 将频道名称和URL添加到对应分类
        else:  # 如果不是M3U格式
            for line in lines:
                line = line.strip()  # 去除行首尾空白字符
                if "#genre#" in line:  # 检查是否为分类标识
                    current_category = line.split(",")[0].strip()  # 提取分类名称
                    channels[current_category] = []  # 初始化该分类的频道列表
                elif current_category:  # 如果当前分类存在
                    match = re.match(r"^(.*?),(.*?)$", line)  # 匹配频道名称和URL
                    if match:
                        channel_name = match.group(1).strip()  # 提取频道名称
                        channel_url = match.group(2).strip()  # 提取频道URL
                        channels[current_category].append((channel_name, channel_url))  # 将频道名称和URL添加到对应分类
                    elif line:  # 如果只有频道名称而没有URL
                        channels[current_category].append((line, ''))  # 将频道名称和空URL添加到对应分类
        if channels:  # 如果成功抓取到频道信息
            categories = ", ".join(channels.keys())  # 提取所有分类名称
            logging.info(f"url: {url} 爬取成功✅，包含频道分类: {categories}")  # 记录日志
    except requests.RequestException as e:  # 捕获请求异常
        logging.error(f"url: {url} 爬取失败❌, Error: {e}")  # 记录错误日志

    return channels  # 返回抓取到的频道分类字典

def match_channels(template_channels, all_channels):
    # 匹配模板中的频道与实际抓取到的频道，并返回匹配结果
    matched_channels = OrderedDict()

    for category, channel_list in template_channels.items():  # 遍历模板中的每个分类及其频道列表
        matched_channels[category] = OrderedDict()  # 初始化该分类的匹配结果
        for channel_name in channel_list:  # 遍历模板中的每个频道名称
            for online_category, online_channel_list in all_channels.items():  # 遍历实际抓取到的每个分类及其频道列表
                for online_channel_name, online_channel_url in online_channel_list:  # 遍历实际抓取到的每个频道名称及其URL
                    if channel_name == online_channel_name:  # 如果模板中的频道名称与实际抓取到的频道名称匹配
                        matched_channels[category].setdefault(channel_name, []).append(online_channel_url)  # 将匹配到的URL添加到对应分类和频道名称中

    return matched_channels  # 返回匹配结果字典

def filter_source_urls(template_file):
    # 过滤并匹配模板中的频道与多个源URL抓取到的频道，并返回匹配结果和模板中的频道分类
    template_channels = parse_template(template_file)  # 解析模板文件
    source_urls = config.source_urls  # 获取源URL列表

    all_channels = OrderedDict()  # 初始化所有频道的有序字典
    for url in source_urls:  # 遍历每个源URL
        fetched_channels = fetch_channels(url)  # 抓取该源URL下的频道信息
        for category, channel_list in fetched_channels.items():  # 遍历抓取到的每个分类及其频道列表
            if category in all_channels:  # 如果该分类已经存在于all_channels中
                all_channels[category].extend(channel_list)  # 将频道列表扩展到现有分类中
            else:
                all_channels[category] = channel_list  # 否则初始化该分类并赋值频道列表

    matched_channels = match_channels(template_channels, all_channels)  # 匹配模板中的频道与抓取到的所有频道

    return matched_channels, template_channels  # 返回匹配结果和模板中的频道分类

def is_ipv6(url):
    # 判断给定URL是否为IPv6地址
    return re.match(r'^http:\/\/\[[0-9a-fA-F:]+\]', url) is not None  # 使用正则表达式匹配IPv6地址模式

async def test_url_speed(url, timeout=5):
    # 测试给定URL的速度并返回响应时间
    try:
        start_time = time.time()  # 记录开始时间
        response = requests.get(url, timeout=timeout)  # 发送GET请求并设置超时时间
        end_time = time.time()  # 记录结束时间
        if response.status_code == 200:  # 如果响应状态码为200（成功）
            return end_time - start_time  # 返回响应时间
    except requests.RequestException:  # 捕获请求异常
        pass  # 忽略异常
    return float('inf')  # 返回无穷大表示无法访问

async def sort_channels_by_speed(channels, ipv6_support):
    # 根据速度对频道进行排序并返回排序后的结果
    from concurrent.futures import ThreadPoolExecutor  # 导入ThreadPoolExecutor以支持并发执行
    import asyncio  # 导入asyncio模块以支持异步编程

    sorted_channels = OrderedDict()  # 初始化排序后的频道有序字典
    loop = asyncio.get_event_loop()  # 获取事件循环对象

    async def sort_category(category, channel_list):
        # 对单个分类中的频道进行速度测试并排序
        tasks = [test_url_speed(url) for _, url in channel_list]  # 创建速度测试任务列表
        results = await asyncio.gather(*tasks)  # 并发执行速度测试任务并获取结果
        sorted_results = sorted(zip(results, channel_list), key=lambda x: x[0])  # 根据响应时间对结果进行排序
        sorted_channels[category] = [(name, url) for _, (name, url) in sorted_results]  # 将排序后的结果保存到sorted_channels中

    for category, channel_list in channels.items():  # 遍历每个分类及其频道列表
        await sort_category(category, channel_list)  # 异步调用sort_category函数对每个分类进行排序

    return sorted_channels  # 返回排序后的频道字典

def updateChannelUrlsM3U(channels, template_channels):
    # 更新M3U文件和TXT文件中的频道URLs
    written_urls = set()  # 初始化已写入的URL集合

    current_date = datetime.now().strftime("%Y-%m-%d")  # 获取当前日期字符串
    for group in config.announcements:  # 遍历公告组
        for announcement in group['entries']:  # 遍历每个公告项
            if announcement['name'] is None:  # 如果公告名称为空
                announcement['name'] = current_date  # 设置公告名称为当前日期

    with open("live.m3u", "w", encoding="utf-8") as f_m3u:  # 打开live.m3u文件进行写入
        f_m3u.write(f"""#EXTM3U x-tvg-url={",".join(f'"{epg_url}"' for epg_url in config.epg_urls)}\n""")  # 写入EPG URL

        with open("live.txt", "w", encoding="utf-8") as f_txt:  # 打开live.txt文件进行写入
            for group in config.announcements:  # 遍历公告组
                f_txt.write(f"{group['channel']},#genre#\n")  # 写入分类标识
                for announcement in group['entries']:  # 遍历每个公告项
                    f_m3u.write(f"""#EXTINF:-1 tvg-id="1" tvg-name="{announcement['name']}" tvg-logo="{announcement['logo']}" group-title="{group['channel']}",{announcement['name']}\n""")  # 写入公告项信息
                    f_m3u.write(f"{announcement['url']}\n")  # 写入公告项URL
                    f_txt.write(f"{announcement['name']},{announcement['url']}\n")  # 写入公告项信息到TXT文件

            for category, channel_list in template_channels.items():  # 遍历模板中的每个分类及其频道列表
                f_txt.write(f"{category},#genre#\n")  # 写入分类标识
                if category in channels:  # 如果该分类存在于channels中
                    sorted_urls = sorted(channels[category], key=lambda item: not is_ipv6(item[1]) if config.ip_version_priority == "ipv6" else is_ipv6(item[1]))  # 根据IP版本优先级对URL进行排序
                    filtered_urls = []  # 初始化过滤后的URL列表
                    for name, url in sorted_urls:  # 遍历排序后的URL
                        if url and url not in written_urls and not any(blacklist in url for blacklist in config.url_blacklist):  # 如果URL有效且未被写入且不在黑名单中
                            filtered_urls.append((name, url))  # 添加到过滤后的URL列表
                            written_urls.add(url)  # 将URL添加到已写入集合中

                    total_urls = len(filtered_urls)  # 获取过滤后的URL总数
                    for index, (name, url) in enumerate(filtered_urls, start=1):  # 遍历过滤后的URL并编号
                        if is_ipv6(url):  # 如果URL为IPv6地址
                            url_suffix = f"$LR•IPV6" if total_urls == 1 else f"$LR•IPV6『线路{index}』"  # 设置URL后缀
                        else:  # 如果URL为IPv4地址
                            url_suffix = f"$LR•IPV4" if total_urls == 1 else f"$LR•IPV4『线路{index}』"  # 设置URL后缀
                        if '$' in url:  # 如果URL中包含'$'
                            base_url = url.split('$', 1)[0]  # 提取基础URL
                        else:
                            base_url = url  # 否则直接使用原URL

                        new_url = f"{base_url}{url_suffix}"  # 构建新的URL

                        f_m3u.write(f"#EXTINF:-1 tvg-id=\"{index}\" tvg-name=\"{name}\" tvg-logo=\"https://gcore.jsdelivr.net/gh/yuanzl77/TVlogo@master/png/{name}.png\" group-title=\"{category}\",{name}\n")  # 写入频道信息到M3U文件
                        f_m3u.write(new_url + "\n")  # 写入新URL到M3U文件
                        f_txt.write(f"{name},{new_url}\n")  # 写入频道信息和新URL到TXT文件

            f_txt.write("\n")  # 写入换行符

if __name__ == "__main__":
    template_file = "demo.txt"  # 设置模板文件路径
    channels, template_channels = filter_source_urls(template_file)  # 过滤并匹配模板中的频道与抓取到的频道

    import asyncio  # 导入asyncio模块以支持异步编程
    loop = asyncio.new_event_loop()  # 创建新的事件循环对象
    asyncio.set_event_loop(loop)  # 设置事件循环对象
    sorted_channels = loop.run_until_complete(sort_channels_by_speed(channels, config.ipv6_support))  # 异步运行速度排序函数并获取排序后的结果

    updateChannelUrlsM3U(sorted_channels, template_channels)  # 更新M3U文件和TXT文件中的频道URLs



