"""
WebSocket API 路由
处理前端 WebSocket 连接
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any
import json
import logging

from app.websocket.manager import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接端点"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON message: {data}")
                await websocket_manager.send_personal_message(
                    json.dumps({"error": "Invalid JSON format"}), 
                    websocket
                )
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any]):
    """处理 WebSocket 消息"""
    message_type = message.get('type')
    
    if message_type == 'subscribe':
        # 订阅频道
        channel = message.get('channel')
        if channel:
            await websocket_manager.subscribe_to_channel(websocket, channel)
            await websocket_manager.send_personal_message(
                json.dumps({
                    "type": "subscription_confirmed",
                    "channel": channel,
                    "status": "success"
                }), 
                websocket
            )
        else:
            await websocket_manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": "Channel not specified"
                }), 
                websocket
            )
    
    elif message_type == 'unsubscribe':
        # 取消订阅频道
        channel = message.get('channel')
        if channel:
            await websocket_manager.unsubscribe_from_channel(websocket, channel)
            await websocket_manager.send_personal_message(
                json.dumps({
                    "type": "unsubscription_confirmed",
                    "channel": channel,
                    "status": "success"
                }), 
                websocket
            )
        else:
            await websocket_manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": "Channel not specified"
                }), 
                websocket
            )
    
    elif message_type == 'ping':
        # 心跳响应
        await websocket_manager.send_personal_message(
            json.dumps({
                "type": "pong",
                "timestamp": message.get('timestamp')
            }), 
            websocket
        )
    
    else:
        # 未知消息类型
        await websocket_manager.send_personal_message(
            json.dumps({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }), 
            websocket
        )

@router.get("/ws/status")
async def get_websocket_status():
    """获取 WebSocket 状态"""
    return {
        "active_connections": websocket_manager.get_connection_count(),
        "channels": {
            channel: websocket_manager.get_channel_connection_count(channel)
            for channel in websocket_manager.channels.keys()
        }
    }
