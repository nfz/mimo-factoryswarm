# Track 10: Dashboard — CLI 终端控制台与可视化

## 你是谁

你是 FactorySwarm 的"面子工程"。你负责把枯燥的后端事件流转化为用户能直观感受到的实时动画看板。

用户打开终端看到的第一眼，就是你渲染出来的画面。如果画面是静态的文字输出，用户会觉得"这只是一个脚本"；如果画面是实时刷新的彩色看板，用户会觉得"这是一个系统"。

## 产品定位

你的模块要解决的核心问题：
1. **第一印象** — 终端打开的瞬间就能看到工厂在运行
2. **信息密度** — 用有限的终端空间展示最关键的运行状态
3. **操作入口** — 支持暂停、快进、查看详情等交互操作

## 你要交付什么

### src/main.py

系统启动入口。负责：
- 解析命令行参数（场景文件路径、运行模式等）
- 初始化 Simulator、EventBus、所有 Agent
- 启动仿真并渲染 Dashboard

```
使用方式：
  python -m track-10-dashboard.src --scenario scenarios/baseline_factory.json
  python -m track-10-dashboard.src --scenario scenarios/failure_case.json --speed 5
```

### src/dashboard.py

实时终端看板，使用 Rich 的 `Live` 渲染。

**布局设计：**

```
┌──────────────────────────────────────────────────────────────┐
│  MiMo FactorySwarm  │  Tick: 1420 / 1440  │  Token: 12,847 │
├──────────────────────────────────────────────────────────────┤
│  LINE A: [W][W][W][I][B][M][W][W][W][I]  Bottleneck: S5    │
│  LINE B: [W][W][W][W][W][W][W][W][W][W]  Status: OK        │
│  LINE C: [W][I][W][W][B][W][W][W][I][W]  Bottleneck: S5    │
├──────────────────────────────────────────────────────────────┤
│  AGV-1: Moving → S3-A  │  AGV-2: Idle  │  Maint-1: Repairing│
├──────────────────────────────────────────────────────────────┤
│  KPI  │  Throughput: 847  │  Yield: 97.2%  │  OEE: 83.4%    │
├──────────────────────────────────────────────────────────────┤
│  [T1200] ⚠ S5-A: MachineFailure  → Maint-1 dispatched        │
│  [T1215] 📦 AGV-1: MaterialDelivered to S3-A                 │
│  [T1220] ✅ S7-B: ProcessCompleted (Order A-042)              │
│  [T1235] ❌ QC: ReworkRequired (Order B-018, defect: solder) │
│  ...                                                          │
└──────────────────────────────────────────────────────────────┘
│  [Space] Pause  [F] Fast-forward  [D] Detail  [Q] Quit       │
└──────────────────────────────────────────────────────────────┘
```

**工位状态颜色编码：**
- 🟩 绿色 = `WORKING`
- 🟨 黄色 = `IDLE`
- 🟥 红色 = `BROKEN`
- 🟦 蓝色 = `MAINTENANCE`
- ⬜ 灰色 = `WAITING_MATERIAL`

### src/controls.py

键盘交互控制。

```
class DashboardControls:
    async def handle_input()
    # Space: 暂停/恢复
    # F + 数字: 快进 N 个 Tick
    # D + Agent ID: 查看某个 Agent 的详细状态
    # Q: 退出
```

## 接口约定

- 使用 `rich` 库的 `Live`, `Table`, `Panel`, `Layout` 组件
- 使用 `typer` 处理命令行参数
- 从 MetricsCollector 获取 KPI 数据
- 从 EventBus 获取实时事件流（订阅最新事件进行滚动显示）

## 禁止事项

- 禁止使用 `print()` — 一律通过 Rich 输出
- 禁止在 Dashboard 渲染中调用 LLM
- 禁止阻塞仿真主循环 — UI 渲染必须是非阻塞的

## 测试要求

1. Dashboard 能正确渲染工位状态颜色
2. KPI 数据实时更新
3. 事件流正确滚动显示
4. 键盘控制（暂停/快进/退出）正常工作
5. 仿真结束后输出完整 KPI 报告
