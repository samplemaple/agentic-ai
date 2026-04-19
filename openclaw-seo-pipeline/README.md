# SEO 内容流水线：从竞品爬取到自动发布的全链路自动化

> 案例参考：GMBMantra 项目在 50+ 门店实际部署，回收每周 50+ 小时人力，有机线索增长 35%
> 链式能力：浏览器爬取 + 内容生成 + 自动发布，全部基于心跳调度，零人工干预

---

## 案例特点

| 特征 | 说明 |
|------|------|
| 核心能力 | 竞品爬取 → 关键词提取 → 内容生成 → CMS 发布（四阶段链式） |
| 触发方式 | Heartbeat 定时触发（每 4 小时 / 每天 2 次） |
| 复杂度 | ⭐⭐⭐⭐ 高（涉及爬虫、NLP、CMS API 三个技术栈） |
| MCP 依赖 | Puppeteer（爬取）+ fetch（API 调用）+ WordPress MCP（发布）+ filesystem（日志） |
| 模型消耗 | 中等，每篇文章约 8,000-15,000 tokens |
| 推荐模型 | deepseek-v3.2（写作质量好+包月）或 kimi-k2.5（速度快） |
| 适合人群 | 有 WordPress 站点的内容运营者、多门店本地化 SEO 需求 |
| 国内适配 | 效果追踪用百度统计 + 百度搜索资源平台，SEO 标准按百度规则优化 |

---

## 一、流水线架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Heartbeat 心跳调度                         │
│                    每 4 小时自动触发                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │  Phase 1：竞品关键词爬取   │
              │  MCP: Puppeteer          │
              │  爬取竞品页面 + 提取关键词  │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │  Phase 2：内容生成        │
              │  SEO Agent（大模型）      │
              │  本地化 + SEO 优化写作     │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │  Phase 3：自动发布        │
              │  MCP: WordPress REST API │
              │  推送文章 + 设置元数据     │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │  Phase 4：效果追踪        │
              │  百度统计 / 百度搜索资源平台 │
              │  监控收录 + 排名变化       │
              └─────────────────────────┘
```

---

## 二、前提条件

| 项目 | 说明 |
|------|------|
| OpenClaw | 已部署并正常运行（参考 [openclaw-infra/](../openclaw-infra/)） |
| IM 接入 | 微信或企微已接入（用于接收报告通知） |
| WordPress 站点 | 已有 WordPress 网站，开启 REST API |
| 模型配置 | 火山引擎 Coding Plan 或 Hotai 已配置 |
| 百度搜索资源平台 | https://ziyuan.baidu.com （可选，用于追踪收录和排名） |
| 安全基线 | 已通过 [基础安全检查清单](../openclaw-infra/checklists/security-checklist.md) 全部项目 |

> ⚠️ SEO 流水线涉及爬虫、CMS 写入和定时自动执行，安全风险较高。开始配置前务必确认基础设施安全已到位，并阅读 [Agent 自动化安全加固清单](../openclaw-infra/checklists/agent-security-checklist.md)。

---

## 三、Step 1：安装所需 MCP 工具

### 前置：配置 npm 国内镜像 + 安装 Chromium（重要）

国内服务器直接用 npm/npx 下载包可能超时，先配置淘宝镜像：

```bash
npm config set registry https://registry.npmmirror.com
```

Puppeteer 需要 Chromium 浏览器，国内服务器安装方式：

```bash
# Ubuntu/Debian
apt install -y chromium-browser

