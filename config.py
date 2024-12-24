import tkinter as tk
from tkinter import ttk

class Config:
    def __init__(self):
        self.open_sort = True
        self.sort_timeout = 5
        self.open_filter_speed = False
        self.min_speed = 1.0
        self.open_filter_resolution = False
        self.min_resolution = "720p"
        self.ip_version_priority = "ipv4"
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

    def set(self, section, option, value):
        setattr(self, option, value)

config = Config()

class SpeedUI:
    def __init__(self, root):
        """
        Initialize the SpeedUI with a Tkinter root window.
        """
        self.root = root
        self.init_ui(root)

    def init_ui(self, root):
        """
        Initialize the user interface components.
        """
        frame_default_sort = tk.Frame(root)
        frame_default_sort.pack(fill=tk.X)
        frame_default_sort_column1 = tk.Frame(frame_default_sort)
        frame_default_sort_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_sort_column2 = tk.Frame(frame_default_sort)
        frame_default_sort_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_sort_label = tk.Label(
            frame_default_sort_column1, text="测速排序:", width=12
        )
        self.open_sort_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_sort_var = tk.BooleanVar(value=config.open_sort)
        self.open_sort_checkbutton = ttk.Checkbutton(
            frame_default_sort_column1,
            variable=self.open_sort_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_sort,
        )
        self.open_sort_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.sort_timeout_label = tk.Label(
            frame_default_sort_column2, text="响应超时(s):", width=12
        )
        self.sort_timeout_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.sort_timeout_entry = tk.Entry(frame_default_sort_column2, width=10)
        self.sort_timeout_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.sort_timeout_entry.insert(0, str(config.sort_timeout))
        self.sort_timeout_entry.bind("<KeyRelease>", self.update_sort_timeout)

        frame_default_speed_params = tk.Frame(root)
        frame_default_speed_params.pack(fill=tk.X)
        frame_default_speed_params_column1 = tk.Frame(
            frame_default_speed_params
        )
        frame_default_speed_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_speed_params_column2 = tk.Frame(
            frame_default_speed_params
        )
        frame_default_speed_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_filter_speed_label = tk.Label(
            frame_default_speed_params_column1, text="速率过滤:", width=12
        )
        self.open_filter_speed_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_filter_speed_var = tk.BooleanVar(
            value=config.open_filter_speed
        )
        self.open_filter_speed_checkbutton = ttk.Checkbutton(
            frame_default_speed_params_column1,
            variable=self.open_filter_speed_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_filter_speed
        )
        self.open_filter_speed_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.min_speed_label = tk.Label(
            frame_default_speed_params_column2, text="最小速率(M/s):", width=12
        )
        self.min_speed_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_speed_entry = tk.Entry(
            frame_default_speed_params_column2, width=10
        )
        self.min_speed_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_speed_entry.insert(0, str(config.min_speed))
        self.min_speed_entry.bind("<KeyRelease>", self.update_min_speed)

        frame_default_resolution_params = tk.Frame(root)
        frame_default_resolution_params.pack(fill=tk.X)
        frame_default_resolution_params_column1 = tk.Frame(
            frame_default_resolution_params
        )
        frame_default_resolution_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_resolution_params_column2 = tk.Frame(
            frame_default_resolution_params
        )
        frame_default_resolution_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_filter_resolution_label = tk.Label(
            frame_default_resolution_params_column1, text="分辨率过滤:", width=12
        )
        self.open_filter_resolution_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_filter_resolution_var = tk.BooleanVar(
            value=config.open_filter_resolution
        )
        self.open_filter_resolution_checkbutton = ttk.Checkbutton(
            frame_default_resolution_params_column1,
            variable=self.open_filter_resolution_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_filter_resolution
        )
        self.open_filter_resolution_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.min_resolution_label = tk.Label(
            frame_default_resolution_params_column2, text="最小分辨率:", width=12
        )
        self.min_resolution_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_resolution_entry = tk.Entry(
            frame_default_resolution_params_column2, width=10
        )
        self.min_resolution_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_resolution_entry.insert(0, config.min_resolution)
        self.min_resolution_entry.bind("<KeyRelease>", self.update_min_resolution)

        # 添加开始测速按钮
        start_button_frame = tk.Frame(root)
        start_button_frame.pack(pady=20)
        self.start_button = ttk.Button(start_button_frame, text="开始测速", command=self.start_speed_test)
        self.start_button.pack()

        # 添加结果显示文本框
        result_frame = tk.Frame(root)
        result_frame.pack(pady=20)
        self.result_text = tk.Text(result_frame, height=10, width=60)
        self.result_text.pack()

    def update_open_sort(self):
        config.set("Settings", "open_sort", str(self.open_sort_var.get()))

    def update_sort_timeout(self, event):
        config.set("Settings", "sort_timeout", self.sort_timeout_entry.get())

    def update_open_filter_speed(self):
        config.set(
            "Settings",
            "open_filter_speed",
            str(self.open_filter_speed_var.get()),
        )

    def update_min_speed(self, event):
        config.set("Settings", "min_speed", self.min_speed_entry.get())

    def update_open_filter_resolution(self):
        config.set(
            "Settings",
            "open_filter_resolution",
            str(self.open_filter_resolution_var.get()),
        )

    def update_min_resolution(self, event):
        config.set("Settings", "min_resolution", self.min_resolution_entry.get())

    def change_entry_state(self, state):
        for entry in [
            "open_sort_checkbutton",
            "sort_timeout_entry",
            "open_filter_speed_checkbutton",
            "min_speed_entry",
            "open_filter_resolution_checkbutton",
            "min_resolution_entry"
        ]:
            getattr(self, entry).config(state=state)

    def start_speed_test(self):
        # 这里可以添加实际的测速逻辑
        test_result = f"Open Sort: {config.open_sort}\nSort Timeout: {config.sort_timeout}s\n" \
                      f"Open Filter Speed: {config.open_filter_speed}\nMin Speed: {config.min_speed} M/s\n" \
                      f"Open Filter Resolution: {config.open_filter_resolution}\nMin Resolution: {config.min_resolution}\n" \
                      f"Ip Version Priority: {config.ip_version_priority}\n" \
                      f"Source URLs: {config.source_urls}\n" \
                      f"Url Blacklist: {config.url_blacklist}\n" \
                      f"Announcements: {config.announcements}\n" \
                      f"Epg URLs: {config.epg_urls}"
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, test_result)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("测速设置")
    app = SpeedUI(root)
    root.mainloop()



