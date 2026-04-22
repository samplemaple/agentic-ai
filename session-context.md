# Agentic AI 项目 - 总状态快照

最后更新：2026-04-22（晚）

---

## 基础设施

| 项目 | 值 |
|------|---|
| 服务器 | OpenClaw 2026.4.15，Ubuntu Linux |
| Tailscale IP | 100.69.216.12 |
| SSH 连接 | `ssh root@100.69.216.12`（走 Tailscale 隧道，公网 22 端口已关闭） |
| 控制台 | `ssh -L 18789:127.0.0.1:18789 root@100.69.216.12` → `http://localhost:18789` |
| Tailscale Serve | 已开启，但浏览器直连有问题（可能是代理工具拦截），用 SSH 端口转发替代 |
| DNS | Tailscale MagicDNS + 全局 fallback（223.5.5.5, 8.8.8.8） |
| 微信 ClawBot | ✅ 连接正常 |
| 模型 | DeepSeek Chat + DeepSeek Reasoner（直连 api.deepseek.com，按量计费） |
| contextWindow | 64,000（模型支持 128k，当前保守设置） |

## Agent 列表（3 个）

| Agent | 用途 | tools.allow | skills | 状态 |
|-------|------|------------|--------|------|
| main | 路由助手 + 投递 | read, edit, write, exec, process, message, web_fetch, memory_search, memory_get, agents_list, sessions_spawn, sessions_send, sessions_list, subagents（14 个） | weather, healthcheck | ✅ |
| morning | 晨间执行官 | read, write, fetch, search | 无 | ✅ |
| wechat-writer | 公众号创作者 | read, write, web_fetch, exec | 无 | ✅ 新建 |

子 Agent 调度权限：`allowAgents: ["morning", "wechat-writer"]`

## 定时任务（6 个）

| 任务 | ID | Agent | cron | 模型 | 状态 | 说明 |
|------|-----|-------|------|------|------|------|
| 晨间简报生成 | `7506dd61-...` | morning | 0 6 * * * | deepseek-chat | ✅ 运行中 | 写入 /tmp/morning-report.txt |
| 晨间简报投递 | `41206a6a-...` | main | 5 6 * * * | deepseek-chat | ✅ 运行中 | 读取 /tmp 投递微信 |
| 晚间简报生成 | `c7176611-...` | morning | 0 19 * * * | deepseek-reasoner | ✅ 运行中 | 写入 /tmp/evening-report.txt |
| 晚间简报投递 | `434a5e43-...` | main | 5 19 * * * | deepseek-chat | ✅ 运行中 | 读取 /tmp 投递微信 |
| 公众号文章生成 | `dd1b9916-...` | wechat-writer | 0 8 * * * | deepseek-chat | ⏸️ 已禁用 | 3 篇 .md → /tmp/wechat-articles/ |
| 公众号文章邮件 | `a29157e8-...` | main | 10 8 * * * | deepseek-chat | ⏸️ 已禁用 | 读取 .md 附件发邮件 |

> 公众号定时任务于 2026-04-22 手动禁用，聚焦智能客服方向。恢复命令：
> `openclaw cron edit dd1b9916-... --enable && openclaw cron edit a29157e8-... --enable`

## 项目模块状态

### ✅ 已完成
| 模块 | 说明 |
|------|------|
| openclaw-infra | 部署、Tailscale、安全加固、排错指南 |
| openclaw-im | 微信 ClawBot + 企微接入指南 |
| openclaw-models | 火山引擎 Coding Plan + Hotai 海外模型 |
| openclaw-multi-agent | Agent 军团架构、路由调度、构建经验 |
| openclaw-morning-briefing | 晨间/晚间简报，已部署运行 |
| openclaw-seo-pipeline | SEO 内容流水线文档（未部署） |
| openclaw-wechat-writer | 公众号 AI 内容流水线，定时任务已暂停 |

### 🚧 开发中
| 模块 | 说明 |
|------|------|
| openclaw-cs-agent | 智能客服 Agent：RAG + 多轮对话 + 工具调用 + 转人工（变现方向 A） |

