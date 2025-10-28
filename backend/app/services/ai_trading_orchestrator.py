"""AI决策引擎与交易执行集成服务"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
from loguru import logger

from app.core.redis_client import RedisClient
from app.services.hyperliquid_trading import HyperliquidTradingService
from app.services.deepseek_decision_engine import DeepSeekDecisionEngine
from app.services.qwen_decision_engine import QwenDecisionEngine
from app.services.hyperliquid_market_data import HyperliquidMarketData


class AITradingOrchestrator:
    """AI交易编排器"""
    
    def __init__(
        self,
        redis_client: RedisClient,
        trading_service: HyperliquidTradingService,
        market_data_service: HyperliquidMarketData,
        testnet: bool = True
    ):
        self.redis_client = redis_client
        self.trading_service = trading_service
        self.market_data_service = market_data_service
        
        # 初始化AI决策引擎
        self.deepseek_engine = DeepSeekDecisionEngine(redis_client)
        self.qwen_engine = QwenDecisionEngine(redis_client)
        
        # 交易配置
        self.testnet = testnet
        self.trading_enabled = True
        self.max_concurrent_trades = 3
        self.decision_interval = 30  # 决策间隔（秒）
        
        # 状态管理
        self.is_running = False
        self.active_trades = {}
        self.decision_history = []
        
        # 性能统计
        self.total_trades = 0
        self.successful_trades = 0
        self.total_pnl = Decimal("0")
        
    async def start_trading(self):
        """开始交易"""
        try:
            logger.info("Starting AI trading orchestrator...")
            self.is_running = True
            
            # 启动决策循环
            asyncio.create_task(self._decision_loop())
            
            # 启动监控循环
            asyncio.create_task(self._monitoring_loop())
            
            logger.info("AI trading orchestrator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start AI trading orchestrator: {e}")
            self.is_running = False
    
    async def stop_trading(self):
        """停止交易"""
        try:
            logger.info("Stopping AI trading orchestrator...")
            self.is_running = False
            
            # 取消所有活跃交易
            await self._cancel_all_active_trades()
            
            logger.info("AI trading orchestrator stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop AI trading orchestrator: {e}")
    
    async def _decision_loop(self):
        """决策循环"""
        while self.is_running:
            try:
                # 获取市场数据
                market_data = await self._get_market_data()
                
                # 获取AI决策
                decisions = await self._get_ai_decisions(market_data)
                
                # 执行交易决策
                await self._execute_decisions(decisions)
                
                # 等待下次决策
                await asyncio.sleep(self.decision_interval)
                
            except Exception as e:
                logger.error(f"Error in decision loop: {e}")
                await asyncio.sleep(5)  # 错误时短暂等待
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                # 监控活跃交易
                await self._monitor_active_trades()
                
                # 更新性能统计
                await self._update_performance_stats()
                
                # 等待下次监控
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _get_market_data(self) -> Dict[str, Any]:
        """获取市场数据"""
        try:
            # 获取价格数据
            prices = await self.market_data_service.get_all_cached_prices()
            
            # 计算市场趋势
            trend = await self._calculate_market_trend(prices)
            
            # 计算波动率
            volatility = await self._calculate_volatility(prices)
            
            return {
                **prices,
                'trend': trend,
                'volatility': volatility,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return {}
    
    async def _calculate_market_trend(self, prices: Dict[str, Any]) -> str:
        """计算市场趋势"""
        try:
            # 简单的趋势计算逻辑
            btc_price = prices.get('BTC', {}).get('price', 0)
            eth_price = prices.get('ETH', {}).get('price', 0)
            
            if btc_price > 95000 and eth_price > 3500:
                return 'bullish'
            elif btc_price < 90000 or eth_price < 3200:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Failed to calculate market trend: {e}")
            return 'neutral'
    
    async def _calculate_volatility(self, prices: Dict[str, Any]) -> str:
        """计算波动率"""
        try:
            # 简单的波动率计算
            price_changes = []
            for symbol, data in prices.items():
                if 'price' in data:
                    price_changes.append(abs(data.get('change', 0)))
            
            if not price_changes:
                return 'medium'
            
            avg_change = sum(price_changes) / len(price_changes)
            
            if avg_change > 5:
                return 'high'
            elif avg_change < 2:
                return 'low'
            else:
                return 'medium'
                
        except Exception as e:
            logger.error(f"Failed to calculate volatility: {e}")
            return 'medium'
    
    async def _get_ai_decisions(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取AI决策"""
        try:
            decisions = []
            
            # 获取DeepSeek决策
            try:
                # 获取DeepSeek账户状态
                deepseek_account = await self.trading_service.get_account_state()
                deepseek_balance = float(deepseek_account.get('marginSummary', {}).get('accountValue', 100))
                
                deepseek_decision = await self.deepseek_engine.analyze_market_data(
                    market_data,
                    account_state={'balance': deepseek_balance, 'initial_capital': 100}
                )
                if await self.deepseek_engine.validate_decision(deepseek_decision, deepseek_balance):
                    decisions.append(deepseek_decision)
            except Exception as e:
                logger.error(f"DeepSeek decision failed: {e}")
            
            # Qwen已禁用 - 只使用DeepSeek单一AI模型
            # try:
            #     qwen_account = await self.trading_service.get_account_state()
            #     qwen_balance = float(qwen_account.get('marginSummary', {}).get('accountValue', 100))
            #     
            #     qwen_decision = await self.qwen_engine.analyze_market_data(
            #         market_data,
            #         account_state={'balance': qwen_balance, 'initial_capital': 100}
            #     )
            #     if await self.qwen_engine.validate_decision(qwen_decision, qwen_balance):
            #         decisions.append(qwen_decision)
            # except Exception as e:
            #     logger.error(f"Qwen decision failed: {e}")
            
            return decisions
            
        except Exception as e:
            logger.error(f"Failed to get AI decisions: {e}")
            return []
    
    async def _execute_decisions(self, decisions: List[Dict[str, Any]]):
        """执行交易决策"""
        try:
            for decision in decisions:
                if not self.trading_enabled:
                    logger.info("Trading disabled, skipping decision execution")
                    continue
                
                if len(self.active_trades) >= self.max_concurrent_trades:
                    logger.warning("Max concurrent trades reached, skipping new trades")
                    continue
                
                # 转换AI决策格式为交易执行格式
                action = decision.get('action', 'hold')
                
                # 检查决策是否应该执行
                if action == 'hold':
                    continue
                
                # 将action转换为recommendation
                if action == 'open_long':
                    decision['recommendation'] = 'buy'
                elif action == 'open_short':
                    decision['recommendation'] = 'sell'
                elif action == 'close_position':
                    decision['recommendation'] = 'close'
                else:
                    continue
                
                # 将symbol转换为target_symbol
                if 'symbol' in decision and 'target_symbol' not in decision:
                    decision['target_symbol'] = decision['symbol']
                
                # 将size_usd转换为position_size
                if 'size_usd' in decision and 'position_size' not in decision:
                    decision['position_size'] = decision['size_usd']
                
                logger.info(f"Executing AI decision: {decision.get('model')} - {decision.get('recommendation')} {decision.get('target_symbol')} ${decision.get('position_size')}")
                
                # 执行交易
                await self._execute_trade(decision)
                
        except Exception as e:
            logger.error(f"Failed to execute decisions: {e}")
    
    async def _execute_trade(self, decision: Dict[str, Any]):
        """执行单个交易"""
        try:
            symbol = decision.get('target_symbol', 'BTC')
            recommendation = decision.get('recommendation', 'hold')
            position_size = decision.get('position_size', 100)
            confidence = decision.get('confidence', 0)
            model_name = decision.get('model', 'unknown')
            
            if recommendation == 'hold':
                return
            
            # 确定交易方向
            side = 'buy' if recommendation == 'buy' else 'sell'
            
            # 执行交易
            trade_result = await self.trading_service.place_order(
                symbol=symbol,
                side=side,
                size=position_size,
                price=None,  # 市价单
                order_type="market"
            )
            
            if trade_result.get('success'):
                order_id = trade_result.get('order_id')
                
                # 记录活跃交易
                self.active_trades[order_id] = {
                    'order_id': order_id,
                    'symbol': symbol,
                    'side': side,
                    'size': position_size,
                    'decision': decision,
                    'model': model_name,
                    'timestamp': datetime.now().isoformat()
                }
                
                # 更新统计
                self.total_trades += 1
                
                # 记录账户历史
                await self._record_account_history(model_name, decision)
                
                logger.info(f"Trade executed successfully: {order_id} by {model_name}")
                
            else:
                logger.error(f"Trade execution failed: {trade_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
    
    async def _record_account_history(self, model: str, decision: Dict[str, Any]):
        """记录账户历史"""
        try:
            # 获取真实的账户状态
            account_state = await self.trading_service.get_account_state()
            logger.info(f"DEBUG: account_state = {account_state}")
            
            # 从marginSummary中获取账户价值
            margin_summary = account_state.get('marginSummary', {})
            current_balance = float(margin_summary.get('accountValue', 100))
            logger.info(f"DEBUG: current_balance = {current_balance}")
            
            # 标准化模型名称（用于API查询）
            # deepseek-chat -> deepseek-chat-v3.1
            # qwen-max -> qwen3-max
            api_model_name = model
            if model == 'deepseek-chat':
                api_model_name = 'deepseek-chat-v3.1'
            elif model == 'qwen-max':
                api_model_name = 'qwen3-max'
            
            history_record = {
                'timestamp': datetime.now().isoformat(),
                'model': api_model_name,
                'account_value': float(current_balance),
                'balance': float(current_balance),
                'action': decision.get('recommendation', 'hold'),
                'symbol': decision.get('target_symbol', ''),
                'confidence': decision.get('confidence', 0)
            }
            
            # 存储到Redis（使用API模型名称作为key）
            cache_key = f"account:history:{api_model_name}"
            
            # 获取现有历史记录
            existing_history = await self.redis_client.get(cache_key) or []
            if not isinstance(existing_history, list):
                existing_history = [existing_history] if existing_history else []
            
            # 添加新记录
            existing_history.append(history_record)
            
            # 保留最近100条记录
            if len(existing_history) > 100:
                existing_history = existing_history[-100:]
            
            # 保存到Redis（保留24小时）
            await self.redis_client.set(cache_key, existing_history, expire=86400)
            
            logger.info(f"Account history recorded for {model}")
            
        except Exception as e:
            logger.error(f"Failed to record account history: {e}")
    
    async def _monitor_active_trades(self):
        """监控活跃交易"""
        try:
            for order_id, trade_info in list(self.active_trades.items()):
                # 检查订单状态
                order_status = await self.trading_service.get_order_status(order_id)
                
                if order_status.get('success') and order_status.get('status') == 'filled':
                    # 交易已完成，从活跃交易中移除
                    del self.active_trades[order_id]
                    
                    # 更新成功交易统计
                    self.successful_trades += 1
                    
                    logger.info(f"Trade completed: {order_id}")
                
        except Exception as e:
            logger.error(f"Failed to monitor active trades: {e}")
    
    async def _cancel_all_active_trades(self):
        """取消所有活跃交易"""
        try:
            for order_id in list(self.active_trades.keys()):
                await self.trading_service.cancel_order(order_id)
                del self.active_trades[order_id]
                
            logger.info("All active trades cancelled")
            
        except Exception as e:
            logger.error(f"Failed to cancel active trades: {e}")
    
    async def _update_performance_stats(self):
        """更新性能统计"""
        try:
            # 获取账户信息
            account_info = await self.trading_service.get_account_info()
            
            # 计算总PnL
            positions = account_info.get('positions', [])
            total_pnl = sum(float(pos.get('unrealizedPnl', 0)) for pos in positions)
            self.total_pnl = Decimal(str(total_pnl))
            
            # 存储统计信息
            stats = {
                'total_trades': self.total_trades,
                'successful_trades': self.successful_trades,
                'success_rate': (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
                'total_pnl': float(self.total_pnl),
                'active_trades': len(self.active_trades),
                'timestamp': datetime.now().isoformat()
            }
            
            await self.redis_client.set('trading_stats', stats, expire=3600)
            
        except Exception as e:
            logger.error(f"Failed to update performance stats: {e}")
    
    async def get_trading_status(self) -> Dict[str, Any]:
        """获取交易状态"""
        try:
            account_info = await self.trading_service.get_account_info()
            positions = await self.trading_service.get_positions()
            trading_stats = await self.trading_service.get_trading_stats()
            
            return {
                'is_running': self.is_running,
                'trading_enabled': self.trading_enabled,
                'active_trades': len(self.active_trades),
                'account_info': account_info,
                'positions': positions,
                'trading_stats': trading_stats,
                'performance_stats': {
                    'total_trades': self.total_trades,
                    'successful_trades': self.successful_trades,
                    'success_rate': (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
                    'total_pnl': float(self.total_pnl)
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get trading status: {e}")
            return {
                'is_running': self.is_running,
                'trading_enabled': self.trading_enabled,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_ai_performance(self) -> Dict[str, Any]:
        """获取AI性能"""
        try:
            deepseek_stats = await self.deepseek_engine.get_performance_stats()
            qwen_stats = await self.qwen_engine.get_performance_stats()
            
            return {
                'deepseek': deepseek_stats,
                'qwen': qwen_stats,
                'combined': {
                    'total_decisions': deepseek_stats['total_decisions'] + qwen_stats['total_decisions'],
                    'total_successful': deepseek_stats['successful_decisions'] + qwen_stats['successful_decisions'],
                    'avg_success_rate': (
                        (deepseek_stats['success_rate'] + qwen_stats['success_rate']) / 2
                        if deepseek_stats['total_decisions'] > 0 or qwen_stats['total_decisions'] > 0
                        else 0
                    )
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get AI performance: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
