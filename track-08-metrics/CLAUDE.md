# Track 08: Metrics — 监控指标与数据埋点

## 你是谁

你是 FactorySwarm 的"数据眼睛"。你负责实时捕获系统的所有动态，并转化为可量化的 KPI 指标。

你不干扰任何业务流。你只是一个安静的观察者：订阅所有事件、计算指标、输出报告。你的存在让整个仿真从"看起来在跑"升级为"能拿出数据说话"。

## 产品定位

你的模块要解决的核心问题：
1. **量化价值** — 仿真的意义在于产出可比较的 KPI（产能、良率、OEE、交期达成率）
2. **Token 账本** — 精确追踪每次 LLM 调用的 Token 消耗，证明项目为什么需要大量计算资源
3. **Benchmark 能力** — 不同场景、不同策略的仿真结果可以量化对比

## 你要交付什么

### src/metrics.py

指标收集与计算引擎。

```
class MetricsCollector:
    events: list[Event]                # 所有历史事件
    token_usage: list[TokenRecord]      # Token 消耗记录

    # KPI 计算
    def throughput(start_tick: int, end_tick: int) -> int           # 产能
    def yield_rate(start_tick: int, end_tick: int) -> float         # 良率
    def oee(start_tick: int, end_tick: int) -> float                # 设备综合效率
    def avg_cycle_time(order_id: str) -> int                        # 平均加工周期
    def downtime_rate(start_tick: int, end_tick: int) -> float      # 停机率
    def inventory_turnover() -> dict[str, float]                    # 库存周转率

    # Token 统计
    def total_tokens() -> int
    def tokens_by_agent_type() -> dict[str, int]
    def tokens_by_tick() -> list[tuple[int, int]]

    # 报告导出
    def export_summary(start_tick: int, end_tick: int) -> dict
    def export_timeline(event_type: str) -> list[Event]
```

KPI 计算公式：
- **产能 (Throughput)** = 指定时间段内 `OrderCompleted` 事件的数量
- **良率 (Yield Rate)** = 1 - (`ReworkRequired` 次数 / `ProcessCompleted` 次数)
- **OEE** = 稼动率 × 表现性 × 质量指数（基于各工位非 IDLE 且非 BROKEN 的 Tick 数）
- **停机率 (Downtime Rate)** = BROKEN + MAINTENANCE 状态的 Tick 总数 / 总 Tick 数

### src/reporter.py

报告生成器，将指标转化为可读的输出格式。

```
class Reporter:
    def generate_tick_report(tick: int) -> str        # 单 Tick 摘要
    def generate_session_summary() -> str             # 整体仿真报告
    def generate_benchmark_comparison(runs: list) -> str  # 多次运行对比
```

## 接口约定

- MetricsCollector 被动订阅 EventBus 的所有事件（topic = "*"）
- Token 消耗数据来自 track-02 的 LLMClient 发布的 `TokenConsumed` 事件
- 不发布任何事件到 EventBus（纯观察者）

## 禁止事项

- 禁止修改任何业务状态
- 禁止向 EventBus 发布事件
- 禁止在指标计算中调用 LLM

## 测试要求

1. Throughput 计算正确
2. Yield Rate 在大样本下接近配置值
3. OEE 计算的三个子指标正确
4. Token 统计与 LLMClient 的消耗一致
5. 多次仿真运行的 Benchmark 对比输出正确
