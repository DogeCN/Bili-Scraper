# Bilibili API 说明文档

本文档详细说明了项目中使用的 Bilibili API 接口。

---

## 目录

- [API 概述](#api-概述)
- [1. 专栏文章列表 API](#1-专栏文章列表-api)
- [2. 文章搜索 API](#2-文章搜索-api)
- [3. 文章内容获取 API](#3-文章内容获取-api)
- [请求头配置](#请求头配置)
- [Cookie 配置](#cookie-配置)
- [错误处理](#错误处理)
- [注意事项](#注意事项)

---

## API 概述

本项目使用以下 Bilibili API 接口：

| API 名称 | 用途 | HTTP 方法 |
|---------|------|-----------|
| 专栏文章列表 API | 获取指定专栏的所有文章 | GET |
| 文章搜索 API | 搜索 Bilibili 专栏文章 | GET |
| 文章内容获取 API | 获取单篇文章的完整内容 | GET |

所有 API 均为 Bilibili 官方接口，需要模拟浏览器请求头以提高成功率。

---

## 1. 专栏文章列表 API

### 接口信息

- **接口地址**: `https://api.bilibili.com/x/article/list/web/articles`
- **请求方法**: GET
- **用途**: 获取指定专栏列表的所有文章信息

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| id | string | 是 | 专栏 ID（从 URL 中提取的数字部分） |
| web_location | string | 否 | 网页位置标识，默认为 `333.1400` |

### 请求示例

```bash
GET https://api.bilibili.com/x/article/list/web/articles?id=123456&web_location=333.1400
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "author": {
      "name": "作者名称",
      "mid": 123456789
    },
    "articles": [
      {
        "id": 987654321,
        "title": "文章标题",
        "summary": "文章摘要",
        "description": "文章描述",
        "publish_time": 1234567890,
        "stats": {
          "view": 12345
        },
        "view": 12345
      }
    ]
  }
}
```

### 响应字段说明

#### 顶层字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | number | 状态码，0 表示成功 |
| message | string | 状态消息 |
| data | object | 数据对象 |

#### data.author 字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| name | string | 作者名称 |
| mid | number | 作者 ID |

#### data.articles 数组元素

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | number | 文章 ID |
| title | string | 文章标题 |
| summary | string | 文章摘要 |
| description | string | 文章描述 |
| publish_time | number | 发布时间（Unix 时间戳，秒） |
| stats.view | number | 阅读数 |
| view | number | 阅读数（备用字段） |

### 使用场景

- 用户输入专栏列表 URL
- 从 URL 中提取专栏 ID（格式：`rl{数字}`）
- 调用此 API 获取文章列表

### 代码实现

```typescript
async function crawlReadlistArticles(readlistId: string, cookie?: string): Promise<Article[]> {
  const apiUrl = `https://api.bilibili.com/x/article/list/web/articles?id=${readlistId}&web_location=333.1400`;

  const headers: Record<string, string> = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
    'Accept': '*/*',
    'Referer': `https://www.bilibili.com/read/readlist/rl${readlistId}`,
    'Origin': 'https://www.bilibili.com',
  };

  if (cookie) {
    headers['Cookie'] = cookie;
  }

  const response = await fetch(apiUrl, { headers });
  const data = await response.json();

  if (data.code !== 0) {
    throw new Error(`Bilibili API error: ${data.message}`);
  }

  return data.data.articles.map(article => ({
    id: article.id.toString(),
    title: article.title,
    summary: article.summary || article.description,
    author: data.data.author.name,
    publishTime: new Date(article.publish_time * 1000).toLocaleString('zh-CN'),
    readCount: article.stats?.view || article.view,
    url: `https://www.bilibili.com/read/${article.id}`,
  }));
}
```

---

## 2. 文章搜索 API

### 接口信息

- **接口地址**: `https://api.bilibili.com/x/web-interface/search/type`
- **请求方法**: GET
- **用途**: 搜索 Bilibili 专栏文章

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| search_type | string | 是 | 搜索类型，固定为 `article` |
| keyword | string | 是 | 搜索关键词（需 URL 编码） |
| page | number | 否 | 页码，默认为 1 |
| order | string | 否 | 排序方式，默认为 `default` |
| duration | number | 否 | 时长筛选，默认为 0 |
| tids | number | 否 | 分区 ID，默认为 0 |

### 请求示例

```bash
GET https://api.bilibili.com/x/web-interface/search/type?search_type=article&keyword=Python&page=1&order=default&duration=0&tids=0
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "result": [
      {
        "id": 987654321,
        "aid": 987654321,
        "title": "文章标题<em>Python</em>教程",
        "desc": "文章描述内容",
        "description": "文章描述内容",
        "author": "作者名称",
        "up_name": "作者名称",
        "pub_time": "2024-01-01 12:00:00",
        "pubdate": 1234567890,
        "view": 12345,
        "read_count": 12345
      }
    ]
  }
}
```

### 响应字段说明

#### 顶层字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | number | 状态码，0 表示成功 |
| message | string | 状态消息 |
| data | object | 数据对象 |

#### data.result 数组元素

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | string | 文章 ID |
| aid | string | 文章 ID（备用字段） |
| title | string | 文章标题（可能包含 `<em>` 高亮标签） |
| desc | string | 文章描述 |
| description | string | 文章描述（备用字段） |
| author | string | 作者名称 |
| up_name | string | 作者名称（备用字段） |
| pub_time | string | 发布时间（格式：YYYY-MM-DD HH:mm:ss） |
| pubdate | number | 发布时间（Unix 时间戳，秒） |
| view | number | 阅读数 |
| read_count | number | 阅读数（备用字段） |

### HTML 标签处理

搜索结果中的标题和描述可能包含 HTML 标签，特别是 `<em>` 标签用于高亮显示搜索关键词：

```typescript
function stripHtmlTags(html: string): string {
  if (!html) return '';
  return html
    .replace(/<em[^>]*>/gi, '')  // 移除 <em> 开始标签
    .replace(/<\/em>/gi, '')     // 移除 </em> 结束标签
    .replace(/<[^>]+>/g, '');    // 移除其他所有 HTML 标签
}
```

### 使用场景

- 用户输入搜索关键词
- 调用此 API 搜索相关文章
- 清理 HTML 标签后展示结果

### 代码实现

```typescript
async function searchArticles(keyword: string, cookie?: string): Promise<SearchResult[]> {
  const searchUrl = `https://api.bilibili.com/x/web-interface/search/type?search_type=article&keyword=${encodeURIComponent(keyword)}&page=1&order=default&duration=0&tids=0`;

  const headers: Record<string, string> = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/',
  };

  if (cookie) {
    headers['Cookie'] = cookie;
  }

  const response = await fetch(searchUrl, { headers });
  const data = await response.json();

  if (data.code !== 0 || !data.data?.result) {
    throw new Error(data.message || '搜索失败');
  }

  return data.data.result.map(item => ({
    id: item.id || String(item.aid),
    title: stripHtmlTags(item.title),
    summary: stripHtmlTags(item.desc || item.description),
    author: item.author || item.up_name,
    publishTime: item.pub_time || item.pubdate,
    readCount: item.view || item.read_count,
    url: `https://www.bilibili.com/read/${item.id || item.aid}`,
  }));
}
```

---

## 3. 文章内容获取 API

### 接口信息

- **接口地址**: `https://api.bilibili.com/x/article/view`
- **请求方法**: GET
- **用途**: 获取单篇文章的完整内容

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| id | string | 是 | 文章 ID |

### 请求示例

```bash
GET https://api.bilibili.com/x/article/view?id=987654321
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 987654321,
    "title": "文章标题",
    "desc": "文章描述",
    "summary": "文章摘要",
    "author": {
      "name": "作者名称",
      "mid": 123456789
    },
    "pub_time": 1234567890,
    "stats": {
      "view": 12345
    },
    "content": "<p>文章内容 HTML</p>",
    "html_content": "<p>文章内容 HTML</p>"
  }
}
```

### 响应字段说明

#### 顶层字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | number | 状态码，0 表示成功 |
| message | string | 状态消息 |
| data | object | 数据对象 |

#### data 字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | number | 文章 ID |
| title | string | 文章标题 |
| desc | string | 文章描述 |
| summary | string | 文章摘要 |
| author.name | string | 作者名称 |
| author.mid | number | 作者 ID |
| pub_time | number | 发布时间（Unix 时间戳，秒） |
| stats.view | number | 阅读数 |
| content | string | 文章内容（HTML 格式） |
| html_content | string | 文章内容（HTML 格式，备用字段） |

### HTML 内容处理流程

文章内容以 HTML 格式返回，需要转换为纯文本：

```typescript
function processHtmlContent(html: string): string {
  // 步骤1：移除非文本元素
  html = html
    .replace(/<(script|style|noscript)[^>]*>[\s\S]*?<\/\1>/gi, '')
    .replace(/<img[^>]*>/gi, '')
    .replace(/<video[^>]*>[\s\S]*?<\/video>/gi, '')
    .replace(/<iframe[^>]*>[\s\S]*?<\/iframe>/gi, '')
    .replace(/<figure[^>]*>[\s\S]*?<\/figure>/gi, '')
    .replace(/<figcaption[^>]*>[\s\S]*?<\/figcaption>/gi, '');

  // 步骤2：将 HTML 标签转换为换行符
  html = html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<li[^>]*>/gi, '\n• ')
    .replace(/<\/li>/gi, '')
    .replace(/<\/[ou]l>/gi, '\n')
    .replace(/<p[^>]*>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<h[1-6][^>]*>/gi, '\n\n')
    .replace(/<\/h[1-6]>/gi, '\n')
    .replace(/<div[^>]*>/gi, '\n')
    .replace(/<\/div>/gi, '\n');

  // 步骤3：移除所有剩余标签
  html = html.replace(/<[^>]+>/g, '');

  // 步骤4：解码 HTML 实体
  html = html
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#(\d+);/g, (match, code) => String.fromCharCode(parseInt(code)));

  // 步骤5：清理多余空白，保留换行
  let lines = html.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  // 步骤6：处理孤立的列表符号
  const processedLines = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line === '•' && i + 1 < lines.length) {
      processedLines.push(`• ${lines[i + 1]}`);
      i++;
    } else {
      processedLines.push(line);
    }
  }

  return processedLines.join('\n\n').trim();
}
```

### 使用场景

- 用户选择要下载的文章
- 批量调用此 API 获取文章内容
- 将 HTML 转换为纯文本后导出

### 代码实现

```typescript
async function fetchArticleContent(articleId: string, cookie?: string): Promise<string> {
  const contentUrl = `https://api.bilibili.com/x/article/view?id=${articleId}`;

  const headers: Record<string, string> = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/',
  };

  if (cookie) {
    headers['Cookie'] = cookie;
  }

  const response = await fetch(contentUrl, { headers });
  const data = await response.json();

  if (data.code !== 0 || !data.data) {
    throw new Error(data.message || '获取内容失败');
  }

  const article = data.data;
  const htmlContent = article.content || article.html_content;

  return processHtmlContent(htmlContent);
}
```

---

## 请求头配置

所有 API 请求都需要配置完整的请求头，模拟浏览器行为：

### 标准请求头

```typescript
const headers: Record<string, string> = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Accept-Encoding': 'gzip, deflate, br',
  'Origin': 'https://www.bilibili.com',
  'Referer': 'https://www.bilibili.com/',
  'Connection': 'keep-alive',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-site',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Cache-Control': 'no-cache',
  'Pragma': 'no-cache',
};
```

### 请求头说明

| 请求头 | 说明 |
|-------|------|
| User-Agent | 浏览器标识，模拟真实浏览器 |
| Accept | 接受的内容类型 |
| Accept-Language | 接受的语言 |
| Accept-Encoding | 接受的编码方式 |
| Origin | 请求来源 |
| Referer | 引用页面 |
| Sec-Fetch-* | 安全相关请求头 |
| Cache-Control | 缓存控制 |

---

## Cookie 配置

### Cookie 的作用

提供 Cookie 可以：

1. 提高爬取成功率
2. 访问私密专栏
3. 绕过部分访问限制
4. 获取更完整的数据

### 获取 Cookie 的方法

1. 打开浏览器，访问 [bilibili.com](https://www.bilibili.com)
2. 按 `F12` 打开开发者工具
3. 切换到 `Application`（或 `Storage`）标签
4. 展开 `Cookies` → `https://www.bilibili.com`
5. 复制所需的 Cookie 值

### 常用 Cookie 字段

| 字段名 | 说明 |
|-------|------|
| SESSDATA | 会话标识，最重要的字段 |
| bili_jct | CSRF 令牌 |
| DedeUserID | 用户 ID |
| DedeUserID__ckMd5 | 用户 ID 的 MD5 值 |

### Cookie 示例

```
SESSDATA=4eb73b3c%2C1787485989%2C25479%2A21CjD9ol6PL-oBAjNTEX7FpHZg0-uqfaaJiC2BXyubvRVSX4BwXPyCnpiR7xC7jsYLUJUSVllLOXRWZzZVaEd3eGpNMUhlZFVFT2s0MXh6NVlLdi1SbWpnZTNJQnkycW1LR3hDUUVJSU44enljb3VnQmZ0Tm5VREpNZ0xXekRWbk82eVVqeTR6TndBIIEC; bili_jct=86302958eeb939f58114101026a15dc4;
```

### 使用 Cookie

```typescript
if (cookie) {
  headers['Cookie'] = cookie;
}
```

---

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| 0 | 成功 | - |
| -101 | 账号未登录 | 提供 Cookie |
| -102 | 帐号被封禁 | 更换账号 |
| -111 | CSRF 校验失败 | 更新 Cookie |
| -400 | 请求错误 | 检查请求参数 |
| -403 | 无权限访问 | 检查 Cookie 或权限 |
| -404 | 资源不存在 | 检查 ID 是否正确 |
| -412 | 请求过快 | 降低请求频率 |
| -500 | 服务器错误 | 稍后重试 |

### 错误处理示例

```typescript
try {
  const response = await fetch(apiUrl, { headers });
  const data = await response.json();

  if (data.code !== 0) {
    switch (data.code) {
      case -101:
        throw new Error('账号未登录，请提供有效的 Cookie');
      case -404:
        throw new Error('资源不存在，请检查 ID 是否正确');
      case -412:
        throw new Error('请求过快，请稍后重试');
      default:
        throw new Error(`API 错误: ${data.message || '未知错误'}`);
    }
  }

  return data.data;
} catch (error) {
  console.error('请求失败:', error);
  throw error;
}
```

---

## 注意事项

### 1. 请求频率限制

- Bilibili 可能对 API 请求进行频率限制
- 建议在批量请求时添加延迟
- 避免短时间内大量请求

```typescript
async function fetchWithDelay(urls: string[], delay = 1000) {
  const results = [];
  for (const url of urls) {
    const result = await fetch(url);
    results.push(result);
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  return results;
}
```

### 2. API 变更风险

- Bilibili API 可能随时变更
- 响应数据结构可能变化
- 建议定期测试 API 可用性

### 3. 合规性要求

- 遵守 Bilibili 服务条款
- 仅用于个人学习和研究
- 不得用于商业用途
- 尊重原作者版权

### 4. 数据准确性

- API 返回的数据可能不完整
- 部分字段可能为空
- 建议添加默认值处理

```typescript
const article = {
  title: data.title || '未知标题',
  author: data.author?.name || '未知作者',
  readCount: data.stats?.view || 0,
};
```

### 5. Cookie 安全

- 不要在代码中硬编码 Cookie
- 不要将 Cookie 提交到版本控制
- Cookie 可能过期，需要定期更新
- 建议使用环境变量存储 Cookie

```typescript
const cookie = process.env.BILIBILI_COOKIE;
```

---

## 附录

### 相关文件

- [专栏文章列表 API 实现](file:///d:/ToDo/projects/src/app/api/crawl/route.ts)
- [文章搜索 API 实现](file:///d:/ToDo/projects/src/app/api/search/route.ts)
- [文章内容获取 API 实现](file:///d:/ToDo/projects/src/app/api/content/route.ts)
- [前端页面实现](file:///d:/ToDo/projects/src/app/page.tsx)

### 参考资源

- [Bilibili API 文档](https://github.com/SocialSisterYi/bilibili-API-collect)
- [Next.js 文档](https://nextjs.org/docs)
- [MDN Web Docs - Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

**最后更新**: 2026-05-23