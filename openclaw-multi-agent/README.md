# OpenClaw 多 Agent 协作与路由调度

> 从单 Agent 到 Agent 军团：15+ Agent 各司其职，一键提升工作效率

---

## 一、什么是 Agent 军团？

Agent 军团不是一个"全能 Agent"，而是多个专职 Agent 组成的协作网络：

- 每个 Agent 有独立的人格（SOUL.md）、技能（Skills）和模型配置
- 路由 Agent 负责接收指令、判断意图、分发任务
- 专职 Agent 各自处理擅长的领域，互不干扰

**参考案例：** @jdrhyne 在 3 台机器上运行 15+ Agent，第一天清理 10,000 封消息，日常审查 122 页 Slides、重构 PR、优化广告投放、起草社交帖子。

---

## 二、架构设计

```
                    ┌──────────────────────┐
                    │    你（微信/企微）      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   路由 Agent（主入口）  │
                    │   模型：kimi-k2.5     │
                    │   职责：意图识别+分发   │
                    └──┬────┬────┬────┬────┘
                       │    │    │    │
          ┌────────────▼┐ ┌▼────▼┐ ┌▼───────────┐
          │ 代码 Agent   │ │ 内容 │ │ 数据分析    │  ...更多
          │ gpt-5.4     │ │Agent │ │ Agent      │
          │ 代码审查     │ │写作  │ │ 报表/可视化 │
          │ PR 重构      │ │社媒  │ │ 流量分析   │
          └─────────────┘ └──────┘ └────────────┘
```

### 部署拓扑（推荐）

| 机器 | Agent | 说明 |
|------|-------|------|
| 服务器 1（主） | 路由 Agent + 日常助手 | 入口，轻量任务 |
| 服务器 2 | 代码 Agent + DevOps Agent | 重计算任务，用旗舰模型 |
| 服务器 3 | 内容 Agent + 数据 Agent | 写作、分析、定时任务 |

> 单台服务器也可以跑多个 Agent（通过不同端口），3 台只是为了隔离负载。

---

## 三、实战：创建你的第一个 Agent 军团

### 3.1 规划你的 Agent 清单

先想清楚你需要哪些 Agent。以下是一个适合国内用户的参考清单：

| # | Agent 名称 | 职责 | 推荐模型 | 关键 Skills |
|---|-----------|------|---------|------------|
| 1 | 路由 Agent | 意图识别、任务分发 | kimi-k2.5（快+便宜） | 无（纯提示词） |
| 2 | 代码 Agent | 代码审查、PR 重构、Bug 修复 | gpt-5.4 / claude-opus-4-6 | Gitee/GitHub MCP |
| 3 | 写作 Agent | 社媒帖子、公众号文案、文档 | kimi-k2.5 | 无 |
| 4 | 数据 Agent | 百度统计/友盟分析、报表生成 | deepseek-v3.2 | fetch MCP |
| 5 | 消息 Agent | 企微消息分类、批量回复、清理 | kimi-k2.5 | 企微 MCP |
| 6 | 日程 Agent | 会议安排、提醒、日程冲突检测 | kimi-k2.5 | 企微日历 API |
| 7 | 运维 Agent | 服务器监控、告警、自动修复 | deepseek-v3.2 | Shell 执行 |

### 3.2 创建多 Agent 配置

编辑 `~/.openclaw/openclaw.json`，在 `agents` 节点下定义多个 Agent：

