"""AI decision schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from decimal import Decimal


class AIDecisionRequest(BaseModel):
    """AI决策请求"""
    symbol: str = Field(default="BTC-PERP", description="Trading symbol")
    force: bool = Field(default=False, description="Force decision even if trading disabled")


class AIDecisionOutput(BaseModel):
    """AI决策输出格式"""
    action: Literal["BUY", "SELL", "HOLD"]
    size: Decimal = Field(ge=0, description="Trade size (0 for HOLD)")
    confidence: Decimal = Field(ge=0, le=1, description="Confidence score 0-1")
    reasoning: str = Field(max_length=500, description="Decision reasoning")


class AIDecisionResponse(BaseModel):
    """AI决策响应"""
    symbol: str
    decision: AIDecisionOutput
    executed: bool
    reject_reason: Optional[str] = None
    latency_ms: Optional[int] = None
    model_name: str = "deepseek"

