"""
Prompt A/B测试框架
科学验证Prompt优化效果，确保统计显著性
"""

import logging
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
from scipy import stats
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.prompt_template import PromptABTest, PromptTemplate
from app.services.quantitative.risk_metrics import PromptRiskMetrics

logger = logging.getLogger(__name__)


class PromptABTestFramework:
    """
    Prompt A/B测试框架
    
    核心功能：
    1. 流量分配（50/50或自定义比例）
    2. 实时统计收集
    3. 卡方检验（Chi-Square Test）判断显著性
    4. 自动判定获胜者
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.risk_calculator = PromptRiskMetrics()
    
    async def create_ab_test(
        self,
        test_name: str,
        prompt_a_id: int,
        prompt_b_id: int,
        traffic_split: float = 0.5,
        duration_days: int = 7,
        created_by: Optional[int] = None
    ) -> PromptABTest:
        """
        创建A/B测试
        
        Args:
            test_name: 测试名称
            prompt_a_id: 对照组Prompt ID
            prompt_b_id: 实验组Prompt ID
            traffic_split: 流量分配比例（0-1，默认0.5表示50/50）
            duration_days: 测试持续天数
            created_by: 创建人ID
        
        Returns:
            创建的A/B测试对象
        """
        logger.info(f"创建A/B测试: {test_name} (A={prompt_a_id}, B={prompt_b_id}, split={traffic_split})")
        
        # 验证Prompt是否存在
        prompt_a = await self.db.get(PromptTemplate, prompt_a_id)
        prompt_b = await self.db.get(PromptTemplate, prompt_b_id)
        
        if not prompt_a or not prompt_b:
            raise ValueError("Prompt不存在")
        
        # 创建测试记录
        ab_test = PromptABTest(
            test_name=test_name,
            prompt_a_id=prompt_a_id,
            prompt_b_id=prompt_b_id,
            traffic_split=Decimal(str(traffic_split)),
            duration_days=duration_days,
            status='RUNNING',
            created_by=created_by
        )
        
        self.db.add(ab_test)
        await self.db.commit()
        await self.db.refresh(ab_test)
        
        logger.info(f"✅ A/B测试创建成功: {test_name} (ID: {ab_test.id})")
        
        return ab_test
    
    def assign_variant(self, test: PromptABTest) -> str:
        """
        分配流量到A或B组
        
        Args:
            test: A/B测试对象
        
        Returns:
            'A' 或 'B'
        """
        # 根据traffic_split分配
        if random.random() < float(test.traffic_split):
            return 'A'
        else:
            return 'B'
    
    async def record_decision_result(
        self,
        test_id: int,
        variant: str,
        is_win: bool,
        pnl: float
    ) -> None:
        """
        记录决策结果
        
        Args:
            test_id: 测试ID
            variant: 'A' 或 'B'
            is_win: 是否盈利
            pnl: 盈亏金额
        """
        test = await self.db.get(PromptABTest, test_id)
        if not test or test.status != 'RUNNING':
            return
        
        if variant == 'A':
            test.a_total_decisions += 1
            if is_win:
                test.a_winning_decisions += 1
            test.a_total_pnl = (test.a_total_pnl or Decimal(0)) + Decimal(str(pnl))
            test.a_win_rate = Decimal(test.a_winning_decisions) / Decimal(test.a_total_decisions)
        else:
            test.b_total_decisions += 1
            if is_win:
                test.b_winning_decisions += 1
            test.b_total_pnl = (test.b_total_pnl or Decimal(0)) + Decimal(str(pnl))
            test.b_win_rate = Decimal(test.b_winning_decisions) / Decimal(test.b_total_decisions)
        
        await self.db.commit()
        
        # 检查是否达到最小样本量
        if test.a_total_decisions >= 30 and test.b_total_decisions >= 30:
            await self._check_significance(test)
    
    async def _check_significance(self, test: PromptABTest) -> None:
        """
        检查统计显著性（卡方检验）
        
        Args:
            test: A/B测试对象
        """
        # 构建列联表
        # | 组别 | 盈利 | 亏损 |
        # | A    | a_win| a_loss|
        # | B    | b_win| b_loss|
        
        a_win = test.a_winning_decisions
        a_loss = test.a_total_decisions - a_win
        b_win = test.b_winning_decisions
        b_loss = test.b_total_decisions - b_win
        
        # 卡方检验
        observed = np.array([[a_win, a_loss], [b_win, b_loss]])
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        
        test.p_value = Decimal(str(p_value))
        test.is_significant = p_value < 0.05
        
        # 判定获胜者
        if test.is_significant:
            if test.a_win_rate > test.b_win_rate:
                test.winner = 'A'
            elif test.b_win_rate > test.a_win_rate:
                test.winner = 'B'
            else:
                test.winner = 'DRAW'
        
        await self.db.commit()
        
        logger.info(f"A/B测试显著性检验: {test.test_name} (p={p_value:.4f}, significant={test.is_significant}, winner={test.winner})")
    
    async def stop_test(self, test_id: int, conclusion: Optional[str] = None) -> PromptABTest:
        """
        停止A/B测试
        
        Args:
            test_id: 测试ID
            conclusion: 测试结论
        
        Returns:
            更新后的测试对象
        """
        test = await self.db.get(PromptABTest, test_id)
        if not test:
            raise ValueError("测试不存在")
        
        test.status = 'COMPLETED'
        test.end_time = datetime.now()
        
        # 最终统计显著性检验
        await self._check_significance(test)
        
        # 生成结论
        if not conclusion:
            conclusion = self._generate_conclusion(test)
        test.conclusion = conclusion
        
        await self.db.commit()
        await self.db.refresh(test)
        
        logger.info(f"✅ A/B测试已停止: {test.test_name} (获胜者: {test.winner})")
        
        return test
    
    def _generate_conclusion(self, test: PromptABTest) -> str:
        """
        生成测试结论
        
        Args:
            test: A/B测试对象
        
        Returns:
            结论文本
        """
        conclusion = f"""
