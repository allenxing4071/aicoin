'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Table, Button, Tag, Space, Modal, message, Select, Input } from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  HistoryOutlined, 
  LineChartOutlined,
  ReloadOutlined,
  RobotOutlined,
  ExperimentOutlined
} from '@ant-design/icons';

const { Search } = Input;
const { Option } = Select;

interface PromptTemplate {
  id: number;
  name: string;
  category: string;
  permission_level: string | null;
  content: string;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function PromptsListPage() {
  const router = useRouter();
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [reloading, setReloading] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    fetchPrompts();
  }, [categoryFilter, levelFilter]);

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('admin_token');
      
      // 构建查询参数
      const params = new URLSearchParams();
      if (categoryFilter) params.append('category', categoryFilter);
      if (levelFilter) params.append('permission_level', levelFilter);
      
      const response = await fetch(`/api/v1/prompts/v2/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('获取失败');
      
      const data = await response.json();
      setPrompts(data);
    } catch (error) {
      message.error('获取 Prompt 列表失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleReload = async () => {
    try {
      setReloading(true);
      const token = localStorage.getItem('admin_token');
      
      const response = await fetch('/api/v1/prompts/v2/reload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          category: categoryFilter || null
        })
      });

      if (!response.ok) throw new Error('热重载失败');
      
      message.success('✅ Prompt 模板已热重载');
      fetchPrompts();
    } catch (error) {
      message.error('❌ 热重载失败');
      console.error(error);
    } finally {
      setReloading(false);
    }
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这个 Prompt 模板吗？',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        try {
          const token = localStorage.getItem('admin_token');
          const response = await fetch(`/api/v1/prompts/v2/${id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (!response.ok) throw new Error('删除失败');
          
          message.success('删除成功');
          fetchPrompts();
        } catch (error) {
          message.error('删除失败');
          console.error(error);
        }
      }
    });
  };

  const getCategoryTag = (category: string) => {
    const colors: Record<string, string> = {
      'decision': 'blue',
      'debate': 'green',
      'intelligence': 'purple'
    };
    return <Tag color={colors[category] || 'default'}>{category}</Tag>;
  };

  const getLevelTag = (level: string | null) => {
    if (!level) return <Tag>通用</Tag>;
    
    const colors: Record<string, string> = {
      'L0': 'green',
      'L1': 'cyan',
      'L2': 'blue',
      'L3': 'orange',
      'L4': 'red',
      'L5': 'volcano'
    };
    return <Tag color={colors[level] || 'default'}>{level}</Tag>;
  };

  const filteredPrompts = prompts.filter(prompt => {
    if (!searchText) return true;
    return prompt.name.toLowerCase().includes(searchText.toLowerCase()) ||
           prompt.content.toLowerCase().includes(searchText.toLowerCase());
  });

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (text: string, record: PromptTemplate) => (
        <div>
          <div className="font-medium">{text}</div>
          <div className="text-xs text-gray-500">v{record.version}</div>
        </div>
      ),
    },
    {
      title: '类别',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: string) => getCategoryTag(category),
    },
    {
      title: '权限等级',
      dataIndex: 'permission_level',
      key: 'permission_level',
      width: 120,
      render: (level: string | null) => getLevelTag(level),
    },
    {
      title: '内容预览',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (content: string) => (
        <div className="text-sm text-gray-600 truncate max-w-md">
          {content.substring(0, 100)}...
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '激活' : '停用'}
        </Tag>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 280,
      fixed: 'right' as const,
      render: (_: any, record: PromptTemplate) => (
        <Space size="small">
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => router.push(`/admin/prompts-v2/${record.id}/edit`)}
          >
            编辑
          </Button>
          <Button
            size="small"
            icon={<HistoryOutlined />}
            onClick={() => router.push(`/admin/prompts-v2/${record.id}/versions`)}
          >
            版本
          </Button>
          <Button
            size="small"
            icon={<LineChartOutlined />}
            onClick={() => router.push(`/admin/prompts-v2/${record.id}/metrics`)}
          >
            指标
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Prompt 模板管理</h1>
          <p className="text-gray-500 mt-1">管理 AI 决策、辩论、情报分析的 Prompt 模板</p>
        </div>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => router.push('/admin/prompts-v2/create')}
          >
            创建 Prompt
          </Button>
          <Button
            icon={<RobotOutlined />}
            onClick={() => router.push('/admin/prompts-v2/generate')}
          >
            AI 生成
          </Button>
          <Button
            icon={<ExperimentOutlined />}
            onClick={() => router.push('/admin/prompts-v2/ab-tests')}
          >
            A/B 测试
          </Button>
          <Button
            icon={<ReloadOutlined />}
            loading={reloading}
            onClick={handleReload}
          >
            热重载
          </Button>
        </Space>
      </div>

      <div className="mb-4 flex gap-4">
        <Search
          placeholder="搜索名称或内容"
          allowClear
          style={{ width: 300 }}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <Select
          placeholder="筛选类别"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setCategoryFilter(value || '')}
        >
          <Option value="decision">决策 (decision)</Option>
          <Option value="debate">辩论 (debate)</Option>
          <Option value="intelligence">情报 (intelligence)</Option>
        </Select>
        <Select
          placeholder="筛选权限等级"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setLevelFilter(value || '')}
        >
          <Option value="L0">L0 - 保守</Option>
          <Option value="L1">L1</Option>
          <Option value="L2">L2</Option>
          <Option value="L3">L3</Option>
          <Option value="L4">L4</Option>
          <Option value="L5">L5 - 激进</Option>
        </Select>
      </div>

      <Table
        columns={columns}
        dataSource={filteredPrompts}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1400 }}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 个模板`,
        }}
      />
    </div>
  );
}

