# 需求文档：晨间执行官（Morning Briefing）

## 简介

晨间执行官是基于 OpenClaw 平台的每日自动简报系统。系统由 Heartbeat 定时触发，Agent 自动从多个数据源（天气、日历、提醒、新闻、阅读列表）收集信息，汇总为结构化简报，通过微信/企微 IM 渠道推送给用户。目标是让用户每天早上用一条消息快速掌握当日要点，提升个人效率。

## 术语表

- **Router_Agent**：路由 Agent（main），作为用户 IM 消息的主入口，负责意图识别和任务分发，将简报相关请求转交给 Briefing_Agent
- **Briefing_Agent**：晨间执行官 Agent（morning），作为专职 Agent，负责收集数据、生成简报并推送的核心执行单元
- **Heartbeat**：OpenClaw 平台的定时任务引擎，基于 cron 表达式触发 Agent 执行
- **MCP**：Model Context Protocol，模型上下文协议，Agent 通过 MCP 工具与外部系统交互
- **fetch_MCP**：基于 MCP 协议的 HTTP 请求工具，用于调用天气 API 和抓取 RSS 新闻源
- **filesystem_MCP**：基于 MCP 协议的文件系统工具，用于读写本地 Markdown 文件
- **Config_File**：位于 `/root/morning-briefing/config.json` 的配置文件，控制各模块的开关和数据源
- **SOUL_File**：Agent 的人格与行为定义文件（SOUL.md），包含简报生成流程和安全边界
- **IM_Channel**：即时通讯渠道，包括微信 ClawBot 和企业微信机器人
- **RSS_Source**：RSS 新闻订阅源，用于获取行业热点信息
- **Reading_Pool**：阅读推荐池，存储在 `reading-list.md` 中的待推荐文章列表
- **Ad_Hoc_Task**：临时任务，用户通过 IM 渠道随时发送给 Briefing_Agent，由 Agent 写入 calendar.md 或 reminders.md

## 需求

### 需求 1：定时触发简报生成

**用户故事：** 作为用户，我希望系统每天早上自动生成简报，这样我无需手动操作即可收到当日要点。

#### 验收标准

1. THE Heartbeat SHALL 按照 Config_File 中 schedule.morning 字段配置的 cron 表达式（默认每天 07:00 Asia/Shanghai 时区）触发 Briefing_Agent 执行简报生成流程
2. WHEN Heartbeat 触发 Briefing_Agent 时，THE Briefing_Agent SHALL 读取 Config_File 获取模块配置信息
3. WHEN Config_File 中某模块的 enabled 字段为 false 时，THE Briefing_Agent SHALL 跳过该模块的数据收集和输出
4. WHEN Config_File 不存在或格式无效时，THE Briefing_Agent SHALL 记录错误日志并终止本次简报生成

### 需求 2：天气数据收集

**用户故事：** 作为用户，我希望简报包含当日天气信息，这样我可以提前做好出行准备。

#### 验收标准

1. WHEN 天气模块启用时，THE Briefing_Agent SHALL 通过 fetch_MCP 请求和风天气 API 获取 Config_File 中指定城市的当前天气数据
2. WHEN 和风天气 API 请求失败时，THE Briefing_Agent SHALL 回退到 wttr.in 备用 API 获取天气数据
3. WHEN 天气数据获取成功时，THE Briefing_Agent SHALL 提取当前温度、天气状况和出行建议（如是否需要带伞）
4. IF 主备天气 API 均请求失败，THEN THE Briefing_Agent SHALL 跳过天气模块并继续生成其余模块的简报

### 需求 3：日历日程读取

**用户故事：** 作为用户，我希望简报包含今日日程安排，这样我可以快速了解当天的会议和事项。

#### 验收标准

1. WHEN 日历模块启用且数据源为 local 时，THE Briefing_Agent SHALL 通过 filesystem_MCP 读取 Config_File 中指定路径的日历 Markdown 文件
2. WHEN 日历文件读取成功时，THE Briefing_Agent SHALL 匹配当天日期对应的日程条目并按时间顺序排列
3. WHEN 当天无日程条目时，THE Briefing_Agent SHALL 在简报中显示"今日无安排"
4. IF 日历文件不存在或读取失败，THEN THE Briefing_Agent SHALL 跳过日历模块并继续生成其余模块的简报

### 需求 4：提醒事项筛选

**用户故事：** 作为用户，我希望简报包含近期到期的关键提醒，这样我不会遗漏重要截止日期。

#### 验收标准

1. WHEN 提醒模块启用时，THE Briefing_Agent SHALL 通过 filesystem_MCP 读取 Config_File 中指定路径的提醒 Markdown 文件
2. WHEN 提醒文件读取成功时，THE Briefing_Agent SHALL 筛选出 3 天内（含当天）到期的提醒条目
3. THE Briefing_Agent SHALL 按截止日期从近到远的顺序排列筛选后的提醒条目
4. IF 提醒文件不存在或读取失败，THEN THE Briefing_Agent SHALL 跳过提醒模块并继续生成其余模块的简报

