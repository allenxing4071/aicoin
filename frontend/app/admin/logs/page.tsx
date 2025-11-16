"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Card, Tabs, Statistic, Tag, Select, Button, Table, Space, message, Modal, Alert, Switch, Tooltip, Progress } from 'antd';
import {
  FileTextOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DownloadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  EyeOutlined,
  SettingOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import axios from 'axios';
import { usePermissions } from '../../hooks/usePermissions';

const { TabPane } = Tabs;
const { Option } = Select;

// 配置axios拦截器，自动添加JWT token
const axiosInstance = axios.create();
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

interface LogFile {
  name: string;
  size: number;
  modified: string;
  lines: number;
}

interface LogStats {
  total_files: number;
  total_size: number;
  log_types: {
    all: { files: number; size: number };
    error: { files: number; size: number };
    ai_decisions: { files: number; size: number };
    trading: { files: number; size: number };
  };
  alerts: {
    error_count: number;
    warning_count: number;
    critical_count: number;
    recent_errors: Array<{ message: string; level: string }>;
  };
}

const LogManagementPage: React.FC = () => {
  const { hasPermission } = usePermissions();
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<LogFile[]>([]);
  const [stats, setStats] = useState<LogStats | null>(null);
  const [logLevel, setLogLevel] = useState('INFO');
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [viewContent, setViewContent] = useState('');
  const [viewFileName, setViewFileName] = useState('');
  const [viewLines, setViewLines] = useState(100);

  // 加载日志文件列表
  const fetchFiles = useCallback(async () => {
      setLoading(true);
    try {
      const response = await axiosInstance.get('/api/v1/admin/logs/files');
      if (response.data.success) {
        setFiles(response.data.data);
      } else {
        message.error('获取日志文件失败');
      }
    } catch (error) {
      console.error('Failed to fetch log files:', error);
      message.error('获取日志文件失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // 加载日志统计
  const fetchStats = useCallback(async () => {
    try {
      const response = await axiosInstance.get('/api/v1/admin/logs/stats');
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Failed to fetch log stats:', error);
    }
  }, []);

  // 加载日志级别
  const fetchLogLevel = useCallback(async () => {
    try {
      const response = await axiosInstance.get('/api/v1/admin/logs/level');
      if (response.data.success) {
        setLogLevel(response.data.data.level);
      }
    } catch (error) {
      console.error('Failed to fetch log level:', error);
    }
  }, []);

  useEffect(() => {
    if (hasPermission('log:view')) {
      fetchFiles();
      fetchStats();
      fetchLogLevel();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasPermission]);

  // 查看日志文件
  const handleViewLog = async (filename: string) => {
      setLoading(true);
    try {
      const response = await axiosInstance.get(`/api/v1/admin/logs/view`, {
        params: { filename, lines: viewLines }
      });
      if (response.data.success) {
        setViewFileName(filename);
        setViewContent(response.data.data.content);
        setViewModalVisible(true);
      } else {
        message.error('查看日志失败');
      }
    } catch (error) {
      console.error('Failed to view log:', error);
      message.error('查看日志失败');
    } finally {
      setLoading(false);
    }
  };

  // 下载日志文件
  const handleDownloadLog = async (filename: string) => {
    try {
      const response = await axiosInstance.get(`/api/v1/admin/logs/download`, {
        params: { filename },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('日志下载成功');
    } catch (error) {
      console.error('Failed to download log:', error);
      message.error('日志下载失败');
    }
  };

  // 清理日志
  const handleCleanupLogs = async () => {
    Modal.confirm({
      title: '确认清理日志？',
      content: '将删除90天前的所有轮转日志文件（当前日志不受影响）',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await axiosInstance.post('/api/v1/admin/logs/cleanup');
          if (response.data.success) {
            const { deleted_count, freed_space } = response.data.data;
            message.success(`清理完成！删除 ${deleted_count} 个文件，释放 ${(freed_space / 1024 / 1024).toFixed(2)} MB 空间`);
            fetchFiles();
            fetchStats();
          } else {
            message.error('清理失败');
      }
    } catch (error) {
          console.error('Failed to cleanup logs:', error);
          message.error('清理失败');
        }
      }
    });
  };

  // 更新日志级别
  const handleUpdateLogLevel = async (level: string) => {
    try {
      const response = await axiosInstance.post('/api/v1/admin/logs/level', { level });
      if (response.data.success) {
        message.success(response.data.message || '日志级别已更新');
        setLogLevel(level);
      } else {
        message.error('更新失败');
      }
    } catch (error) {
      console.error('Failed to update log level:', error);
      message.error('更新失败');
    }
  };

  // 格式化文件大小
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  // 文件列表表格列
  const fileColumns = [
    {
      title: '文件名',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => {
        let icon = <FileTextOutlined />;
        let color = 'default';
        if (name.includes('error')) {
          icon = <CloseCircleOutlined />;
          color = 'red';
        } else if (name.includes('ai_decision')) {
          icon = <ThunderboltOutlined />;
          color = 'purple';
        }
    return (
          <Space>
            <Tag color={color} icon={icon}>{name}</Tag>
          </Space>
        );
      }
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => formatSize(size),
      sorter: (a: LogFile, b: LogFile) => a.size - b.size
    },
    {
      title: '行数',
      dataIndex: 'lines',
      key: 'lines',
      render: (lines: number) => lines.toLocaleString(),
      sorter: (a: LogFile, b: LogFile) => a.lines - b.lines
    },
    {
      title: '修改时间',
      dataIndex: 'modified',
      key: 'modified',
      sorter: (a: LogFile, b: LogFile) => new Date(a.modified).getTime() - new Date(b.modified).getTime()
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: LogFile) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewLog(record.name)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownloadLog(record.name)}
          >
            下载
          </Button>
        </Space>
      )
    }
  ];

  if (!hasPermission('log:view')) {
    return (
      <div className="p-6">
        <Alert message="您没有权限访问日志管理" type="warning" showIcon />
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center">
            <FileTextOutlined className="mr-3 text-blue-600" />
            日志管理中心
          </h1>
          <p className="text-gray-500 mt-2">实时监控系统日志、错误报警、性能追踪</p>
        </div>

        {/* 统计卡片 */}
      {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="shadow-sm hover:shadow-md transition-shadow">
              <Statistic
                title="总文件数"
                value={stats.total_files}
                prefix={<FileTextOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
            <Card className="shadow-sm hover:shadow-md transition-shadow">
              <Statistic
                title="占用空间"
                value={formatSize(stats.total_size)}
                prefix={<FileTextOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
            <Card className="shadow-sm hover:shadow-md transition-shadow">
              <Statistic
                title="错误日志"
                value={stats.alerts.error_count}
                prefix={<CloseCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
            <Card className="shadow-sm hover:shadow-md transition-shadow">
              <Statistic
                title="警告日志"
                value={stats.alerts.warning_count}
                prefix={<WarningOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
            </div>
        )}

        {/* 报警区域 */}
        {stats && stats.alerts.critical_count > 0 && (
          <Alert
            message={`检测到 ${stats.alerts.critical_count} 条严重错误！`}
            description="请及时查看错误日志并处理"
            type="error"
            showIcon
            icon={<CloseCircleOutlined />}
            className="mb-6"
          />
        )}

        {/* 最近错误 */}
        {stats && stats.alerts.recent_errors.length > 0 && (
          <Card title="最近错误" className="mb-6 shadow-sm">
            <Space direction="vertical" className="w-full">
              {stats.alerts.recent_errors.map((error, index) => (
                <Alert
                  key={index}
                  message={<Tag color={error.level === 'CRITICAL' ? 'red' : 'orange'}>{error.level}</Tag>}
                  description={<code className="text-xs">{error.message}</code>}
                  type={error.level === 'CRITICAL' ? 'error' : 'warning'}
                  showIcon
                  className="mb-2"
                />
              ))}
            </Space>
          </Card>
        )}

        {/* 操作栏 */}
        <Card className="mb-6 shadow-sm">
          <Space wrap>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={() => {
                fetchFiles();
                fetchStats();
              }}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleCleanupLogs}
              disabled={!hasPermission('log:clean')}
            >
              清理旧日志
            </Button>
            <div className="flex items-center space-x-2">
              <SettingOutlined />
              <span>日志级别:</span>
              <Select
                value={logLevel}
                style={{ width: 120 }}
                onChange={handleUpdateLogLevel}
                disabled={!hasPermission('log:config')}
              >
                <Option value="DEBUG">DEBUG</Option>
                <Option value="INFO">INFO</Option>
                <Option value="WARNING">WARNING</Option>
                <Option value="ERROR">ERROR</Option>
                <Option value="CRITICAL">CRITICAL</Option>
              </Select>
              <Tooltip title="修改后需要重启后端服务才能完全生效">
                <WarningOutlined className="text-orange-500" />
              </Tooltip>
            </div>
          </Space>
        </Card>

        {/* 日志分类统计 */}
        {stats && (
          <Card title="日志分类统计" className="mb-6 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <div className="text-gray-500 text-sm">所有日志</div>
                <div className="text-2xl font-bold text-blue-600">{stats.log_types.all.files} 个文件</div>
                <div className="text-gray-400 text-xs">{formatSize(stats.log_types.all.size)}</div>
              </div>
              <div className="border-l-4 border-red-500 pl-4">
                <div className="text-gray-500 text-sm">错误日志</div>
                <div className="text-2xl font-bold text-red-600">{stats.log_types.error.files} 个文件</div>
                <div className="text-gray-400 text-xs">{formatSize(stats.log_types.error.size)}</div>
              </div>
              <div className="border-l-4 border-purple-500 pl-4">
                <div className="text-gray-500 text-sm">AI决策日志</div>
                <div className="text-2xl font-bold text-purple-600">{stats.log_types.ai_decisions.files} 个文件</div>
                <div className="text-gray-400 text-xs">{formatSize(stats.log_types.ai_decisions.size)}</div>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <div className="text-gray-500 text-sm">交易日志</div>
                <div className="text-2xl font-bold text-green-600">{stats.log_types.trading.files} 个文件</div>
                <div className="text-gray-400 text-xs">{formatSize(stats.log_types.trading.size)}</div>
              </div>
            </div>
          </Card>
      )}

        {/* 文件列表 */}
        <Card title="日志文件列表" className="shadow-sm">
          <Table
            columns={fileColumns}
            dataSource={files}
            rowKey="name"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个文件`
            }}
          />
        </Card>

        {/* 查看日志模态框 */}
        <Modal
          title={`查看日志: ${viewFileName}`}
          open={viewModalVisible}
          onCancel={() => setViewModalVisible(false)}
          width={900}
          footer={[
            <Button key="close" onClick={() => setViewModalVisible(false)}>
              关闭
            </Button>,
            <Button
              key="download"
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => handleDownloadLog(viewFileName)}
            >
              下载完整日志
            </Button>
          ]}
        >
          <div className="mb-3">
            <span className="mr-2">显示最后:</span>
            <Select
              value={viewLines}
              style={{ width: 120 }}
              onChange={(value) => {
                setViewLines(value);
                handleViewLog(viewFileName);
              }}
            >
              <Option value={50}>50 行</Option>
              <Option value={100}>100 行</Option>
              <Option value={200}>200 行</Option>
              <Option value={500}>500 行</Option>
            </Select>
        </div>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-auto max-h-96 text-xs font-mono">
            {viewContent}
          </pre>
        </Modal>
      </div>
    </div>
  );
};

export default LogManagementPage;
