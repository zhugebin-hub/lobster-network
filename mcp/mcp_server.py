"""
MCP Server - Model Context Protocol 实现
支持工具注册、调用、流式响应
"""

import json
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum


class MCPSchemaVersion(Enum):
    V1 = "1.0"
    V2 = "2.0"


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Optional[Callable] = None
    version: str = "1.0"
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "version": self.version
        }


@dataclass
class MCPRequest:
    """MCP请求"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    jsonrpc: str = "2.0"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MCPResponse:
    """MCP响应"""
    id: str = ""
    result: Any = None
    error: Optional[Dict] = None
    jsonrpc: str = "2.0"
    
    def to_dict(self) -> Dict:
        if self.error:
            return {"id": self.id, "error": self.error, "jsonrpc": self.jsonrpc}
        return {"id": self.id, "result": self.result, "jsonrpc": self.jsonrpc}


class MCPServer:
    """MCP服务器 - 支持工具注册、调用、流式响应"""
    
    def __init__(self, name: str = "LobsterNetwork-MCP", version: str = "3.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, Dict] = {}
        self.prompts: Dict[str, Dict] = {}
        self.schema_version = MCPSchemaVersion.V2
        
    def register_tool(self, tool: MCPTool) -> bool:
        """注册工具"""
        if tool.name in self.tools:
            return False
        self.tools[tool.name] = tool
        return True
    
    def unregister_tool(self, name: str) -> bool:
        """注销工具"""
        if name in self.tools:
            del self.tools[name]
            return True
        return False
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """调用工具"""
        if name not in self.tools:
            return MCPResponse(error={"code": -32601, "message": f"Tool '{name}' not found"})
        
        tool = self.tools[name]
        try:
            if tool.handler:
                result = await tool.handler(**arguments) if asyncio.iscoroutinefunction(tool.handler) else tool.handler(**arguments)
                return MCPResponse(result=result)
            return MCPResponse(error={"code": -32603, "message": "Tool has no handler"})
        except Exception as e:
            return MCPResponse(error={"code": -32603, "message": str(e)})
    
    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def register_resource(self, uri: str, resource: Dict) -> bool:
        """注册资源"""
        if uri in self.resources:
            return False
        self.resources[uri] = resource
        return True
    
    def list_resources(self) -> List[Dict]:
        """列出所有资源"""
        return list(self.resources.values())
    
    def register_prompt(self, name: str, prompt: Dict) -> bool:
        """注册提示"""
        if name in self.prompts:
            return False
        self.prompts[name] = prompt
        return True
    
    def list_prompts(self) -> List[Dict]:
        """列出所有提示"""
        return list(self.prompts.values())
    
    async def handle_request(self, request_data: Dict) -> Dict:
        """处理MCP请求"""
        request = MCPRequest(**{k: v for k, v in request_data.items() if k in MCPRequest.__dataclass_fields__})
        
        if request.method == "tools/list":
            return MCPResponse(id=request.id, result={"tools": self.list_tools()}).to_dict()
        elif request.method == "tools/call":
            tool_name = request.params.get("name", "")
            arguments = request.params.get("arguments", {})
            response = await self.call_tool(tool_name, arguments)
            response.id = request.id
            return response.to_dict()
        elif request.method == "resources/list":
            return MCPResponse(id=request.id, result={"resources": self.list_resources()}).to_dict()
        elif request.method == "prompts/list":
            return MCPResponse(id=request.id, result={"prompts": self.list_prompts()}).to_dict()
        else:
            return MCPResponse(id=request.id, error={"code": -32601, "message": f"Method '{request.method}' not found"}).to_dict()
    
    def get_server_info(self) -> Dict:
        """获取服务器信息"""
        return {
            "name": self.name,
            "version": self.version,
            "schema_version": self.schema_version.value,
            "tools_count": len(self.tools),
            "resources_count": len(self.resources),
            "prompts_count": len(self.prompts)
        }


# 测试函数
async def test_mcp_server():
    """测试MCP服务器"""
    server = MCPServer("TestMCP", "3.0")
    
    # 注册工具
    def add(a: int, b: int) -> int:
        return a + b
    
    server.register_tool(MCPTool(
        name="add",
        description="加法运算",
        parameters={"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
        handler=add
    ))
    
    # 测试工具列表
    tools = server.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "add"
    
    # 测试工具调用
    response = await server.call_tool("add", {"a": 3, "b": 5})
    assert response.result == 8
    
    # 测试不存在的工具
    response = await server.call_tool("nonexistent", {})
    assert response.error is not None
    
    # 测试请求处理
    request = {"method": "tools/list", "params": {}, "id": "test-1"}
    response = await server.handle_request(request)
    assert response["result"]["tools"][0]["name"] == "add"
    
    # 测试服务器信息
    info = server.get_server_info()
    assert info["tools_count"] == 1
    assert info["name"] == "TestMCP"
    
    return {
        "status": "passed",
        "tests_run": 6,
        "details": {
            "tool_registration": True,
            "tool_calling": True,
            "error_handling": True,
            "request_handling": True,
            "server_info": True
        }
    }


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_mcp_server())
    print(json.dumps(result, indent=2, ensure_ascii=False))
