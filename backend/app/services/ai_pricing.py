"""
AI 模型定价管理
统一管理各平台的最新价格，确保成本计算准确
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
from app.utils.timezone import get_beijing_time, format_beijing_time

logger = logging.getLogger(__name__)


# ===== 各平台最新价格（2025-11 更新）=====
# 价格单位: 元/1K tokens

PRICING_TABLE = {
    "qwen": {
        "qwen-plus": {
            "input": 0.004,   # ¥0.004/1K tokens
            "output": 0.012,  # ¥0.012/1K tokens
            "description": "通义千问Plus - 高性能模型",
            "last_updated": "2025-11-13"
        },
        "qwen-turbo": {
            "input": 0.002,
            "output": 0.006,
            "description": "通义千问Turbo - 快速响应",
            "last_updated": "2025-11-13"
        },
        "qwen-max": {
            "input": 0.040,
            "output": 0.120,
            "description": "通义千问Max - 最强性能",
            "last_updated": "2025-11-13"
        }
    },
    "deepseek": {
        "deepseek-chat": {
            "input": 0.001,        # ¥1/M tokens = ¥0.001/1K tokens
            "output": 0.002,       # ¥2/M tokens = ¥0.002/1K tokens
            "input_cached": 0.0001,  # 缓存命中更便宜
            "description": "DeepSeek Chat - 性价比之王",
            "last_updated": "2025-11-13",
            "note": "支持缓存，命中后输入成本降低10倍"
        },
        "deepseek-coder": {
            "input": 0.001,
            "output": 0.002,
            "description": "DeepSeek Coder - 代码专用",
            "last_updated": "2025-11-13"
        }
    },
    "baidu": {
        "qwen-plus": {
            "input": 0.008,   # 百度云上的 Qwen 价格
            "output": 0.016,
            "description": "百度云 - 通义千问Plus",
            "last_updated": "2025-11-13"
        },
        "ernie-4.0": {
            "input": 0.120,
            "output": 0.120,
            "description": "文心一言 4.0",
            "last_updated": "2025-11-13"
        }
    },
    "tencent": {
        "qwen-plus": {
            "input": 0.008,
            "output": 0.016,
            "description": "腾讯云 - 通义千问Plus",
            "last_updated": "2025-11-13"
        },
        "hunyuan-lite": {
            "input": 0.000,   # 免费
            "output": 0.000,
            "description": "混元Lite - 免费版",
            "last_updated": "2025-11-13"
        }
    },
    "volcano": {
        "qwen-plus": {
            "input": 0.008,
            "output": 0.016,
            "description": "火山引擎 - 通义千问Plus",
            "last_updated": "2025-11-13"
        },
        "doubao-pro": {
            "input": 0.008,
            "output": 0.008,
            "description": "豆包Pro",
            "last_updated": "2025-11-13"
        }
    },
    "openai": {
        "gpt-4": {
            "input": 0.210,   # $30/M tokens ≈ ¥210/M tokens
            "output": 0.420,  # $60/M tokens ≈ ¥420/M tokens
            "description": "GPT-4 - OpenAI",
            "last_updated": "2025-11-13"
        },
        "gpt-3.5-turbo": {
            "input": 0.0035,  # $0.5/M tokens
            "output": 0.0105, # $1.5/M tokens
            "description": "GPT-3.5 Turbo",
            "last_updated": "2025-11-13"
        }
    }
}


class AIPricingManager:
    """AI 定价管理器"""
    
    def __init__(self):
        self.pricing_table = PRICING_TABLE
        logger.info("✅ AI 定价管理器初始化完成")
    
    def get_price(
        self, 
        provider: str, 
        model: str,
        token_type: str = "input"
    ) -> float:
        """
        获取指定模型的价格
        
        Args:
            provider: 平台标识 (qwen, deepseek, baidu等)
            model: 模型名称
            token_type: token类型 (input/output/input_cached)
            
        Returns:
            价格 (元/1K tokens)
        """
        try:
            provider = provider.lower()
            
            # 如果 model 包含 provider 前缀，去掉
            if model.startswith(f"{provider}_"):
                model = model[len(provider)+1:]
            
            # 查找价格
            if provider in self.pricing_table:
                if model in self.pricing_table[provider]:
                    price = self.pricing_table[provider][model].get(token_type, 0)
                    return price
                else:
                    # 尝试模糊匹配
                    for model_key in self.pricing_table[provider].keys():
                        if model_key in model or model in model_key:
                            price = self.pricing_table[provider][model_key].get(token_type, 0)
                            logger.debug(f"模糊匹配: {model} -> {model_key}, 价格: {price}")
                            return price
            
            logger.warning(f"⚠️  未找到价格: {provider}/{model}/{token_type}")
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ 获取价格失败: {e}")
            return 0.0
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0
    ) -> float:
        """
        计算调用成本
        
        Args:
            provider: 平台标识
            model: 模型名称
            input_tokens: 输入token数
            output_tokens: 输出token数
            cached_tokens: 缓存命中token数（如果支持）
            
        Returns:
            成本（元）
        """
        try:
            # 计算输入成本
            input_price = self.get_price(provider, model, "input")
            input_cost = (input_tokens / 1000.0) * input_price
            
            # 如果有缓存命中，使用缓存价格
            if cached_tokens > 0:
                cached_price = self.get_price(provider, model, "input_cached")
                if cached_price > 0:
                    # 缓存部分使用缓存价格
                    cached_cost = (cached_tokens / 1000.0) * cached_price
                    # 非缓存部分使用正常价格
                    non_cached_tokens = input_tokens - cached_tokens
                    input_cost = (non_cached_tokens / 1000.0) * input_price + cached_cost
            
            # 计算输出成本
            output_price = self.get_price(provider, model, "output")
            output_cost = (output_tokens / 1000.0) * output_price
            
            total_cost = input_cost + output_cost
            
            logger.debug(
                f"💰 成本计算: {provider}/{model} | "
                f"输入:{input_tokens}tokens(¥{input_cost:.6f}) + "
                f"输出:{output_tokens}tokens(¥{output_cost:.6f}) = "
                f"¥{total_cost:.6f}"
            )
            
            return total_cost
            
        except Exception as e:
            logger.error(f"❌ 成本计算失败: {e}")
            return 0.0
    
    def get_model_info(self, provider: str, model: str) -> Optional[Dict[str, Any]]:
        """
        获取模型详细信息
        
        Returns:
            模型信息字典
        """
        try:
            provider = provider.lower()
            
            if provider in self.pricing_table:
                if model in self.pricing_table[provider]:
                    info = self.pricing_table[provider][model].copy()
                    info["provider"] = provider
                    info["model"] = model
                    return info
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取模型信息失败: {e}")
            return None
    
    def get_all_pricing(self) -> Dict[str, Any]:
        """获取完整价格表"""
        # 为每个模型添加动态的北京时间戳
        pricing_with_timestamps = {}
        current_time = format_beijing_time(get_beijing_time(), "%Y-%m-%d %H:%M:%S")
        
        for provider, models in self.pricing_table.items():
            pricing_with_timestamps[provider] = {}
            for model, info in models.items():
                model_info = info.copy()
                # 总是使用当前的北京时间，覆盖原有的 last_updated
                model_info["last_updated"] = current_time
                pricing_with_timestamps[provider][model] = model_info
        
        return {
            "pricing_table": pricing_with_timestamps,
            "last_updated": current_time,
            "currency": "CNY",
            "unit": "元/1K tokens"
        }
    
    def update_price(
        self,
        provider: str,
        model: str,
        input_price: Optional[float] = None,
        output_price: Optional[float] = None
    ) -> bool:
        """
        更新价格（用于手动校准）
        
        Args:
            provider: 平台标识
            model: 模型名称
            input_price: 新的输入价格
            output_price: 新的输出价格
            
        Returns:
            是否更新成功
        """
        try:
            provider = provider.lower()
            
            if provider not in self.pricing_table:
                self.pricing_table[provider] = {}
            
            if model not in self.pricing_table[provider]:
                self.pricing_table[provider][model] = {}
            
            if input_price is not None:
                self.pricing_table[provider][model]["input"] = input_price
            
            if output_price is not None:
                self.pricing_table[provider][model]["output"] = output_price
            
            # 使用北京时间
            self.pricing_table[provider][model]["last_updated"] = format_beijing_time(
                get_beijing_time(), "%Y-%m-%d %H:%M:%S"
            )
            
            logger.info(f"✅ 价格已更新: {provider}/{model}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 价格更新失败: {e}")
            return False


# 全局单例
_pricing_manager = None


def get_pricing_manager() -> AIPricingManager:
    """获取定价管理器单例"""
    global _pricing_manager
    if _pricing_manager is None:
        _pricing_manager = AIPricingManager()
    return _pricing_manager

