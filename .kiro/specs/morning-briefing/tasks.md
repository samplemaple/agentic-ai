# 实施计划：晨间执行官（Morning Briefing）

## 概述

本实施计划将设计文档中的 OpenClaw Agent 配置方案转化为可执行的任务步骤。主要产出物为配置文件（config.json、SOUL.md、openclaw.json）和数据源文件（calendar.md、reminders.md、reading-list.md）。属性测试使用 Python + Hypothesis 验证配置文件结构和输出格式的正确性。

## 任务

- [x] 1. 搭建项目目录结构与基础配置
  - [x] 1.1 创建项目目录和 config.json 配置文件
    - 创建 `/root/morning-briefing/` 目录
    - 编写 `config.json`，包含 `user`、`modules`、`output` 三个顶层字段
    - `modules` 下包含 weather、calendar、reminders、news、reading、quote 六个模块，每个模块包含 `enabled` 布尔字段
    - weather 模块配置主数据源（和风天气）和备用数据源（wttr.in）
    - news 模块配置 RSS 源列表（InfoQ、开源中国、36氪）及 filter 关键词和 maxItems
    - reading 模块配置阅读池文件路径和 maxItems
    - quote 模块配置 style 风格描述
    - output 配置 pushTo 推送渠道
    - 添加 `schedule` 字段，包含 `morning`（晨间简报 cron，默认 `0 7 * * *`）和 `evening`（晚间日报/周报 cron，默认 `0 19 * * *`），用户可自定义触发时间
    - 确保 config.json 中不包含任何真实 API Key、密码或 Token
    - _需求: 10.1, 10.2, 10.3, 10.4, 2.1, 2.2, 5.1, 5.2, 5.3, 6.1, 6.2, 7.1_

  - [x] 1.2 创建数据源 Markdown 文件
    - 创建 `calendar.md`，按 `## YYYY-MM-DD（星期X）` 格式组织日程，列表项格式为 `- HH:MM 事项描述（备注）`
    - 创建 `reminders.md`，按"本周"和"长期"分组，列表项包含截止日期信息
    - 创建 `reading-list.md`，分"未读"和"已推荐"两部分，每条格式为 `- 《标题》 URL`
    - _需求: 3.1, 3.2, 4.1, 6.1, 6.2_

- [x] 2. 创建路由 Agent（main）
  - [x] 2.1 编写路由 Agent 的 SOUL.md
    - 创建 `~/.openclaw/agents/main/SOUL.md` 文件
    - 定义 Agent 身份：智能任务路由器，用户 IM 消息的统一入口
    - 编写路由规则：简报相关（"生成简报"、"今日简报"）→ `/agent morning`
    - 编写路由规则：日程相关（"添加日程"、"今天 14:00 开会"）→ `/agent morning`
    - 编写路由规则：提醒相关（"提醒我周五前..."）→ `/agent morning`
    - 编写路由规则：其他请求 → 自行处理
    - 行为准则：收到任务后先判断类别，告诉用户"已转交给 XX"；保持简洁
    - 不配置任何 MCP 工具调用，纯提示词路由
    - _需求: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [x] 2.2 在 openclaw.json 中注册 main Agent 实例
    - 在 `agents.instances` 中注册 `main` 实例，name 为"路由助手"
    - 复用平台已有的 DeepSeek 模型
    - _需求: 12.1_

- [x] 3. 编写晨间执行官 SOUL.md 人格与行为定义文件
  - [x] 3.1 创建 SOUL.md 核心流程定义
    - 创建 `~/.openclaw/agents/morning/SOUL.md` 文件
    - 定义 Agent 身份：高效的个人执行助理
    - 编写简报生成流程（8 个步骤）：读取配置 → 天气 → 日历 → 提醒 → 热点 → 阅读 → 每日一句 → 组装发送
    - 天气模块：优先和风天气 API，失败回退 wttr.in，提取温度、状况、建议
    - 日历模块：读取 calendar.md，匹配当天日期，按时间排序，无日程显示"今日无安排"
    - 提醒模块：读取 reminders.md，筛选 3 天内到期条目，按截止日期排序
    - 新闻模块：逐一抓取 RSS 源，按 filter 关键词优先匹配，选取最多 maxItems 条
    - 阅读模块：从 reading-list.md "未读"部分随机选取，选中后移至"已推荐"，未读为空时提示补充
    - 每日一句：根据 config.json 中 quote.style 生成不超过 30 个汉字的中文短句
    - _需求: 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4, 7.1, 7.2_

  - [x] 3.2 编写简报格式模板
    - 定义标题行格式：`☀️ 晨间简报 · {月}月{日}日 {星期}`
    - 定义各模块 emoji 标识：🌤📅⚡📰📖💪，按天气、日程、提醒、热点、阅读、每日一句固定顺序
    - 每个模块内容不超过 5 行
    - 整条简报控制在手机一屏可阅读的长度
    - _需求: 8.1, 8.2, 8.3, 8.4_

  - [x] 3.3 编写错误处理与安全边界规则
    - 错误处理：config.json 不可用时终止执行；其他数据源失败时跳过该模块继续生成；不进行无限重试
    - 安全边界：禁止访问内网地址（127.0.0.1、10.x.x.x、192.168.x.x、169.254.x.x）
    - 安全边界：禁止在简报消息中输出 API Key、密码或 Token 等凭证信息
    - 安全边界：禁止访问 `/root/morning-briefing` 以外的目录
    - _需求: 1.4, 2.4, 3.4, 4.4, 5.4, 5.5, 6.5, 11.2, 11.3, 11.4_

  - [x] 3.4 编写临时任务识别与写入规则
    - 在 SOUL.md 中添加临时任务处理流程
    - 定义识别规则：包含具体时间点（如"14:00 开会"）的消息写入 calendar.md，包含截止日期（如"周五前提交"）的消息写入 reminders.md
    - 写入 calendar.md 时，追加到对应日期的章节下；如果该日期章节不存在，创建新章节
    - 写入 reminders.md 时，追加到"本周"分组下
    - 写入成功后回复用户确认消息，包含写入的具体内容和生效时间
    - _需求: 13.1, 13.2, 13.3, 13.4_

