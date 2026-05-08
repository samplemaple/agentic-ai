# 文档维护流程

> Spec 完成后的归档流程和文档维护规范。
> 确保项目文档保持最新、可追溯。

---

## 归档流程总览

```
验证通过 → Bug 归纳 → 更新项目文档 → 精简 spec 文档 → 归档完成
```

---

## 步骤 1：Bug 归纳

在归档前，检查开发过程中遇到的 bug 是否已沉淀：

### 1.1 检查清单
- [ ] 通用性踩坑是否追加到代码规范？
- [ ] 预防性规则是否追加到预防指南？
- [ ] 测试盲区是否补充了测试用例？
- [ ] 文档不准确是否已修正？

### 1.2 沉淀规则

| 类型 | 沉淀位置 | 示例 |
|------|---------|------|
| 通用性踩坑 | 代码规范 | "不要在循环中创建对象" |
| 预防性规则 | 预防指南 | "修改接口前先搜索所有调用点" |
| 测试盲区 | 测试用例 | "补充并发场景测试" |
| 文档不准确 | 对应文档 | "修正接口参数说明" |

---

## 步骤 2：更新项目文档

### 2.1 更新项目进度文档
更新 `STATUS.md` 或类似的进度文档：

```markdown
## 已完成 Spec

| Spec | 名称 | 状态 | 完成日期 | 核心产出 |
|------|------|------|---------|---------|
| {N} | {名称} | ✅ | {日期} | {一句话描述} |

## 下一步计划
- {下一步1}
- {下一步2}
```

### 2.2 更新项目规范（如有新规则）
如果开发过程中发现了新的规范：

**代码规范**：
```markdown
## 踩坑记录

| 编号 | 场景 | 解决 |
|------|------|------|
| {N} | {场景} | {解决方案} |
```

**预防指南**：
```markdown
## {规则类别}

### {N}. {规则名称}

{规则描述}

**正确做法**：
{示例}

**错误做法**：
{示例}
```

### 2.3 更新文件索引
更新项目结构文档，添加新文件：

```markdown
## 新增文件

| 文件 | 说明 | 所属 Spec |
|------|------|----------|
| {文件路径} | {描述} | Spec {N} |
```

---

## 步骤 3：精简 spec 文档

将 spec 的详细说明替换为摘要，详细内容迁移到归档目录。

### 3.1 精简 project-outline.md
将详细说明替换为 3-4 行摘要：

```markdown
### ✅ Spec {N}: {名称}

- **spec 名称**: `{spec-name}`
- **状态**: ✅ 已完成（{日期}）
- **职责**: {一句话核心产出}
- **详细归档**: `docs/SpecHistory/phase{N}-completed-specs.md`
```

### 3.2 迁移详细内容
将详细内容迁移到归档目录：

```
docs/SpecHistory/
└── phase{N}-completed-specs.md
```

归档文档格式：

```markdown
# Spec {N} 归档：{名称}

> 完成日期：{日期}
> Spec 目录：`.kiro/specs/{spec-name}/`

## 概述
{一句话描述}

## 核心产出
- {产出1}
- {产出2}

## 关键设计决策
- {决策1} — {理由}
- {决策2} — {理由}

## 文件变更

### 新增文件
| 文件 | 说明 |
|------|------|
| {文件} | {描述} |

### 修改文件
| 文件 | 改动摘要 |
|------|---------|
| {文件} | {描述} |

## 测试覆盖
- 单元测试：{N} 个
- 集成测试：{N} 个
- 端到端测试：{N} 个

## 经验教训
- {教训1}
- {教训2}

## 原始文档
- 需求文档：`.kiro/specs/{spec-name}/requirements.md`
- 设计文档：`.kiro/specs/{spec-name}/design.md`
- 任务列表：`.kiro/specs/{spec-name}/tasks.md`
- 实施注意事项：`.kiro/specs/{spec-name}/implementation-notes.md`
```

