"use client";

import React, { useState, useEffect } from 'react';
import { Table, Tag, Space, Button, DatePicker, Select, message, Card, Statistic, Row, Col } from 'antd';
import { ReloadOutlined, DownloadOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

interface LogEntry {
  id: number;
  timestamp: string;
  level: string;
  module: string;
  message: string;
  user?: string;
  ip_address?: string;
  request_id?: string;
}

interface LogStats {
  total_logs: number;
    error_count: number;
    warning_count: number;
  info_count: number;
}

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [stats, setStats] = useState<LogStats>({
    total_logs: 0,
    error_count: 0,
    warning_count: 0,
    info_count: 0,
  });
  const [loading, setLoading] = useState(false);
  const [levelFilter, setLevelFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, [levelFilter, dateRange]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('admin_token');
      const params: any = {};
      
      if (levelFilter !== 'all') {
        params.level = levelFilter;
      }
      
      if (dateRange) {
        params.start_date = dateRange[0].format('YYYY-MM-DD');
        params.end_date = dateRange[1].format('YYYY-MM-DD');
      }

      const response = await axios.get(`${API_BASE}/api/v1/admin/logs`, {
        headers: { Authorization: `Bearer ${token}` },
        params,
      });

      if (response.data.success) {
        setLogs(response.data.data || []);
      }
    } catch (error: any) {
      message.error('获取日志失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await axios.get(`${API_BASE}/api/v1/admin/logs/stats`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('获取日志统计失败:', error);
    }
  };

  const handleExport = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await axios.get(`${API_BASE}/api/v1/admin/logs/export`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `logs_${dayjs().format('YYYY-MM-DD_HH-mm-ss')}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      message.success('日志导出成功');
    } catch (error: any) {
      message.error('导出失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleCleanup = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      await axios.post(
        `${API_BASE}/api/v1/admin/logs/cleanup`,
        { days: 30 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      message.success('清理完成');
      fetchLogs();
      fetchStats();
    } catch (error: any) {
      message.error('清理失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'red';
      case 'WARNING':
        return 'orange';
      case 'INFO':
        return 'blue';
      case 'DEBUG':
        return 'default';
      default:
        return 'default';
    }
  };

  const columns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (level: string) => (
        <Tag color={getLevelColor(level)}>{level.toUpperCase()}</Tag>
      ),
    },
    {
      title: '模块',
      dataIndex: 'module',
      key: 'module',
      width: 150,
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: '用户',
      dataIndex: 'user',
      key: 'user',
      width: 120,
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 140,
    },
  ];

    return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ fontSize: '24px', marginBottom: '24px' }}>📋 日志管理</h1>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic title="总日志数" value={stats.total_logs} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="错误"
              value={stats.error_count}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="警告"
              value={stats.warning_count}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="信息"
              value={stats.info_count}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选和操作 */}
      <Card style={{ marginBottom: '16px' }}>
        <Space wrap>
          <Select
            value={levelFilter}
            onChange={setLevelFilter}
            style={{ width: 120 }}
          >
            <Option value="all">全部级别</Option>
            <Option value="error">ERROR</Option>
            <Option value="warning">WARNING</Option>
            <Option value="info">INFO</Option>
            <Option value="debug">DEBUG</Option>
          </Select>

          <RangePicker
            value={dateRange}
            onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
            placeholder={['开始日期', '结束日期']}
          />

          <Button icon={<ReloadOutlined />} onClick={fetchLogs}>
            刷新
          </Button>

          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出CSV
          </Button>

          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={handleCleanup}
          >
            清理30天前日志
          </Button>
        </Space>
      </Card>

      {/* 日志表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
}
