'use client';

import React, { useState, useEffect } from 'react';
import { Card, Table, Button, message, Spin, Tag, Modal, Form, Input, InputNumber, Space, Statistic, Row, Col } from 'antd';
import { ReloadOutlined, EditOutlined, DollarOutlined, SyncOutlined, InfoCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

// 使用相对路径，通过Nginx代理到后端
const API_BASE_URL = '';

interface PricingData {
  provider: string;
  model: string;
  input_price: number;
  output_price: number;
  cache_price?: number;
  last_updated: string;
  source: string;
}

interface PricingStats {
  total_models: number;
  total_providers: number;
  avg_input_price: number;
  avg_output_price: number;
}

export default function AIPricingPage() {
  const [loading, setLoading] = useState(false);
  const [pricingData, setPricingData] = useState<PricingData[]>([]);
  const [stats, setStats] = useState<PricingStats | null>(null);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingRecord, setEditingRecord] = useState<PricingData | null>(null);
  const [form] = Form.useForm();

  // 获取价格表数据
  const fetchPricingData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/ai-pricing/pricing-table`);
      if (response.data.success) {
        const data = response.data.data;
        
        // 转换数据格式
        const tableData: PricingData[] = [];
        Object.entries(data).forEach(([provider, models]: [string, any]) => {
          Object.entries(models).forEach(([model, pricing]: [string, any]) => {
            tableData.push({
              provider,
              model,
              input_price: pricing.input_price,
              output_price: pricing.output_price,
              cache_price: pricing.cache_price,
              last_updated: pricing.last_updated,
              source: pricing.source
            });
          });
        });
        
        setPricingData(tableData);
        calculateStats(tableData);
      }
    } catch (error) {
      console.error('获取价格表失败:', error);
      message.error('获取价格表失败');
    } finally {
      setLoading(false);
    }
  };

  // 计算统计数据
  const calculateStats = (data: PricingData[]) => {
    const providers = new Set(data.map(d => d.provider));
    const avgInput = data.reduce((sum, d) => sum + d.input_price, 0) / data.length;
    const avgOutput = data.reduce((sum, d) => sum + d.output_price, 0) / data.length;
    
    setStats({
      total_models: data.length,
      total_providers: providers.size,
      avg_input_price: avgInput,
      avg_output_price: avgOutput
    });
  };

  // 同步官方价格
  const syncOfficialPricing = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/ai-pricing/sync-official`);
      if (response.data.success) {
        message.success('同步成功');
        fetchPricingData();
      }
    } catch (error) {
      console.error('同步失败:', error);
      message.error('同步失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开编辑对话框
  const handleEdit = (record: PricingData) => {
    setEditingRecord(record);
    form.setFieldsValue({
      provider: record.provider,
      model: record.model,
      input_price: record.input_price,
      output_price: record.output_price,
      cache_price: record.cache_price
    });
    setEditModalVisible(true);
  };

  // 更新价格
  const handleUpdatePrice = async (values: any) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/ai-pricing/update-price`, values);
      if (response.data.success) {
        message.success('更新成功');
        setEditModalVisible(false);
        fetchPricingData();
      }
    } catch (error) {
      console.error('更新失败:', error);
      message.error('更新失败');
    }
  };

  useEffect(() => {
    fetchPricingData();
  }, []);

  const columns = [
    {
      title: '平台',
      dataIndex: 'provider',
      key: 'provider',
      width: 120,
      render: (provider: string) => {
        const colorMap: Record<string, string> = {
          qwen: 'blue',
          deepseek: 'purple',
          doubao: 'orange',
          openai: 'green',
          claude: 'cyan'
        };
        return <Tag color={colorMap[provider] || 'default'}>{provider.toUpperCase()}</Tag>;
      }
    },
    {
      title: '模型',
      dataIndex: 'model',
      key: 'model',
      width: 200,
      render: (model: string) => <span className="font-mono text-sm">{model}</span>
    },
    {
      title: '输入价格',
      dataIndex: 'input_price',
      key: 'input_price',
      width: 120,
      render: (price: number) => (
        <span className="text-green-600 font-semibold">
          ¥{price.toFixed(4)}/1K
        </span>
      )
    },
    {
      title: '输出价格',
      dataIndex: 'output_price',
      key: 'output_price',
      width: 120,
      render: (price: number) => (
        <span className="text-blue-600 font-semibold">
          ¥{price.toFixed(4)}/1K
        </span>
      )
    },
    {
      title: '缓存价格',
      dataIndex: 'cache_price',
      key: 'cache_price',
      width: 120,
      render: (price?: number) => 
        price ? (
          <span className="text-purple-600 font-semibold">
            ¥{price.toFixed(4)}/1K
          </span>
        ) : (
          <span className="text-gray-400">-</span>
        )
    },
    {
      title: '数据来源',
      dataIndex: 'source',
      key: 'source',
      width: 100,
      render: (source: string) => {
        const colorMap: Record<string, string> = {
          official: 'success',
          manual: 'warning',
          default: 'default'
        };
        const textMap: Record<string, string> = {
          official: '官方',
          manual: '手动',
          default: '默认'
        };
        return <Tag color={colorMap[source] || 'default'}>{textMap[source] || source}</Tag>;
      }
    },
    {
      title: '更新时间',
      dataIndex: 'last_updated',
      key: 'last_updated',
      width: 180,
      render: (time: string) => (
        <span className="text-gray-500 text-xs">
          {new Date(time).toLocaleString('zh-CN')}
        </span>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right' as const,
      render: (_: any, record: PricingData) => (
        <Button
          type="link"
          size="small"
          icon={<EditOutlined />}
          onClick={() => handleEdit(record)}
        >
          编辑
        </Button>
      )
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI定价管理</h1>
          <p className="text-gray-500 mt-1">管理各AI平台的模型价格信息</p>
        </div>
        <Space>
          <Button
            icon={<SyncOutlined />}
            onClick={syncOfficialPricing}
            loading={loading}
          >
            同步官方价格
          </Button>
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={fetchPricingData}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总模型数"
                value={stats.total_models}
                prefix={<DollarOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="平台数"
                value={stats.total_providers}
                prefix={<InfoCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="平均输入价格"
                value={stats.avg_input_price}
                precision={4}
                prefix="¥"
                suffix="/1K"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="平均输出价格"
                value={stats.avg_output_price}
                precision={4}
                prefix="¥"
                suffix="/1K"
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 价格表 */}
      <Card>
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={pricingData}
            rowKey={(record) => `${record.provider}-${record.model}`}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条记录`
            }}
            scroll={{ x: 1200 }}
          />
        </Spin>
      </Card>

      {/* 编辑对话框 */}
      <Modal
        title="编辑价格"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdatePrice}
        >
          <Form.Item
            label="平台"
            name="provider"
          >
            <Input disabled />
          </Form.Item>
          
          <Form.Item
            label="模型"
            name="model"
          >
            <Input disabled />
          </Form.Item>
          
          <Form.Item
            label="输入价格 (元/1K tokens)"
            name="input_price"
            rules={[{ required: true, message: '请输入输入价格' }]}
          >
            <InputNumber
              min={0}
              step={0.0001}
              precision={4}
              style={{ width: '100%' }}
            />
          </Form.Item>
          
          <Form.Item
            label="输出价格 (元/1K tokens)"
            name="output_price"
            rules={[{ required: true, message: '请输入输出价格' }]}
          >
            <InputNumber
              min={0}
              step={0.0001}
              precision={4}
              style={{ width: '100%' }}
            />
          </Form.Item>
          
          <Form.Item
            label="缓存价格 (元/1K tokens，可选)"
            name="cache_price"
          >
            <InputNumber
              min={0}
              step={0.0001}
              precision={4}
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

