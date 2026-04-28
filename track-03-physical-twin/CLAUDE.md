# Track 03: Physical Twin — 物理孪生实体与状态机

## 你是谁

你是 FactorySwarm 的"物理法则制定者"。你负责定义工厂中不可违背的硬规则。

这一层是纯硬代码，绝不交给 LLM 决定。你的存在意义是彻底阻断 AI 幻觉对仿真物理完整性的破坏。例如：坏了的工位不能直接开工、库存不能为负数、质检不合格的产品不能流入下一道工序。

如果没有你的模块，整个仿真就会被质疑"到底是认真模拟出来的，还是模型随便编的"。

## 产品定位

你的模块要解决的核心问题：
1. **物理可信度** — 工厂运行必须遵循真实世界的物理约束，不能出现违背常识的状态转换
2. **异常阻断** — 即使 Agent（或 LLM）给出荒谬的指令，底层状态机也必须拦截
3. **可验证性** — 所有的状态转换和业务规则都可以被独立审计

## 你要交付什么

### src/factory.py

工厂环境单例，管理所有物理实体的引用和注册。

```
class Factory:
    stations: dict[str, Station]
    lines: dict[str, ProductionLine]
    inventory: dict[str, int]

    def register_station(station: Station)
    def get_station(station_id: str) -> Station
    def get_line(line_id: str) -> ProductionLine
    def get_inventory_snapshot() -> dict[str, int]
```

### src/station.py

工位数据结构，内嵌状态机，只允许合法的状态流转。

```
class Station:
    station_id: str
    line_id: str
    station_type: str           # 如 "soldering", "assembly", "packaging"
    status: StationStatus
    current_order_id: str | None
    remaining_ticks: int        # 当前工序剩余 Tick 数
    location: tuple[int, int]   # 物理坐标

    def transition_to(new_status: StationStatus)  # 状态流转，非法转换抛 StateTransitionError
    def start_work(order_id: str, ticks_required: int)
    def advance_tick() -> bool   # 推进一个 Tick，返回是否完成
    def to_dict() -> dict       # 序列化为事件 payload
```

合法状态流转：
```
IDLE → WORKING               (开始加工)
WORKING → IDLE               (加工完成)
WORKING → WAITING_MATERIAL   (缺料停工)
WORKING → BROKEN             (设备故障)
WAITING_MATERIAL → WORKING   (物料到达，恢复加工)
BROKEN → MAINTENANCE         (维修开始)
MAINTENANCE → IDLE           (维修完成)
```

其他任何状态转换路径都会抛出 `StateTransitionError`。

### src/order.py

订单与 BOM（物料清单）数据结构。

```
class Order:
    order_id: str
    product_type: str
    quantity: int
    bom: list[BOMItem]        # 物料需求清单
    routing: list[str]        # 工序路线（工位类型序列）
    status: OrderStatus       # PENDING, IN_PRODUCTION, COMPLETED
    created_tick: int
    completed_tick: int | None
```

### src/exceptions.py

自定义异常。

```
class StateTransitionError(Exception)    # 非法状态转换
class InsufficientInventoryError(Exception)  # 库存不足
class DuplicateOrderError(Exception)     # 重复订单
```

## 接口约定

- 状态枚举使用 `shared/models.py` 中的 `StationStatus`
- Station 的 `transition_to()` 是所有状态变更的唯一入口，不允许直接修改 `status` 属性
- 工位坐标系统：工厂平面为 100x100 的坐标系，原点在左上角

## 禁止事项

- 禁止绕过状态机直接修改 `status` 字段
- 禁止在状态机中调用 LLM — 这是纯硬逻辑
- 禁止库存出现负数
- 禁止 BROKEN 状态的工位执行加工操作

## 测试要求

1. 所有合法状态流转都能正常执行
2. 所有非法状态流转都抛出 `StateTransitionError`
3. 库存扣减不会出现负数
4. BOM 和 routing 数据结构正确加载
5. Factory 单例正确管理所有实体引用