```json
{
    "agents": {
        "defaults": {
            "model": "volcengine/kimi-k2.5",
            "memorySearch": {
                "provider": "openai",
                "model": "doubao-embedding-vision",
                "remote": {
                    "baseUrl": "https://ark.cn-beijing.volces.com/api/coding/v3",
                    "apiKey": "你的API Key"
                }
            }
        },
        "instances": {
            "main": {
                "name": "路由助手",
                "model": "volcengine/kimi-k2.5",
                "soul": "你是一个智能路由助手。根据用户的意图，将任务分发给合适的专职 Agent。"
            },
            "coder": {
                "name": "代码专家",
                "model": "hotai/gpt-5.4",
                "soul": "你是一个资深软件工程师。专注于代码审查、重构建议和 Bug 修复。"
            },
            "writer": {
                "name": "内容创作者",
                "model": "volcengine/kimi-k2.5",
                "soul": "你是一个专业的内容创作者。擅长社交媒体文案、公众号文章和文档编辑。"
            },
            "analyst": {
                "name": "数据分析师",
                "model": "volcengine/deepseek-v3.2",
                "soul": "你是一个数据分析专家。擅长数据解读、报表生成和趋势分析。"
            }
        }
    }
}
```

### 3.3 为每个 Agent 编写 SOUL.md

每个 Agent 需要一个独立的人格文件。在 `~/.openclaw/agents/<agent-name>/` 目录下创建：

**路由 Agent（~/.openclaw/agents/main/SOUL.md）：**

```markdown
# 路由助手

## 身份
你是一个智能任务路由器。你的职责是理解用户意图，将任务分发给最合适的专职 Agent。

## 路由规则
- 代码相关（审查、重构、Bug）→ /agent coder
- 写作相关（文案、公众号、社媒）→ /agent writer
- 数据相关（分析、报表、流量）→ /agent analyst
- 日常对话、不确定的 → 自己处理

## 行为准则
- 收到任务后，先判断类别，告诉用户"已转交给 XX Agent"
- 如果任务跨多个领域，拆分后分别转交
- 保持简洁，不要啰嗦
```

**代码 Agent（~/.openclaw/agents/coder/SOUL.md）：**

```markdown
# 代码专家

## 身份
你是一个资深全栈工程师，拥有 10 年以上开发经验。

## 能力范围
- 代码审查：发现潜在 Bug、性能问题、安全漏洞
- 重构建议：提供更优雅的实现方案
- PR Review：逐文件审查，给出 approve/request changes 建议
- 技术方案：架构设计、技术选型建议

## 工作风格
- 直接指出问题，不绕弯子
- 给出具体的修改建议和代码示例
- 关注安全性和性能
- 使用中文回复，代码注释用中文
```

**写作 Agent（~/.openclaw/agents/writer/SOUL.md）：**

```markdown
# 内容创作者

## 身份
你是一个专业的内容创作者，擅长多种文体和平台风格。

## 能力范围
- 社交媒体：微博、小红书、抖音文案风格的短内容
- 公众号文章：深度长文、行业分析、教程类内容
- 文档编辑：技术文档、产品说明、会议纪要
- 翻译润色：中英互译，保持语感自然

## 工作风格
- 根据平台调整语气和格式
- 提供 2-3 个版本供选择
- 注意 SEO 关键词（如果适用）
```

### 3.4 为 Agent 配置 Skills（MCP 工具）

Skills 是 Agent 的"手"——让 Agent 能操作外部系统。通过 MCP（Model Context Protocol）接入。

> ⚠️ 国内服务器先配置 npm 淘宝镜像，否则 npx 下载可能超时：
> ```bash
> npm config set registry https://registry.npmmirror.com
> ```

```json
{
    "mcpServers": {
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxx"
            }
        },
        "fetch": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-fetch"]
        },
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/data"]
        }
    }
}
```

> fetch MCP 是万能工具——可以调用百度统计 API、友盟 API、企微开放平台 API 等任何 HTTP 接口，不需要专门的 MCP 插件。

### 3.5 配置 Heartbeat（定时自动化）

Heartbeat 让 Agent 定时执行任务，无需人工触发：

