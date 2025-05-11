import os
import threading
import time
from tkinter import Tk, Entry, Button, Listbox, Scrollbar, Label, StringVar, END, SINGLE, messagebox, Text, Frame, font
from PIL import Image, ImageTk
from io import BytesIO
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from xpinyin import Pinyin

# 代理和UA配置（如有需要可修改）
PROXY = '127.0.0.1:7890'
USER_AGENT = 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36'
SEARCH_URL = 'https://appcn2-vdhk.baozimh.com/baozimhapp/search?q='

# Selenium浏览器配置

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=http://{PROXY}')
    chrome_options.add_argument(f'--user-agent={USER_AGENT}')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=375,812')  # 模拟手机尺寸
    chrome_options.add_argument('--headless')  # 隐藏浏览器窗口
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# GUI主类
class BaozimhGUI:
    def __init__(self, master):
        master.title('包子漫画爬虫 - 搜索与解析')
        master.geometry('700x800')
        master.configure(bg='#f8f8f8')
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        # 主标题
        title_font = font.Font(family='微软雅黑', size=18, weight='bold')
        self.main_title = Label(master, text='包子漫画爬虫', font=title_font, bg='#f8f8f8')
        self.main_title.pack(pady=(18, 8))
        # 搜索输入区
        input_frame = Frame(master, bg='#f8f8f8')
        input_frame.pack(fill='x', padx=20, pady=5)
        self.label = Label(input_frame, text='请输入关键词:', bg='#f8f8f8')
        self.label.pack(side='left', padx=(0, 8))
        self.keyword_var = StringVar()
        self.entry = Entry(input_frame, textvariable=self.keyword_var, width=32)
        self.entry.pack(side='left', padx=(0, 8))
        self.search_btn = Button(input_frame, text='搜索', width=10, command=self.start_search)
        self.search_btn.pack(side='left', padx=(0, 8))
        self.stop_btn = Button(input_frame, text='停止', width=10, command=self.stop_crawler, state='disabled')
        self.stop_btn.pack(side='left')
        # 搜索结果区
        result_frame = Frame(master, bg='#f8f8f8')
        result_frame.pack(fill='both', padx=20, pady=(10, 5), expand=False)
        result_label_font = font.Font(size=12, weight='bold')
        self.result_label = Label(result_frame, text='搜索结果:', font=result_label_font, bg='#f8f8f8')
        self.result_label.pack(anchor='w', pady=(0, 2))
        listbox_frame = Frame(result_frame, bg='#f8f8f8')
        listbox_frame.pack(fill='both')
        self.scrollbar = Scrollbar(listbox_frame)
        self.listbox = Listbox(listbox_frame, width=80, height=10, selectmode=SINGLE, yscrollcommand=self.scrollbar.set, font=default_font)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        # 信息与封面区
        info_cover_frame = Frame(master, bg='#f8f8f8')
        info_cover_frame.pack(fill='x', padx=20, pady=(10, 5))
        # 信息区
        info_frame = Frame(info_cover_frame, bg='#f8f8f8')
        info_frame.pack(side='left', fill='both', expand=True)
        self.info_label = Label(info_frame, text='漫画信息:', font=result_label_font, bg='#f8f8f8')
        self.info_label.pack(anchor='w', pady=(0, 2))
        self.info_text = Label(info_frame, text='', justify='left', anchor='w', bg='#f8f8f8', wraplength=350)
        self.info_text.pack(anchor='w', pady=(0, 2))
        # 封面区
        cover_frame = Frame(info_cover_frame, bg='#f8f8f8')
        cover_frame.pack(side='right', fill='y', padx=(20, 0))
        self.cover_label = Label(cover_frame, bg='#f8f8f8')
        self.cover_label.pack()
        # 可复制字段区
        copy_frame = Frame(master, bg='#f8f8f8')
        copy_frame.pack(fill='x', padx=20, pady=(10, 5))
        self.copy_label = Label(copy_frame, text='可复制字段:', font=result_label_font, bg='#f8f8f8')
        self.copy_label.pack(anchor='w', pady=(0, 2))
        self.copy_text = Text(copy_frame, width=80, height=5, wrap='none', font=default_font)
        self.copy_text.pack(fill='x', pady=(0, 2))
        self.copy_text.config(state='disabled')
        # 其余初始化
        self.driver = None
        self.search_results = []
        self.p = Pinyin()
        self.stop_flag = False
        self.search_thread = None

    def start_search(self):
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showwarning('提示', '请输入关键词')
            return
        self.listbox.delete(0, END)
        self.info_text.config(text='')
        self.cover_label.config(image='')
        self.stop_flag = False
        self.search_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.search_thread = threading.Thread(target=self.search, args=(keyword,), daemon=True)
        self.search_thread.start()

    def search(self, keyword):
        try:
            if self.driver is None:
                self.driver = get_driver()
            url = SEARCH_URL + keyword
            self.driver.get(url)
            for _ in range(30):  # 最多等待15秒
                if self.stop_flag:
                    return
                time.sleep(0.5)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.comics-card'))
                )
            except Exception:
                if not self.stop_flag:
                    self.listbox.insert(END, '未找到搜索结果')
                return
            if self.stop_flag:
                return
            cards = self.driver.find_elements(By.CSS_SELECTOR, '.comics-card')
            self.search_results = []
            self.listbox.delete(0, END)
            for card in cards:
                if self.stop_flag:
                    return
                try:
                    title = card.find_element(By.CSS_SELECTOR, '.comics-card__title h3').text.strip()
                    author = card.find_element(By.CSS_SELECTOR, 'small.tags.text-truncate').text.strip()
                    cover_url = card.find_element(By.CSS_SELECTOR, '.img-box img').get_attribute('src')
                    detail_url = card.get_attribute('onclick')
                    if detail_url and "call_page('" in detail_url:
                        detail_url = detail_url.split("call_page('")[1].split("')")[0]
                        detail_url = 'https://appcn1-vdkr.baozimh.com/baozimhapp/' + detail_url
                    else:
                        title_py = self.p.get_pinyin(title, '').replace(' ', '')
                        author_py = self.p.get_pinyin(author, '').replace(' ', '')
                        detail_url = f"https://appcn1-vdkr.baozimh.com/baozimhapp/comic/{title_py}-{author_py}"
                    self.search_results.append((title, author, cover_url, detail_url))
                    self.listbox.insert(END, f'{title} | {author}')
                except Exception as e:
                    continue
            if not self.search_results and not self.stop_flag:
                self.listbox.insert(END, '未找到搜索结果')
        finally:
            self.search_btn.config(state='normal')
            self.stop_btn.config(state='disabled')

    def stop_crawler(self):
        self.stop_flag = True
        self.stop_btn.config(state='disabled')
        self.search_btn.config(state='normal')
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception:
            pass

    def on_select(self, event):
        if not self.search_results:
            return
        idx = self.listbox.curselection()
        if not idx:
            return
        idx = idx[0]
        if idx >= len(self.search_results):
            return
        title, author, cover_url, detail_url = self.search_results[idx]
        if not detail_url:
            self.info_text.config(text='未找到详情页URL')
            return
        threading.Thread(target=self.parse_detail, args=(title, author, cover_url, detail_url), daemon=True).start()

    def parse_detail(self, title, author, cover_url, detail_url):
        self.driver.get(detail_url)
        try:
            # 等待标题出现
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.comics-detail__title'))
            )
        except Exception:
            self.info_text.config(text='详情页加载失败')
            self._clear_copy_fields()
            return
        # 解析封面（优先.de-info__bg）
        try:
            bg_div = self.driver.find_element(By.CSS_SELECTOR, '.de-info__bg')
            style = bg_div.get_attribute('style')
            import re
            m = re.search(r"background-image:url\('([^']+)'", style)
            cover_img = m.group(1) if m else cover_url
        except Exception:
            cover_img = cover_url
        # 解析标题
        try:
            real_title = self.driver.find_element(By.CSS_SELECTOR, 'h1.comics-detail__title').text.strip()
        except Exception:
            real_title = title
        # 解析作者
        try:
            real_author = self.driver.find_element(By.CSS_SELECTOR, 'h2.comics-detail__author').text.strip()
        except Exception:
            real_author = author
        # 解析简介
        try:
            desc = self.driver.find_element(By.CSS_SELECTOR, 'p.comics-detail__desc').text.strip()
        except Exception:
            desc = ''
        # 若有"查看全部章节"按钮则点击
        try:
            show_all_btn = self.driver.find_element(By.ID, 'button_show_all_chatper')
            if show_all_btn.is_displayed():
                show_all_btn.click()
                time.sleep(1.5)
        except Exception:
            pass
        # 统计chapter-items和chapters_other_list下所有章节
        try:
            chapter_count = 0
            # 章节目录主区块
            try:
                chapter_items = self.driver.find_element(By.ID, 'chapter-items')
                chapters1 = chapter_items.find_elements(By.CSS_SELECTOR, '.comics-chapters__item')
                chapter_count += len(chapters1)
            except Exception:
                pass
            # 章节目录扩展区块
            try:
                chapters_other = self.driver.find_element(By.ID, 'chapters_other_list')
                # 等待其display变为可见
                WebDriverWait(self.driver, 5).until(
                    lambda d: chapters_other.is_displayed() or chapters_other.get_attribute('style') == ''
                )
                chapters2 = chapters_other.find_elements(By.CSS_SELECTOR, '.comics-chapters__item')
                chapter_count += len(chapters2)
            except Exception:
                pass
        except Exception:
            chapter_count = 0
        # BASE_URL拼接
        title_py = self.p.get_pinyin(real_title, '').replace(' ', '')
        author_py = self.p.get_pinyin(real_author, '').replace(' ', '')
        BASE_URL = f"https://app.baozimh.com/baozimhapp/comic/chapter/{title_py}-{author_py}/"
        COVER_URL = cover_img
        CHAPTER_START = 0
        CHAPTER_END = chapter_count - 1 if chapter_count > 0 else 0
        # 展示基础信息
        info = f"标题: {real_title}\n作者: {real_author}\n简介: {desc}"
        self.info_text.config(text=info)
        # 展示可复制字段到Text控件
        copy_str = f"COVER_URL: {COVER_URL}\nBASE_URL: {BASE_URL}\nCHAPTER_START: {CHAPTER_START}\nCHAPTER_END: {CHAPTER_END}"
        self._set_copy_text(copy_str)
        # 显示封面
        try:
            resp = requests.get(COVER_URL, timeout=10)
            img = Image.open(BytesIO(resp.content)).resize((150, 200))
            photo = ImageTk.PhotoImage(img)
            self.cover_label.config(image=photo)
            self.cover_label.image = photo
        except Exception:
            self.cover_label.config(image='')

    def _set_copy_text(self, value):
        self.copy_text.config(state='normal')
        self.copy_text.delete('1.0', 'end')
        self.copy_text.insert('1.0', value)
        self.copy_text.config(state='disabled')

    def _clear_copy_fields(self):
        self._set_copy_text("")

    def on_closing(self):
        if self.driver:
            self.driver.quit()
        self.master.destroy()

if __name__ == '__main__':
    root = Tk()
    app = BaozimhGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 