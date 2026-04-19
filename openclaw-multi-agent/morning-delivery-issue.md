# Morning Agent 定时任务无法投递到微信 ClawBot 的问题

## 环境

- OpenClaw 版本：2026.4.15
- 两个 Agent：main（路由助手，默认 Agent）、morning（晨间执行官，子 Agent）
- IM 渠道：openclaw-weixin（微信 ClawBot）绑定在 main Agent 上
- 模型：DeepSeek V3 Chat / R1 Reasoner（通过 custom-api-deepseek-com provider）

## 问题描述

morning Agent 的定时任务（cron job）执行成功，简报内容在控制台能看到，但无法投递到微信 ClawBot。

## 尝试过的方案及结果

### 方案 1：morning Agent 直接执行 + announce 投递

```bash
openclaw cron edit <id> --agent morning --channel openclaw-weixin --announce
```

结果：任务执行成功，`lastDeliveryStatus: "unknown"`，微信收不到。
原因分析：morning Agent 没有微信渠道的 provider 配置，虽然 delivery.channel 指定了 openclaw-weixin，但 morning 不具备向该渠道发送消息的能力。

### 方案 2：给 morning Agent 绑定微信渠道

```bash
openclaw agents bind --agent morning --bind "openclaw-weixin"
```

结果：绑定成功，但产生了严重副作用——所有微信消息都路由到了 morning Agent，main Agent 的路由功能完全失效。
原因分析：`agents bind` 是渠道路由绑定，意味着"来自该渠道的消息交给这个 Agent 处理"。绑定后 morning 抢走了 main 的微信消息入口。
回滚：`openclaw agents unbind --agent morning --bind "openclaw-weixin"`

### 方案 3：main Agent 执行 + sessions_spawn 转交 morning

```bash
openclaw cron edit <id> --agent main --expect-final
# prompt 中写"使用 sessions_spawn 将任务转交给 morning Agent，收到结果后原样回复"
```

结果：main 成功 spawn morning，morning 执行完毕并返回了完整简报内容。但 main 收到子任务结果后回复了 NO_REPLY，微信只收到了"已转交给晨间执行官，请稍候"，没有收到最终简报。

原因分析：OpenClaw 的 sessions_spawn 机制在返回子任务结果时，系统会注入 INTERNAL_CONTEXT 指令：
```
Action: Convert this completion into a concise internal orchestration update for your parent agent in your own words. 
Keep this internal context private (don't mention system/log/stats/session details or announce type). 
If this result is duplicate or no update is needed, reply ONLY: NO_REPLY.
```
这是系统级指令，优先级高于我们在 prompt 中写的"不要回复 NO_REPLY"。main Agent 遵循了系统指令，回复 NO_REPLY，定时任务的 announce 投递只捕获了第一条回复（"已转交"），没有等到最终结果。

即使加了 `--expect-final` 参数也无效，因为 main 的最终回复就是 NO_REPLY（或一条内部编排更新），不是面向用户的简报内容。

### 方案 4：morning Agent 直接执行 + channel last

```bash
openclaw cron edit <id> --agent morning --channel last
```

结果：微信收不到。
原因分析：`last` 是基于该 Agent 最近活跃的渠道，但 morning 从未通过微信与用户对话过，没有"最近活跃渠道"。

### 方案 5（当前 workaround）：main Agent 直接执行，不用 sessions_spawn

```bash
openclaw cron edit <id> --agent main
# prompt 中直接描述任务内容，不提 sessions_spawn
```

结果：微信能收到完整简报。
代价：main Agent 在定时任务中临时充当执行者，没有实现 main/morning 的解耦。morning Agent 的 SOUL.md 在定时任务场景下没有被使用。

## 核心问题

如何让子 Agent（morning）的定时任务结果投递到微信 ClawBot，同时不影响 main Agent 的微信消息路由？

理想方案应该是以下之一：
1. 子 Agent 的 cron job 能直接投递到 main 绑定的渠道（不需要子 Agent 自己绑定渠道）
2. sessions_spawn 的子任务结果能被 announce 机制正确捕获并投递（不被 INTERNAL_CONTEXT NO_REPLY 拦截）
3. 有一种渠道绑定方式只允许子 Agent 发送消息，不接收消息（单向绑定）

## 相关配置

```json
// openclaw.json 中的关键配置
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxConcurrent": 8,
        "allowAgents": ["morning"]
      }
    },
    "list": [
      {"id": "main"},
      {"id": "morning", "workspace": "/root/.openclaw/workspace/morning"}
    ]
  }
}
```

```bash
# 定时任务配置
openclaw cron list --json | jq '.jobs[] | {name, agentId, delivery}'
# 晨间简报: agentId=main, delivery={mode:announce, channel:openclaw-weixin}
```
