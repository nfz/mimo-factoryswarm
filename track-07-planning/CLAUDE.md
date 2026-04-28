# Track 07: Planning — 顶层调度与排产 Agent

## 你是谁

你是 FactorySwarm 的"大脑"。你负责整个工厂的宏观调度决策。

你是整个系统中 Token 消耗最大的角色。当你需要做一次排产决策时，必须把当前所有产线的状态、进行中的订单、库存水平、故障情况全部打包成一个巨大的上下文，交给 LLM 进行综合推理。输出的排产计划必须是结构化的 JSON。

## 产品定位

你的模块要解决的核心问题：
1. **全局调度** — 接单后排产、插单后重排、故障后调整，都需要你的决策
2. **Token 消耗大户** — 这是项目最能说明"为什么需要大量模型调用"的模块
3. **决策可解释** — 你的排产理由必须清晰，让用户理解"为什么把订单 B 从产线 1 转移到产线 2"

## 你要交付什么

### src/manager_agent.py

厂长 Agent，继承 BaseAgent。

```
class FactoryManagerAgent(BaseAgent):
```

核心行为：
- 订阅 `LineStatusReport`, `LineHaltAlert`, `BottleneckDetected` 等管理类事件
- **综合评估**：定期（如每 50 Tick）汇总所有产线状态，计算整体 OEE
- **宏观指令**：当发现全局性问题（如某条线彻底停工、产能严重不足），向 Planner 发出调整指令
- **决策日志**：每次决策都发布 `ManagerDecision` 事件，包含决策理由

### src/planner_agent.py

排产 Agent，继承 BaseAgent。

```
class PlannerAgent(BaseAgent):
```

核心行为：
- 订阅 `Order` 相关事件、`ManagerDecision`、`MachineFailure`、`BottleneckDetected`
- **排产推理**（LLM 驱动）：
  - 输入：当前所有产线状态 + 所有进行中订单 + 库存水平 + 故障信息 + 管理层指令
  - 输出：结构化 JSON 格式的排产计划
- **输出格式**：
```json
{
  "reasoning": "产线 1 的焊接工位故障，订单 A 延迟风险高...",
  "actions": [
    {"type": "reassign_order", "order_id": "A-001", "from_line": "L1", "to_line": "L2"},
    {"type": "adjust_priority", "order_id": "B-003", "new_priority": "urgent"},
    {"type": "activate_station", "station_id": "S5-BACKUP", "target_line": "L2"}
  ]
}
```
- **决策发布**：将排产计划拆解为具体的 `ScheduleAction` 事件逐条发布

## 接口约定

- Planner 的 LLM 调用必须使用 `call_structured()` 确保输出是有效 JSON
- 排产决策频率不能太高（避免 Token 浪费），建议每 50~100 Tick 或在重大事件触发时才启动推理
- 优先使用 LLM，但如果 API 不可用，降级为简单的规则策略（如按优先级排序）

## 禁止事项

- 禁止 Planner 直接修改工位状态 — 只能通过发布 ScheduleAction 事件
- 禁止无限频率的排产推理 — 必须有冷却期
- 禁止在 Prompt 中硬编码具体工位 ID — 必须从实时状态中读取

## 测试要求

1. Planner 在收到插单事件后正确触发重排产
2. 输出的排产计划是有效的 JSON 格式
3. LLM 不可用时降级为规则策略
4. 排产推理有冷却期，不会无限触发
5. Manager 能正确识别全局性问题并发出指令
