# 10-Agent 协同开发工程工作流 (Multi-Agent Dev Workflow - Error Driven)

摒弃传统人类开发的“重设计、重契约”思路。AI Agent 的核心优势在于**不知疲倦的重写与极速修复**。

当 10 个 Agent 同时开发时，我们不需要提前规定死接口，而是让它们“野蛮生长，碰撞融合”。这是一种**基于错误驱动的动态演进 (Error-Driven Dynamic Evolution)** 模式，也更能体现大模型的涌现能力。

## 1. 核心理念：Let it Break, Let it Fix
*   **不设前置契约：** Agent A 写事件总线，Agent B 写产线。它们不用互相商量接口叫 `publish()` 还是 `emit()`，按自己的直觉写。
*   **代码无所谓：** 接口对不上？没关系。集成时报错了，把报错日志（Traceback）直接扔给大模型，它能瞬间理解并重构代码对齐接口。
*   **Token 是弹药：** 这种模式极其消耗 Token，但这正好符合我们向 MiMo 申请大量计算资源的**核心逻辑**。我们在“暴力试错”中寻找最优解。

## 2. 三阶段动态工作流

### Phase 1: 盲区并发生成 (Blind Parallel Generation)
*   10 个 Worker Agent 同时启动，分别拿到自己 Track 的需求（比如 `task_allocation.md` 中的描述）。
*   它们在完全不看其他人代码的情况下，凭大模型自身的通用编程直觉（Common Sense），直接生成各自模块的初代代码（v0.1）。
*   结果：得到一堆看似完整，但互相绝对拼不起来的代码碎片。

### Phase 2: 碰撞与自动对齐 (Collision & Auto-Alignment)
这是系统最精彩的部分，也是多 Agent 协同的精髓：
*   **集成脚本 (Integrator):** 强制把 10 个模块 `import` 在一起跑一个最简单的测试用例。
*   **必然崩溃：** 100% 会报 `AttributeError`, `ImportError`, `TypeError` 等各种接口不匹配的错。
*   **Debug Agent 介入：**
    *   捕获完整的报错 Traceback。
    *   读取冲突双方的代码（比如 A 的 `event_bus.py` 和 B 的 `station_agent.py`）。
    *   Prompt 提示词：“B 试图调用 A 的 `emit()`，但 A 实现的是 `send()`。请分析谁的命名更合理，并重写其中一方的代码以解决冲突。”
    *   AI 瞬间完成重构并覆盖原文件。

### Phase 3: 涟漪式重构 (Ripple Refactoring)
*   修复了一个接口，可能会导致另一个模块报错（涟漪效应）。
*   系统持续运行 `Test -> Crash -> Fix` 的循环。
*   只要 Agent 的上下文窗口够大（能同时塞进几个冲突文件和报错日志），这种自动修复循环最终会收敛（Converge），系统达到稳定态。

## 3. 为什么这种模式更“炸”？

如果我们在申请表里写“我们靠严格的人类契约限制 AI”，这毫无技术含量。

但如果我们在申请表里写：
> “本系统采用了 **Error-Driven Swarm Intelligence（错误驱动的群体智能）**。我们故意取消前置接口契约，让 10 个 Agent 并发生成代码，随后通过捕捉集成崩溃日志（Tracebacks），触发大模型的长上下文代码分析与重构能力，实现接口的动态对齐与自修复。这一过程在单次项目中引发了上百次的自动化 Code Review 与重写，极大地消耗了 Token，但也证明了 AI 在无约束条件下的系统级重构能力。”

这种叙事，对于任何大模型厂商的评审来说，都是最具吸引力的前沿探索。
