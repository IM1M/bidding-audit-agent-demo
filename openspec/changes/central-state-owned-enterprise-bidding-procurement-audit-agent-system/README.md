# 招标文件AI审核系统 - 演示复现版

> **说明**：本 change 为完整系统设计规范；公开演示仅实现前端切片，见 `../archive/2026-11-25-public-demo-ui`。本目录保留为设计参考，未执行 apply 与 archive，因此任务清单保持未勾选状态。

## 项目说明

本系统为**招标文件AI审核系统**的演示复现版本，基于实际项目经验和技术方案构建，用于技术展示和个人简历项目呈现。

### 重要声明

1. **团队协作成果**：原系统为团队协作交付的商业项目，本文档及代码中的技术方案、架构设计和性能指标均为**团队协作成果**，非个人独立完成。

2. **脱敏处理**：
   - 所有示例数据均为模拟值，不包含实际业务信息
   - 客户信息、供应商名称、金额等敏感数据已移除
   - 系统集成描述已泛化，不涉及具体客户系统

3. **指标说明**：
   - 效率提升、准确率等指标为原系统**团队验证结果**
   - 演示版指标为参考值，实际效果依赖具体业务场景
   - 不主张演示版的独立交付价值

## 功能特性

### 核心审核流程
- **六节点状态机**：文档解析 → 条款抽取 → 双分支判定 → 证据绑定 → 分级报告 → 专家复核
- **双路判定引擎**：客观规则引擎 + 主观LLM辅助
- **完整证据链**：每条结论可追溯原文位置和判定依据
- **专家回流机制**：修正样本持续优化模型判断

### 演示功能
- **FR-01 示例文档**：脱敏文档元信息展示
- **FR-02 流水线可视化**：六节点状态与耗时
- **FR-03 分级报告**：红/黄/绿三级结论展示
- **FR-04 证据链定位**：规则依据与原文高亮
- **FR-05 专家复核**：强制修正理由填写
- **FR-06 指标看板**：核心业务指标展示

## 技术栈

### 后端
- **Python 3.9+**
- **FastAPI**：Web框架
- **LangGraph**：工作流编排
- **Celery**：异步任务队列
- **PostgreSQL + pgvector**：数据存储与向量检索
- **PaddleOCR**：文档解析

### 前端
- **Jinja2模板引擎**
- **原生HTML/CSS/JavaScript**
- 响应式设计，企业级视觉风格
- 无React/Vue等前端框架

### 部署
- **Docker + Kubernetes**
- 支持多架构部署（amd64/arm64）
- 监控：Prometheus + Grafana + Langfuse

## 设计原则

### 视觉风格
- **简约克制**：黑白灰为主色调，低饱和度状态色
- **企业感**：系统字体，不对称栅格，充足留白
- **无模板化AI感**：不使用通用插画、emoji和营销文案

### 交互设计
- **必要动效**：仅150-200ms状态过渡
- **明确反馈**：操作状态清晰可见
- **无障碍考虑**：颜色不单独传达信息

## 部署运行

### 环境要求
```bash
# Python环境
python 3.9+
pip 21.0+

# 数据库
PostgreSQL 13+ with pgvector
Redis 6.0+

# 可选：GPU支持（用于OCR和LLM推理）
CUDA 11.8+
NVIDIA驱动兼容版本
```

### 快速启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd bidding-audit-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑.env文件，设置数据库连接等

# 4. 初始化数据库
python scripts/init_db.py

# 5. 启动服务
# 后端API服务
uvicorn app.main:app --reload --port 8000

# Celery worker（新终端）
celery -A app.celery_app worker --loglevel=info

# 前端访问
# 浏览器打开 http://localhost:8000
```

### Docker部署
```bash
# 构建镜像
docker buildx build --platform linux/amd64,linux/arm64 -t bidding-audit-demo .

# 运行容器
docker run -p 8000:8000 --env-file .env bidding-audit-demo
```

## 项目结构

```
bidding-audit-system/
├── app/                          # 应用主目录
│   ├── api/                      # API路由
│   ├── core/                     # 核心模块
│   ├── models/                   # 数据模型
│   ├── services/                 # 业务服务
│   ├── templates/                # Jinja2模板
│   ├── static/                   # 静态资源
│   └── main.py                   # FastAPI应用入口
├── celery_app/                   # Celery配置
├── config/                       # 配置文件
├── scripts/                      # 工具脚本
├── tests/                        # 测试文件
├── requirements.txt              # Python依赖
├── Dockerfile                    # Docker配置
├── docker-compose.yml            # Docker编排
└── README.md                     # 项目说明
```

## 开发说明

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解（Type Hints）
- 函数和类有清晰的文档字符串
- 前端代码保持原生简洁，避免过度工程化

### 测试要求
- 单元测试覆盖核心业务逻辑
- 集成测试验证系统流程
- 前端功能测试确保交互正常
- 性能测试验证8分钟审查目标

### 贡献指南
1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request
5. 通过代码审查和测试

## 许可与声明

本项目为个人求职展示作品，仅供学习与演示参考，不构成开源授权。

本系统涉及的技术方案与架构设计源自实际商业项目经验，相关知识产权归原项目团队所有。公开版本已做脱敏处理，不含真实业务数据与系统实现，请勿用于商业用途。

## 联系方式

如有技术问题或合作意向，请通过项目Issue或邮件联系。

---

*最后更新：2024年*
*版本：演示复现版 v1.0*