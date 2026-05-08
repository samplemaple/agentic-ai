# 设计文档模板

> 用于生成 design.md 的模板。
> AI 根据 requirements.md，使用此模板生成设计文档。

---

## 模板

```markdown
# 设计文档：{中文名称}（{英文 spec 名称}）

> 生成日期：{日期}
> 基于 requirements.md

---

## 架构概述

{一段话描述整体架构}

## 架构图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  {组件1}    │────▶│  {组件2}    │────▶│  {组件3}    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  {数据1}    │     │  {数据2}    │     │  {数据3}    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 组件设计

### 组件 1：{组件名称}

**职责**：
- {职责1}
- {职责2}

**接口**：

```typescript
interface {ComponentName} {
  // 属性
  {property}: {type};

  // 方法
  {method}({params}): {ReturnType};
}
```

**数据模型**：

```typescript
interface {DataName} {
  {field}: {type};
  {field}: {type};
}
```

### 组件 2：{组件名称}

...

## 数据模型

### 核心数据结构

```typescript
// {数据结构名称}
interface {Name} {
  {field}: {type};  // {说明}
  {field}: {type};  // {说明}
}
```

### 数据库设计

```sql
-- {表名}
CREATE TABLE {table_name} (
  {column} {type} {constraints},
  {column} {type} {constraints},
  PRIMARY KEY ({pk})
);
```

## 接口设计

### API 1：{API 名称}

```
{METHOD} {path}

请求：
{
  "{field}": "{type}"
}

响应：
{
  "{field}": "{type}"
}

错误：
- {错误码}: {错误描述}
```

### API 2：{API 名称}

...

## 错误处理

### 错误类型

| 错误类型 | 处理方式 | 用户提示 |
|---------|---------|---------|
| {错误1} | {处理} | {提示} |
| {错误2} | {处理} | {提示} |

### 错误码定义

| 错误码 | 含义 | HTTP 状态码 |
|--------|------|------------|
| {code} | {含义} | {status} |

## 安全设计

### 认证
- {认证方式}

### 授权
- {授权方式}

### 数据保护
- {保护措施}

## 性能设计

### 性能目标
- {目标1}
- {目标2}

### 优化策略
- {策略1}
- {策略2}

## 扩展性设计

### 未来扩展点
- {扩展点1} — 预留接口：{接口}
- {扩展点2} — 预留接口：{接口}

### 扩展方式
- {扩展方式1}
- {扩展方式2}

## 测试策略

### 单元测试
- {测试内容1}
- {测试内容2}

### 集成测试
- {测试内容1}
- {测试内容2}

### 端到端测试
- {测试内容1}
- {测试内容2}

## 竞品分析（可选）

### 竞品 1：{竞品名称}
- {做法}
- {优缺点}

### 竞品 2：{竞品名称}
- {做法}
- {优缺点}

### 设计决策
基于竞品分析，我们选择 {方案}，因为 {理由}。
```

---

## 示例

```markdown
# 设计文档：用户认证系统（user-auth）

> 生成日期：2024-01-15
> 基于 requirements.md

---

## 架构概述

采用分层架构，分为 API 层、服务层、数据层。API 层处理 HTTP 请求，服务层处理业务逻辑，数据层处理数据持久化。使用 JWT 进行无状态认证。

## 架构图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   API 层    │────▶│   服务层    │────▶│   数据层    │
│  (Express)  │     │  (Auth)     │     │  (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   中间件    │     │   JWT 管理  │     │   用户表    │
│  (认证)     │     │   密码哈希  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 组件设计

### 组件 1：AuthController

**职责**：
- 处理认证相关的 HTTP 请求
- 参数验证
- 调用 AuthService

**接口**：

```typescript
interface AuthController {
  register(req: Request, res: Response): Promise<void>;
  login(req: Request, res: Response): Promise<void>;
  resetPassword(req: Request, res: Response): Promise<void>;
}
```

### 组件 2：AuthService

**职责**：
- 处理认证业务逻辑
- 密码哈希和验证
- JWT token 生成和验证

**接口**：

```typescript
interface AuthService {
  register(email: string, password: string): Promise<User>;
  login(email: string, password: string): Promise<{accessToken, refreshToken}>;
  resetPassword(email: string): Promise<void>;
  verifyToken(token: string): Promise<User>;
}
```

## 数据模型

### User 模型

```typescript
interface User {
  id: string;           // 用户 ID
  email: string;        // 邮箱
  passwordHash: string; // 密码哈希
  verified: boolean;    // 是否验证邮箱
  createdAt: Date;      // 创建时间
  updatedAt: Date;      // 更新时间
}
```

### 数据库设计

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

## 接口设计

### API 1：用户注册

```
POST /api/auth/register

