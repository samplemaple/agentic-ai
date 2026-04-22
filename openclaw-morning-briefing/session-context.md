# 晨间执行官项目 - 配置快照

## 状态：已部署，运行正常 ✅

最后更新：2026-04-22

---

## 定时任务（4 个）

| 名称 | ID | Agent | cron | 模型 |
|------|-----|-------|------|------|
| 晨间简报 | 7506dd61-0135-4f1f-9f6f-a0daadbb9643 | morning | 0 6 * * * | deepseek-chat |
| 晨间简报投递 | 41206a6a-7ea8-464d-8272-e2b1e77c9bd2 | main | 5 6 * * * | deepseek-chat |
| 晚间简报 | c7176611-6980-4528-a067-0f815f99b413 | morning | 0 19 * * * | deepseek-reasoner |
| 晚间简报投递 | 434a5e43-10dd-4b0e-865e-4470c0538b60 | main | 5 19 * * * | deepseek-chat |

投递方式：文件中转（morning 写 /tmp → main 读取投递微信）

## 服务器文件

| 文件 | 路径 |
|------|------|
| config.json | /root/morning-briefing/config.json |
| calendar.md | /root/morning-briefing/calendar.md |
| reminders.md | /root/morning-briefing/reminders.md |
| reading-list.md | /root/morning-briefing/reading-list.md |
| morning SOUL.md | ~/.openclaw/workspace/morning/SOUL.md |

## 简报模块

天气（Open-Meteo，南京坐标）→ 日程 → 提醒 → 每日一句

## Token 优化记录

- 2026-04-21：SOUL.md 精简 + 工具限制 + 文件中转 → 30,000→4,500 tok/次（-85%）
- 2026-04-22：AGENTS.md 裁剪 + main 工具白名单 → 固定开销 -2,700 tok

## 已解决的问题

- ✅ 微信投递（文件中转方案）
- ✅ 服务崩溃循环（僵尸进程）
- ✅ 天气数据源（Open-Meteo）
- ✅ 100% ctx（--light-context + 工具限制）
- ✅ DNS 解析失败（全局 fallback DNS）