========== A/B测试结论 ==========
测试名称: {test.test_name}
测试时长: {(test.end_time - test.start_time).days if test.end_time else 0}天

【A组（对照组）】
- 决策次数: {test.a_total_decisions}
- 盈利次数: {test.a_winning_decisions}
- 胜率: {test.a_win_rate:.2%}
- 总盈亏: ${test.a_total_pnl:.2f}
- 夏普比率: {test.a_sharpe_ratio or 'N/A'}

【B组（实验组）】
- 决策次数: {test.b_total_decisions}
- 盈利次数: {test.b_winning_decisions}
- 胜率: {test.b_win_rate:.2%}
- 总盈亏: ${test.b_total_pnl:.2f}
- 夏普比率: {test.b_sharpe_ratio or 'N/A'}

【统计检验】
- p值: {test.p_value:.4f}
- 统计显著: {'是' if test.is_significant else '否'}
- 获胜者: {test.winner or '未确定'}

【最终建议】
"""
        
        if not test.is_significant:
            conclusion += "⚠️  两组差异不显著（p>0.05），建议延长测试时间或增加样本量。"
        elif test.winner == 'A':
            conclusion += "✅ A组（对照组）显著优于B组，建议保持使用A组Prompt。"
        elif test.winner == 'B':
            conclusion += "✅ B组（实验组）显著优于A组，建议切换到B组Prompt。"
        else:
            conclusion += "⚠️  两组表现相当，可根据其他因素（如稳定性、可解释性）选择。"
        
        conclusion += "\n" + "=" * 35
        
        return conclusion
    
    async def get_active_tests(self) -> List[PromptABTest]:
        """
        获取所有正在运行的测试
        
        Returns:
            正在运行的测试列表
        """
        query = select(PromptABTest).where(PromptABTest.status == 'RUNNING')
        result = await self.db.execute(query)
        tests = result.scalars().all()
        
        return list(tests)
    
    async def auto_stop_expired_tests(self) -> int:
        """
        自动停止已过期的测试
        
        Returns:
            停止的测试数量
        """
        active_tests = await self.get_active_tests()
        stopped_count = 0
        
        for test in active_tests:
            # 检查是否超过duration_days
            elapsed_days = (datetime.now() - test.start_time).days
            if elapsed_days >= test.duration_days:
                await self.stop_test(test.id)
                stopped_count += 1
        
        logger.info(f"自动停止了 {stopped_count} 个过期的A/B测试")
        
        return stopped_count