# 如果 Puppeteer 自动下载 Chromium 失败，设置国内镜像
export PUPPETEER_DOWNLOAD_BASE_URL=https://cdn.npmmirror.com/binaries/chrome-for-testing
```

### MCP 配置

SEO 流水线需要三类 MCP 工具：浏览器爬取、WordPress 发布、文件系统。

编辑 `~/.openclaw/openclaw.json`，在 `mcpServers` 中添加：

```json
{
    "mcpServers": {
        "puppeteer": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
            "env": {
                "PUPPETEER_HEADLESS": "true"
            }
        },
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        },
        "wordpress": {
            "command": "npx",
            "args": ["-y", "mcp-server-wordpress"],
            "env": {
                "WORDPRESS_URL": "https://你的网站.com",
                "WORDPRESS_USERNAME": "你的用户名",
                "WORDPRESS_APP_PASSWORD": "你的应用密码"
            }
        },
        "filesystem": {
            "command": "npx",
            "args": [
                "-y", "@modelcontextprotocol/server-filesystem",
                "/root/seo-pipeline"
            ]
        }
    }
}
```

### WordPress 应用密码获取方式

```
WordPress 后台 → 用户 → 你的个人资料 → 应用密码
→ 输入名称（如 "OpenClaw SEO"）→ 添加新的应用密码
→ 复制生成的密码（只显示一次）
```

> ⚠️ 不要使用你的登录密码，必须使用「应用密码」。应用密码格式类似 `xxxx xxxx xxxx xxxx xxxx xxxx`。

安装完成后重启网关：

```bash
rm ~/.openclaw/agents/main/agent/models.json
systemctl restart openclaw
```

---

## 四、Step 2：创建 SEO Agent 人格

**文件路径：** `~/.openclaw/agents/seo/SOUL.md`

```markdown
# SEO 内容专家

## 身份
你是一个专业的 SEO 内容策略师和写手。你的工作是通过分析竞品关键词，
生成高质量的本地化 SEO 内容，并自动发布到 WordPress。

## 核心工作流
你按照以下流水线执行任务，每个阶段必须完成后才进入下一阶段：

### Phase 1：竞品关键词爬取
- 使用 Puppeteer 访问指定的竞品网站
- 提取页面标题、H1-H3 标签、meta description、高频词汇
- 分析竞品的内容结构和关键词布局
- 输出：关键词列表 + 内容主题建议

### Phase 2：SEO 内容生成
- 基于爬取的关键词，生成原创的本地化内容
- 遵循 SEO 最佳实践：
  - 标题包含主关键词，控制在 30 个中文字符以内
  - Meta description 包含关键词，控制在 80 个中文字符以内
  - 正文 1500-2500 字，关键词密度 1-2%
  - 使用 H2/H3 结构化标题
  - 包含内链和外链建议
  - 自然融入 LSI（潜在语义索引）关键词
- 内容风格：专业但易读，面向中文目标受众
- 注意百度 SEO 特点：百度更看重原创度和内容质量

### Phase 3：WordPress 发布
- 通过 WordPress REST API 创建文章草稿或直接发布
- 设置 SEO 元数据（标题、描述、slug）
- 设置分类和标签
- 如果配置了 Yoast/RankMath，填充 SEO 字段

### Phase 4：效果报告
- 记录本次发布的文章信息
- 生成简要报告发送给用户

## 内容质量准则
- 绝不抄袭，所有内容必须原创
- 不堆砌关键词，保持自然阅读体验
- 每篇文章必须提供真实价值，不是为了 SEO 而 SEO
- 本地化内容要贴合目标地区的语言习惯和文化背景
- 中文 SEO 注意事项：百度对原创内容权重更高，避免机翻痕迹