请求：
{
  "email": "string",
  "password": "string"
}

响应：
{
  "id": "string",
  "email": "string",
  "message": "注册成功，请验证邮箱"
}

错误：
- 400: 邮箱已注册
- 422: 密码强度不足
```

### API 2：用户登录

```
POST /api/auth/login

请求：
{
  "email": "string",
  "password": "string"
}

响应：
{
  "accessToken": "string",
  "refreshToken": "string",
  "user": {
    "id": "string",
    "email": "string"
  }
}

错误：
- 401: 邮箱或密码错误
```

## 错误处理

### 错误类型

| 错误类型 | 处理方式 | 用户提示 |
|---------|---------|---------|
| 邮箱已注册 | 返回 400 | "邮箱已注册" |
| 密码错误 | 返回 401 | "邮箱或密码错误" |
| Token 过期 | 返回 401 | "登录已过期，请重新登录" |

### 错误码定义

| 错误码 | 含义 | HTTP 状态码 |
|--------|------|------------|
| AUTH_001 | 邮箱已注册 | 400 |
| AUTH_002 | 密码强度不足 | 422 |
| AUTH_003 | 邮箱或密码错误 | 401 |
| AUTH_004 | Token 过期 | 401 |

## 安全设计

### 认证
- 使用 JWT 进行无状态认证
- Access Token 有效期 15 分钟
- Refresh Token 有效期 7 天

### 授权
- 使用中间件验证 token
- 从 token 中提取用户信息

### 数据保护
- 密码使用 bcrypt 哈希（cost factor 12）
- 敏感信息不返回给客户端
- 使用 HTTPS 传输

## 性能设计

### 性能目标
- 注册接口响应时间 < 500ms
- 登录接口响应时间 < 200ms
- 支持 1000 并发用户

### 优化策略
- 数据库连接池
- 密码哈希异步处理
- 缓存热门查询

## 扩展性设计

### 未来扩展点
- 第三方登录 — 预留 OAuth 接口
- 手机号登录 — 预留 SMS 验证接口
- MFA — 预留 TOTP 接口

### 扩展方式
- 使用策略模式支持多种认证方式
- 使用插件机制扩展验证逻辑

## 测试策略

### 单元测试
- AuthService 的所有方法
- 密码哈希和验证
- JWT token 生成和验证

### 集成测试
- API 接口的完整流程
- 数据库操作
- 错误处理

### 端到端测试
- 注册→验证→登录 完整流程
- 密码重置完整流程
- Token 刷新流程

## 竞品分析

### 竞品 1：Auth0
- 提供完整的认证解决方案
- 优点：功能全面、安全可靠
- 缺点：成本高、依赖第三方

### 竞品 2：Firebase Auth
- 提供简单的认证 API
- 优点：易用、免费额度
- 缺点：定制性差、依赖 Google

### 设计决策
基于竞品分析，我们选择自建认证系统，因为：
- 需要完全控制用户数据
- 成本考虑（自建更便宜）
- 定制需求（支持特殊业务逻辑）
```

---

## 填写说明

### 架构图
- 使用 ASCII 图或 Mermaid 图
- 展示组件之间的关系
- 标注数据流向

### 组件设计
- 每个组件有明确的职责
- 接口定义要完整（参数、返回值、异常）
- 数据模型要覆盖所有场景

### 错误处理
- 定义所有可能的错误类型
- 明确每种错误的处理方式
- 提供用户友好的错误提示

### 安全设计
- 认证方式要明确
- 授权机制要清晰
- 数据保护措施要具体

### 性能设计
- 性能目标要可量化
- 优化策略要具体可行

### 扩展性设计
- 识别未来可能的扩展点
- 预留扩展接口
- 说明扩展方式

---

## 注意事项

1. **架构图要清晰**：一眼能看出组件关系和数据流向
2. **接口定义要完整**：参数、返回值、异常都要定义
3. **数据模型要覆盖所有场景**：正常、异常、边界都要考虑
4. **错误处理要具体**：不能只写"处理错误"，要写具体怎么处理
5. **安全设计要重视**：认证、授权、数据保护都要考虑
6. **性能目标要可量化**：不能只写"高性能"，要写具体指标
7. **扩展性要提前考虑**：预留扩展点，避免后期重构
