# 晨间执行官：一条消息简报开启高效率生活

> 案例参考：@danpeguine 在 OpenClaw 官方 Showcase 发布，详细列出 Agent 10 项日常任务，获 257 次点赞
> Reddit 用户 ShabzSparq 报告该工作流每天节省 20 分钟
> AI 咨询公司 Interactive Studio 全员使用，员工到办公室时已收到当日执行摘要

---

## 案例特点

| 特征 | 说明 |
|------|------|
| 核心能力 | 多数据源聚合 → 结构化格式 → IM 推送 |
| 触发方式 | Heartbeat 定时触发（每天早 7 点） |
| 复杂度 | ⭐⭐ 低（入门级，适合第一个自动化场景） |
| MCP 依赖 | fetch（天气/新闻）+ filesystem（日程/提醒） |
| 模型消耗 | 极低，每次约 2,000-4,000 tokens |
| 推荐模型 | kimi-k2.5（包月，零额外成本） |
| 适合人群 | 所有人——个人效率提升的起点 |

---

## 一、它做什么？

每天早上 7:00，Agent 自动执行以下任务，汇总为一条结构化简报推送到你的微信/企微：

```
┌─────────────────────────────────────────────┐
│           ☀️ 今日晨间简报 · 4月19日            │
├─────────────────────────────────────────────┤
│                                             │
│  🌤 天气：上海 22°C 多云，午后阵雨，带伞       │
│                                             │
│  📅 今日日程（3 项）：                        │
│  · 09:30 产品评审会（腾讯会议）               │
│  · 14:00 客户 Demo（线下 · 望京 SOHO）        │
│  · 16:00 周报截止提醒                        │
│                                             │
│  ⚡ 关键提醒：                               │
│  · Q2 OKR 明天截止提交                       │
│  · 客户合同本周五到期，需续签                  │
│                                             │
│  📰 行业热点（3 条）：                        │
│  · 火山引擎方舟新增 3 个模型...               │
│  · Anthropic 开源 Claude Code...            │
│  · DeepSeek 发布 V3.2 推理优化...            │
│                                             │
│  📖 推荐阅读：                               │
│  · 《Agent 设计模式最佳实践》                  │
│  · 《2026 年 SEO 趋势报告》                   │
│                                             │
│  💪 今日一句：                               │
│  "专注于过程，结果自然会来。"                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 二、架构设计

```
                    Heartbeat 定时触发
                    每天 07:00
                         │
              ┌──────────▼──────────┐
              │   晨间执行官 Agent    │
              │   模型：kimi-k2.5    │
              └──┬───┬───┬───┬───┬──┘
                 │   │   │   │   │
    ┌────────────▼┐ ┌▼──────┐▼──┐▼────────────┐
    │ 天气 API    │ │本地文件 │RSS│ 文件系统     │
    │ (fetch)    │ │(日程)  │源 │ (提醒/备忘)  │
    └────────────┘ └───────┘└──┘└────────────┘
                 │   │   │   │   │
              ┌──▼───▼───▼───▼───▼──┐
              │   汇总 + 格式化       │
              │   生成结构化简报       │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  推送到微信/企微       │
              └─────────────────────┘
