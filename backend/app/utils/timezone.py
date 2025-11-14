"""时区处理工具"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from app.core.config import settings


def get_beijing_time(dt: Optional[datetime] = None) -> datetime:
    """
    获取北京时间
    
    Args:
        dt: 可选的datetime对象，如果为None则返回当前时间
        
    Returns:
        北京时区的datetime对象
    """
    beijing_tz = ZoneInfo(settings.TIMEZONE)
    
    if dt is None:
        return datetime.now(beijing_tz)
    
    # 如果输入的datetime没有时区信息，假设它是UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    
    # 转换到北京时区
    return dt.astimezone(beijing_tz)


def format_beijing_time(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化为北京时间字符串
    
    Args:
        dt: datetime对象
        format_str: 格式化字符串
        
    Returns:
        格式化后的时间字符串
    """
    beijing_dt = get_beijing_time(dt)
    return beijing_dt.strftime(format_str)


def utc_to_beijing(dt: datetime) -> datetime:
    """
    UTC时间转北京时间
    
    Args:
        dt: UTC时间的datetime对象
        
    Returns:
        北京时区的datetime对象
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo(settings.TIMEZONE))


def beijing_to_utc(dt: datetime) -> datetime:
    """
    北京时间转UTC时间
    
    Args:
        dt: 北京时间的datetime对象
        
    Returns:
        UTC时区的datetime对象
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(settings.TIMEZONE))
    return dt.astimezone(ZoneInfo("UTC"))

