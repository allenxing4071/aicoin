"""
日志管理系统配置
支持多级别、多输出、自动轮转
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

# 日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logging():
    """
    配置项目日志系统
    
    日志输出：
    1. 控制台：INFO及以上级别
    2. 文件（所有日志）：logs/aicoin_all.log
    3. 文件（错误日志）：logs/aicoin_error.log
    4. 文件（AI决策日志）：logs/ai_decisions.log
    5. 文件（交易日志）：logs/trading.log
    """
    
    # 获取日志级别（从环境变量）
    log_level = os.getenv("LOG_LEVEL", "INFO")
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    
    # 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 捕获所有级别，由handler过滤
    
    # 清除现有handlers（避免重复）
    root_logger.handlers.clear()
    
    # ===== 1. 控制台输出 (彩色) =====
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # ===== 2. 所有日志文件 (自动轮转) =====
    all_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "aicoin_all.log",
        when="midnight",  # 每天午夜轮转
        interval=1,
        backupCount=30,  # 保留30天
        encoding="utf-8"
    )
    all_handler.setLevel(logging.DEBUG)
    all_handler.setFormatter(DetailedFormatter())
    root_logger.addHandler(all_handler)
    
    # ===== 3. 错误日志文件 =====
    error_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_DIR / "aicoin_error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(DetailedFormatter())
    root_logger.addHandler(error_handler)
    
    # ===== 4. AI决策日志（专用） =====
    ai_logger = logging.getLogger("app.services.decision")
    ai_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "ai_decisions.log",
        when="midnight",
        interval=1,
        backupCount=90,  # AI决策保留90天
        encoding="utf-8"
    )
    ai_handler.setLevel(logging.INFO)
    ai_handler.setFormatter(AIDecisionFormatter())
    ai_logger.addHandler(ai_handler)
    
    # ===== 5. 交易日志（专用） =====
    trading_logger = logging.getLogger("app.services.orchestrator")
    trading_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / "trading.log",
        when="midnight",
        interval=1,
        backupCount=90,  # 交易记录保留90天
        encoding="utf-8"
    )
    trading_handler.setLevel(logging.INFO)
    trading_handler.setFormatter(TradingFormatter())
    trading_logger.addHandler(trading_handler)
    
    # ===== 6. 抑制第三方库的DEBUG日志 =====
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # 启动日志
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"🚀 AIcoin Trading System 启动")
    logger.info(f"📊 日志级别: {log_level}")
    logger.info(f"📁 日志目录: {LOG_DIR.absolute()}")
    logger.info(f"🔧 调试模式: {os.getenv('DEBUG', 'false')}")
    logger.info("=" * 60)


# ===== 自定义日志格式器 =====

class ColoredFormatter(logging.Formatter):
    """彩色控制台输出"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class DetailedFormatter(logging.Formatter):
    """详细日志格式（文件）"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class AIDecisionFormatter(logging.Formatter):
    """AI决策专用格式"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)s | 🤖 AI决策 | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class TradingFormatter(logging.Formatter):
    """交易专用格式"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)s | 💰 交易 | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