- [x] 4. 配置 openclaw.json（MCP 工具与 Heartbeat）
  - [x] 4.1 配置 MCP 工具
    - 在 `~/.openclaw/openclaw.json` 中配置 `mcpServers` 节点
    - 配置 fetch MCP：`npx -y @modelcontextprotocol/server-fetch`（如平台已有则复用）
    - 配置 filesystem MCP：`npx -y @modelcontextprotocol/server-filesystem /root/morning-briefing`，路径限制为 `/root/morning-briefing`，实现与其他 Agent 的数据目录隔离
    - _需求: 11.1_

  - [x] 4.2 注册 morning Agent 实例并配置 Heartbeat
    - 在 `~/.openclaw/openclaw.json` 的 `agents.instances` 中注册 `morning` Agent 实例（复用平台已有的 DeepSeek 模型，无需单独配置模型）
    - 在 `heartbeat.tasks` 中添加晨间简报任务：cron 表达式按 config.json 中 `schedule.morning` 配置（默认 `0 7 * * *`），`agent` 字段指定为 `morning`
    - 编写触发 prompt，指示 Agent 读取 config.json 并按 SOUL.md 流程执行
    - 确保 Heartbeat 任务只触发 morning Agent，不影响 main 或其他 Agent 实例
    - _需求: 1.1, 9.1_

- [x] 5. 配置服务器时区与凭证安全
  - [x] 5.1 设置云服务器时区为 Asia/Shanghai
    - 执行 `timedatectl set-timezone Asia/Shanghai` 设置服务器时区
    - 执行 `timedatectl` 验证时区已正确设置为 CST (China Standard Time)
    - 确保 Heartbeat 的 cron 表达式按上海时间触发

  - [x] 5.2 配置凭证安全与环境变量
    - 创建 `/opt/openclaw.env` 文件，存放和风天气 API Key 等凭证
    - 设置文件权限为 600：`chmod 600 /opt/openclaw.env`
    - 确认 config.json 中 API URL 通过环境变量引用 Key，不直接包含真实凭证
    - _需求: 11.5, 10.4_

- [x] 6. Checkpoint - 核心配置验证
  - 确保所有配置文件已创建且格式正确，询问用户是否有疑问。

- [x] 7. 编写属性测试验证配置正确性
  - [x] 7.1 搭建 Python 测试环境
    - 创建测试目录和测试文件
    - 配置 Hypothesis 测试库依赖
    - _需求: 10.1_

  - [ ]* 7.2 编写 Property 1 属性测试：config.json Schema 验证
    - **Property 1: config.json Schema 验证**
    - 随机生成 config.json 变体，验证包含 `user`、`modules`、`output` 三个顶层字段
    - 验证 `modules` 下每个模块包含 `enabled` 布尔字段
    - **验证需求: 10.1, 10.2**

  - [ ]* 7.3 编写 Property 2 属性测试：config.json 凭证安全
    - **Property 2: config.json 凭证安全**
    - 随机注入凭证模式字符串（如 `sk-`、`ghp_`、`key=`后跟长字符串），验证检测能力
    - **验证需求: 10.4**

  - [ ]* 7.4 编写 Property 3 属性测试：简报模块顺序与 emoji 标识
    - **Property 3: 简报模块顺序与 emoji 标识**
    - 随机生成模块启用组合，验证输出中 emoji（🌤📅⚡📰📖💪）按固定顺序出现
    - **验证需求: 8.1, 8.2**

  - [ ]* 7.5 编写 Property 4 属性测试：简报标题行格式
    - **Property 4: 简报标题行格式**
    - 随机生成日期，验证标题行匹配 `☀️ 晨间简报 · {月}月{日}日 {星期}` 格式
    - **验证需求: 8.3**

  - [ ]* 7.6 编写 Property 5 属性测试：简报模块行数限制
    - **Property 5: 简报模块行数限制**
    - 随机生成模块内容，验证每个模块不超过 5 行
    - **验证需求: 8.4**

  - [ ]* 7.7 编写 Property 6 属性测试：阅读池状态流转不变量
    - **Property 6: 阅读池状态流转不变量**
    - 随机生成阅读池和推荐数量，验证推荐前后文章总数不变，"未读"减少量等于"已推荐"增加量
    - **验证需求: 6.3**

  - [ ]* 7.8 编写 Property 7 属性测试：每日一句字数限制
    - **Property 7: 每日一句字数限制**
    - 随机生成中文短句，验证汉字字符数不超过 30 个
    - **验证需求: 7.2**

