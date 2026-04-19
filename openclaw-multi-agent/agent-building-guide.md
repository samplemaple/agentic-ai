# OpenClaw Agent 构建实战经验

> 基于 main（路由助手）+ morning（晨间执行官）的构建过程总结
> OpenClaw 版本：2026.4.15

---

## 一、Agent 注册

### 创建新 Agent

```bash
openclaw agents add <agent-id>
```

交互式引导，依次填写：
- Workspace 目录：默认 `/root/.openclaw/workspace/<agent-id>`
- 模型认证：选 Custom Provider → 填 Base URL 和 API Key → 选 OpenAI-compatible → 填 Model ID
- 渠道：子 Agent 选 No（通过 main 投递）

### 查看已注册 Agent

```bash
openclaw agents list
```

### 关键目录结构

```
~/.openclaw/
├── workspace/              # main Agent 的 workspace（SOUL.md 等）
├── workspace/<agent-id>/   # 子 Agent 的 workspace（SOUL.md 等）
├── agents/main/agent/      # main 的 models.json、auth.json
├── agents/<agent-id>/agent/ # 子 Agent 的 models.json
└── openclaw.json           # 全局配置
```

### 踩坑记录

- `auth.json` 必须保持 `{}` 空对象，写入内容会导致控制台 Loading schema 卡死
- `auth-profiles.json` 在 2026.4.15 版本中不被读取，不要手动创建
- 模型认证通过 `models.json` 中的 `apiKey` 字段，或通过 `openclaw configure` 交互式配置
- 每个 Agent 需要独立的 `models.json`，可以从 main 复制：`cp ~/.openclaw/agents/main/agent/models.json ~/.openclaw/agents/<id>/agent/models.json`

---

## 二、模型配置

### 通过 CLI 配置（推荐）

```bash
openclaw configure
# 选 Model → Custom Provider → 填 Base URL / API Key / Model ID
```

每个新 Agent 创建时也会引导配置模型。

### models.json 结构

```json
{
  "providers": {
    "openai": {
      "baseUrl": "https://api.deepseek.com/v1",
      "apiKey": "sk-xxx",
      "api": "openai-completions",
      "models": [
        {"id": "deepseek-chat", "name": "DeepSeek V3 Chat", "reasoning": false, "contextWindow": 64000, "maxTokens": 8192},
        {"id": "deepseek-reasoner", "name": "DeepSeek R1", "reasoning": true, "contextWindow": 64000, "maxTokens": 8192}
      ]
    }
  }
}
```

### 踩坑记录

- `contextWindow` 默认 16000 太小，会导致 `100% context used` 错误，建议设为 64000
- 通过 `openclaw configure` 创建的 provider 名称是 `custom-api-deepseek-com`，定时任务中引用模型格式为 `custom-api-deepseek-com/deepseek-chat`
- 手动在 models.json 中创建的 provider 名称是 `openai`，引用格式为 `openai/deepseek-chat`
- 修改 contextWindow：`jq '(.models.providers."custom-api-deepseek-com".models[]).contextWindow = 64000' ~/.openclaw/openclaw.json > /tmp/tmp.json && mv /tmp/tmp.json ~/.openclaw/openclaw.json`

---

## 三、SOUL.md 编写

### 存放位置

- main Agent：`~/.openclaw/workspace/SOUL.md`
- 子 Agent：`~/.openclaw/workspace/<agent-id>/SOUL.md`
- 同时在 `~/.openclaw/agents/<agent-id>/SOUL.md` 也放一份

### 编写原则

1. 明确身份和职责范围
2. 流程步骤要具体（读哪个文件、调哪个 API、失败怎么处理）
3. 输出格式要固定（emoji、标题行格式、模块顺序）
4. 明确写"只输出内容本身，不要附加执行说明或调试信息"
5. 安全边界单独一节，列出所有禁止项

### 更新 SOUL.md

```bash
cat > ~/.openclaw/workspace/<agent-id>/SOUL.md << 'SOULEOF'
# 内容
SOULEOF

cp ~/.openclaw/workspace/<agent-id>/SOUL.md ~/.openclaw/agents/<agent-id>/SOUL.md
```