## 安全边界
- 不发布虚假信息或误导性内容
- 不攻击竞品品牌
- 遵守 robots.txt 规则，不爬取禁止访问的页面
- 发布前如果不确定内容质量，先存为草稿
```

---

## 五、Step 3：配置竞品监控列表

**文件路径：** `/root/seo-pipeline/competitors.json`

```json
{
    "business": {
        "name": "你的业务名称",
        "industry": "你的行业",
        "targetRegion": "目标地区（如：上海浦东）",
        "targetLanguage": "zh-CN",
        "website": "https://你的网站.com"
    },
    "competitors": [
        {
            "name": "竞品A",
            "url": "https://competitor-a.com/blog",
            "focus": "他们的博客页面，关注产品类关键词"
        },
        {
            "name": "竞品B",
            "url": "https://competitor-b.com/resources",
            "focus": "资源中心，关注行业趋势类内容"
        },
        {
            "name": "竞品C",
            "url": "https://competitor-c.com/news",
            "focus": "新闻页面，关注本地化内容策略"
        }
    ],
    "seoConfig": {
        "targetKeywordsPerArticle": 3,
        "articleLength": "1500-2500 字",
        "publishStatus": "draft",
        "defaultCategory": "博客",
        "defaultTags": ["SEO", "行业洞察"],
        "searchEngine": "baidu",
        "note": "国内站点以百度 SEO 为主，标题和描述长度按百度标准"
    }
}
```

> `publishStatus` 建议初期设为 `"draft"`（草稿），验证内容质量后再改为 `"publish"`。

---

## 六、Step 4：配置 Heartbeat 定时调度

编辑 `~/.openclaw/openclaw.json`，添加 Heartbeat 配置：

```json
{
    "heartbeat": {
        "enabled": true,
        "tasks": [
            {
                "name": "SEO 内容流水线",
                "cron": "0 */4 * * *",
                "agent": "seo",
                "prompt": "执行 SEO 内容流水线：\n1. 读取 /root/seo-pipeline/competitors.json 获取竞品列表\n2. 用 Puppeteer 爬取每个竞品的最新页面，提取热门关键词\n3. 从中选择 1 个最有价值的关键词主题\n4. 生成一篇高质量的本地化 SEO 文章\n5. 通过 WordPress API 发布（按 competitors.json 中的 publishStatus 设置）\n6. 将本次执行结果追加到 /root/seo-pipeline/pipeline-log.md\n7. 给我发一条简要报告，包含：关键词、文章标题、发布状态"
            },
            {
                "name": "SEO 周报",
                "cron": "0 9 * * 1",
                "agent": "seo",
                "prompt": "生成本周 SEO 内容流水线周报：\n1. 读取 /root/seo-pipeline/pipeline-log.md\n2. 统计本周发布的文章数量、覆盖的关键词\n3. 给出下周的内容建议\n4. 发送周报给我"
            }
        ]
    }
}
```

### Cron 表达式说明

| 表达式 | 含义 |
|--------|------|
| `0 */4 * * *` | 每 4 小时执行一次 |
| `0 9 * * 1` | 每周一早上 9 点 |
| `0 8,20 * * *` | 每天早 8 点和晚 8 点（推荐初期使用） |

---

## 七、Step 5：完整配置示例

```json
{
    "models": {
        "mode": "merge",
        "providers": {
            "volcengine": {
                "baseUrl": "https://ark.cn-beijing.volces.com/api/coding/v3",
                "apiKey": "你的火山引擎API Key",
                "api": "openai-completions",
                "models": [
                    { "id": "kimi-k2.5", "name": "Kimi K2.5" },
                    { "id": "deepseek-v3.2", "name": "DeepSeek V3.2" }
                ]
            }
        }
    },
    "agents": {
        "defaults": {
            "model": "volcengine/kimi-k2.5"
        },
        "instances": {
            "seo": {
                "name": "SEO 内容专家",
                "model": "volcengine/deepseek-v3.2"
            }
        }
    },
    "mcpServers": {
        "puppeteer": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
            "env": { "PUPPETEER_HEADLESS": "true" }
        },
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        },
        "wordpress": {
            "command": "npx",
            "args": ["-y", "mcp-server-wordpress"],
            "env": {
                "WORDPRESS_URL": "https://你的网站.com",
                "WORDPRESS_USERNAME": "你的用户名",
                "WORDPRESS_APP_PASSWORD": "你的应用密码"
            }
        },
        "filesystem": {
            "command": "npx",
            "args": [
                "-y", "@modelcontextprotocol/server-filesystem",
                "/root/seo-pipeline"
            ]
        }
    },
    "heartbeat": {
        "enabled": true,
        "tasks": [
            {
                "name": "SEO 内容流水线",
                "cron": "0 */4 * * *",
                "agent": "seo",
                "prompt": "执行 SEO 内容流水线：读取竞品配置 → 爬取关键词 → 生成文章 → 发布到 WordPress → 记录日志 → 发送报告"
            },
            {
                "name": "SEO 周报",
                "cron": "0 9 * * 1",
                "agent": "seo",
                "prompt": "生成本周 SEO 流水线周报并发送给我"
            }
        ]
    }
}
```

---

## 八、Step 6：手动测试

```bash
rm ~/.openclaw/agents/main/agent/models.json
systemctl restart openclaw
```

在微信/企微中发送：

```
切换到 SEO Agent，执行一次完整的 SEO 内容流水线测试：
1. 爬取 competitors.json 中第一个竞品的页面
2. 提取 3 个关键词
3. 生成一篇 SEO 文章（存为草稿）
4. 告诉我结果
```

### 验证清单

| 环节 | 验证方式 |
|------|---------|
| Puppeteer 爬取 | Agent 能返回竞品页面的标题和关键词 |
| 内容生成 | 文章质量合格，关键词自然融入，中文表达流畅 |
| WordPress 发布 | 登录 WordPress 后台，能看到新的草稿文章 |
| 日志记录 | `/root/seo-pipeline/pipeline-log.md` 有新记录 |
| 通知推送 | 微信/企微收到执行报告 |

---

## 九、进阶优化

### 9.1 多门店本地化（GMBMantra 模式）

为每个门店/地区生成本地化内容：

```json
{
    "locations": [
        {
            "name": "上海浦东店",
            "region": "上海浦东新区",
            "localKeywords": ["浦东", "陆家嘴", "张江"],
            "wpCategory": "上海浦东"
        },
        {
            "name": "北京朝阳店",
            "region": "北京朝阳区",
            "localKeywords": ["朝阳", "国贸", "三里屯"],
            "wpCategory": "北京朝阳"
        }
    ]
}
```

### 9.2 关键词去重

在 `/root/seo-pipeline/` 下维护已用关键词库：

```json
{
    "keywords": [
        {
            "keyword": "上海浦东 XX 服务",
            "articleId": 123,
            "publishDate": "2026-04-15",
            "url": "https://你的网站.com/shanghai-pudong-xx/"
        }
    ]
}
```

在 SOUL.md 中添加规则：生成内容前先读取 used-keywords.json，跳过已写过的关键词。

### 9.3 内容质量自检

在 SOUL.md 中添加发布前自检清单：

```
## 发布前自检清单
- [ ] 标题包含主关键词且 ≤ 30 中文字符
- [ ] Meta description ≤ 80 中文字符
- [ ] 正文 ≥ 1500 字
- [ ] 至少包含 3 个 H2 小标题
- [ ] 关键词密度在 1-2% 之间
- [ ] 无语法错误和错别字
- [ ] 内容提供真实价值