```

---

## 三、前提条件

| 项目 | 说明 |
|------|------|
| OpenClaw | 已部署并正常运行 |
| IM 接入 | 微信 ClawBot 或企微机器人已接入（用于接收简报） |
| 模型 | 火山引擎 Coding Plan 已配置（日常任务用包月最划算） |
| 安全基线 | 已通过 [基础安全检查清单](../openclaw-infra/checklists/security-checklist.md) 全部项目 |

> ⚠️ 开始配置前，务必确认你的 OpenClaw 实例已完成安全加固（Gateway 绑定 127.0.0.1、Tailscale 穿透、安全组关闭所有入站端口）。详见 [Agent 自动化安全加固清单](../openclaw-infra/checklists/agent-security-checklist.md)。

---

## 四、Step 1：安装 MCP 工具

### 前置：配置 npm 国内镜像（重要）

国内服务器直接用 npm/npx 下载包可能超时，先配置淘宝镜像：

```bash
npm config set registry https://registry.npmmirror.com
```

### MCP 配置

晨间简报需要从多个数据源拉取信息。编辑 `~/.openclaw/openclaw.json`：

```json
{
    "mcpServers": {
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        },
        "filesystem": {
            "command": "npx",
            "args": [
                "-y", "@modelcontextprotocol/server-filesystem",
                "/root/morning-briefing"
            ]
        }
    }
}
```

### 可选：接入企微日历

如果你用企业微信管理日程，可以通过企微开放平台 API 实现日程自动拉取：

```
企微开放平台：https://developer.work.weixin.qq.com/document/path/93624
```

> 也可以直接用本地 markdown 文件维护日程，每周花 2 分钟更新即可。

---

## 五、Step 2：创建数据源配置

创建目录和配置文件：

```bash
mkdir -p /root/morning-briefing
```

**文件：** `/root/morning-briefing/config.json`

```json
{
    "user": {
        "name": "你的名字",
        "city": "上海",
        "timezone": "Asia/Shanghai",
        "language": "zh-CN"
    },
    "modules": {
        "weather": {
            "enabled": true,
            "primary": {
                "provider": "和风天气",
                "api": "https://devapi.qweather.com/v7/weather/now?location=101020100&key=你的Key",
                "note": "和风天气免费版每天 1000 次调用，注册：https://dev.qweather.com"
            },
            "fallback": {
                "provider": "wttr.in",
                "api": "https://wttr.in/Shanghai?format=j1&lang=zh",
                "note": "备用方案，免费无需注册，但国内偶尔不稳定"
            }
        },
        "calendar": {
            "enabled": true,
            "source": "local",
            "file": "/root/morning-briefing/calendar.md",
            "note": "本地日历文件；也可通过 fetch MCP 调用企微日历 API"
        },
        "reminders": {
            "enabled": true,
            "file": "/root/morning-briefing/reminders.md"
        },
        "news": {
            "enabled": true,
            "sources": [
                {
                    "name": "AI 行业",
                    "url": "https://www.infoq.cn/feed",
                    "filter": "AI, LLM, Agent, 大模型, 智能体"
                },
                {
                    "name": "技术热点",
                    "url": "https://www.oschina.net/news/rss",
                    "filter": ""
                },
                {
                    "name": "36氪",
                    "url": "https://36kr.com/feed",
                    "filter": "AI, 融资, SaaS"
                }
            ],
            "maxItems": 3
        },
        "reading": {
            "enabled": true,
            "file": "/root/morning-briefing/reading-list.md",
            "maxItems": 2
        },
        "quote": {
            "enabled": true,
            "style": "简短有力的中文句子，偏向行动和专注，不要鸡汤"
        }
    },
    "output": {
        "format": "structured",
        "pushTo": "wechat"
    }
}
```

**文件：** `/root/morning-briefing/calendar.md`

```markdown
# 本周日程

## 2026-04-19（周日）
- 无安排，休息日

## 2026-04-20（周一）
- 09:30 产品评审会（腾讯会议，链接：xxx）
- 14:00 客户 Demo（线下，望京 SOHO A座 12F）
- 16:00 周报截止提醒

## 2026-04-21（周二）
- 10:00 团队站会（企微群视频）
- 15:00 技术分享：Agent 设计模式
```

**文件：** `/root/morning-briefing/reminders.md`

```markdown
# 关键提醒

## 本周
- Q2 OKR 4月20日截止提交
- 客户合同 4月23日到期，需联系续签
- 服务器 SSL 证书 4月25日过期

## 长期
- 每月 1 号提交月报
- 每季度末更新安全检查清单
```

**文件：** `/root/morning-briefing/reading-list.md`

```markdown
# 推荐阅读池

未读：
- 《Agent 设计模式最佳实践》 https://example.com/agent-patterns
- 《2026 年 SEO 趋势报告》 https://example.com/seo-2026
- 《MCP 协议深度解析》 https://example.com/mcp-deep-dive
- 《Heartbeat 自动化实战》 https://example.com/heartbeat-guide
- 《SOUL.md 人格工程指南》 https://example.com/soul-engineering

已推荐：
（Agent 推荐过的文章会自动移到这里，避免重复）
```

---

## 六、Step 3：编写晨间执行官 SOUL.md

**文件路径：** `~/.openclaw/agents/morning/SOUL.md`

```markdown
# 晨间执行官

## 身份
你是一个高效的个人执行助理。每天早上你的职责是收集多源信息，
生成一条结构化的晨间简报，帮助用户快速掌握今日要点。

## 简报生成流程

每次被 Heartbeat 触发时，严格按以下顺序执行：

### 1. 读取配置
- 读取 /root/morning-briefing/config.json 获取模块配置
- 只处理 enabled: true 的模块

### 2. 天气模块
- 优先用 fetch 工具请求和风天气 API（国内稳定）
- 如果和风天气不可用，回退到 wttr.in
- 提取：当前温度、天气状况、今日最高/最低温、是否需要带伞
- 格式：🌤 天气：{城市} {温度}°C {状况}，{建议}

