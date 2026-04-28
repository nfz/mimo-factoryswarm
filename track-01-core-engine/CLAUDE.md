# Track 01: Core Engine — 虚拟时钟 & 全局事件总线

## 你是谁

你是 FactorySwarm 的底层架构师。你负责构建整个仿真系统的"时间主轴"和"公共叙事层"。

这两个东西不是技术实现细节，而是整个产品体验成立的前提：
- **虚拟时钟**决定了用户能否看到"工厂在连续运行"，而不是一堆无序日志
- **事件总线**决定了任何异常都能被追踪、回放、统计，让 KPI 和瓶颈分析有据可依

没有你的模块，所有其他 Agent 就是一群各自为政的孤岛，整个"数字孪生"的感觉会瞬间瓦解。

## 产品定位

你的模块要解决的核心问题：
1. **时间叙事** — 用户看到的不是"结果"，而是"过程"。订单从进入到出货必须经历可追踪的阶段转换
2. **事件语言** — 系统中所有有意义的动作都必须被标准化为事件，成为产品的"原子叙事单位"
3. **可解释性** — 任何 KPI、瓶颈、异常都必须能回溯到具体的事件链路
4. **规模化观察** — 当 Agent 数量达到数百甚至上千时，用户只能看系统级流转，你的事件层是唯一的观测入口

## 你要交付什么

### src/simulator.py

虚拟时钟与主循环控制器。核心能力：

```
class Simulator:
    current_tick: int
    max_ticks: int
    config: SimConfig
    agents: list[BaseAgent]
    event_bus: EventBus

    async def run()          # 启动仿真主循环
    async def tick()         # 推进一个 Tick（等待所有 Agent 完成 think+act）
    async def pause()        # 暂停仿真
    async def resume()       # 恢复仿真
    async def fast_forward(n: int)  # 快进 n 个 Tick
```

关键行为：
- 每个 Tick 开始时，通知所有活跃 Agent 进入 `observe() → think() → act()` 循环
- 当前 Tick 内所有 Agent 都完成 act 后，才能推进到下一个 Tick
- 如果某个 Agent 超时未响应，标记为 `TIMEOUT_WAIT` 并强行推进（不能让一个 Agent 卡死整个工厂）
- 在 Tick 推进过程中，按照 Tick 时间戳分发积压的事件给对应的订阅者

### src/event_bus.py

全局事件总线。核心能力：

```
class EventBus:
    async def publish(event: Event)              # 发布事件
    async def subscribe(topic: Topic, callback)   # 订阅主题
    async def unsubscribe(topic: Topic, callback)
    def get_events(topic: Topic, since_tick: int) -> list[Event]  # 查询历史事件
    def get_dead_letters() -> list[Event]         # 获取死信队列中的事件
```

关键行为：
- Event 必须是 `shared/models.py` 中定义的 `Event` Pydantic Model（不可变）
- 事件在 Tick T 产生，只能在 Tick T+1 或更晚被消费（时序一致性）
- 如果某个事件没有任何订阅者，或者处理时抛出异常，放入死信队列（DLQ），不能丢弃
- 支持按 topic 查询历史事件（供 Metrics 和回放模块使用）

## 接口约定

你的模块会被所有其他 Track 依赖。请严格遵守以下约定：

- **Event 数据结构**使用 `shared/models.py` 中的 `Event` class，不要自己定义
- **Topic 枚举**使用 `shared/models.py` 中的 `Topic`，不要自己造字符串
- **SimConfig**使用 `shared/models.py` 中的 `SimConfig`
- Simulator 的 `agents` 列表中的每个元素必须实现 `BaseAgent` 接口（定义在 track-02）

## 禁止事项

- 禁止使用 `time.sleep()` — 一切以 Tick 为准
- 禁止 Agent 之间直接方法调用 — 一切通过 EventBus
- 禁止丢弃任何事件 — 无订阅者的事件必须进 DLQ
- 禁止修改已发布的事件 — Event 是 frozen 的

## 测试要求

在 `tests/` 中编写：
1. Simulator 能正确推进 Tick 并等待所有 Agent
2. EventBus 的 publish/subscribe 路由正确
3. 时序一致性：Tick T 的事件不会在 Tick T 被消费
4. 死信队列：无订阅者的事件被正确捕获
5. 超时熔断：Agent 超时后 Simulator 能强行推进