### ❌ 未开发
| 模块 | 说明 |
|------|------|
| openclaw-soul | 人格工程：SOUL.md 设计与调教 |
| openclaw-heartbeat | 心跳引擎：Heartbeat 定时自动化 |
| openclaw-skills | 技能开发：Skills 编写与 ClawHub 生态 |
| claude-code | Claude Code CLI 深度实战 |

## 本地 ↔ 服务器文件映射

| 本地路径 | 服务器路径 |
|---------|-----------|
| `openclaw-morning-briefing/deploy/agents/main/SOUL.md` | `~/.openclaw/workspace/SOUL.md` + `~/.openclaw/agents/main/SOUL.md` |
| `openclaw-morning-briefing/deploy/agents/morning/SOUL.md` | `~/.openclaw/workspace/morning/SOUL.md` + `~/.openclaw/agents/morning/SOUL.md` |
| `openclaw-morning-briefing/deploy/morning-briefing/*` | `/root/morning-briefing/` |
| `openclaw-wechat-writer/deploy/agents/wechat-writer/SOUL.md` | `~/.openclaw/workspace/wechat-writer/SOUL.md` + `~/.openclaw/agents/wechat-writer/SOUL.md` |
| `openclaw-wechat-writer/deploy/scripts/send-articles.py` | `~/.openclaw/scripts/send-articles.py` |

SOUL.md 在服务器上有两份（workspace + agents），更新后需要同步：
```bash
scp <本地文件> root@100.69.216.12:~/.openclaw/workspace/<agent-id>/SOUL.md
ssh root@100.69.216.12 "cp ~/.openclaw/workspace/<agent-id>/SOUL.md ~/.openclaw/agents/<agent-id>/SOUL.md"
```

## 关键配置文件（服务器）

| 文件 | 路径 | 说明 |
|------|------|------|
| 全局配置 | ~/.openclaw/openclaw.json | Agent 列表、模型、工具 |
| SMTP 凭证 | ~/.openclaw/wechat-writer-smtp.env | 163 邮箱 SMTP（权限 600） |
| 文章历史 | /tmp/wechat-articles/history.txt | 防重复话题 |
| 简报数据 | /root/morning-briefing/ | config.json, calendar.md, reminders.md |

## Steering 文件

| 文件 | inclusion | 说明 |
|------|-----------|------|
| openclaw-commands.md | auto | CLI 命令速查 + 6 个 cron job ID |
| agent-building-guide.md | manual | Token 优化、工具精简、配置生效方式、踩坑 |
| server-deploy.md | manual | 连接方式、Tailscale 网络、路径映射 |
| chinese-response.md | auto | 所有回复使用中文 |

## 月费估算

| 项目 | 月费 | 状态 |
|------|------|------|
| 晨间/晚间简报 | ~¥3 | ✅ 运行中 |
| 公众号文章（3 篇/天） | ~¥1.9 | ⏸️ 已暂停 |
| 日常对话 | ~¥2-5 | ✅ |
| **总计（当前）** | **约 ¥5-8/月** | |

## 变现方向规划

### 🔥 方向 A：智能客服 Agent（当前推进）

目标：将已有的 hmsdkbot 智能客服系统（14 容器 Docker Compose）通用化，变成可交付给企业客户的商业产品。

已有基础（hmsdkbot，路径 D:\HMProject\HmCloudApp_Copy\HmCloudApp\hmsdkbot）：
- Dify Chatflow 工作流（意图识别 + GraphRAG + LLM 路由）
- Neo4j 图谱（13,817 节点）+ Qdrant 向量（8,180 条）+ BGE-M3 本地 Embedding
- 企微适配器 + 访问控制 + 反馈收集 + 管理后台（Vue3）
- 100 题质量测试 98% 通过率，131 个单元测试
- 知识库构建流水线（code-parser + doc-parser + knowledge-indexer + LLM 语义提取）

