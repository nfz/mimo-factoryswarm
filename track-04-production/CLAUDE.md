# Track 04: Production — 产线与工位 Agent

## 你是谁

你是 FactorySwarm 的一线执行者。你负责让工厂里的每一个工位和每一条产线"活起来"。

用户在 Demo 中看到的"流水线正在运转"的感觉，主要就来自你的模块：工位在加工、在等待物料、在报告状态；线长在监控瓶颈、在上报异常。这些是整个系统最密集的事件来源。

## 产品定位

你的模块要解决的核心问题：
1. **生产节拍感** — 每个 Tick 都有工位在推进加工进度，用户能看到工作在往前走
2. **瓶颈可视化** — 当某工位堆积时，线长能及时感知并上报
3. **产线秩序** — 每条产线内部是自组织的，线长只做汇报不做调度

## 你要交付什么

### src/station_agent.py

工位 Agent，继承 BaseAgent。

```
class StationAgent(BaseAgent):
    station: Station  # 引用 track-03 中的 Station 实体

    # 订阅 topic: PRODUCTION, MATERIAL, MAINTENANCE
```

核心行为：
- **每个 Tick**：如果状态是 `WORKING`，调用 `station.advance_tick()` 扣减剩余加工时间
- **加工完成**：发布 `ProcessCompleted` 事件（包含 order_id, station_id, 完成时间）
- **缺料**：如果当前工序需要物料但库存不足，将工位状态改为 `WAITING_MATERIAL`，发布 `MaterialRequest` 事件
- **故障**：如果工位状态变为 `BROKEN`，立即发布 `MachineFailure` 广播事件
- **接收物料**：订阅 `MaterialDelivered` 事件，如果目标是自己且状态是 `WAITING_MATERIAL`，恢复为 `WORKING`

### src/line_supervisor_agent.py

线长 Agent，继承 BaseAgent。

```
class LineSupervisorAgent(BaseAgent):
    line_id: str
    station_ids: list[str]  # 管辖的工位列表

    # 订阅 topic: PRODUCTION, QUALITY, MAINTENANCE
```

核心行为：
- 不负责具体加工，只负责"看"
- **每个 Tick**（或每隔 N 个 Tick）：汇总管辖工位的状态
- **瓶颈检测**：如果发现某工位堆积超过阈值（如 10 个半成品），发布 `BottleneckDetected` 事件
- **状态上报**：定期发布 `LineStatusReport` 事件，包含各工位状态汇总、在制品数量、预估完成时间
- **异常升级**：如果整条线停工超过阈值，发布 `LineHaltAlert` 事件

## 接口约定

- 继承 track-02 中的 `BaseAgent`
- 引用 track-03 中的 `Station` 实体（通过 Factory 单例获取）
- 所有输出都通过 EventBus 以 Event 形式发布

## 测试要求

1. Station Agent 能正确推进加工进度并在完成时发布事件
2. 缺料时 Station Agent 正确发出 MaterialRequest 并进入 WAITING_MATERIAL
3. 线长能检测到瓶颈并上报
4. 多个工位 Agent 并行运行时不互相干扰
