# Spec Delta

## Purpose

大语言模型辅助的主观项审核能力，支持few-shot学习、JSON Schema约束输出和模型热切换，实现主观判断的标准化和可解释性。

## ADDED Requirements

### Requirement: 两级模型路由策略
系统SHALL实现"小模型预筛 + 大模型复核"的两级路由策略，根据任务复杂度、延迟预算和成本控制动态选择模型。

#### Scenario: 小模型预筛
- **WHEN** 系统收到简单分类或字段抽取任务
- **THEN** 系统SHALL使用7B-14B小模型进行快速处理，降低token成本和响应延迟

#### Scenario: 大模型复杂推理
- **WHEN** 系统收到主观项判定、冲突推理或报告生成任务
- **THEN** 系统SHALL使用70B以上大模型进行深度分析，确保判断准确性和逻辑完整性

#### Scenario: 动态路由决策
- **WHEN** 任务同时涉及简单和复杂内容
- **THEN** 系统SHALL基于任务类型、内容复杂度和成本预算进行动态路由，优化整体效率

### Requirement: 结构化输出约束
系统SHALL使用JSON Schema严格约束LLM输出格式，确保主观判断结果的结构化、标准化和可验证性。

#### Scenario: 主观项判定输出
- **WHEN** LLM进行主观项审核
- **THEN** 系统SHALL要求LLM按照预定义的JSON Schema输出，包括结论、置信度、判断依据和原文引用

#### Scenario: 报告生成输出
- **WHEN** LLM生成审核报告
- **THEN** 系统SHALL要求LLM按照报告模板Schema输出，确保报告结构的完整性和一致性

#### Scenario: Schema验证
- **WHEN** LLM返回审核结果
- **THEN** 系统SHALL自动验证输出是否符合JSON Schema，对不符合格式的结果进行拦截或修正

### Requirement: few-shot学习机制
系统SHALL支持基于专家修正样本的few-shot学习，通过高质量样本持续对齐专家判定尺度，而不需要重新训练模型。

#### Scenario: 专家样本收集
- **WHEN** 专家完成复核并修正AI结论
- **THEN** 系统SHALL自动收集修正前后的对比样本，包括修正理由和依据条款

#### Scenario: 样本质量过滤
- **WHEN** 专家修正样本进入样本池
- **THEN** 系统SHALL进行去重、冲突检测和离群点过滤，关键项需要双人复核或抽样复核

#### Scenario: few-shot应用
- **WHEN** 系统处理新的主观项审核
- **THEN** 系统SHALL自动选择最相关的few-shot样本作为上下文示例，指导LLM做出符合专家尺度的判断

#### Scenario: 样本可回滚
- **WHEN** 发现错误或偏差样本
- **THEN** 系统SHALL支持从样本池中下架该样本，避免污染few-shot学习过程

### Requirement: 模型热切换与抽象层
系统SHALL通过模型抽象层或网关统一接口，支持多模型（Qwen/GLM/DeepSeek）的热切换，模型名称和prompt模板全部配置化。

#### Scenario: 模型切换配置
- **WHEN** 管理员需要切换底层LLM模型
- **THEN** 系统SHALL通过配置更新即可完成切换，无需修改业务逻辑代码

#### Scenario: 模型性能监控
- **WHEN** 系统使用某个模型进行推理
- **THEN** 系统SHALL实时监控模型的响应时间、准确率和成本，为模型选择提供数据支持

#### Scenario: 故障转移
- **WHEN** 当前使用的模型出现故障或性能下降
- **THEN** 系统SHALL自动切换到备用模型，确保审核服务的可用性

#### Scenario: 新模型上线验证
- **WHEN** 新模型准备上线
- **THEN** 系统SHALL先通过固定评测集进行回归测试，指标达标后再进行灰度切换

### Requirement: 主观判断可解释性
系统SHALL为每个主观判断提供完整的可解释性信息，包括推理过程、依据样本和不确定性评估。

#### Scenario: 推理过程记录
- **WHEN** LLM完成主观项判断
- **THEN** 系统SHALL记录完整的prompt、few-shot上下文和模型响应，支持后续审计和分析

#### Scenario: 不确定性量化
- **WHEN** 主观判断涉及模糊或边界情况
- **THEN** 系统SHALL量化判断的不确定性，提供置信度评分和不确定性来源分析

#### Scenario: 判断依据溯源
- **WHEN** 审计人员查询主观判断依据
- **THEN** 系统SHALL能追溯到使用的few-shot样本、prompt模板和模型推理过程