需要做的改造：
1. 知识库通用化：支持客户上传任意 PDF/Word/MD，自动构建（5-7 天）
2. 多租户支持：Qdrant/Neo4j 按 tenant_id 隔离（3-5 天）
3. Demo + 交付模板：通用场景演示 + 客户交付文档（3-5 天）
4. 企微联调上线（2-3 天）

定价：搭建费 ¥8,000-15,000 + 月维护 ¥1,000-2,000
详细方案：openclaw-cs-agent/README.md
服务器配置：openclaw-cs-agent/server-requirements.md

关键技术决策：
- BGE-M3 本地推理 → 替换为硅基流动 Qwen3-Embedding-0.6B API
  - 效果更好（MMTEB 64.33 vs 59.56，同 0.6B 参数同 1024 维度）
  - 延迟增加 ~100-200ms（总链路 30 秒中可忽略）
  - 省 1.2GB 内存 + 10.6GB 磁盘，服务器从 4C16G 降到 4C8G
  - API 月费 <¥1，服务器月省 ¥100-150
- Neo4j 本地容器 → 迁移到 Neo4j AuraDB Free
  - 数据量仅 13,817 节点（免费额度 200K 的 7%）
  - 延迟增加 ~100-400ms（总链路 30 秒中 <2%）
  - 省 832MB 内存 + 1.5GB 磁盘，减少 1 个容器
  - Cypher 100% 兼容，只改连接地址
- 两项优化合计：省 2GB 内存 + 12GB 磁盘，17 容器→15 容器
- 优化后服务器：最低 2C4G（¥80-120/月），推荐 4C8G（¥150-250/月）

状态：🚧 规划完成，待开发

### 📝 方向 B：内容运营 Agent 升级版

目标：将 wechat-writer 从"定时写文章"升级为有策略的内容运营系统。

核心能力：
- 热点感知：自动抓取行业热点，判断是否值得写
- 选题规划：基于历史数据和热点规划选题（非随机生成）
- 内容质检：事实准确性、SEO 优化、可读性评分
- 效果反馈闭环：读取阅读数据 → 分析效果 → 调整策略

状态：⏳ 待开发

### 🧑‍💻 方向 C：个人效率 Agent

目标：真正的个人助理，超越简报推送。

核心能力：
- 邮件摘要 + 分类 + 建议回复
- GitHub/RSS 监控 → 过滤重要信息推送
- 日程冲突检测 + 自动协调
- 主题调研 → 多步搜索 → 整理报告

状态：⏳ 待开发

## 待优化

- [x] ~~公众号文章质量持续调优~~ → 定时任务已暂停，聚焦智能客服
- [ ] 监控首周定时任务运行情况（晨间/晚间简报）
- [ ] Tailscale Serve 浏览器直连排查（代理工具拦截）
- [ ] 公众号认证后切换 API 草稿箱模式（暂缓）
- [ ] contextWindow 切到 Coding Plan 后调大到 128k

## 智能客服项目文档索引

| 文件 | 说明 |
|------|------|
| openclaw-cs-agent/README.md | 方向 A 总方案：架构、改造计划、定价、竞争分析 |
| openclaw-cs-agent/server-requirements.md | 服务器配置：17 容器资源实测、云服务器选型、BGE-M3 优化方案 |

## 智能客服项目（hmsdkbot）关键信息

| 项目 | 值 |
|------|---|
| 本地路径 | D:\HMProject\HmCloudApp_Copy\HmCloudApp\hmsdkbot |
| 部署方式 | Docker Compose（17 个容器） |
| AI 引擎 | Dify Chatflow（意图识别 + GraphRAG + LLM 路由） |
| 知识库 | Neo4j（13,817 节点）+ Qdrant（8,190 向量）+ BGE-M3（1024 维） |
| 模型 | DeepSeek Chat / Reasoner（通过 Dify OpenAI-compatible 接入） |
| 质量 | 100 题 98% 通过率，131 个单元测试 |
| 知识库文档 | 21 个 MD 文件，~343,000 字符，~230,000 tokens |
| 状态文档 | hmsdkbot/SESSION_CONTEXT.md + hmsdkbot/data/知识库质量优化计划.md |
