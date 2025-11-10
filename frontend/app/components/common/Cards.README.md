# 统一卡片组件库使用指南

## 📦 组件列表

### 1. StatCard - 统计卡片（方形卡片）
用于显示统计数据的方形卡片，支持8种颜色主题。

#### 使用示例
```tsx
import { StatCard, StatCardGrid } from '@/app/components/common/Cards';

<StatCardGrid columns={4}>
  <StatCard 
    label="启用平台" 
    value={4} 
    icon="🕵️"
    color="purple" 
  />
  <StatCard 
    label="总调用次数" 
    value={145} 
    color="blue" 
  />
  <StatCard 
    label="成功率" 
    value="93.1%" 
    color="green" 
  />
  <StatCard 
    label="总成本" 
    value="¥3.32" 
    color="orange" 
  />
</StatCardGrid>
```

#### Props
- `label`: string - 卡片标签
- `value`: string | number - 显示的值
- `icon?`: string - 可选图标（emoji）
- `color?`: 颜色主题（默认 'blue'）
- `className?`: 额外的CSS类

### 2. InfoCard - 信息卡片
用于显示提示、建议等信息的卡片。

#### 使用示例
```tsx
import { InfoCard } from '@/app/components/common/Cards';

<InfoCard
  icon="📈"
  title="成本优化建议"
  description="建议优先使用成本较低的模型"
  color="blue"
/>
```

#### Props
- `icon`: string - 图标（emoji）
- `title`: string - 标题
- `description`: string - 描述文字
- `color?`: 颜色主题（默认 'blue'）
- `className?`: 额外的CSS类

### 3. ListCard - 列表卡片
用于显示列表项的卡片，带左侧彩色边框。

#### 使用示例
```tsx
import { ListCard } from '@/app/components/common/Cards';

<ListCard color="purple">
  <div className="flex items-start justify-between mb-4">
    <div className="flex items-center gap-3">
      <div className="text-3xl">🕵️</div>
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Qwen-Plus</h3>
        <p className="text-sm text-gray-500">qwen • intelligence</p>
      </div>
    </div>
    <span className="px-3 py-1 text-xs rounded-full font-medium bg-green-100 text-green-800">
      ✓ 已启用
    </span>
  </div>
  {/* 更多内容 */}
</ListCard>
```

#### Props
- `children`: React.ReactNode - 卡片内容
- `color?`: 颜色主题（默认 'blue'）
- `className?`: 额外的CSS类

### 4. PageHeaderCard - 页面头部卡片
用于页面顶部的标题区域，带渐变背景。

#### 使用示例
```tsx
import { PageHeaderCard } from '@/app/components/common/Cards';

<PageHeaderCard
  icon="🕵️"
  title="情报模型配置"
  description="管理Qwen系列情报收集模型"
  color="purple"
  action={
    <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg">
      + 添加平台
    </button>
  }
/>
```

#### Props
- `icon`: string - 图标（emoji）
- `title`: string - 页面标题
- `description`: string - 页面描述
- `color?`: 颜色主题（默认 'blue'）
- `action?`: React.ReactNode - 右侧操作按钮
- `className?`: 额外的CSS类

### 5. StatCardGrid - 统计卡片网格容器
用于布局多个统计卡片。

#### 使用示例
```tsx
import { StatCardGrid, StatCard } from '@/app/components/common/Cards';

<StatCardGrid columns={4}>
  <StatCard label="卡片1" value={100} color="purple" />
  <StatCard label="卡片2" value={200} color="blue" />
  <StatCard label="卡片3" value={300} color="green" />
  <StatCard label="卡片4" value={400} color="orange" />
</StatCardGrid>
```

#### Props
- `children`: React.ReactNode - 子组件（通常是 StatCard）
- `columns?`: 2 | 3 | 4 | 5 | 6 - 列数（默认 4）
- `className?`: 额外的CSS类

### 6. ContentCard - 内容卡片
用于包裹页面内容的白色卡片。

#### 使用示例
```tsx
import { ContentCard } from '@/app/components/common/Cards';

<ContentCard title="数据统计">
  <p>这里是卡片内容...</p>
</ContentCard>
```

#### Props
- `children`: React.ReactNode - 卡片内容
- `title?`: string - 可选标题
- `className?`: 额外的CSS类

## 🎨 支持的颜色主题

所有组件都支持以下8种颜色主题：
- `purple` - 紫色
- `blue` - 蓝色
- `green` - 绿色
- `orange` - 橙色
- `red` - 红色
- `pink` - 粉色
- `yellow` - 黄色
- `indigo` - 靛蓝色
- `gray` - 灰色（仅 StatCard）

## 📝 完整页面示例

```tsx
'use client';

import { useState, useEffect } from 'react';
import { 
  PageHeaderCard, 
  StatCardGrid, 
  StatCard, 
  ListCard,
  InfoCard 
} from '@/app/components/common/Cards';

export default function ExamplePage() {
  const [data, setData] = useState(null);

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <PageHeaderCard
        icon="🕵️"
        title="情报模型配置"
        description="管理Qwen系列情报收集模型"
        color="purple"
        action={
          <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg">
            + 添加平台
          </button>
        }
      />

      {/* 统计卡片 */}
      <StatCardGrid columns={4}>
        <StatCard label="启用平台" value={4} color="purple" />
        <StatCard label="总调用次数" value={145} color="blue" />
        <StatCard label="成功率" value="93.1%" color="green" />
        <StatCard label="总成本" value="¥3.32" color="orange" />
      </StatCardGrid>

      {/* 信息提示 */}
      <InfoCard
        icon="💡"
        title="优化建议"
        description="建议优先使用成本较低的模型以降低总体开销"
        color="blue"
      />

      {/* 列表卡片 */}
      <div className="space-y-4">
        <ListCard color="purple">
          <h3 className="text-lg font-semibold mb-2">Qwen-Plus</h3>
          <p className="text-gray-600">情报收集模型</p>
        </ListCard>
      </div>
    </div>
  );
}
```

## ✅ 迁移指南

### 旧代码
```tsx
<div className="bg-purple-50 border-purple-200 rounded-lg p-4 border">
  <div className="text-sm text-gray-600 mb-2">启用平台</div>
  <div className="text-2xl font-bold text-purple-600">4</div>
</div>
```

### 新代码
```tsx
<StatCard label="启用平台" value={4} color="purple" />
```

## 🚀 优势

1. **代码复用** - 一次定义，到处使用
2. **统一样式** - 所有页面风格一致
3. **易于维护** - 修改组件即可更新所有页面
4. **类型安全** - TypeScript 类型检查
5. **简洁代码** - 减少重复代码