```json
{
    "heartbeat": {
        "enabled": true,
        "tasks": [
            {
                "name": "每日消息摘要",
                "cron": "0 8 * * *",
                "agent": "main",
                "prompt": "检查今天的未处理消息，生成摘要发给我"
            },
            {
                "name": "每周数据报告",
                "cron": "0 9 * * 1",
                "agent": "analyst",
                "prompt": "生成上周的网站流量报告，包含关键指标变化和趋势分析"
            },
            {
                "name": "每日代码审查",
                "cron": "0 10 * * *",
                "agent": "coder",
                "prompt": "检查代码仓库上待审查的 PR，给出审查意见"
            }
        ]
    }
}
```

---

## 四、扩展到多台机器

当单台服务器负载过高，或你需要隔离不同类型的任务时，可以扩展到多台机器。

### 4.1 多机部署方案

每台机器独立运行一个 OpenClaw 实例，通过 Tailscale 组网：

```
┌─────────────────────────────────────────────────────┐
│                  Tailscale 私有网络                    │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ 服务器 1      │  │ 服务器 2      │  │ 服务器 3     │ │
│  │ 路由+日常     │  │ 代码+运维     │  │ 内容+数据    │ │
│  │ :18789       │  │ :18789       │  │ :18789      │ │
│  │ kimi-k2.5    │  │ gpt-5.4      │  │ deepseek    │ │
│  └──────────────┘  └──────────────┘  └─────────────┘ │
│                                                       │
│  所有机器通过 Tailscale 互通，零公网暴露                  │
└─────────────────────────────────────────────────────┘
```

### 4.2 部署步骤

每台新机器重复基础设施部署流程：

```bash
# 在新机器上执行（参考 openclaw-infra/scripts/setup-openclaw.sh）
git clone https://github.com/DjangoPeng/agentic-ai.git
cd agentic-ai/openclaw-infra
chmod +x scripts/setup-openclaw.sh
sudo scripts/setup-openclaw.sh
```

然后为每台机器配置不同的 Agent 实例和 SOUL.md。

---

## 五、成本控制策略

Agent 军团的 Token 消耗是单 Agent 的 N 倍，成本控制至关重要：

| 策略 | 说明 |
|------|------|
| 分层模型 | 路由/日常用 kimi-k2.5（包月），复杂任务用 gpt-5.4（按量） |
| Heartbeat 频率 | 定时任务不要太频繁，每日 1-2 次足够 |
| Token 预算 | 配置 `maxTokensPerDay` 防止失控 |
| 按需启用 | 不常用的 Agent 可以设为 disabled，需要时再开启 |
| Coding Plan | 火山引擎包月覆盖日常 80% 的调用 |

### 成本估算参考

| 规模 | Agent 数量 | 月成本估算 |
|------|-----------|-----------|
| 个人轻度 | 3-5 个 | Coding Plan Lite + Hotai ¥50 ≈ ¥100-150/月 |
| 个人重度 | 8-10 个 | Coding Plan Pro + Hotai ¥99 ≈ ¥200-300/月 |
| 小团队 | 15+ 个 | 多台服务器 + Pro + Hotai ¥198 ≈ ¥500-800/月 |

---

## 六、从零开始的推荐路线

### Phase 1：单 Agent 跑通（你已完成 ✅）
- [x] OpenClaw 部署 + Tailscale 穿透
- [x] 微信/企微接入
- [x] 模型配置（火山引擎 + Hotai）

### Phase 2：人格工程（1-2 天）
- [ ] 编写主 Agent 的 SOUL.md（定义人格、边界、行为准则）
- [ ] 测试不同提示词对 Agent 行为的影响
- [ ] 配置记忆（MEMORY.md）让 Agent 记住你的偏好

### Phase 3：技能扩展（2-3 天）
- [ ] 接入 1-2 个 MCP 工具（如 GitHub、文件系统）
- [ ] 编写自定义 Skill（如特定业务流程）
- [ ] 在 ClawHub 上发现和安装社区 Skills

### Phase 4：多 Agent 协作（3-5 天）
- [ ] 创建 2-3 个专职 Agent（代码、写作、数据）
- [ ] 配置路由 Agent 实现意图分发
- [ ] 测试 Agent 间的协作流程

