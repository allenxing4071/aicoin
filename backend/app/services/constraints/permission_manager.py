"""权限管理器 - 动态L0-L5权限系统"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceData:
    """性能数据结构"""
    win_rate_7d: float
    win_rate_30d: float
    sharpe_ratio: float
    max_drawdown: float
    consecutive_losses: int
    total_trades: int
    profitable_trades: int
    days_active: int
    profit_consistency: float = 0.0
    consecutive_profitable_days: int = 0


@dataclass
class PermissionLevel:
    """权限等级定义"""
    level: str
    name: str
    max_position_pct: float  # 单仓位最大占比
    max_leverage: int        # 最大杠杆
    confidence_threshold: float  # 置信度门槛
    max_daily_trades: int    # 每日最大交易次数
    
    
class PermissionManager:
    """
    权限管理器
    负责评估AI表现并动态调整权限等级
    """
    
    # 权限等级配置
    LEVELS = {
        "L0": PermissionLevel(
            level="L0",
            name="保护模式",
            max_position_pct=0.0,
            max_leverage=1,
            confidence_threshold=1.0,
            max_daily_trades=0
        ),
        "L1": PermissionLevel(
            level="L1",
            name="新手级",
            max_position_pct=0.10,
            max_leverage=2,
            confidence_threshold=0.80,
            max_daily_trades=1
        ),
        "L2": PermissionLevel(
            level="L2",
            name="成长级",
            max_position_pct=0.12,
            max_leverage=2,
            confidence_threshold=0.75,
            max_daily_trades=2
        ),
        "L3": PermissionLevel(
            level="L3",
            name="稳定级",
            max_position_pct=0.15,
            max_leverage=3,
            confidence_threshold=0.70,
            max_daily_trades=4
        ),
        "L4": PermissionLevel(
            level="L4",
            name="熟练级",
            max_position_pct=0.20,
            max_leverage=4,
            confidence_threshold=0.65,
            max_daily_trades=6
        ),
        "L5": PermissionLevel(
            level="L5",
            name="专家级",
            max_position_pct=0.25,
            max_leverage=5,
            confidence_threshold=0.60,
            max_daily_trades=999  # 无限制
        )
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def evaluate_permission_level(
        self,
        current_level: str,
        performance_data: PerformanceData
    ) -> tuple[str, str]:
        """
        评估当前权限等级是否需要调整
        
        Returns:
            (new_level, reason)
        """
        
        # 1. 检查降级触发器（优先）
        downgrade_result = self._check_downgrade_triggers(
            current_level, 
            performance_data
        )
        if downgrade_result:
            level, reason = downgrade_result
            logger.warning(f"权限降级: {current_level} → {level}, 原因: {reason}")
            return downgrade_result
        
        # 2. 检查升级条件
        upgrade_result = self._check_upgrade_conditions(
            current_level,
            performance_data
        )
        if upgrade_result:
            level, reason = upgrade_result
            logger.info(f"权限升级: {current_level} → {level}, 原因: {reason}")
            return upgrade_result
        
        # 3. 保持当前等级
        return current_level, "保持当前等级"
    
    def _check_downgrade_triggers(
        self,
        current_level: str,
        performance_data: PerformanceData
    ) -> Optional[tuple[str, str]]:
        """
        检查是否触发降级（风控优先）
        """
        
        # 触发L0（保护模式）的条件
        if any([
            performance_data.max_drawdown >= 0.10,  # 最大回撤≥10%
            performance_data.consecutive_losses >= 5,  # 连续5次亏损
        ]):
            return "L0", "触发风控保护"
        
        # 各等级降级逻辑
        if current_level == "L5":
            if performance_data.win_rate_30d < 0.65:
                return "L4", "近期表现下降"
        
        elif current_level == "L4":
            if performance_data.win_rate_30d < 0.55:
                return "L3", "近期表现下降"
        
        elif current_level == "L3":
            if performance_data.win_rate_7d < 0.45:
                return "L2", "近期表现下降"
        
        elif current_level == "L2":
            if performance_data.consecutive_losses >= 3:
                return "L1", "连续亏损，回到新手模式"
        
        return None
    
    def _check_upgrade_conditions(
        self,
        current_level: str,
        performance_data: PerformanceData
    ) -> Optional[tuple[str, str]]:
        """
        检查是否满足升级条件
        """
        
        # L0 → L1: 需要人工审核
        if current_level == "L0":
            return None  # 不自动升级
        
        # L1 → L2
        elif current_level == "L1":
            if (performance_data.days_active >= 7 and
                performance_data.win_rate_7d >= 0.50 and
                performance_data.max_drawdown < 0.15):
                return "L2", "新手期表现合格"
        
        # L2 → L3
        elif current_level == "L2":
            if (performance_data.days_active >= 30 and
                performance_data.win_rate_30d >= 0.50 and
                performance_data.sharpe_ratio >= 1.0 and
                performance_data.max_drawdown < 0.10):
                return "L3", "成长期表现优秀"
        
        # L3 → L4
        elif current_level == "L3":
            if (performance_data.win_rate_30d >= 0.60 and
                performance_data.sharpe_ratio >= 1.5 and
                performance_data.max_drawdown < 0.08):
                return "L4", "稳定盈利能力确认"
        
        # L4 → L5
        elif current_level == "L4":
            if (performance_data.win_rate_30d >= 0.70 and
                performance_data.consecutive_profitable_days >= 20 and
                performance_data.sharpe_ratio >= 2.0):
                return "L5", "达到专家级标准"
        
        return None
    
    def get_permission(self, level: str) -> PermissionLevel:
        """获取权限等级配置"""
        return self.LEVELS.get(level, self.LEVELS["L1"])
    
    def validate_trade_request(
        self,
        level: str,
        position_size: Decimal,
        account_balance: Decimal,
        leverage: int,
        confidence: float,
        daily_trade_count: int
    ) -> tuple[bool, str]:
        """
        验证交易请求是否符合当前权限
        
        Returns:
            (is_valid, reason)
        """
        permission = self.get_permission(level)
        
        # 1. 检查仓位大小
        position_pct = float(position_size / account_balance)
        if position_pct > permission.max_position_pct:
            return False, f"仓位超限: {position_pct:.1%} > {permission.max_position_pct:.1%}"
        
        # 2. 检查杠杆
        if leverage > permission.max_leverage:
            return False, f"杠杆超限: {leverage}x > {permission.max_leverage}x"
        
        # 3. 检查置信度
        if confidence < permission.confidence_threshold:
            return False, f"置信度不足: {confidence:.2f} < {permission.confidence_threshold:.2f}"
        
        # 4. 检查交易频率
        if daily_trade_count >= permission.max_daily_trades:
            return False, f"超过每日交易次数限制: {permission.max_daily_trades}次"
        
        return True, "通过权限验证"
    
    async def manual_upgrade_to_l1(
        self,
        reason: str,
        operator: str
    ) -> bool:
        """
        人工审核：L0 → L1
        
        Args:
            reason: 升级原因
            operator: 操作员
        
        Returns:
            是否成功
        """
        logger.info(f"人工审核升级L0→L1: {reason}, 操作员: {operator}")
        # TODO: 记录到数据库
        return True
    
    def get_permission_summary(self, level: str) -> Dict[str, Any]:
        """获取权限等级摘要（用于Prompt）"""
        permission = self.get_permission(level)
        return {
            "level": permission.level,
            "name": permission.name,
            "max_position_pct": f"{permission.max_position_pct:.0%}",
            "max_leverage": f"{permission.max_leverage}x",
            "confidence_threshold": f"{permission.confidence_threshold:.0%}",
            "max_daily_trades": permission.max_daily_trades if permission.max_daily_trades < 100 else "无限制"
        }