---

## 步骤 4：更新文档联动关系

### 4.1 更新文档索引
如果项目有文档索引，更新：

```markdown
## 文档索引

| 文档 | 用途 | 更新时机 |
|------|------|---------|
| STATUS.md | 项目进度 | Spec 完成后 |
| project-outline.md | Spec 模块大纲 | Spec 完成后 |
| code-conventions.md | 代码规范 | 发现新规则时 |
| preventive-guidelines.md | 预防指南 | 发现新规则时 |
```

### 4.2 更新 Skills（如有）
如果 spec 的设计模式有通用价值，更新或创建 skill：

```markdown
## Skills 索引

| Skill | 用途 | 来源 Spec |
|-------|------|----------|
| {skill-name} | {描述} | Spec {N} |
```

---

## 文档分层体系

### 自动加载层
每个 session 自动注入的文档：
- 项目概况
- 代码规范
- 预防指南

### 条件加载层
匹配特定条件时自动注入：
- 测试相关：测试策略、测试模式
- 性能相关：性能优化指南

### 手动加载层
需要时通过引用加载：
- Spec 生命周期
- 质量保障流程
- 任务执行规范
- 文档维护流程

### 文档联动关系

```
阶段 1 准备
  读 → STATUS.md + project-outline.md
  自动 → code-conventions.md + preventive-guidelines.md

阶段 2-3 三件套 + 质量保障
  写 → requirements.md + design.md + tasks.md + implementation-notes.md
  参考 → 01-spec-lifecycle.md + 03-quality-assurance.md

阶段 4 执行
  读 → 三件套 + implementation-notes.md
  参考 → 04-task-execution.md

阶段 5 归档
  参考 → 05-doc-maintenance.md（本文件）
  更新 → STATUS.md + project-outline.md + code-conventions.md
  写 → docs/SpecHistory/phase{N}-completed-specs.md
```

---

## 文档维护检查清单

归档完成后，自查：

- [ ] Bug 已归纳到代码规范/预防指南？
- [ ] STATUS.md 已更新？
- [ ] project-outline.md 已精简？
- [ ] 详细内容已迁移到 SpecHistory？
- [ ] 文件索引已更新？
- [ ] Skills 已更新（如有）？
- [ ] 文档联动关系正确？

---

## 文档更新时机速查

| 文档 | 更新时机 | 更新内容 |
|------|---------|---------|
| STATUS.md | Spec 完成后 | 进度、下一步计划 |
| project-outline.md | Spec 完成后 | 精简为摘要 |
| code-conventions.md | 发现新规则时 | 踩坑记录、新规范 |
| preventive-guidelines.md | 发现新规则时 | 预防性规则 |
| SpecHistory | Spec 完成后 | 归档详细内容 |
| Skills | 发现通用模式时 | 新增或更新 skill |

---

## 常见问题

### Q: 所有 spec 都需要归档吗？

**建议**：
- 简单 spec（任务 < 5）：可选，只更新 STATUS.md
- 中等 spec（任务 5-15）：推荐，精简 project-outline.md
- 复杂 spec（任务 > 15）：必须，完整归档流程

### Q: 归档文档放哪里？

**建议**：
- `docs/SpecHistory/` — 按阶段组织
- 或 `docs/archive/` — 按日期组织
- 保持一致性即可

### Q: 归档后还能修改 spec 文档吗？

**可以**，但要注意：
- 修改归档文档时，更新"最后修改日期"
- 重大修改需要记录修改原因
- 保持归档文档的可追溯性

### Q: 多人协作时如何避免文档冲突？

**建议**：
- 每个 spec 有唯一的负责人
- 修改文档前先拉取最新版本
- 使用版本控制（Git）管理文档
- 重大修改前先沟通

---

## 下一步

归档完成后，可以开始下一个 spec 的 [准备+澄清阶段](02-clarification.md)。