### Phase 5：自动化（持续优化）
- [ ] 配置 Heartbeat 定时任务
- [ ] 设置监控和告警
- [ ] 根据使用情况调整模型和成本

---

## 七、注意事项

1. **循序渐进** — 不要一次性创建 15 个 Agent，从 2-3 个开始，跑通后再扩展
2. **SOUL.md 是核心** — Agent 的行为质量 80% 取决于 SOUL.md 的设计
3. **安全边界** — 每个 Agent 的权限要最小化，特别是有 Shell 执行能力的 Agent
4. **成本监控** — 多 Agent 的 Token 消耗会快速增长，务必设置预算上限
5. **日志审计** — 定期查看 Agent 的操作日志，确保行为符合预期

---

## 八、安全加固

Agent 军团涉及多个 Agent 并行运行、MCP 工具调用和 Heartbeat 定时执行，安全风险是单 Agent 的数倍。

> ⚠️ 开始构建 Agent 军团前，务必先通过 [基础安全检查清单](../openclaw-infra/checklists/security-checklist.md) 和 [Agent 自动化安全加固清单](../openclaw-infra/checklists/agent-security-checklist.md) 的全部项目。

### 8.1 权限最小化原则

每个 Agent 只开放它需要的 MCP 工具和目录：

| Agent | 允许的 MCP | 允许的目录 | 禁止 |
|-------|-----------|-----------|------|
| 路由 Agent | 无 | 无 | 不直接执行任务 |
| 代码 Agent | GitHub MCP | 代码仓库目录 | 不访问生产数据 |
| 写作 Agent | fetch | /root/content | 不执行 Shell |
| 数据 Agent | fetch | /root/analytics | 不写入文件系统 |
| 运维 Agent | Shell | /var/log | 不访问业务数据 |

### 8.2 所有 Agent 的 SOUL.md 必须包含安全边界

```markdown
## 安全边界（不可违反）
- 不得删除、修改或覆盖系统文件
- 不得访问 /etc、/opt、~/.ssh 等敏感目录
- 不得将 API Key、密码、Token 等凭证输出到消息中
- 不得访问内网地址（127.0.0.1、10.x.x.x、192.168.x.x、169.254.x.x）
- 遇到不确定的操作，先暂停并通知用户确认
```

### 8.3 Token 预算控制

```json
{
    "agents": {
        "defaults": {
            "maxTokensPerDay": 500000
        }
    }
}
```

### 8.4 紧急停止

```bash
# 停止所有 Agent
sudo systemctl stop openclaw

# 仅停止 Heartbeat 自动任务
openclaw config set heartbeat.enabled false
sudo systemctl restart openclaw
```

---

## 八、相关资源

| 资源 | 链接 |
|------|------|
| OpenClaw 基础设施部署 | [openclaw-infra/](../openclaw-infra/) |
| 微信接入 | [openclaw-im/wechat-clawbot.md](../openclaw-im/wechat-clawbot.md) |
| 企微接入 | [openclaw-im/wecom-bot.md](../openclaw-im/wecom-bot.md) |
| 火山引擎模型配置 | [openclaw-models/volcengine-coding-plan.md](../openclaw-models/volcengine-coding-plan.md) |
| Hotai 海外模型 | [openclaw-models/hotai-api.md](../openclaw-models/hotai-api.md) |
| 安全检查清单 | [openclaw-infra/checklists/security-checklist.md](../openclaw-infra/checklists/security-checklist.md) |

### 实战案例

| 案例 | 链接 | 说明 |
|------|------|------|
| 晨间执行官 | [openclaw-morning-briefing/](../openclaw-morning-briefing/) | 每日自动简报，一条消息开启高效率生活 |
| SEO 内容流水线 | [openclaw-seo-pipeline/](../openclaw-seo-pipeline/) | 竞品爬取→内容生成→自动发布，零人工干预 |
