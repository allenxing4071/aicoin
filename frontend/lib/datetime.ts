/**
 * 时间格式化工具 - 统一使用北京时间
 */

/**
 * 格式化为北京时间字符串
 * @param date - Date对象、时间戳或ISO字符串
 * @param options - Intl.DateTimeFormatOptions配置
 * @returns 格式化后的时间字符串
 */
export function formatBeijingTime(
  date: Date | string | number,
  options?: Intl.DateTimeFormatOptions
): string {
  const dateObj = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    ...options,
  };

  return new Intl.DateTimeFormat('zh-CN', defaultOptions).format(dateObj);
}

/**
 * 格式化为北京时间日期字符串
 * @param date - Date对象、时间戳或ISO字符串
 * @returns 格式化后的日期字符串 (YYYY-MM-DD)
 */
export function formatBeijingDate(date: Date | string | number): string {
  return formatBeijingTime(date, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: undefined,
    minute: undefined,
    second: undefined,
  });
}

/**
 * 格式化为北京时间时间字符串
 * @param date - Date对象、时间戳或ISO字符串
 * @returns 格式化后的时间字符串 (HH:MM:SS)
 */
export function formatBeijingTimeOnly(date: Date | string | number): string {
  return formatBeijingTime(date, {
    year: undefined,
    month: undefined,
    day: undefined,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

/**
 * 格式化为北京时间短时间字符串
 * @param date - Date对象、时间戳或ISO字符串
 * @returns 格式化后的时间字符串 (HH:MM)
 */
export function formatBeijingTimeShort(date: Date | string | number): string {
  return formatBeijingTime(date, {
    year: undefined,
    month: undefined,
    day: undefined,
    hour: '2-digit',
    minute: '2-digit',
    second: undefined,
  });
}

/**
 * 格式化为北京时间完整日期时间字符串
 * @param date - Date对象、时间戳或ISO字符串
 * @returns 格式化后的日期时间字符串 (YYYY-MM-DD HH:MM:SS)
 */
export function formatBeijingDateTime(date: Date | string | number): string {
  const dateObj = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
  
  return dateObj.toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

/**
 * 获取当前北京时间
 * @returns Date对象
 */
export function getBeijingNow(): Date {
  return new Date();
}

/**
 * 将UTC时间字符串转换为北京时间显示
 * @param utcString - UTC时间字符串
 * @returns 北京时间字符串
 */
export function utcToBeijingString(utcString: string): string {
  return formatBeijingDateTime(utcString);
}

