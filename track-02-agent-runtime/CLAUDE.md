# Track 02: Agent Runtime — LLM 通信层 & Agent 基类

## 你是谁

你是 FactorySwarm 的"角色引擎"。你负责让每一个 Agent 看起来真的像一个有角色、有职责、有行为风格的工厂成员，而不是同一个模型换了十个名字。

如果你的模块做得好，用户看到排产 Agent 和维修 Agent 的输出会感觉"这真的是两个不同岗位的人在说话"。如果做得不好，整个系统就会退化成一个模型套了十层壳。

## 产品定位

你的模块要解决的核心问题：
1. **角色可信度** — 不同 Agent 的说话方式、处理方式、输出结构必须有明显区别
2. **行为标准化** — 每个 Agent 都遵循统一的生命周期（observe → think → act），但角色内容不同
3. **边界感** — 仓储 Agent 不会替代排产 Agent 做决策，维修 Agent 不会越权改订单
4. **Token 消耗合理化** — Token 不是白烧的，而是角色网络持续运转带来的业务消耗

## 你要交付什么

### utils/llm_client.py

LLM API 客户端封装。

```
class LLMClient:
    async def call(prompt: str, system: str = None, temperature: float = 0.7) -> str
    async def call_structured(prompt: str, response_model: type[BaseModel], ...) -> BaseModel
```

关键行为：
- 并发限制：使用 `asyncio.Semaphore` 控制最大并发请求数（默认 10）
- 指数退避重试：请求失败时按 1s → 2s → 4s → 8s 间隔重试，最多 3 次
- Token 追踪：每次调用后记录 `prompt_tokens` 和 `completion_tokens`，发布 `TokenConsumed` 事件到 EventBus
- 通过环境变量读取 API 配置：`LLM_API_BASE`, `LLM_API_KEY`, `LLM_MODEL`

### src/agent.py

Agent 基类，定义所有 Agent 的统一骨架。

```
class BaseAgent(ABC):
    agent_id: str
    agent_type: str          # 如 "station", "line_supervisor", "qc"
    subscribed_topics: list[Topic]
    status: str              # "active", "idle", "timeout"

    async def observe(tick: int) -> list[Event]     # 从 EventBus 读取订阅事件
    async def think(events: list[Event]) -> str      # LLM 推理或本地策略
    async def act(thought: str) -> list[Event]       # 发布事件或更新状态
    async def on_tick(tick: int)                     # observe → think → act 的编排
```

关键行为：
- `observe()` 只读取自己订阅的 Topic 的事件
- `think()` 是 Agent 的核心推理环节，子类必须实现。可以是 LLM 调用，也可以是纯逻辑
- `act()` 必须返回 Event 列表（即使为空列表），通过 EventBus 发布
- 如果 `think()` 或 `act()` 执行时间过长，Simulator 会标记为超时并强行推进

### prompts/ 目录

为不同 Agent 角色准备 system prompt 模板。每个文件是一个角色的 prompt：
- `station.md` — 工位 Agent 的角色定义和行为指引
- `line_supervisor.md` — 线长
- `warehouse.md` — 仓库
- `qc.md` — 质检
- `maintenance.md` — 维修
- `planner.md` — 排产
- `manager.md` — 厂长

每个 prompt 必须包含：角色身份、职责范围、输出格式要求、禁止事项。

## 接口约定

- 依赖 `shared/models.py` 中的 `Event`, `Topic`
- `BaseAgent.on_tick()` 的签名是 `Simulator` 调用 Agent 的唯一入口，所有 Track 都必须遵循
- LLMClient 通过环境变量配置，不硬编码 API 地址

## 禁止事项

- 禁止在 BaseAgent 中实现业务逻辑 — 业务逻辑由各 Track 的子类实现
- 禁止 Agent 之间直接 import — 一切通过 EventBus
- 禁止 think() 中返回非结构化输出 — 必须有明确的决策格式

## 测试要求

1. LLMClient 的并发限制和重试逻辑
2. BaseAgent 的 observe → think → act 生命周期编排
3. Token 消耗事件正确发布
4. 不同 Agent 子类的角色 prompt 正确加载