### 3. 日历模块
- 读取 calendar.md，找到今天日期对应的日程
- 按时间排序，标注会议方式（腾讯会议/企微群视频/线下）
- 如果今天无日程，显示"今日无安排"
- 格式：📅 今日日程（N 项）

### 4. 提醒模块
- 读取 reminders.md
- 筛选出 3 天内到期的提醒（含今天）
- 按紧急程度排序
- 格式：⚡ 关键提醒

### 5. 行业热点模块
- 用 fetch 工具抓取配置中的 RSS/新闻源
- 筛选最近 24 小时内的文章
- 如果配置了 filter 关键词，优先匹配相关文章
- 选取最多 3 条，每条一行标题摘要
- 格式：📰 行业热点（N 条）

### 6. 推荐阅读模块
- 读取 reading-list.md 的"未读"部分
- 随机选取 1-2 篇
- 将选中的文章从"未读"移到"已推荐"
- 格式：📖 推荐阅读

### 7. 每日一句
- 生成一句简短有力的中文句子
- 风格：偏向行动、专注、积极
- 不要鸡汤，要有力量感
- 格式：💪 今日一句

### 8. 组装并发送
- 将所有模块按上述顺序组装为一条消息
- 使用 emoji 分隔各模块，保持视觉清晰
- 直接发送给用户（通过当前 IM 渠道）

## 格式模板

☀️ 晨间简报 · {月}月{日}日 {星期}

🌤 天气：{内容}

📅 今日日程（{N} 项）：
· {时间} {事项}（{备注}）

⚡ 关键提醒：
· {提醒内容}

📰 行业热点：
· {标题} — {一句话摘要}

📖 推荐阅读：
· 《{标题}》{链接}

💪 今日一句：
"{句子}"

## 行为准则
- 简洁至上，每个模块不超过 3-5 行
- 如果某个数据源获取失败，跳过该模块，不要报错给用户
- 整条简报控制在手机一屏能看完的长度
- 语气轻松专业，像一个靠谱的助理在汇报
```

---

## 七、Step 4：配置 Heartbeat 定时触发

编辑 `~/.openclaw/openclaw.json`，添加 Heartbeat 任务：

```json
{
    "heartbeat": {
        "enabled": true,
        "tasks": [
            {
                "name": "晨间简报",
                "cron": "0 7 * * *",
                "agent": "morning",
                "prompt": "现在是早上 7 点，请执行晨间简报流程：读取 /root/morning-briefing/config.json 配置，按照 SOUL.md 中定义的流程逐步收集天气、日程、提醒、行业热点、推荐阅读，组装为结构化简报发送给我。"
            }
        ]
    }
}
```

### 时间调整

| 场景 | Cron 表达式 | 说明 |
|------|-----------|------|
| 早起型 | `0 6 * * *` | 每天 6:00 |
| 标准型 | `0 7 * * *` | 每天 7:00（推荐） |
| 仅工作日 | `0 7 * * 1-5` | 周一到周五 7:00 |
| 早晚双推 | `0 7 * * *` + `0 22 * * *` | 早 7 点简报 + 晚 10 点回顾 |

---

## 八、Step 5：添加晚间回顾（可选）

形成"早晚闭环"：

```json
{
    "name": "晚间回顾",
    "cron": "0 22 * * *",
    "agent": "morning",
    "prompt": "现在是晚上 10 点，请生成今日回顾：\n1. 读取今早的日程，标注哪些已完成、哪些未完成\n2. 检查提醒事项的完成情况\n3. 提前预览明天的日程\n4. 生成简短的晚间回顾发送给我\n\n格式：\n🌙 今日回顾 · {日期}\n✅ 已完成：...\n⏳ 未完成：...\n📅 明日预览：...\n💤 晚安提醒：{一句话}"
}
```

---

## 九、Step 6：手动测试

```bash
mkdir -p /root/morning-briefing
# 将上面的 config.json、calendar.md、reminders.md、reading-list.md 写入该目录