### 需求 5：行业热点抓取

**用户故事：** 作为用户，我希望简报包含行业热点新闻，这样我可以快速了解行业动态。

#### 验收标准

1. WHEN 新闻模块启用时，THE Briefing_Agent SHALL 通过 fetch_MCP 逐一抓取 Config_File 中配置的 RSS_Source 列表
2. WHEN RSS_Source 配置了 filter 关键词时，THE Briefing_Agent SHALL 优先选取标题或摘要中包含关键词的文章
3. THE Briefing_Agent SHALL 从所有 RSS_Source 中选取最多 Config_File 中 maxItems 指定数量的文章条目
4. WHEN 某个 RSS_Source 抓取失败时，THE Briefing_Agent SHALL 跳过该源并继续处理其余 RSS_Source
5. IF 所有 RSS_Source 均抓取失败，THEN THE Briefing_Agent SHALL 跳过新闻模块并继续生成其余模块的简报

### 需求 6：推荐阅读选取

**用户故事：** 作为用户，我希望简报每天推荐几篇阅读内容，这样我可以持续学习和成长。

#### 验收标准

1. WHEN 阅读模块启用时，THE Briefing_Agent SHALL 通过 filesystem_MCP 读取 Config_File 中指定路径的 Reading_Pool 文件
2. WHEN Reading_Pool 文件读取成功时，THE Briefing_Agent SHALL 从"未读"部分随机选取最多 Config_File 中 maxItems 指定数量的文章
3. WHEN 文章被选取推荐后，THE Briefing_Agent SHALL 将该文章从 Reading_Pool 的"未读"部分移动到"已推荐"部分
4. WHEN Reading_Pool 的"未读"部分为空时，THE Briefing_Agent SHALL 在简报中显示"阅读池已空，请补充新文章"
5. IF Reading_Pool 文件不存在或读取失败，THEN THE Briefing_Agent SHALL 跳过阅读模块并继续生成其余模块的简报

### 需求 7：每日一句生成

**用户故事：** 作为用户，我希望简报包含一句激励性的话语，这样我可以以积极的心态开始新的一天。

#### 验收标准

1. WHEN 每日一句模块启用时，THE Briefing_Agent SHALL 根据 Config_File 中 quote.style 字段定义的风格生成一句中文短句
2. THE Briefing_Agent SHALL 确保生成的短句简短有力，不超过 30 个汉字

### 需求 8：简报组装与格式化

**用户故事：** 作为用户，我希望简报格式清晰、结构化，这样我可以在手机上快速浏览。

#### 验收标准

1. THE Briefing_Agent SHALL 按照天气、日程、提醒、热点、阅读、每日一句的固定顺序组装各模块内容
2. THE Briefing_Agent SHALL 使用 emoji 图标（🌤📅⚡📰📖💪）作为各模块的视觉分隔标识
3. THE Briefing_Agent SHALL 在简报顶部包含标题行，格式为"☀️ 晨间简报 · {月}月{日}日 {星期}"
4. THE Briefing_Agent SHALL 将整条简报控制在手机一屏可阅读的长度范围内，每个模块不超过 5 行

### 需求 9：简报推送

**用户故事：** 作为用户，我希望简报自动推送到我的微信或企微，这样我无需主动查看即可收到。

#### 验收标准

1. WHEN 简报组装完成后，THE Briefing_Agent SHALL 通过 Config_File 中 output.pushTo 指定的 IM_Channel 发送简报消息
2. IF 简报推送失败，THEN THE Briefing_Agent SHALL 记录推送失败的错误日志

### 需求 10：配置文件管理

**用户故事：** 作为用户，我希望通过配置文件灵活控制简报的模块和数据源，这样我可以根据个人需求定制简报内容。

#### 验收标准

1. THE Config_File SHALL 包含 user（用户信息）、modules（模块配置）和 output（输出配置）三个顶层字段
2. THE Config_File 中每个模块 SHALL 包含 enabled 布尔字段用于控制模块的启用和禁用
3. THE Config_File SHALL 使用 JSON 格式存储，位于 `/root/morning-briefing/config.json` 路径
4. THE Config_File SHALL 不包含任何真实的 API Key、密码或 Token 等凭证信息

### 需求 11：安全边界控制

**用户故事：** 作为系统管理员，我希望 Agent 的行为受到严格的安全约束，这样系统不会因自动化执行而产生安全风险。

#### 验收标准

1. THE filesystem_MCP SHALL 将文件访问路径限制为 `/root/morning-briefing` 目录
2. THE SOUL_File SHALL 包含安全边界规则，明确禁止 Briefing_Agent 访问内网地址（127.0.0.1、10.x.x.x、192.168.x.x、169.254.x.x）
3. THE SOUL_File SHALL 包含安全边界规则，明确禁止 Briefing_Agent 在简报消息中输出 API Key、密码或 Token 等凭证信息
4. THE Briefing_Agent SHALL 在数据源获取失败时跳过对应模块，不进行无限重试
5. THE Config_File 中引用的 API Key SHALL 存放在独立的环境变量文件中，该文件权限设置为 600

