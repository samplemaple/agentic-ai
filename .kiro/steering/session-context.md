---
inclusion: auto
---

# 晨间执行官项目 - 当前配置快照

## 项目状态：已部署，main 直接执行定时任务（workaround），子 Agent 投递问题待解决

## 当前生效的定时任务

| 名称 | ID | Agent | cron | 时区 | 模型 | 超时 |
|------|-----|-------|------|------|------|------|
| 晨间简报 | 7506dd61-0135-4f1f-9f6f-a0daadbb9643 | main | 0 6 * * * | Asia/Shanghai | custom-api-deepseek-com/deepseek-chat | 600s |
| 晚间简报 | c7176611-6980-4528-a067-0f815f99b413 | main | 0 19 * * * | Asia/Shanghai | openai/deepseek-reasoner | 600s |

两个任务都用 main Agent 执行（workaround），因为子 Agent 无法投递到微信。

## Agent 列表

| Agent | 状态 | 渠道绑定 | 用途 |
|-------|------|---------|------|
| main | 默认 Agent | openclaw-weixin + wecom | 路由 + 定时任务执行 |
| morning | 子 Agent | 无绑定 | sessions_spawn 实时路由（定时任务暂未使用） |

## 关键文件路径（服务器）

| 文件 | 路径 |
|------|------|
| main SOUL.md | ~/.openclaw/workspace/SOUL.md |
| morning SOUL.md | ~/.openclaw/workspace/morning/SOUL.md + ~/.openclaw/agents/morning/SOUL.md |
| main models.json | ~/.openclaw/agents/main/agent/models.json |
| morning models.json | ~/.openclaw/agents/morning/agent/models.json |
| openclaw.json | ~/.openclaw/openclaw.json |
| 数据文件 | /root/morning-briefing/（config.json, calendar.md, reminders.md, reading-list.md） |

## openclaw.json 关键配置

```
agents.defaults.subagents.allowAgents = ["morning"]
agents.defaults.model.primary = "custom-api-deepseek-com/deepseek-reasoner"
models.providers.custom-api-deepseek-com: deepseek-chat + deepseek-reasoner（contextWindow: 64000）
```

## 晨间简报 prompt（当前生效）

```
执行晨间简报流程：
1. 读取 /root/morning-briefing/config.json 获取配置
2. 请求天气 API：先尝试和风天气，失败则用 wttr.in
3. 读取 calendar.md，匹配今天日期的日程
4. 读取 reminders.md，筛选 3 天内到期的提醒
5. 通过 fetch 抓取南京今日油价（92号、95号、下次调整预计涨跌）
6. 生成一句不超过 30 个汉字的中文短句
7. 按照 ☀️晨间简报 · 月日星期 格式，emoji 分隔（🌤📅⚡⛽💪）
失败的模块跳过。只输出简报内容。
```

## 晚间日报 prompt（当前生效）

```
先读取 config.json 中 schedule.weeklyReportDay 字段。
周报日：三段式周报（本周总结/下周目标/周学习）
非周报日：晚间日报（已完成/未完成/明日预览/晚安提醒）
只输出报告内容。
```

## 待解决问题

1. 子 Agent（morning）定时任务无法投递到微信（详见 openclaw-multi-agent/morning-delivery-issue.md）
2. 100% ctx 问题（已加 --light-context 缓解）
