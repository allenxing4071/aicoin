"""约束验证器 - 硬约束+软约束验证"""

from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from app.core.redis_client import RedisClient

logger = logging.getLogger(__name__)


class ConstraintValidator:
    """
    约束验证器
    负责验证交易请求是否符合硬约束和软约束
    """
    
    # 硬约束配置（绝对红线）
    HARD_CONSTRAINTS = {
        # 1. 爆仓保护
        "min_margin_ratio": 0.20,              # 最低保证金率20%
        "forced_liquidation_threshold": 0.15,  # 15%强制平仓
        
        # 2. 最大回撤保护
        "max_total_drawdown": 0.10,            # 总账户最大回撤10%
        "max_single_trade_loss": 0.03,         # 单笔最大亏损3%
        
        # 3. 单日亏损保护
        "max_daily_loss": 0.05,                # 单日最大亏损5%
        "daily_loss_action": "STOP_TRADING",   # 触发后停止交易
        
        # 4. 杠杆硬上限
        "absolute_max_leverage": 5,            # 绝对最大杠杆5x
        
        # 5. 流动性保护
        "min_cash_reserve": 0.10,              # 至少保留10%现金
        
        # 6. 单一资产集中度
        "max_single_asset_exposure": 0.30,     # 单一资产最大30%
    }
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
    
    async def validate_hard_constraints(
        self,
        account_state: Dict[str, Any],
        proposed_trade: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        验证硬性约束，任何违反都拒绝交易
        
        Args:
            account_state: 账户状态
            proposed_trade: 提议的交易
        
        Returns:
            (is_valid, reason)
        """
        
        # 【新增】检查交易控制开关（仅限建仓）
        action = proposed_trade.get("action", "").lower()
        if action in ["open_long", "open_short", "buy", "long", "short", "sell"]:
            # 检查全局交易开关
            try:
                from app.api.v1.constraints import TRADING_ENABLED
                if not TRADING_ENABLED:
                    logger.warning("🚫 交易已停用，拒绝建仓")
                    return False, "交易已停用，当前仅允许平仓操作"
            except Exception as e:
                logger.error(f"检查交易控制开关失败: {e}")
                # 如果检查失败，为安全起见，拒绝交易
                return False, "交易控制检查失败，拒绝交易"
        
        # 1. 检查保证金率
        margin_ratio = account_state.get("margin_ratio", 1.0)
        if margin_ratio < self.HARD_CONSTRAINTS["min_margin_ratio"]:
            return False, f"保证金率不足: {margin_ratio:.1%} < 20%"
        
        # 2. 检查总回撤
        total_drawdown = account_state.get("total_drawdown", 0.0)
        if total_drawdown >= self.HARD_CONSTRAINTS["max_total_drawdown"]:
            return False, f"达到最大回撤限制: {total_drawdown:.1%} >= 10%"
        
        # 3. 检查单日亏损
        daily_loss = account_state.get("daily_loss_pct", 0.0)
        if daily_loss >= self.HARD_CONSTRAINTS["max_daily_loss"]:
            return False, f"超过单日亏损限制: {daily_loss:.1%} >= 5%"
        
        # 4. 检查杠杆
        leverage = proposed_trade.get("leverage", 1)
        if leverage > self.HARD_CONSTRAINTS["absolute_max_leverage"]:
            return False, f"杠杆超限: {leverage}x > 5x"
        
        # 5. 检查流动性
        available_cash = Decimal(str(account_state.get("cash_balance", 0)))
        total_value = Decimal(str(account_state.get("total_value", 0)))
        required_margin = Decimal(str(proposed_trade.get("required_margin", 0)))
        required_reserve = total_value * Decimal(str(self.HARD_CONSTRAINTS["min_cash_reserve"]))
        
        if available_cash - required_margin < required_reserve:
            return False, f"现金储备不足: 需保留{required_reserve:.2f}，剩余{available_cash:.2f}"
        
        # 6. 检查单一资产集中度
        symbol = proposed_trade.get("symbol", "")
        asset_exposure = account_state.get("asset_exposure", {})
        current_exposure = Decimal(str(asset_exposure.get(symbol, 0)))
        position_value = Decimal(str(proposed_trade.get("position_value", 0)))
        new_exposure = current_exposure + position_value
        
        if total_value > 0:
            exposure_pct = float(new_exposure / total_value)
            if exposure_pct > self.HARD_CONSTRAINTS["max_single_asset_exposure"]:
                return False, f"{symbol}敞口过大: {exposure_pct:.1%} > 30%"
        
        return True, "通过硬性约束检查"
    
    async def validate_soft_constraints(
        self,
        ai_decision: Dict[str, Any],
        current_level: str,
        daily_trade_count: int
    ) -> Dict[str, Any]:
        """
        应用软性约束（指导性约束）
        
        Args:
            ai_decision: AI决策
            current_level: 当前权限等级
            daily_trade_count: 今日交易次数
        
        Returns:
            调整后的决策
        """
        
        # 1. 置信度门槛调整
        ai_decision = self._apply_confidence_threshold(ai_decision, current_level)
        
        # 2. 交易频率指导
        ai_decision = await self._apply_frequency_guidance(ai_decision, current_level, daily_trade_count)
        
        return ai_decision
    
    def _apply_confidence_threshold(
        self,
        ai_decision: Dict[str, Any],
        current_level: str
    ) -> Dict[str, Any]:
        """
        根据置信度和权限等级调整决策
        """
        from app.services.constraints.permission_manager import PermissionManager
        
        permission_mgr = PermissionManager(None)
        permission = permission_mgr.get_permission_sync(current_level)
        
        confidence = ai_decision.get("confidence", 0.0)
        threshold = permission.confidence_threshold
        
        # 高于门槛：正常执行
        if confidence >= threshold:
            ai_decision["status"] = "APPROVED"
            ai_decision["notes"] = "置信度达标"
            return ai_decision
        
        # 略低于门槛（-0.05内）：降低仓位执行
        elif confidence >= (threshold - 0.05):
            ai_decision["status"] = "APPROVED_REDUCED"
            if "size_usd" in ai_decision:
                ai_decision["size_usd"] *= 0.5  # 减半仓位
            ai_decision["notes"] = f"置信度略低({confidence:.2f} < {threshold:.2f})，减半仓位"
            logger.warning(f"置信度略低，减半仓位: {confidence:.2f} < {threshold:.2f}")
            return ai_decision
        
        # 明显低于门槛：拒绝
        else:
            ai_decision["status"] = "REJECTED"
            ai_decision["notes"] = f"置信度不足: {confidence:.2f} < {threshold:.2f}"
            logger.info(f"置信度不足，拒绝交易: {confidence:.2f} < {threshold:.2f}")
            return ai_decision
    
    async def _apply_frequency_guidance(
        self,
        ai_decision: Dict[str, Any],
        current_level: str,
        daily_trade_count: int
    ) -> Dict[str, Any]:
        """
        应用交易频率指导
        """
        from app.services.constraints.permission_manager import PermissionManager
        
        permission_mgr = PermissionManager(None)
        permission = await permission_mgr.get_permission(current_level)
        
        max_daily_trades = permission.max_daily_trades
        
        # 已达到每日交易上限
        if daily_trade_count >= max_daily_trades:
            ai_decision["status"] = "REJECTED"
            ai_decision["notes"] = f"超过每日交易次数限制: {daily_trade_count}/{max_daily_trades}"
            logger.info(f"超过每日交易次数，拒绝交易: {daily_trade_count}/{max_daily_trades}")
        
        # 接近上限时警告（80%）
        elif daily_trade_count >= max_daily_trades * 0.8:
            if "notes" not in ai_decision:
                ai_decision["notes"] = ""
            ai_decision["notes"] += f" [警告: 今日已交易{daily_trade_count}次，接近上限{max_daily_trades}次]"
        
        return ai_decision
    
    async def check_forced_liquidation(
        self,
        account_state: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        检查是否触发强制平仓
        
        Returns:
            (should_liquidate, reason)
        """
        
        # 触发条件
        margin_ratio = account_state.get("margin_ratio", 1.0)
        daily_loss = account_state.get("daily_loss_pct", 0.0)
        total_drawdown = account_state.get("total_drawdown", 0.0)
        
        # 1. 保证金率过低
        if margin_ratio < self.HARD_CONSTRAINTS["forced_liquidation_threshold"]:
            return True, f"保证金率过低: {margin_ratio:.1%} < 15%"
        
        # 2. 单日亏损超限
        if daily_loss >= self.HARD_CONSTRAINTS["max_daily_loss"]:
            return True, f"单日亏损超限: {daily_loss:.1%} >= 5%"
        
        # 3. 总回撤超限
        if total_drawdown >= self.HARD_CONSTRAINTS["max_total_drawdown"]:
            return True, f"总回撤超限: {total_drawdown:.1%} >= 10%"
        
        return False, "无需强制平仓"
    
    def get_constraint_summary(self) -> Dict[str, Any]:
        """获取约束配置摘要（用于Prompt）"""
        return {
            "hard_constraints": {
                "max_leverage": f"{self.HARD_CONSTRAINTS['absolute_max_leverage']}x",
                "max_drawdown": f"{self.HARD_CONSTRAINTS['max_total_drawdown']:.0%}",
                "max_daily_loss": f"{self.HARD_CONSTRAINTS['max_daily_loss']:.0%}",
                "min_margin_ratio": f"{self.HARD_CONSTRAINTS['min_margin_ratio']:.0%}",
                "min_cash_reserve": f"{self.HARD_CONSTRAINTS['min_cash_reserve']:.0%}",
                "max_single_asset": f"{self.HARD_CONSTRAINTS['max_single_asset_exposure']:.0%}"
            },
            "protection_mode": {
                "forced_liquidation": f"保证金率 < {self.HARD_CONSTRAINTS['forced_liquidation_threshold']:.0%}",
                "stop_trading": "单日亏损 >= 5% 或 总回撤 >= 10%"
            }
        }