---

## 四、主从调度（sessions_spawn）

### 开启调度权限

在 `openclaw.json` 的 `agents.defaults.subagents` 下添加 `allowAgents`：

```bash
jq '.agents.defaults.subagents.allowAgents = ["morning", "其他agent"]' ~/.openclaw/openclaw.json > /tmp/tmp.json && mv /tmp/tmp.json ~/.openclaw/openclaw.json
```

### main SOUL.md 中的调度指令

```markdown
## 可调度的子 Agent

| Agent ID | 名称 | 擅长领域 |
|----------|------|---------|
| morning | 晨间执行官 | 简报、日程、提醒 |

## 路由规则

以下消息使用 sessions_spawn 分发给 morning Agent：
- 简报相关、日程相关、提醒相关

分发流程：
1. 告知用户"已转交给晨间执行官，请稍候"
2. 使用 sessions_spawn 发送任务
3. 等待结果返回
4. 将结果原样回复给用户
```

### 踩坑记录

- sessions_spawn 的结果会作为 `INTERNAL_CONTEXT` 返回给 main，默认不会转发给用户
- 系统会提示 main "If this result is duplicate, reply ONLY: NO_REPLY"
- 必须在定时任务 prompt 中明确写"不要回复 NO_REPLY，必须将结果原样回复给用户"
- `/agent morning` 文本指令在 SOUL.md 中无效，必须用 sessions_spawn

---

## 五、定时任务（Cron）

### 创建任务

通过控制台「定时任务」页面创建，或 CLI：

```bash
openclaw cron add --name "任务名" --cron "0 7 * * *" --tz "Asia/Shanghai" --exact \
  --agent main --model openai/deepseek-chat --thinking medium \
  --session isolated --announce --channel openclaw-weixin \
  --best-effort-deliver --expect-final --timeout-seconds 300 \
  --message "任务提示词"
```

### 关键参数

| 参数 | 作用 | 推荐值 |
|------|------|--------|
| --agent | 执行 Agent | main（有微信渠道） |
| --model | 模型 | openai/deepseek-chat 或 openai/deepseek-reasoner |
| --thinking | 思考深度 | medium（简报）/ high（周报） |
| --cron + --tz | 精确时间 | "0 6 * * *" + "Asia/Shanghai" |
| --exact | 禁用抖动 | 必加，否则时间不精确 |
| --timeout-seconds | 超时 | 180-300（需要调 API 的任务） |
| --expect-final | 等待最终回复 | 必加，否则只捕获第一条回复 |
| --announce | 投递到聊天 | 必加 |
| --best-effort-deliver | 投递失败不报错 | 建议加 |

### 管理命令

```bash
openclaw cron list                    # 查看任务
openclaw cron edit <id> --cron "..."  # 修改调度
openclaw cron edit <id> --message "..." # 修改提示词
openclaw cron run <id>                # 手动触发
openclaw cron disable <id>            # 禁用
openclaw cron enable <id>             # 启用
openclaw cron rm <id>                 # 删除
```

### 踩坑记录

- 控制台创建的任务默认是间隔频率（every 30m），不是精确时间，需要用 CLI 改成 cron 表达式
- 定时任务的 agent 应该直接设为子 Agent 自己（如 morning），不要设为 main
- 设为 main + sessions_spawn 的方案会被 INTERNAL_CONTEXT 的 NO_REPLY 机制拦截，导致微信收不到
- `--expect-final` 在 sessions_spawn 场景下无效（系统指令优先级更高）
- 默认超时 30 秒太短，需要调 API 的任务建议 300-600 秒
- 子 Agent 必须先绑定渠道（`openclaw agents bind`）才能投递到微信

---

## 六、openclaw.json 注意事项

### 不支持的顶层节点（会导致启动失败）

- `heartbeat`（顶层）→ 用 `openclaw cron` 管理
- `mcpServers`（顶层）→ 通过控制台「技能」页面管理
- `agents.instances`（旧格式）→ 用 `openclaw agents add` 注册