- [x] 8. Checkpoint - 核心功能测试验证
  - 确保所有属性测试通过，询问用户是否有疑问。

- [x] 9. 晚间日报与周五周报配置（需求 14、15）
  - [x] 9.1 扩展 SOUL.md 添加晚间日报流程
    - 在 SOUL.md 中添加晚间日报生成流程
    - 读取当天日程标注已完成/未完成事项
    - 检查提醒事项完成情况
    - 预览明天日程安排
    - 定义晚间日报格式模板：🌙 标题 + ✅ 已完成 + ⏳ 未完成 + 📅 明日预览 + 💤 晚安提醒
    - _需求: 14.2, 14.3, 14.4, 14.5_

  - [x] 9.2 扩展 SOUL.md 添加周五周报流程
    - 在 SOUL.md 中添加周报生成流程，周五 19:00 触发时生成周报替代普通日报
    - 定义周报固定格式模板：
      - 一、本周目标总结（已完成、进行中含百分比、配合团队、计划外任务）
      - 二、下周工作目标（项目/任务、完成时间、优先级、阶段性成果拆分）
      - 三、周学习总结（技术学习、培训、交流研讨）
    - Agent 基于本周 calendar.md 和 reminders.md 的记录汇总生成周报
    - _需求: 15.2, 15.3, 15.4, 15.5_

  - [x] 9.3 在 openclaw.json 中添加晚间 Heartbeat 任务
    - 添加晚间任务：cron 表达式按 config.json 中 `schedule.evening` 配置（默认 `0 19 * * *`）
    - 编写触发 prompt，指示 Agent 判断当天是否为周五：周五生成周报，其他日生成日报
    - _需求: 14.1, 15.1_

  - [ ]* 9.4 编写 Property 8 属性测试：晚间日报结构完整性
    - **Property 8: 晚间日报结构完整性**
    - 随机生成晚间日报内容，验证包含已完成、未完成、明日预览、晚安提醒四个部分
    - **验证需求: 14.5**

  - [ ]* 9.5 编写 Property 9 属性测试：周报三段式结构验证
    - **Property 9: 周报三段式结构验证**
    - 验证周报输出包含「本周目标总结」「下周工作目标」「周学习总结」三个部分
    - **验证需求: 15.3**

- [ ] 10. 可选功能：团队版简报配置（需求 16）
  - [ ] 10.1 扩展 config.json 添加团队版配置
    - 在 config.json 中添加 `teams` 数组字段
    - 每个团队对象包含 `name`（团队名称）、`focus`（关注领域）、`cron`（独立 cron 表达式）、`pushTo`（推送渠道）
    - _需求: 16.1_

  - [ ] 10.2 在 openclaw.json 中添加团队版 Heartbeat 任务
    - 按各团队配置的 cron 表达式添加独立的 Heartbeat 任务
    - 每个任务的 prompt 包含团队关注领域，用于定制新闻热点内容
    - _需求: 16.2, 16.3_

  - [ ]* 10.3 编写 Property 10 属性测试：团队版配置结构验证
    - **Property 10: 团队版配置结构验证**
    - 随机生成团队配置，验证每个团队对象包含 `name`、`focus`、`pushTo` 字段
    - **验证需求: 16.1**

- [x] 11. 最终 Checkpoint - 全部配置与测试验证
  - 确保所有配置文件完整且格式正确
  - 确保所有属性测试通过
  - 询问用户是否有疑问

## 备注

- 标记 `*` 的任务为可选任务，可跳过以加快 MVP 交付
- 每个任务引用了具体的需求编号，确保可追溯性
- 需求 16（团队版简报）为可选功能，任务 10 可根据需要跳过
- 晚间日报（需求 14）和周五周报（需求 15）共用一个 Heartbeat 任务（每天 19:00），Agent 根据星期判断输出日报还是周报
- 属性测试使用 Python + Hypothesis 库验证配置文件结构和输出格式
- Checkpoint 任务用于阶段性验证，确保增量交付的正确性
