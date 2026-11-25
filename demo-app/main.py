from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

app = FastAPI(
    title="招标文件AI审核系统演示版",
    description="脱敏复现公开演示版本 - 仅用于技术展示",
    version="1.0.0"
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="templates")

# Mock数据状态管理
class MockDataManager:
    def __init__(self):
        self.current_document = None
        self.review_state = "not_started"  # not_started, in_progress, completed
        self.node_states = {}
        self.expert_review_data = {}
        self.metrics = {}
        self._init_mock_data()
    
    def _init_mock_data(self):
        # 示例文档数据
        self.current_document = {
            "id": "doc_001",
            "name": "招标文件示例-某市智慧城市建设项目",
            "pages": 52,
            "clauses": 187,
            "upload_time": "2024-01-15 10:30:00",
            "file_size": "8.2 MB",
            "description": "示例招标文件，已脱敏处理，用于演示AI审核系统工作流程"
        }
        
        # 六节点流水线初始状态
        self.node_states = {
            "document_parsing": {
                "id": "node_1",
                "name": "文档解析",
                "description": "OCR识别文档内容，提取文本结构",
                "status": "waiting",  # waiting, processing, completed, failed
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "can_retry": False
            },
            "clause_extraction": {
                "id": "node_2",
                "name": "条款抽取",
                "description": "智能识别招标条款，结构化存储",
                "status": "waiting",
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "can_retry": False
            },
            "dual_branch_judgment": {
                "id": "node_3",
                "name": "双分支判定",
                "description": "规则匹配与LLM推理双路并行审查",
                "status": "waiting",
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "can_retry": False
            },
            "evidence_binding": {
                "id": "node_4",
                "name": "证据绑定",
                "description": "关联审查结论与原文位置",
                "status": "waiting",
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "can_retry": False
            },
            "grading_report": {
                "id": "node_5",
                "name": "分级报告",
                "description": "生成红黄绿三级风险报告",
                "status": "waiting",
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "can_retry": False
            },
            "expert_review": {
                "id": "node_6",
                "name": "专家复核",
                "description": "人工审核确认与修正",
                "status": "waiting",
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "can_retry": False
            }
        }
        
        # 示例审查结果
        self.review_results = [
            {
                "id": "result_001",
                "clause_id": "clause_045",
                "description": "投标保证金条款未明确退还时间",
                "risk_level": "high",  # high, medium, low
                "confidence": 0.87,
                "page": 12,
                "position": {"x": 120, "y": 340, "width": 280, "height": 45},
                "rule_id": "rule_002_v1.2",
                "rule_version": "v1.2",
                "rule_description": "保证金条款必须明确退还时间和条件",
                "rule_quote": "根据《招标投标法实施条例》第35条：投标保证金应当在招标文件中明确规定退还的时间、条件和方式。",
                "original_text": "投标人须缴纳投标保证金人民币伍拾万元整"
            },
            {
                "id": "result_002",
                "clause_id": "clause_078",
                "description": "技术参数要求存在模糊表述",
                "risk_level": "medium",
                "confidence": 0.72,
                "page": 24,
                "position": {"x": 85, "y": 210, "width": 320, "height": 60},
                "rule_id": "rule_015_v1.1",
                "rule_version": "v1.1",
                "rule_description": "技术参数应当清晰明确，避免主观描述",
                "rule_quote": "根据《政府采购法实施条例》第28条：技术规格应当明确、清晰，不得使用模糊、主观的表述。",
                "original_text": "设备应具备良好的性能和稳定性"
            },
            {
                "id": "result_003",
                "clause_id": "clause_112",
                "description": "评标标准权重分配合理",
                "risk_level": "low",
                "confidence": 0.95,
                "page": 31,
                "position": {"x": 65, "y": 180, "width": 290, "height": 35},
                "rule_id": "rule_028_v1.3",
                "rule_version": "v1.3",
                "rule_description": "评标标准应当量化并合理分配权重",
                "rule_quote": "根据《招标投标法》第41条：评标标准应当具体、明确，权重分配应当合理，不得含有歧视性条款。",
                "original_text": "技术方案40分，商务报价35分，实施方案25分"
            },
            {
                "id": "result_004",
                "clause_id": "clause_156",
                "description": "合同模板包含不公平条款",
                "risk_level": "high",
                "confidence": 0.81,
                "page": 42,
                "position": {"x": 95, "y": 265, "width": 305, "height": 55},
                "rule_id": "rule_042_v1.0",
                "rule_version": "v1.0",
                "rule_description": "合同条款应当遵循公平原则",
                "rule_quote": "根据《民法典》第497条：提供格式条款一方不合理地免除或者减轻其责任、加重对方责任、限制对方主要权利的，该格式条款无效。",
                "original_text": "采购方有权单方面终止合同且不承担违约责任"
            }
        ]
        
        # 指标数据
        self.metrics = {
            "review_time": {
                "auto_review": 142,
                "end_to_end": 356,
                "unit": "秒"
            },
            "accuracy": {
                "ai_accuracy": 0.89,
                "expert_consistency": 0.92,
                "unit": "百分比"
            },
            "positioning_accuracy": {
                "clause_positioning": 0.94,
                "text_positioning": 0.87,
                "unit": "百分比"
            },
            "cost": {
                "tokens_per_doc": 12480,
                "cost_per_doc": 0.25,
                "unit": "美元"
            }
        }
    
    def start_review(self):
        self.review_state = "in_progress"
        return {"success": True, "message": "审查已开始"}
    
    def get_review_progress(self):
        return {
            "review_state": self.review_state,
            "node_states": self.node_states,
            "current_document": self.current_document
        }
    
    def get_review_results(self):
        return self.review_results
    
    def get_metrics(self):
        return self.metrics
    
    def retry_node(self, node_id: str):
        if node_id in self.node_states:
            self.node_states[node_id]["status"] = "processing"
            self.node_states[node_id]["start_time"] = datetime.now().isoformat()
            return {"success": True, "message": f"节点 {self.node_states[node_id]['name']} 已开始重试"}
        return {"success": False, "message": "节点不存在"}

    def update_node_status(self, node_id: str, status: str, duration: int = 0):
        """更新节点状态（供前端上报，保持前后端状态同步）"""
        if node_id not in self.node_states:
            return {"success": False, "message": "节点不存在"}
        node = self.node_states[node_id]
        node["status"] = status
        if status == "processing":
            node["start_time"] = datetime.now().isoformat()
        elif status in ("completed", "failed"):
            node["end_time"] = datetime.now().isoformat()
            node["duration"] = duration
        return {"success": True, "message": "节点状态已同步"}

    def submit_expert_review(self, result_id: str, revised_conclusion: str, reason: str, basis: str):
        """提交专家复核结果：强制校验修正理由与依据条款（FR-05）"""
        if not reason or not reason.strip():
            return {"success": False, "message": "修正理由为必填项"}
        if not basis or not basis.strip():
            return {"success": False, "message": "依据条款为必填项"}
        target = next((r for r in self.review_results if r["id"] == result_id), None)
        if not target:
            return {"success": False, "message": "结论不存在"}
        record = {
            "result_id": result_id,
            "original_conclusion": target["description"],
            "revised_conclusion": revised_conclusion,
            "reason": reason.strip(),
            "basis": basis.strip(),
            "submitted_at": datetime.now().isoformat()
        }
        self.expert_review_data[result_id] = record
        return {"success": True, "message": "复核结果已提交", "data": record}

