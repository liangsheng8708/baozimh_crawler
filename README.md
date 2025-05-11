# 包子漫画爬虫与GUI搜索工具

## 项目简介
本项目为逆向包子漫画APP制作的爬虫工具，用于爬取包子漫画APP中的漫画
本项目包含两个主要工具：
- **baozimh_gui_search.py**：基于Tkinter的包子漫画搜索与详情解析GUI工具。
- **baozimh_crawler.py**：多线程高效下载包子漫画章节图片的爬虫脚本。

适用于需要批量下载包子漫画图片、快速检索漫画信息、获取章节目录等场景。

---

## 主要功能

### 1. GUI搜索与详情解析（`baozimh_gui_search.py`）
- 支持关键词搜索包子漫画，展示结果列表。
- 选中漫画后自动解析详情页，显示标题、作者、简介、章节数、封面等。
- 可一键复制爬虫所需字段（如BASE_URL、COVER_URL、章节范围等）。
- 支持停止搜索、异常提示、界面友好。

### 2. 漫画批量下载爬虫（`baozimh_crawler.py`）
- 支持多线程下载指定漫画的所有章节图片。
- 支持断点续爬，自动记录已完成章节。
- 自动下载封面。
- 失败图片自动记录日志，便于后续补爬。
- 代理与UA可自定义。

---

## 环境依赖
- Python 3.7 及以上
- 推荐使用最新版Chrome浏览器及对应chromedriver

安装依赖：
```bash
pip install -r requirements.txt
```

`requirements.txt`内容包括：
- requests
- beautifulsoup4
- selenium
- chromedriver-autoinstaller
- Pillow
- xpinyin
- tk

---

## 使用说明

### 1. 启动GUI搜索工具
```bash
python baozimh_gui_search.py
```
- 输入关键词，点击"搜索"
- 选择结果，自动解析详情
- 可复制爬虫字段，便于后续下载

### 2. 使用爬虫批量下载漫画
1. 先用GUI工具获取`BASE_URL`、`COVER_URL`、章节起止编号。
2. 编辑`baozimh_crawler.py`顶部相关变量：
   - `COVER_URL`：封面图片链接
   - `BASE_URL`：章节图片基础链接
   - `CHAPTER_START`/`CHAPTER_END`：章节编号范围
   - `OUTPUT_DIR`：图片保存目录
   - `PROXY`：如需代理请设置
3. 运行爬虫：
```bash
python baozimh_crawler.py
```
- 支持断点续爬，进度保存在`baozimh_crawler_jindu.json`
- 失败图片记录在`baozimh_crawler_failed.log`

---

## 注意事项
- **代理设置**：如需科学上网，请正确设置`PROXY`变量。
- **chromedriver**：需与本地Chrome版本匹配，推荐使用`chromedriver-autoinstaller`自动管理。
- **反爬机制**：如遇频繁失败，可适当降低线程数或更换代理。
- **仅供学习交流，请勿用于商业用途。**

---

## 目录结构
```
├── baozimh_gui_search.py      # GUI搜索与详情解析工具
├── baozimh_crawler.py         # 多线程漫画图片下载爬虫
├── requirements.txt           # 依赖包列表
├── README.md                  # 项目说明文档
```

---

## 致谢
- 本项目仅供学习与技术交流。
- 感谢包子漫画平台。
- 感谢[selenium](https://www.selenium.dev)
- 感谢[xpinyin](https://github.com/lxneng/xpinyin)
