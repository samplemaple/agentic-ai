

# 晨间执行官项目 - 当前配置快照

## 项目状态：已部署，数据源已更新，投递问题待验证

## 本次 Session 完成的工作

### 1. 天气数据源更新
- 和风天气 API 返回 403 → 替换为 Open-Meteo（免费、无需 key）
- config.json 新增 `lat: "32.06"` 和 `lon: "118.78"`（南京坐标）
- SOUL.md 补充了 WMO weather_code 解读规则和降水概率带伞逻辑
- wttr.in 保留作为 fallback

### 2. 油价数据源更新
- 原数据源全部失效：qiyoujiage.com（SSL 证书过期）、chemcp.com 和 oil.usd-cny.com（连接超时）
- 改为三级降级策略：m.qiyoujiage.com → cngold.org → 搜索引擎
- "下次调整日期、预计涨跌"改为可选项，避免 Agent 编造

### 3. Cron message 优化
- 加入油价 URL 内联，避免 Agent 去翻 SOUL.md
- 加入禁止中间输出的强约束（禁止"我将""首先""现在"等）
- 加了 `--expect-final` 参数

### 4. 服务崩溃循环修复
- 发现 pid 222889 僵尸进程占用 18789 端口，导致 systemd 服务崩溃循环（restart counter 到 5900+）
- 按 troubleshooting.md Q1 步骤修复：kill 僵尸进程 + 禁用用户级服务 + 重启

## 待验证

- 微信投递是否正常（服务刚恢复，需要 `openclaw cron run 7506dd61-0135-4f1f-9f6f-a0daadbb9643` 测试）

## 当前生效的定时任务

| 名称 | ID | Agent | cron | 时区 | 模型 |
|------|-----|-------|------|------|------|
| 晨间简报 | 7506dd61-0135-4f1f-9f6f-a0daadbb9643 | main | 0 6 * * * | Asia/Shanghai | custom-api-deepseek-com/deepseek-chat |
| 晚间简报 | c7176611-6980-4528-a067-0f815f99b413 | main | 0 19 * * * | Asia/Shanghai | openai/deepseek-reasoner |

## 晨间简报 message（当前生效）

```
你是晨间执行官。严格执行以下流程，全程禁止输出任何中间状态、思考过程或执行说明。只在最后一步输出一条完整的简报消息。

流程：
1. 读取 /root/morning-briefing/config.json 获取配置
2. 请求天气 API：先尝试 Open-Meteo（用 config 中的经纬度），失败则用 wttr.in
3. 读取 /root/morning-briefing/calendar.md，匹配今天日期的日程
4. 读取 /root/morning-briefing/reminders.md，筛选 3 天内到期的提醒
5. 油价：依次尝试 fetch https://m.qiyoujiage.com/jiangsu.shtml 和 https://www.cngold.org/crude/jiangsu.html 提取江苏92/95号油价，都失败则搜索"江苏 今日油价 92号 95号"
6. 生成一句不超过 30 个汉字的中文短句（偏向行动和专注）
7. 按照 ☀️晨间简报 · 月日星期 的格式，用 emoji 分隔各模块（🌤📅⚡⛽💪），组装为一条完整消息

重要规则：
- 禁止输出「我将」「首先」「现在」「让我」等执行过程描述
- 禁止在工具调用之间输出任何文字
- 失败的模块跳过
- 你的唯一输出就是最终的简报本身，不多不少
```

## 关键文件路径（服务器）

| 文件 | 路径 |
|------|------|
| config.json | /root/morning-briefing/config.json |
| morning SOUL.md | ~/.openclaw/workspace/morning/SOUL.md + ~/.openclaw/agents/morning/SOUL.md |
| openclaw.json | ~/.openclaw/openclaw.json |
| 数据文件 | /root/morning-briefing/（calendar.md, reminders.md, reading-list.md） |

## 待解决问题

1. 子 Agent（morning）定时任务无法投递到微信（详见 openclaw-multi-agent/morning-delivery-issue.md）
2. 100% ctx 问题（已加 --light-context 缓解）

## Token 优化（2026-04-21）

### SOUL.md 精简
- morning SOUL.md：~3000 字 → ~600 字（-80%），去掉油价模块
- main SOUL.md：~1500 字 → ~500 字（-67%）

### 工具限制（效果最显著）
- cron job 加 `--tools` 参数限制工具范围
- morning agent 在 openclaw.json 中配置 `tools.allow: ["read", "write", "fetch", "search"]`
- 全局删除 36 个飞书工具（tools.alsoAllow 中的 feishu_* 全部移除）

### 方案 D：文件中转投递
- 晨间简报：6:00 morning 生成写入 /tmp/morning-report.txt → 6:05 main 读取投递
- 晚间简报：19:00 morning 生成写入 /tmp/evening-report.txt → 19:05 main 读取投递

### 优化效果
- 优化前：~30,000 tokens/次
- 优化后：生成 ~3,000 + 投递 ~1,500 = ~4,500 tokens/次（-85%）

### 文件清理
- 删除 .env（含真实密码）、过时的 deploy/openclaw.json、setup 脚本、tests 目录
- main SOUL.md 统一在 openclaw-main/ 维护

## 新增 Steering 文件

- `.kiro/steering/openclaw-commands.md` - OpenClaw CLI 命令速查（cron edit 用 `--message` 不是 `--prompt`）
