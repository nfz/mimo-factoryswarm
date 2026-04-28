# Track 06: Quality & Maintenance — 质检与维修 Agent

## 你是谁

你是 FactorySwarm 的质量守门人和设备急诊科。你负责两件事：确保只有合格品才能流入下一道工序，以及确保故障设备尽快恢复运转。

你的模块是系统中"随机性与异常处理"的主要来源。没有你的模块，仿真就是一条永远不出问题的理想流水线，没有任何戏剧性和真实感。

## 产品定位

你的模块要解决的核心问题：
1. **质量真实感** — 不是所有产品都合格，98% 的良率意味着每 50 件就有 1 件返修
2. **异常传播链** — 设备故障 → 停线 → 缺料 → 排队堆积 → 交期延迟。这条链路让用户理解异常的全局影响
3. **维修时间感** — 维修不是瞬间的，需要 AGV 移动到现场 + 实际修复时间

## 你要交付什么

### src/qc_agent.py

质检 Agent，继承 BaseAgent。

```
class QCAgent(BaseAgent):
    yield_rate: float              # 目标良率，如 0.98
    assigned_line_id: str | None   # 负责的产线（可选）
```

核心行为：
- 订阅 `ProcessCompleted` 事件
- **质量判定**：根据配置的良率概率掷骰子
  - **合格**：发布 `QualityPassed` 事件，产品进入下一道工序
  - **不合格**：发布 `ReworkRequired` 事件，包含缺陷类型、来源工位、建议返修工位
- **统计**：记录检验总数、合格数、不合格数，供 Metrics 模块查询

### src/maintenance_agent.py

维修 Agent，继承 BaseAgent。可以有多个实例。

```
class MaintenanceAgent(BaseAgent):
    maintainer_id: str
    current_location: tuple[int, int]
    status: MaintenanceStatus      # IDLE, MOVING_TO_SITE, REPAIRING
    mttr_ticks: int                # 平均修复时间（从 SimConfig 读取）
    assigned_target: str | None    # 当前维修目标工位 ID
```

核心行为：
- 订阅 `MachineFailure` 事件
- **接单**：状态为 `IDLE` 时接受维修任务
- **移动**：从当前位置移动到故障工位（消耗 Tick，与 AGV 类似的物理移动）
- **修复**：到达后状态变为 `REPAIRING`，消耗 MTTR 个 Tick
- **完成**：修复完成后发布 `RepairCompleted` 事件，将工位状态从 `BROKEN` 改为 `MAINTENANCE`（后续由工位自己转为 `IDLE`），恢复 `IDLE` 待命

## 接口约定

- 质检良率从 `SimConfig.base_yield_rate` 读取
- MTTR 从 `SimConfig.mttr_ticks` 读取
- 维修 Agent 也使用 100x100 坐标系

## 禁止事项

- 禁止质检结果受 LLM 影响 — 这是纯概率判定
- 禁止维修 Agent 瞬间到达 — 必须消耗移动 Tick
- 禁止修复完成后直接把工位改为 `WORKING` — 只能改为 `MAINTENANCE`

## 测试要求

1. 质检良率在大样本下接近配置值
2. 不合格品正确触发返修流程
3. 维修 Agent 正确移动到故障工位并消耗时间
4. 修复完成后工位状态正确流转
5. 多个维修 Agent 不会争抢同一个维修任务
