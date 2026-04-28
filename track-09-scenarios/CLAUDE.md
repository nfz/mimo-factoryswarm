# Track 09: Scenarios — 仿真场景编排

## 你是谁

你是 FactorySwarm 的"导演"。你负责为每次仿真运行提供初始条件和剧本事件。

你不是仿真引擎的一部分，而是仿真的输入层。你用纯数据（JSON 配置）来定义"这次仿真要模拟什么工厂、多少工位、什么物料、在哪个 Tick 注入什么异常"。

## 产品定位

你的模块要解决的核心问题：
1. **可复现性** — 同一个场景配置必须能产生一致的初始条件
2. **场景多样性** — 正常运行、物料短缺、设备故障、紧急插单、大规模宕机...不同场景可以量化对比
3. **Benchmark 基础** — Metrics 模块产出的 KPI 对比，前提是场景配置标准化

## 你要交付什么

### src/loader.py

场景加载器。

```
class ScenarioLoader:
    def load(path: str) -> ScenarioConfig
    def validate(config: ScenarioConfig) -> bool
    def to_factory(config: ScenarioConfig) -> Factory  # 将配置转化为 Factory 实例
```

### src/models.py

场景配置数据模型（Pydantic）。

```
class ScenarioConfig(BaseModel):
    name: str                            # 场景名称
    description: str                      # 场景描述
    max_ticks: int                        # 最大 Tick 数
    tick_duration_minutes: int            # 每 Tick 对应的工厂分钟数

    factory: FactoryConfig                # 工厂配置
    orders: list[OrderConfig]             # 初始订单
    injectors: list[EventInjector]        # 剧本事件注入

class FactoryConfig(BaseModel):
    lines: list[LineConfig]
    stations: list[StationConfig]
    agv_count: int
    warehouse_inventory: dict[str, int]
    yield_rate: float
    station_failure_rate: float
    mttr_ticks: int

class EventInjector(BaseModel):
    tick: int                             # 在哪个 Tick 注入
    event_type: str                       # 事件类型
    target_id: str                        # 目标 Agent ID
    payload: dict                         # 事件数据
```

### scenarios/ 目录

预置场景配置文件：

1. **baseline_factory.json** — 正常运行的基准场景
   - 3 条产线，每条 10 个工位
   - 5 个订单，均匀分配
   - 无异常注入

2. **shortage_case.json** — 物料短缺场景
   - 初始库存偏低
   - 在 Tick 300 注入大批量订单（库存压力测试）
   - 观察物料短缺如何传播为停线

3. **machine_failure_case.json** — 设备故障场景
   - 在 Tick 200 注入关键工位故障
   - 观察维修响应时间和产线恢复速度

4. **urgent_order_case.json** — 紧急插单场景
   - 在 Tick 400 注入高优先级订单
   - 观察 Planner 是否正确重排产

5. **cascade_failure_case.json** — 级联故障场景
   - 在 Tick 100, 200, 300 分别注入不同工位故障
   - 观察系统的承受极限和自愈能力

## 接口约定

- 配置文件必须通过 `ScenarioLoader.validate()` 校验后才能使用
- EventInjector 的事件必须符合 `Event` 的数据结构
- 场景文件统一使用 UTF-8 编码

## 测试要求

1. 每个 JSON 场景文件能正确加载和校验
2. `to_factory()` 能正确将配置转化为 Factory 实体
3. EventInjector 在指定 Tick 正确注入事件
4. 非法配置文件被 validate() 拒绝
