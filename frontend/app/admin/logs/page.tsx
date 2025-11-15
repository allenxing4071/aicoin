"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';

interface LogFile {
  name: string;
  size: number;
  modified: string;
  lines: number;
}

interface LogStats {
  total_files: number;
  total_size: string;
  error_count: number;
  warning_count: number;
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  module?: string;
}

export default function LogsPage() {
  const [files, setFiles] = useState<LogFile[]>([]);
  const [stats, setStats] = useState<LogStats | null>(null);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [logContent, setLogContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [viewLines, setViewLines] = useState(100);

  useEffect(() => {
    fetchLogFiles();
    fetchLogStats();
  }, []);

  const fetchLogFiles = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/api/v1/admin/logs/files', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const result = await response.json();
      if (result.success) {
        setFiles(result.data);
        if (result.data.length > 0 && !selectedFile) {
          setSelectedFile(result.data[0].name);
          fetchLogContent(result.data[0].name);
        }
      }
    } catch (error) {
      console.error('Failed to fetch log files:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLogStats = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('/api/v1/admin/logs/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const result = await response.json();
      if (result.success) {
        setStats(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch log stats:', error);
    }
  };

  const fetchLogContent = async (filename: string, lines: number = viewLines) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`/api/v1/admin/logs/view?filename=${filename}&lines=${lines}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const result = await response.json();
      if (result.success) {
        setLogContent(result.data.content);
      }
    } catch (error) {
      console.error('Failed to fetch log content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (filename: string) => {
    setSelectedFile(filename);
    fetchLogContent(filename);
  };

  const handleDownload = (filename: string) => {
    const token = localStorage.getItem('admin_token');
    window.open(`/api/v1/admin/logs/download?filename=${filename}&token=${token}`, '_blank');
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getLogLevelColor = (line: string) => {
    if (line.includes('ERROR')) return 'text-red-600 bg-red-50';
    if (line.includes('WARNING')) return 'text-yellow-600 bg-yellow-50';
    if (line.includes('INFO')) return 'text-blue-600 bg-blue-50';
    if (line.includes('DEBUG')) return 'text-gray-600 bg-gray-50';
    return 'text-gray-800';
  };

  return (
    <div className="w-full max-w-full p-6 space-y-6">
      {/* 页面标题 */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 shadow-lg">
        <h1 className="text-3xl font-bold text-white mb-2">📋 日志管理中心</h1>
        <p className="text-blue-100">实时监控系统日志，排查问题，确保系统稳定运行</p>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">日志文件</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total_files}</p>
              </div>
              <div className="text-4xl">📁</div>
            </div>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">总大小</p>
                <p className="text-2xl font-bold text-green-900">{stats.total_size}</p>
              </div>
              <div className="text-4xl">💾</div>
            </div>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">错误数</p>
                <p className="text-2xl font-bold text-red-900">{stats.error_count}</p>
              </div>
              <div className="text-4xl">❌</div>
            </div>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">警告数</p>
                <p className="text-2xl font-bold text-yellow-900">{stats.warning_count}</p>
              </div>
              <div className="text-4xl">⚠️</div>
            </div>
          </Card>
        </div>
      )}

      {/* 主内容区 - 自适应宽度 */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 左侧：文件列表 */}
        <div className="lg:col-span-1">
          <Card className="p-4">
            <h3 className="text-lg font-bold mb-4 text-gray-800">📂 日志文件</h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {files.map((file) => (
                <div
                  key={file.name}
                  onClick={() => handleFileSelect(file.name)}
                  className={`p-3 rounded-lg cursor-pointer transition-all ${
                    selectedFile === file.name
                      ? 'bg-blue-100 border-2 border-blue-500'
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-800 truncate">
                      {file.name}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownload(file.name);
                      }}
                      className="text-blue-600 hover:text-blue-800 text-xs"
                    >
                      ⬇️
                    </button>
                  </div>
                  <div className="text-xs text-gray-500">
                    <div>{formatSize(file.size)}</div>
                    <div>{file.lines} 行</div>
                    <div>{file.modified}</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* 右侧：日志内容 - 自适应宽度 */}
        <div className="lg:col-span-3">
          <Card className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-800">📄 {selectedFile || '选择一个日志文件'}</h3>
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">显示行数:</label>
                <select
                  value={viewLines}
                  onChange={(e) => {
                    const lines = parseInt(e.target.value);
                    setViewLines(lines);
                    if (selectedFile) {
                      fetchLogContent(selectedFile, lines);
                    }
                  }}
                  className="border rounded px-2 py-1 text-sm"
                >
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={200}>200</option>
                  <option value={500}>500</option>
                  <option value={1000}>1000</option>
                </select>
                <button
                  onClick={() => selectedFile && fetchLogContent(selectedFile)}
                  className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                >
                  🔄 刷新
                </button>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">加载中...</div>
              </div>
            ) : (
              <div className="bg-gray-900 rounded-lg p-4 max-h-[600px] overflow-auto">
                <pre className="text-xs text-gray-100 font-mono whitespace-pre-wrap break-all">
                  {logContent.split('\n').map((line, index) => (
                    <div
                      key={index}
                      className={`py-0.5 px-2 rounded ${getLogLevelColor(line)}`}
                    >
                      {line}
                    </div>
                  ))}
                </pre>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
