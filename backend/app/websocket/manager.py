"""
WebSocket 连接管理器
处理前端实时数据推送
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, List
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储所有活跃连接
        self.active_connections: Set[WebSocket] = set()
        
        # 按频道分组连接
        self.channels: Dict[str, Set[WebSocket]] = {
            'price_update': set(),
            'trade_executed': set(),
            'position_update': set(),
            'ai_decision': set(),
            'account_update': set(),
            'kline_update': set()
        }
        
        # 广播任务
        self.broadcast_task = None
        self.running = False
        
    async def connect(self, websocket: WebSocket):
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    async def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        self.active_connections.discard(websocket)
        
        # 从所有频道中移除
        for channel_connections in self.channels.values():
            channel_connections.discard(websocket)
            
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def subscribe_to_channel(self, websocket: WebSocket, channel: str):
        """订阅特定频道"""
        if channel in self.channels:
            self.channels[channel].add(websocket)
            logger.info(f"WebSocket subscribed to channel: {channel}")
    
    async def unsubscribe_from_channel(self, websocket: WebSocket, channel: str):
        """取消订阅频道"""
        if channel in self.channels:
            self.channels[channel].discard(websocket)
            logger.info(f"WebSocket unsubscribed from channel: {channel}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            await self.disconnect(websocket)
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """向特定频道广播消息"""
        if channel not in self.channels:
            logger.warning(f"Unknown channel: {channel}")
            return
            
        message_str = json.dumps(message)
        disconnected = set()
        
        for websocket in self.channels[channel]:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Failed to send message to {channel}: {e}")
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """向所有连接广播消息"""
        message_str = json.dumps(message)
        disconnected = set()
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def start_broadcast_service(self):
        """启动广播服务"""
        self.running = True
        self.broadcast_task = asyncio.create_task(self._broadcast_loop())
        logger.info("WebSocket broadcast service started")
    
    async def stop_broadcast_service(self):
        """停止广播服务"""
        self.running = False
        if self.broadcast_task:
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
        logger.info("WebSocket broadcast service stopped")
    
    async def _broadcast_loop(self):
        """广播循环 - 定期发送心跳和状态更新"""
        while self.running:
            try:
                # 发送心跳消息
                heartbeat = {
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat(),
                    'active_connections': len(self.active_connections)
                }
                
                await self.broadcast_to_all(heartbeat)
                
                # 每30秒发送一次心跳
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(10)
    
    # 便捷方法
    async def broadcast_price_update(self, symbol: str, price_data: Dict[str, Any]):
        """广播价格更新"""
        message = {
            'type': 'price_update',
            'symbol': symbol,
            'data': price_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast_to_channel('price_update', message)
    
    async def broadcast_trade_executed(self, trade_data: Dict[str, Any]):
        """广播交易执行"""
        message = {
            'type': 'trade_executed',
            'data': trade_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast_to_channel('trade_executed', message)
    
    async def broadcast_position_update(self, position_data: Dict[str, Any]):
        """广播持仓更新"""
        message = {
            'type': 'position_update',
            'data': position_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast_to_channel('position_update', message)
    
    async def broadcast_ai_decision(self, decision_data: Dict[str, Any]):
        """广播AI决策"""
        message = {
            'type': 'ai_decision',
            'data': decision_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast_to_channel('ai_decision', message)
    
    async def broadcast_account_update(self, account_data: Dict[str, Any]):
        """广播账户更新"""
        message = {
            'type': 'account_update',
            'data': account_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast_to_channel('account_update', message)
    
    async def broadcast_kline_update(self, symbol: str, kline_data: List[Dict[str, Any]]):
        """广播K线更新"""
        message = {
            'type': 'kline_update',
            'symbol': symbol,
            'data': kline_data,
            'timestamp': datetime.now().isoformat()
        }
        await self.broadcast_to_channel('kline_update', message)
    
    def get_connection_count(self) -> int:
        """获取连接数量"""
        return len(self.active_connections)
    
    def get_channel_connection_count(self, channel: str) -> int:
        """获取频道连接数量"""
        return len(self.channels.get(channel, set()))

# 全局 WebSocket 管理器实例
websocket_manager = WebSocketManager()