### 安全修改方式

```bash
# 用 jq 修改，不要手动编辑
jq '.path.to.field = "value"' ~/.openclaw/openclaw.json > /tmp/tmp.json && mv /tmp/tmp.json ~/.openclaw/openclaw.json

# 修改后验证
jq '.path.to.field' ~/.openclaw/openclaw.json

# 重启生效（cron 修改不需要重启）
sudo systemctl restart openclaw
```

### 服务管理

```bash
sudo systemctl restart openclaw       # 重启
sudo systemctl status openclaw         # 状态
journalctl -u openclaw -n 30 --no-pager  # 日志

# 端口冲突时
sudo killall -9 openclaw openclaw-gateway 2>/dev/null
sleep 2
sudo systemctl start openclaw
```

---

## 七、渠道投递与定时任务

### 核心结论

定时任务必须由 main Agent 执行，prompt 中直接描述任务内容（不要用 sessions_spawn）。main 有微信渠道绑定，投递可靠。

### 为什么不能用子 Agent 执行定时任务

1. 子 Agent 没有微信渠道绑定，投递失败（lastDeliveryStatus: unknown）
2. 给子 Agent 绑定微信渠道（`openclaw agents bind --agent morning --bind "openclaw-weixin"`）会导致所有微信消息都路由到子 Agent，main 的路由功能失效
3. 通过 main + sessions_spawn 中转的方案，子任务结果会被系统的 INTERNAL_CONTEXT NO_REPLY 机制拦截，微信收不到

### 为什么不能用 sessions_spawn 投递

sessions_spawn 的子任务结果返回给 main 时，OpenClaw 系统会注入：
```
Action: Convert this completion into a concise internal orchestration update...
If this result is duplicate or no update is needed, reply ONLY: NO_REPLY.
```
这是系统级指令，优先级高于 prompt 中的"不要回复 NO_REPLY"。main 会遵循系统指令回复 NO_REPLY，微信收不到。

### 正确方案

定时任务的 agent 设为 main，prompt 直接描述任务内容：

```bash
openclaw cron add --name "晨间简报" --agent main \
  --cron "0 6 * * *" --tz "Asia/Shanghai" --exact \
  --model custom-api-deepseek-com/deepseek-chat --thinking medium \
  --light-context --session isolated --announce \
  --channel openclaw-weixin --best-effort-deliver \
  --timeout-seconds 600 \
  --message "执行晨间简报流程：..."
```

main 在定时任务中临时充当执行者，日常对话时仍然走路由逻辑，不会臃肿。

### sessions_spawn 的正确使用场景

sessions_spawn 只适合用户在微信里实时对话时的路由（用户发消息 → main spawn 子 Agent → 结果回传 → main 回复用户）。不适合定时任务投递。

### 渠道绑定注意事项

- 不要给子 Agent 绑定微信渠道，会抢走 main 的消息
- 如果误绑了，用 `openclaw agents unbind --agent <id> --bind "openclaw-weixin"` 解除
- 查看绑定：`openclaw agents bindings`
- 微信渠道只保留在 main Agent 上

---

## 八、构建新 Agent 的标准流程

1. `openclaw agents add <id>` 注册 Agent，配置模型（用于 sessions_spawn 实时路由场景）
2. 编写 SOUL.md，cat 到 workspace 和 agents 目录
3. 复制 models.json：`cp ~/.openclaw/agents/main/agent/models.json ~/.openclaw/agents/<id>/agent/models.json`
4. 不要给子 Agent 绑定微信渠道（会抢走 main 的消息）
5. 开启调度权限（如需 main 实时路由）：`jq '.agents.defaults.subagents.allowAgents += ["<id>"]' ...`
6. 更新 main SOUL.md 的路由规则（用于实时对话路由）
7. 创建定时任务：agent 设为 main，prompt 直接描述任务内容（不要用 sessions_spawn）
8. 加 `--light-context` 减少 token 消耗，`--timeout-seconds 600` 防超时
9. 重启服务：`sudo systemctl restart openclaw`
10. 测试：控制台点运行 / 微信发消息验证