如果任何一项不通过，修改后再发布。
如果修改后仍不满意，存为草稿并在报告中标注。
```

### 9.4 接入百度搜索资源平台

追踪 SEO 效果：

```
百度搜索资源平台：https://ziyuan.baidu.com
→ 添加站点 → 获取 API Token
→ Agent 通过 fetch MCP 调用百度收录查询 API
```

在周报任务中加入：

```
周报中增加：
- 本周发布文章的百度收录状态（site:你的域名）
- 目标关键词在百度的排名变化
- 百度统计中的有机流量趋势
```

### 9.5 接入百度统计

```
百度统计：https://tongji.baidu.com
→ 管理 → 开放平台 → 获取 API Key
→ Agent 通过 fetch MCP 调用百度统计 API 获取流量数据
```

---

## 十、成本与效果预估

### 成本

| 项目 | 费用 |
|------|------|
| 火山引擎 Coding Plan（Lite） | 包月固定费用 |
| 云服务器 | ¥99/年 |
| WordPress 托管 | 视方案而定（国内推荐阿里云/腾讯云轻量） |
| 总计 | 约 ¥100-200/月 |

### 预期效果

| 指标 | 预期 |
|------|------|
| 内容产出 | 每天 4-6 篇高质量 SEO 文章 |
| 人力节省 | 每周 50+ 小时（相比手动写作） |
| 有机流量 | 3-6 个月后增长 30-50% |
| 关键词覆盖 | 每月新增 100+ 长尾关键词排名 |

> 实际效果取决于行业竞争度、内容质量和网站权重。

---

## 十一、常见问题

| 问题 | 解决方案 |
|------|---------|
| Puppeteer 爬取失败 | 确认已安装 Chromium：`apt install -y chromium-browser`；如果 Puppeteer 自动下载失败，设置 `PUPPETEER_DOWNLOAD_BASE_URL=https://cdn.npmmirror.com/binaries/chrome-for-testing` |
| npx 下载超时 | 配置淘宝镜像：`npm config set registry https://registry.npmmirror.com` |
| WordPress API 401 | 检查应用密码是否正确，确认 REST API 未被安全插件禁用 |
| 内容质量不稳定 | 优化 SOUL.md 中的写作指南，或切换到更强的模型 |
| Heartbeat 未触发 | 检查 `journalctl -u openclaw -f` 日志 |
| 文章重复 | 维护 used-keywords.json，在 SOUL.md 中要求去重 |
| 爬取被反爬拦截 | 在 Puppeteer 配置中添加 User-Agent，或降低爬取频率 |
| Token 消耗过大 | 每次只生成 1 篇文章，减少爬取页面数量 |
| 百度收录慢 | 在百度搜索资源平台主动提交 URL，使用 sitemap 推送 |