rm ~/.openclaw/agents/main/agent/models.json
systemctl restart openclaw
```

在微信/企微中手动触发测试：

```
请立即执行一次晨间简报流程，按照 /root/morning-briefing/config.json 的配置生成今日简报。
```

### 验证清单

| 模块 | 验证点 |
|------|--------|
| 天气 | 能正确获取你所在城市的天气（优先和风天气，备用 wttr.in） |
| 日程 | 能读取 calendar.md 并匹配今天日期 |
| 提醒 | 能筛选出近期到期的提醒 |
| 热点 | 能抓取 InfoQ 中文站/开源中国/36氪 的 RSS |
| 阅读 | 能从阅读池中选取并标记已推荐 |
| 格式 | 整体简报结构清晰，一屏可读 |

---

## 十、进阶玩法

### 10.1 接入企微日历实现全自动日程

通过 fetch MCP 调用企微开放平台 API，不再手动维护 calendar.md：

```
企微管理后台 → 应用管理 → 自建应用 → 开启日历权限
→ 获取 corpid 和 corpsecret
→ Agent 通过 fetch 调用企微日历 API 获取日程
```

在 SOUL.md 中日历模块改为：
```
### 3. 日历模块
- 通过 fetch 调用企微日历 API 获取今天的所有事件
- 如果 API 不可用，回退到读取 calendar.md
```

### 10.2 健康数据整合

如果你使用小米手环/华为手表等设备，可以通过导出数据文件接入：

```
在简报中增加：
🏃 健康数据：
· 昨日步数：8,432 步
· 睡眠时长：7h 23min（深睡 2h 10min）
· 静息心率：62 bpm
```

### 10.3 团队版晨间简报

参考 Interactive Studio 的做法，为团队每个成员生成个性化简报：

```json
{
    "heartbeat": {
        "tasks": [
            {
                "name": "团队晨间简报-产品组",
                "cron": "0 7 * * 1-5",
                "agent": "morning",
                "prompt": "为产品组生成晨间简报，重点关注：产品需求进度、用户反馈、竞品动态"
            },
            {
                "name": "团队晨间简报-工程组",
                "cron": "0 7 * * 1-5",
                "agent": "morning",
                "prompt": "为工程组生成晨间简报，重点关注：线上告警、PR 待审、技术债务"
            }
        ]
    }
}
```

---

## 十一、成本估算

| 项目 | 消耗 |
|------|------|
| 每次简报 Token | 约 2,000-4,000 tokens（含数据抓取和生成） |
| 每月消耗（每天 1 次） | 约 60,000-120,000 tokens |
| 火山引擎 Coding Plan | Lite 套餐完全覆盖，几乎零额外成本 |

> 晨间简报是 Coding Plan 包月模式下最划算的场景之一——每天固定消耗，成本可预测。

---

## 十二、常见问题

| 问题 | 解决方案 |
|------|---------|
| 天气获取失败 | 优先用和风天气（https://dev.qweather.com，免费 1000 次/天）；wttr.in 作为备用 |
| npx 下载超时 | 配置淘宝镜像：`npm config set registry https://registry.npmmirror.com` |
| RSS 抓取为空 | 部分网站 RSS 有反爬，用 fetch 工具直接抓取网页再提取 |
| 简报太长 | 在 SOUL.md 中强调"一屏可读"，减少每个模块的条目数 |
| 推送时间不准 | 检查服务器时区：`timedatectl set-timezone Asia/Shanghai` |
| 周末不想收 | Cron 改为 `0 7 * * 1-5`（仅工作日） |
| 想增加模块 | 在 config.json 中添加新模块，在 SOUL.md 中添加对应处理流程 |

---

## 十三、安全加固

晨间简报虽然是轻量场景，但涉及定时自动执行和外部 API 调用，仍需注意安全。

### 必须完成

- [ ] filesystem MCP 路径限制为 `/root/morning-briefing`，不开放其他目录
- [ ] SOUL.md 中包含安全边界（禁止访问内网地址、禁止输出 API Key）
- [ ] Heartbeat 频率合理（每天 1-2 次，不要每分钟触发）
- [ ] 和风天气 API Key 存放在 `/opt/openclaw.env` 中，权限 600
- [ ] config.json 中不包含任何真实密码或 Token

### SOUL.md 安全边界模板

在晨间执行官的 SOUL.md 末尾添加：

```markdown
## 安全边界（不可违反）
- 不得将 API Key、密码、Token 等凭证输出到简报消息中
- 不得访问 /root/morning-briefing 以外的目录
- 不得通过 fetch 访问内网地址（127.0.0.1、10.x.x.x、192.168.x.x）
- 如果某个数据源获取失败，跳过该模块，不要无限重试
- 简报中不暴露敏感信息（如合同金额、具体密码、内部系统地址）
```

### 紧急停止

如果简报内容异常或 Agent 行为失控：

```bash
# 停止 Heartbeat
openclaw config set heartbeat.enabled false
sudo systemctl restart openclaw

# 或直接停止服务
sudo systemctl stop openclaw
```

> 完整的安全加固清单见 [Agent 自动化安全加固清单](../openclaw-infra/checklists/agent-security-checklist.md)。