### 需求 12：路由 Agent 配置与任务分发

**用户故事：** 作为用户，我希望通过一个统一的 IM 入口与所有 Agent 交互，路由 Agent 自动识别我的意图并转交给对应的专职 Agent。

#### 验收标准

1. THE Router_Agent SHALL 作为 `main` Agent 实例注册，接收所有来自 IM_Channel 的用户消息
2. THE Router_Agent 的 SOUL_File SHALL 包含路由规则，将简报相关请求（如"生成简报"、"添加日程"、"添加提醒"）转交给 Briefing_Agent（`/agent morning`）
3. WHEN Router_Agent 将任务转交给 Briefing_Agent 时，THE Router_Agent SHALL 回复用户"已转交给晨间执行官"的确认消息
4. WHEN 用户发送的消息不属于任何专职 Agent 的职责范围时，THE Router_Agent SHALL 自行处理该消息
5. THE Router_Agent 的 SOUL_File SHALL 不包含任何 MCP 工具调用指令，路由 Agent 仅做意图识别和分发，不直接执行任务

### 需求 13：通过 IM 动态添加临时任务

**用户故事：** 作为用户，我希望随时通过微信/企微向 Agent 发送临时任务，Agent 自动写入日程或提醒文件，这样我不需要 SSH 登录服务器就能管理当天的安排。

#### 验收标准

1. WHEN 用户通过 IM_Channel 发送包含日程信息的消息时，THE Briefing_Agent SHALL 通过 filesystem_MCP 将该日程条目追加到 calendar.md 中对应日期的章节下
2. WHEN 用户通过 IM_Channel 发送包含提醒信息的消息时，THE Briefing_Agent SHALL 通过 filesystem_MCP 将该提醒条目追加到 reminders.md 的对应分组中
3. WHEN Briefing_Agent 成功写入日程或提醒后，THE Briefing_Agent SHALL 回复用户确认消息，包含写入的具体内容和生效时间
4. THE SOUL_File SHALL 包含临时任务识别规则，能够区分用户发送的是日程（含具体时间点）还是提醒（含截止日期）

### 需求 14：晚间日报

**用户故事：** 作为用户，我希望每天晚上收到一份当日工作回顾，这样我可以复盘当天的完成情况并预览明天的安排。

#### 验收标准

1. THE Heartbeat SHALL 按照 Config_File 中 schedule.evening 字段配置的 cron 表达式（默认每天 19:00 Asia/Shanghai 时区）触发 Briefing_Agent 执行晚间日报流程
2. WHEN Heartbeat 触发晚间日报时，THE Briefing_Agent SHALL 读取当天日程并标注已完成和未完成的事项
3. WHEN Heartbeat 触发晚间日报时，THE Briefing_Agent SHALL 读取提醒事项并检查完成情况
4. WHEN Heartbeat 触发晚间日报时，THE Briefing_Agent SHALL 预览明天的日程安排
5. THE Briefing_Agent SHALL 将晚间日报格式化为包含已完成、未完成、明日预览和晚安提醒四个部分的结构化消息

### 需求 15：周五周报生成

**用户故事：** 作为用户，我希望每周五晚上自动收到一份结构化周报，这样我可以直接用于团队汇报，无需手动整理。

#### 验收标准

1. THE Heartbeat SHALL 在每周五按照 Config_File 中 schedule.evening 字段配置的时间（默认 19:00 Asia/Shanghai 时区）触发 Briefing_Agent 执行周报生成流程
2. WHEN 当天为周五时，THE Briefing_Agent SHALL 生成周报替代普通晚间日报
3. THE Briefing_Agent SHALL 按照以下固定格式生成周报：
   - 第一部分「本周目标总结」：包含已完成项目/任务、进行中任务（含完成百分比和预计进度）、配合其他团队解决的问题、计划外新增任务
   - 第二部分「下周工作目标」：列出项目/任务及预计完成时间和优先级，对无法完全交付的需求拆分为阶段性成果
   - 第三部分「周学习总结」：技术学习、培训或交流研讨活动
4. THE Briefing_Agent SHALL 基于本周的 calendar.md 日程记录和 reminders.md 提醒记录汇总生成周报内容
5. THE SOUL_File SHALL 包含周报格式模板，确保每次生成的周报结构一致

### 需求 16：团队版简报（可选）

**用户故事：** 作为团队负责人，我希望为不同团队生成个性化简报，这样每个团队可以收到与其职责相关的信息。

#### 验收标准

1. WHERE 团队版功能启用，THE Config_File SHALL 支持配置多个团队的简报任务，每个任务包含团队名称、关注领域和推送渠道
2. WHERE 团队版功能启用，THE Heartbeat SHALL 按照各团队配置的 cron 表达式分别触发对应的简报生成任务
3. WHERE 团队版功能启用，THE Briefing_Agent SHALL 根据团队配置的关注领域筛选和定制新闻热点内容