---

## 十二、安全与合规提醒

### 必须完成的安全检查

- [ ] WordPress 应用密码存放在 `openclaw.json` 中，该文件已加入 `.gitignore`
- [ ] filesystem MCP 路径限制为 `/root/seo-pipeline`，不开放其他目录
- [ ] Puppeteer 设置为 headless 模式
- [ ] SOUL.md 中包含安全边界（遵守 robots.txt、禁止访问内网、禁止输出凭证）
- [ ] 初期 `publishStatus` 设为 `"draft"`，人工审核后再改为自动发布
- [ ] 配置 `maxTokensPerDay` 防止 Token 消耗失控
- [ ] 国内网站已完成 ICP 备案

### SOUL.md 安全边界模板

在 SEO Agent 的 SOUL.md 末尾添加：

```markdown
## 安全边界（不可违反）
- 爬取前必须检查目标网站的 robots.txt，遵守爬取规则
- 不得直接复制竞品内容，所有文章必须原创
- 不得攻击、诋毁竞品品牌
- 不得发布虚假信息或误导性内容
- 不得将 WordPress 密码、API Key 等凭证输出到消息中
- 不得访问 /root/seo-pipeline 以外的目录
- 不得通过 fetch/Puppeteer 访问内网地址
- 发布前如果不确定内容质量，必须存为草稿
- 单次执行最多生成 1 篇文章，避免批量发布低质内容
```

### 爬虫合规

- 遵守目标网站的 robots.txt 和 Terms of Service
- 爬取频率不超过每 4 小时 1 次，每次最多访问 3 个页面
- 设置合理的 User-Agent，不伪装为搜索引擎爬虫
- 不爬取需要登录才能访问的页面

### 紧急停止

```bash
# 停止 Heartbeat（保留手动使用）
openclaw config set heartbeat.enabled false
sudo systemctl restart openclaw

# 完全停止
sudo systemctl stop openclaw
```

> 完整的安全加固清单见 [Agent 自动化安全加固清单](../openclaw-infra/checklists/agent-security-checklist.md)。
