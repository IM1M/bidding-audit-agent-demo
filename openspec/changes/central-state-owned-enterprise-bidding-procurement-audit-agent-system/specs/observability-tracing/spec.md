# Spec Delta

## Purpose

全链路可观测性，包括LLM调用追踪、成本统计、节点级监控和审计日志，支持系统性能分析、故障排查和持续优化。

## ADDED Requirements

### Requirement: LLM全链路追踪
系统SHALL使用Langfuse实现LLM调用的全链路追踪，包括节点级Trace、token统计、成本分析和few-shot命中率监控。

#### Scenario: 节点级Trace记录
- **WHEN** LangGraph状态机执行六节点审核流水线
- **THEN** 系统SHALL记录每个节点的开始时间、结束时间、输入数据、输出结果和中间状态

#### Scenario: LLM调用追踪
- **WHEN** 系统调用LLM进行审核
- **THEN** 系统SHALL记录完整的prompt、few-shot上下文、模型响应、token使用量和响应时间

#### Scenario: token成本统计
- **WHEN** LLM调用完成
- **THEN** 系统SHALL统计输入token数、输出token数和总成本，支持按模型、时间段、任务类型等多维度分析

#### Scenario: few-shot命中率监控
- **WHEN** 系统使用few-shot样本辅助LLM判断
- **THEN** 系统SHALL监控样本命中率、样本有效性和对判断准确性的影响

### Requirement: 基础设施监控
系统SHALL使用Prometheus+Grafana监控基础设施，包括CPU、GPU、内存、队列积压、API延迟等关键指标。

#### Scenario: 资源使用监控
- **WHEN** 系统运行时
- **THEN** 系统SHALL监控CPU使用率、GPU显存占用、内存使用量、磁盘IO和网络带宽

#### Scenario: 队列积压监控
- **WHEN** 系统处理多个采购包审核任务
- **THEN** 系统SHALL监控任务队列长度、处理延迟和积压情况，及时告警避免任务堆积

#### Scenario: API性能监控
- **WHEN** 系统对外提供API服务
- **THEN** 系统SHALL监控API响应时间（P50/P95/P99）、成功率、错误率和吞吐量

#### Scenario: 容器健康监控
- **WHEN** 系统在K8s容器中运行
- **THEN** 系统SHALL监控容器状态、重启次数、资源限制和健康检查结果

### Requirement: 业务指标监控
系统SHALL监控关键业务指标，包括审核效率、准确率、专家一致性和成本效益。

#### Scenario: 审核效率监控
- **WHEN** 系统处理招标文件
- **THEN** 系统SHALL监控单份文件处理时间、端到端审查时间和专家复核时间，确保达到8分钟自动审查和1.2小时端到端的目标

#### Scenario: 准确率监控
- **WHEN** 专家复核完成
- **THEN** 系统SHALL计算AI审核与专家结论的一致率，监控审查准确率变化趋势

#### Scenario: 专家一致性监控
- **WHEN** 多名专家复核同一内容
- **THEN** 系统SHALL计算跨专家复评结论一致率，监控专家尺度对齐情况

#### Scenario: 成本效益分析
- **WHEN** 系统运行一段时间
- **THEN** 系统SHALL分析token成本变化、资源使用效率和整体成本效益比，验证38%成本下降目标

### Requirement: 告警与通知机制
系统SHALL建立多级告警机制，根据严重程度通过不同渠道通知相关人员。

#### Scenario: 关键错误告警
- **WHEN** 系统发生关键错误（如审核流水线中断、数据库连接失败）
- **THEN** 系统SHALL立即通过短信、钉钉、微信等渠道通知运维人员

#### Scenario: 性能阈值告警
- **WHEN** 系统性能指标超过预设阈值（如API延迟超过10秒、队列积压超过100）
- **THEN** 系统SHALL发送警告通知，提示可能需要扩容或优化

#### Scenario: 业务异常告警
- **WHEN** 业务指标出现异常（如准确率下降5%、专家一致率低于80%）
- **THEN** 系统SHALL通知业务负责人，提示可能需要调整规则或模型

#### Scenario: 告警集成
- **WHEN** 客户已有监控平台
- **THEN** 系统SHALL将告警统一接入客户现有监控平台，支持自定义告警规则和通知方式

### Requirement: 审计日志与追溯
系统SHALL记录完整的审计日志，支持操作追溯和安全审计，所有日志脱敏处理避免数据泄露。

#### Scenario: 操作完整留痕
- **WHEN** 用户进行任何操作（审核、复核、配置修改等）
- **THEN** 系统SHALL记录操作时间、操作人、操作内容、操作前状态和操作后状态

#### Scenario: 数据访问审计
- **WHEN** 用户访问敏感数据（招标文件、审核结论、专家修正样本）
- **THEN** 系统SHALL记录访问时间、访问人、访问内容和访问目的

#### Scenario: 系统变更审计
- **WHEN** 系统配置或规则发生变更
- **THEN** 系统SHALL记录变更时间、变更人、变更内容和变更原因，支持变更回滚

#### Scenario: 日志脱敏保护
- **WHEN** 系统记录审计日志
- **THEN** 系统SHALL对敏感信息进行脱敏处理，Trace里不落原文，只存脱敏后的结构化数据

#### Scenario: 日志留存合规
- **WHEN** 系统存储审计日志
- **THEN** 系统SHALL确保日志留存不少于180天，符合等保三级要求，支持按需导出和归档