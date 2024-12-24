import tkinter as tk

class Config:
    def __init__(self):
        self.ip_version_priority = "ipv6"
        self.source_urls = [
            "http://175.178.251.183:6689/aktvlive.txt",
            "https://live.fanmingming.com/tv/m3u/ipv6.m3u",
            "https://raw.githubusercontent.com/yuanzl77/IPTV/main/直播/央视频道.txt",
            "http://120.79.4.185/new/mdlive.txt",
            "https://raw.githubusercontent.com/Fairy8o/IPTV/main/PDX-V4.txt",
            "https://raw.githubusercontent.com/Fairy8o/IPTV/main/PDX-V6.txt",
            "https://live.zhoujie218.top/tv/iptv6.txt",
            "https://live.zhoujie218.top/tv/iptv4.txt",
            "https://www.mytvsuper.xyz/m3u/Live.m3u",
            "https://tv.youdu.fan:666/live/",
            "http://ww.weidonglong.com/dsj.txt",
            "http://xhztv.top/zbc.txt",
            "https://raw.githubusercontent.com/qingwen07/awesome-iptv/main/tvbox_live_all.txt",
            "https://raw.githubusercontent.com/Guovin/TV/gd/output/result.txt",
            "http://home.jundie.top:81/Cat/tv/live.txt",
            "https://raw.githubusercontent.com/vbskycn/iptv/master/tv/hd.txt",
            "https://cdn.jsdelivr.net/gh/YueChan/live@main/IPTV.m3u",
            "https://raw.githubusercontent.com/cymz6/AutoIPTV-Hotel/main/lives.txt",
            "https://raw.githubusercontent.com/PizazzGY/TVBox_warehouse/main/live.txt",
            "https://fm1077.serv00.net/SmartTV.m3u",
            "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.txt",
            "https://raw.githubusercontent.com/kimwang1978/collect-tv-txt/main/merged_output.txt"
        ]
        self.url_blacklist = [
            "epg.pw/stream/",
            "103.40.13.71:12390",
            "[2409:8087:1a01:df::4077]/PLTV/",
            "8.210.140.75:68",
            "154.12.50.54",
            "yinhe.live_hls.zte.com",
            "8.137.59.151",
            "[2409:8087:7000:20:1000::22]:6060",
            "histar.zapi.us.kg",
            "www.tfiplaytv.vip",
            "dp.sxtv.top",
            "111.230.30.193",
            "148.135.93.213:81",
            "live.goodiptv.club",
            "iptv.luas.edu.cn",
            "[2409:8087:2001:20:2800:0:df6e:eb22]:80",
            "[2409:8087:2001:20:2800:0:df6e:eb23]:80",
            "[2409:8087:2001:20:2800:0:df6e:eb1d]/ott.mobaibox.com/",
            "[2409:8087:2001:20:2800:0:df6e:eb1d]:80",
            "[2409:8087:2001:20:2800:0:df6e:eb24]",
            "2409:8087:2001:20:2800:0:df6e:eb25]:80",
            "[2409:8087:2001:20:2800:0:df6e:eb27]"
        ]
        self.announcements = [
            {
                "channel": "公告",
                "entries": [
                    {"name": "请阅读", "url": "https://liuliuliu.tv/api/channels/1997/stream", "logo": "http://175.178.251.183:6689/LR.jpg"},
                    {"name": "yuanzl77.github.io", "url": "https://liuliuliu.tv/api/channels/233/stream", "logo": "http://175.178.251.183:6689/LR.jpg"},
                    {"name": "更新日期", "url": "https://gitlab.com/lr77/IPTV/-/raw/main/%E4%B8%BB%E8%A7%92.mp4", "logo": "http://175.178.251.183:6689/LR.jpg"},
                    {"name": None, "url": "https://gitlab.com/lr77/IPTV/-/raw/main/%E8%B5%B7%E9%A3%8E%E4%BA%86.mp4", "logo": "http://175.178.251.183:6689/LR.jpg"}
                ]
            }
        ]
        self.epg_urls = [
            "https://live.fanmingming.com/e.xml",
            "http://epg.51zmt.top:8000/e.xml",
            "http://epg.aptvapp.com/xml",
            "https://epg.pw/xmltv/epg_CN.xml",
            "https://epg.pw/xmltv/epg_HK.xml",
            "https://epg.pw/xmltv/epg_TW.xml"
        ]

    def set(self, option, value):
        setattr(self, option, value)

class SpeedUI:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.init_ui(root)

    def init_ui(self, root):
        self.result_text = tk.Text(root, height=20, width=80)
        self.result_text.pack()
        self.start_button = tk.Button(root, text="Start Speed Test", command=self.start_speed_test)
        self.start_button.pack()

    def start_speed_test(self):
        test_result = f"IP Version Priority: {self.config.ip_version_priority}\n" \
                      f"Source URLs: {self.config.source_urls}\n" \
                      f"URL Blacklist: {self.config.url_blacklist}\n" \
                      f"Announcements: {self.config.announcements}\n" \
                      f"EPG URLs: {self.config.epg_urls}"
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, test_result)

# 创建Config实例
config = Config()

# 创建Tkinter根窗口
root = tk.Tk()
root.title("Speed Test UI")

# 创建SpeedUI实例
speed_ui = SpeedUI(root, config)

# 运行Tkinter主循环
root.mainloop()



