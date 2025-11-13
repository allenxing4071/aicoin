"""告警管理器"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertManager:
    """
    告警管理器
    负责监控系统状态并发送告警
    """
    
    def __init__(self):
        self.alert_history = []
    
    async def send_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        channels: List[str] = None
    ) -> bool:
        """
        发送告警
        
        Args:
            level: 告警级别
            title: 标题
            message: 消息
            data: 附加数据
            channels: 通知渠道（email/sms/telegram）
        
        Returns:
            是否成功
        """
        try:
            alert = {
                "level": level.value,
                "title": title,
                "message": message,
                "data": data or {},
                "timestamp": datetime.now().isoformat(),
                "channels": channels or ["logger"]
            }
            
            # 记录到历史
            self.alert_history.append(alert)
            
            # 根据级别选择日志方法
            if level == AlertLevel.CRITICAL:
                logger.critical(f"🚨 {title}: {message}")
            elif level == AlertLevel.WARNING:
                logger.warning(f"⚠️ {title}: {message}")
            else:
                logger.info(f"ℹ️ {title}: {message}")
            
            # TODO: 实现实际的通知渠道
            # - Email
            # - SMS
            # - Telegram
            
            return True
        
        except Exception as e:
            logger.error(f"发送告警失败: {e}")
            return False
    
    async def check_risk_alerts(
        self,
        account_state: Dict[str, Any],
        thresholds: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        检查风险告警（同时保存到数据库）
        
        Returns:
            触发的告警列表
        """
        alerts = []
        
        # 1. 保证金率告警
        margin_ratio = account_state.get("margin_ratio", 1.0)
        if margin_ratio < thresholds.get("min_margin_ratio", 0.2):
            await self.send_alert(
                AlertLevel.CRITICAL,
                "保证金率过低",
                f"当前保证金率: {margin_ratio:.1%}，低于{thresholds['min_margin_ratio']:.1%}",
                {"margin_ratio": margin_ratio}
            )
            alerts.append({"type": "margin_ratio", "value": margin_ratio})
            
            # ✅ 保存到数据库
            await self._save_risk_event(
                event_type="MARGIN_RATIO_LOW",
                severity="CRITICAL",
                description=f"保证金率过低: {margin_ratio:.1%}，低于阈值{thresholds['min_margin_ratio']:.1%}",
                action_taken="发送告警通知"
            )
        
        # 2. 回撤告警
        drawdown = account_state.get("total_drawdown", 0.0)
        if drawdown >= thresholds.get("max_drawdown", 0.1):
            await self.send_alert(
                AlertLevel.CRITICAL,
                "最大回撤超限",
                f"当前回撤: {drawdown:.1%}，超过{thresholds['max_drawdown']:.1%}",
                {"drawdown": drawdown}
            )
            alerts.append({"type": "drawdown", "value": drawdown})
            
            # ✅ 保存到数据库
            await self._save_risk_event(
                event_type="MAX_DRAWDOWN_EXCEEDED",
                severity="CRITICAL",
                description=f"最大回撤超限: {drawdown:.1%}，超过阈值{thresholds['max_drawdown']:.1%}",
                action_taken="发送告警通知"
            )
        
        # 3. 单日亏损告警
        daily_loss = account_state.get("daily_loss_pct", 0.0)
        if daily_loss >= thresholds.get("max_daily_loss", 0.05):
            await self.send_alert(
                AlertLevel.CRITICAL,
                "单日亏损超限",
                f"今日亏损: {daily_loss:.1%}，超过{thresholds['max_daily_loss']:.1%}",
                {"daily_loss": daily_loss}
            )
            alerts.append({"type": "daily_loss", "value": daily_loss})
            
            # ✅ 保存到数据库
            await self._save_risk_event(
                event_type="DAILY_LOSS_EXCEEDED",
                severity="CRITICAL",
                description=f"单日亏损超限: {daily_loss:.1%}，超过阈值{thresholds['max_daily_loss']:.1%}",
                action_taken="发送告警通知"
            )
        
        return alerts
    
    async def _save_risk_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        action_taken: str,
        related_trade_id: int = None
    ):
        """保存风控事件到数据库"""
        try:
            from app.models.risk_event import RiskEvent
            from app.core.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db_session:
                risk_event = RiskEvent(
                    event_type=event_type,
                    severity=severity,
                    description=description,
                    action_taken=action_taken,
                    related_trade_id=related_trade_id,
                    resolved=False
                )
                db_session.add(risk_event)
                await db_session.commit()
                logger.info(f"✅ Risk event saved to database: {event_type} ({severity})")
                
        except Exception as e:
            logger.error(f"❌ Failed to save risk event to database: {e}")
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近的告警"""
        return self.alert_history[-count:]