# 全局数据管理器
data_manager = MockDataManager()

# API路由
@app.get("/api/document")
async def get_document():
    """获取当前文档信息"""
    return {
        "success": True,
        "data": data_manager.current_document,
        "message": "示例文档数据，已脱敏处理"
    }

@app.post("/api/review/start")
async def start_review():
    """开始审查"""
    result = data_manager.start_review()
    return result

@app.get("/api/review/progress")
async def get_review_progress():
    """获取审查进度"""
    return {
        "success": True,
        "data": data_manager.get_review_progress()
    }

@app.get("/api/review/results")
async def get_review_results():
    """获取审查结果"""
    return {
        "success": True,
        "data": data_manager.get_review_results()
    }

@app.get("/api/metrics")
async def get_metrics():
    """获取指标数据"""
    return {
        "success": True,
        "data": data_manager.get_metrics()
    }

@app.post("/api/nodes/{node_id}/retry")
async def retry_node(node_id: str):
    """重试指定节点"""
    return data_manager.retry_node(node_id)

@app.post("/api/expert/submit")
async def submit_expert_review(request: Request):
    """提交专家复核结果：校验修正理由与依据条款（FR-05）"""
    payload = await request.json()
    return data_manager.submit_expert_review(
        result_id=payload.get("result_id", ""),
        revised_conclusion=payload.get("revised_conclusion", ""),
        reason=payload.get("reason", ""),
        basis=payload.get("basis", "")
    )

@app.post("/api/nodes/{node_id}/status")
async def update_node_status(node_id: str, request: Request):
    """前端上报节点状态，保持前后端状态同步"""
    payload = await request.json()
    result = data_manager.update_node_status(
        node_id=node_id,
        status=payload.get("status", "waiting"),
        duration=payload.get("duration", 0)
    )
    if result["success"]:
        await manager.broadcast({
            "type": "node_status",
            "node_id": node_id,
            "status": payload.get("status", "waiting"),
            "node_states": data_manager.node_states
        })
    return result

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """向所有连接广播状态更新，失败的连接自动清理"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/review")
async def review_websocket(websocket: WebSocket):
    """审查进度实时推送通道"""
    await manager.connect(websocket)
    try:
        # 连接建立后立即推送一次当前完整状态
        await websocket.send_json({
            "type": "progress",
            "data": data_manager.get_review_progress()
        })
        # 保持连接，接收客户端心跳；客户端发来的消息暂不处理，仅维持长连接
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 页面路由
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页 - 示例文档展示"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "document": data_manager.current_document,
            "title": "首页 - 招标文件AI审核系统演示版"
        }
    )

@app.get("/review", response_class=HTMLResponse)
async def review_page(request: Request):
    """审查页面 - 六节点流水线可视化"""
    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "title": "审查流程 - 招标文件AI审核系统演示版",
            "nodes": list(data_manager.node_states.values())
        }
    )

@app.get("/results", response_class=HTMLResponse)
async def results_page(request: Request):
    """结果页面 - 分级报告展示"""
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "title": "审查结果 - 招标文件AI审核系统演示版",
            "results": data_manager.review_results
        }
    )

@app.get("/expert", response_class=HTMLResponse)
async def expert_page(request: Request):
    """专家复核页面"""
    return templates.TemplateResponse(
        "expert.html",
        {
            "request": request,
            "title": "专家复核 - 招标文件AI审核系统演示版",
            "results": data_manager.review_results,
            "reviewed": data_manager.expert_review_data
        }
    )

@app.get("/metrics", response_class=HTMLResponse)
async def metrics_page(request: Request):
    """指标看板页面"""
    return templates.TemplateResponse(
        "metrics.html",
        {
            "request": request,
            "title": "指标看板 - 招标文件AI审核系统演示版",
            "metrics": data_manager.metrics
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)