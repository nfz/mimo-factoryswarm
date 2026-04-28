# Track 05: Logistics — 仓储与物流 Agent

## 你是谁

你是 FactorySwarm 的物流神经。你负责管理工厂内部的空间物流与库存水位。

用户在 Demo 中会看到这样的画面："11:20 某条线缺料 → 11:21 仓库确认库存 → 11:21 AGV 派发 → 11:29 AGV 到达 → 11:30 产线恢复"。这条链路的真实感，完全取决于你的模块。

物流延迟是真实的物理约束（AGV 有速度、有距离），不是瞬间传送。这个约束让仿真变得可信。

## 产品定位

你的模块要解决的核心问题：
1. **物流时间感** — 物料不能瞬间到达，AGV 搬运需要消耗真实的 Tick
2. **库存水位** — 仓库不是无限的，缺料会导致停线
3. **空间约束** — AGV 一次只能搬一趟，不能同时响应多个请求

## 你要交付什么

### src/warehouse_agent.py

仓库 Agent，继承 BaseAgent。

```
class WarehouseAgent(BaseAgent):
    inventory: dict[str, int]         # 物料库存 {"screws": 5000, "screens": 200}
    low_threshold: dict[str, int]     # 低库存阈值 {"screws": 500}
```

核心行为：
- 订阅 `MaterialRequest` 事件
- 收到请求后检查库存：
  - **充足**：扣减库存，发布 `MaterialDispatch` 事件（包含物料类型、数量、目标工位）
  - **不足**：发布 `InventoryWarning` 事件（包含物料类型、当前库存、需求数量）
- **低库存监控**：任何物料扣减后如果低于阈值，发布 `LowStockAlert` 事件
- **库存查询**：支持其他模块查询当前库存快照

### src/logistics_agent.py

AGV 物流 Agent，继承 BaseAgent。可以有多个实例（AGV-001, AGV-002...）。

```
class LogisticsAgent(BaseAgent):
    agv_id: str
    current_location: tuple[int, int]
    target_location: tuple[int, int] | None
    status: AGVStatus                 # IDLE, MOVING, LOADING, UNLOADING
    cargo: str | None                 # 当前携带的物料类型
    cargo_quantity: int
    speed: float                      # 每 Tick 移动的距离单位
```

核心行为：
- 订阅 `MaterialDispatch` 事件
- **接单**：如果状态是 `IDLE` 且事件未被其他 AGV 接走，接受任务
- **移动**：每个 Tick 按速度向目标移动，消耗实际的 Tick 数（`距离 / 速度`）
- **到达**：到达目标工位后，发布 `MaterialDelivered` 事件，状态恢复 `IDLE`
- **搬运途中**：状态为 `MOVING` 时不接受新请求

## 接口约定

- AGV 坐标使用 100x100 坐标系（与 track-03 工位坐标一致）
- 速度单位：每 Tick 移动的坐标距离
- 一次只能搬运一趟，不支持中途改目的地

## 禁止事项

- 禁止库存出现负数
- 禁止 AGV 瞬间传送（必须消耗移动 Tick）
- 禁止一个 AGV 同时执行多个搬运任务

## 测试要求

1. 仓库收到请求后正确扣减库存并派发 AGV
2. 库存不足时正确发出警告
3. AGV 移动消耗正确的 Tick 数
4. AGV 搬运途中拒绝新请求
5. 多个 AGV 不会争抢同一个搬运任务
