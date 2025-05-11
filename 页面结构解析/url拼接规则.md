# 包子漫画爬虫 URL 拼接与章节范围获取规则

## 1. BASE_URL 拼接规则
- BASE_URL = "https://app.baozimh.com/baozimhapp/comic/chapter/" + 漫画标题拼音（去空格） + "-" + 作者拼音（去空格） + "/"
- 其中，漫画标题和作者需转为拼音，推荐使用 [xpinyin](https://github.com/lxneng/xpinyin) 库：
  ```python
  from xpinyin import Pinyin
  p = Pinyin()
  title_py = p.get_pinyin(漫画标题, '').replace(' ', '')
  author_py = p.get_pinyin(作者, '').replace(' ', '')
  BASE_URL = f"https://app.baozimh.com/baozimhapp/comic/chapter/{title_py}-{author_py}/"
  ```
- 标题和作者的获取方式见下文。

## 2. 介绍页URL拼接规则
- 介绍页URL = "https://appcn1-vdkr.baozimh.com/baozimhapp/comic/" + 漫画标题拼音（去空格） + "-" + 作者拼音（去空格）

## 3. 标题与作者的提取（参考@搜索页面结构解析.md）
- 搜索结果卡片选择器：`.comics-card`
  - 标题：`.comics-card__title h3`（文本内容）
  - 作者：`small.tags.text-truncate`（文本内容）

## 4. CHAPTER_START 和 CHAPTER_END 获取规则（参考@漫画介绍页结构解析.md）
- 访问介绍页URL，解析章节列表：
  - 章节列表容器：`.chapter-list`
  - 每个章节：`.chapter-item`
- 章节编号通常为0_0、0_1、0_2……
- CHAPTER_START = 最小章节编号（通常为0）
- CHAPTER_END = 最大章节编号（可通过统计`.chapter-item`数量-1，或解析章节编号）

## 5. 参考选择器与结构
- 搜索页面：
  - 标题：`.comics-card__title h3`
  - 作者：`small.tags.text-truncate`
- 介绍页：
  - 章节列表：`.chapter-list .chapter-item`

## 6. 依赖说明
- 需安装 xpinyin：
  ```bash
  pip install xpinyin
  ```

## 7. 章节编号与章节URL拼接规则
- 访问介绍页，解析章节列表（`.chapter-list .chapter-item`），按页面实际顺序依次提取所有章节。
- 章节编号从0开始递增（即第一章为0，第二章为1，依此类推）。
- 每个章节的URL拼接为：
  BASE_URL + "0_" + 章节编号 + ".html"
  例如：
  - 第一章：BASE_URL + "0_0.html"
  - 第二章：BASE_URL + "0_1.html"
  - 以此类推。
- 章节顺序必须与介绍页中`.chapter-list .chapter-item`的顺序一致。
- CHAPTER_START = 0
- CHAPTER_END = 章节总数 - 1

---

本规则适用于包子漫画爬虫脚本变量自动生成与章节范围自动获取。
