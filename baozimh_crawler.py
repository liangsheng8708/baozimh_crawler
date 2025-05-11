import os
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed

# 代理设置（如需更改请修改此处）
PROXY = '127.0.0.1:7890'  # 示例代理地址，请根据实际情况修改
THREADS = 256  # 每章节图片下载线程数

COVER_URL = ''
BASE_URL = 'https://app.baozimh.com/baozimhapp/comic/chapter/chaonenglifang-shuiluoshengsheng/'
CHAPTER_START = 0
CHAPTER_END = 327
OUTPUT_DIR = 'chaonenglifang_shuiluoshengsheng'


USER_AGENT = 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36'
JINDU_FILE = 'baozimh_crawler_jindu.json'
FAILED_LOG = 'baozimh_crawler_failed.log'

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_jindu():
    if os.path.exists(JINDU_FILE):
        try:
            with open(JINDU_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_jindu(done_set):
    with open(JINDU_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(done_set)), f, ensure_ascii=False)

def remove_jindu():
    if os.path.exists(JINDU_FILE):
        os.remove(JINDU_FILE)

# Selenium浏览器配置
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server=http://{PROXY}')
    chrome_options.add_argument(f'--user-agent={USER_AGENT}')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=375,812')  # 模拟手机尺寸
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_img_urls(driver):
    # 等待ul.comic-contain加载
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.comic-contain'))
        )
    except Exception as e:
        print('页面主要内容加载超时')
        return []
    imgs = driver.find_elements(By.CSS_SELECTOR, 'ul.comic-contain img.comic-contain__item')
    img_urls = []
    for img in imgs:
        url = img.get_attribute('data-src') or img.get_attribute('src')
        if url and not url.endswith('pixel.gif'):
            img_urls.append(url)
    return img_urls

def download_img_task(args):
    url, path, headers, proxies, chapter_name = args
    for attempt in range(5):
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            if resp.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(resp.content)
                return True
        except Exception as e:
            print(f"下载失败: {url}，重试{attempt+1}/5，错误: {e}")
            time.sleep(1 + attempt)
    print(f"图片下载失败超过5次，跳过: {url}")
    if chapter_name:
        with open(FAILED_LOG, 'a', encoding='utf-8') as flog:
            flog.write(f"章节{chapter_name} 图片链接: {url}\n")
    return False

def download_cover(cover_url, headers, proxies):
    if not cover_url:
        return
    cover_path = os.path.join(OUTPUT_DIR, 'cover.jpg')
    print(f"正在下载漫画封面: {cover_url}")
    # 复用图片下载逻辑，但chapter_name传空字符串，不写入章节失败日志
    download_img_task((cover_url, cover_path, headers, proxies, ''))

def crawl_chapter(driver, chapter_idx, headers, proxies):
    chapter_name = f"chapter_0_{chapter_idx}"
    chapter_dir = os.path.join(OUTPUT_DIR, chapter_name)
    os.makedirs(chapter_dir, exist_ok=True)
    url = f"{BASE_URL}0_{chapter_idx}.html"
    print(f"正在爬取: {url}")
    try:
        driver.get(url)
        img_urls = get_img_urls(driver)
        if not img_urls:
            print(f"未找到图片: {url}")
            return False
        tasks = []
        for idx, img_url in enumerate(img_urls, 1):
            ext = os.path.splitext(img_url)[-1].split('?')[0] or '.jpg'
            img_path = os.path.join(chapter_dir, f"{idx}{ext}")
            tasks.append((img_url, img_path, headers, proxies, chapter_name))
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = [executor.submit(download_img_task, t) for t in tasks]
            for future in as_completed(futures):
                pass
        return True
    except Exception as e:
        print(f"章节爬取异常: {url}，错误: {e}")
        return False

def main():
    proxies = {
        'http': f'http://{PROXY}',
        'https': f'http://{PROXY}',
    }
    headers = {
        'User-Agent': USER_AGENT,
        'Referer': 'https://app.baozimh.com/',
    }
    done_set = load_jindu()
    # 下载封面
    if COVER_URL:
        download_cover(COVER_URL, headers, proxies)
    driver = get_driver()
    try:
        for chapter_idx in range(CHAPTER_START, CHAPTER_END + 1):
            if chapter_idx in done_set:
                print(f"章节0_{chapter_idx}已完成，跳过。")
                continue
            ok = crawl_chapter(driver, chapter_idx, headers, proxies)
            if ok:
                done_set.add(chapter_idx)
                save_jindu(done_set)
            time.sleep(1)
    finally:
        driver.quit()
        if len(done_set) == (CHAPTER_END - CHAPTER_START + 1):
            remove_jindu()

if __name__ == '__main__':
    main() 