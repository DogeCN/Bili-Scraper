# Bilibili Scraper

交互式终端工具，用于从 Bilibili 专栏（readlist）获取文章列表并合并内容导出为 TXT 文件。

## 功能

- 读取本地 `cookie.json`，自动生成 Bilibili 请求 Cookie
- 查询指定专栏文章列表
- 合并专栏文章内容并保存为单个 TXT 文件
- 终端交互式菜单

## 依赖

- Python 3.13
- `httpx`
- `rich`

## 安装

推荐使用 PDM：

```bash
cd d:/ToDo/projects
pdm install
```

## 运行

```bash
python -m bilibili_scraper
```

## 使用说明

1. 将浏览器导出的 `cookie.json` 放到项目根目录
2. 启动程序
3. 选择菜单中的“查看专栏文章列表”或“合并专栏文章为 TXT”
4. 输入专栏 URL 或 `rl` ID，例如 `rl123456` 或完整链接

## Cookie 支持

程序会从 `cookie.json` 读取 Bilibili 域名下的 Cookie，用于提升 API 请求成功率。

## 注意

- 请确保 `cookie.json` 内容为浏览器导出格式的数组对象
- 本工具仅用于个人学习与研究，遵守 Bilibili 服务条款
