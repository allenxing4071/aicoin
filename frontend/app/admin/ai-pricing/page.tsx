"use client";

import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RefreshCw, Calculator, TrendingUp } from "lucide-react";

interface ModelPricing {
  input: number;
  output: number;
  input_cached?: number;
  description: string;
  last_updated: string;
  note?: string;
}

interface PricingTable {
  [provider: string]: {
    [model: string]: ModelPricing;
  };
}

interface PricingData {
  pricing_table: PricingTable;
  last_updated: string;
  currency: string;
  unit: string;
}

interface Comparison {
  provider: string;
  model: string;
  description: string;
  cost: number;
  input_price: number;
  output_price: number;
}

export default function AIPricingPage() {
  const [pricingData, setPricingData] = useState<PricingData | null>(null);
  const [comparisons, setComparisons] = useState<Comparison[]>([]);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [inputTokens, setInputTokens] = useState(1000);
  const [outputTokens, setOutputTokens] = useState(1000);

  const fetchPricingTable = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/ai-pricing/pricing-table");
      const result = await response.json();
      if (result.success) {
        setPricingData(result.data);
      }
    } catch (error) {
      console.error("获取价格表失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchComparisons = async () => {
    try {
      setComparing(true);
      const response = await fetch(
        `/api/v1/ai-pricing/compare-platforms?input_tokens=${inputTokens}&output_tokens=${outputTokens}`
      );
      const result = await response.json();
      if (result.success) {
        setComparisons(result.data.comparisons);
      }
    } catch (error) {
      console.error("获取平台对比失败:", error);
    } finally {
      setComparing(false);
    }
  };

  useEffect(() => {
    fetchPricingTable();
    fetchComparisons();
  }, []);

  const getProviderName = (provider: string) => {
    const names: { [key: string]: string } = {
      qwen: "阿里云 - 通义千问",
      deepseek: "DeepSeek",
      baidu: "百度智能云",
      tencent: "腾讯云",
      volcano: "火山引擎",
      openai: "OpenAI",
    };
    return names[provider] || provider;
  };

  const getProviderColor = (provider: string) => {
    const colors: { [key: string]: string } = {
      qwen: "bg-orange-100 text-orange-800",
      deepseek: "bg-blue-100 text-blue-800",
      baidu: "bg-purple-100 text-purple-800",
      tencent: "bg-green-100 text-green-800",
      volcano: "bg-red-100 text-red-800",
      openai: "bg-gray-100 text-gray-800",
    };
    return colors[provider] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI 模型定价管理</h1>
          <p className="text-gray-500 mt-1">
            查看和管理各平台 AI 模型的最新价格
          </p>
        </div>
        <Button onClick={fetchPricingTable} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          刷新价格表
        </Button>
      </div>

      {/* 价格表概览 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="w-5 h-5" />
            价格表概览
          </CardTitle>
          <CardDescription>
            单位: {pricingData?.unit} | 货币: {pricingData?.currency}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {pricingData &&
              Object.entries(pricingData.pricing_table).map(
                ([provider, models]) => (
                  <div key={provider} className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge className={getProviderColor(provider)}>
                        {getProviderName(provider)}
                      </Badge>
                      <span className="text-sm text-gray-500">
                        {Object.keys(models).length} 个模型
                      </span>
                    </div>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>模型</TableHead>
                          <TableHead>描述</TableHead>
                          <TableHead className="text-right">输入价格</TableHead>
                          <TableHead className="text-right">输出价格</TableHead>
                          <TableHead className="text-right">缓存价格</TableHead>
                          <TableHead>更新时间</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {Object.entries(models).map(([modelName, pricing]) => (
                          <TableRow key={modelName}>
                            <TableCell className="font-mono text-sm">
                              {modelName}
                            </TableCell>
                            <TableCell className="text-sm">
                              {pricing.description}
                              {pricing.note && (
                                <div className="text-xs text-gray-500 mt-1">
                                  {pricing.note}
                                </div>
                              )}
                            </TableCell>
                            <TableCell className="text-right font-mono">
                              ¥{pricing.input.toFixed(4)}
                            </TableCell>
                            <TableCell className="text-right font-mono">
                              ¥{pricing.output.toFixed(4)}
                            </TableCell>
                            <TableCell className="text-right font-mono">
                              {pricing.input_cached
                                ? `¥${pricing.input_cached.toFixed(4)}`
                                : "-"}
                            </TableCell>
                            <TableCell className="text-xs text-gray-500">
                              {pricing.last_updated}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )
              )}
          </div>
        </CardContent>
      </Card>

      {/* 平台成本对比 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            平台成本对比
          </CardTitle>
          <CardDescription>
            对比不同平台在相同 token 数量下的成本
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Token 输入 */}
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <label className="text-sm font-medium">输入 Tokens</label>
                <input
                  type="number"
                  value={inputTokens}
                  onChange={(e) => setInputTokens(Number(e.target.value))}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  min="0"
                />
              </div>
              <div className="flex-1">
                <label className="text-sm font-medium">输出 Tokens</label>
                <input
                  type="number"
                  value={outputTokens}
                  onChange={(e) => setOutputTokens(Number(e.target.value))}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  min="0"
                />
              </div>
              <Button onClick={fetchComparisons} disabled={comparing}>
                <Calculator className={`w-4 h-4 mr-2 ${comparing ? "animate-spin" : ""}`} />
                重新计算
              </Button>
            </div>

            {/* 对比结果 */}
            {comparisons.length > 0 && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>排名</TableHead>
                    <TableHead>平台</TableHead>
                    <TableHead>模型</TableHead>
                    <TableHead>描述</TableHead>
                    <TableHead className="text-right">总成本</TableHead>
                    <TableHead className="text-right">输入价格</TableHead>
                    <TableHead className="text-right">输出价格</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {comparisons.map((comp, index) => (
                    <TableRow key={`${comp.provider}-${comp.model}`}>
                      <TableCell>
                        <Badge
                          variant={index === 0 ? "default" : "outline"}
                          className={
                            index === 0
                              ? "bg-green-500"
                              : index === 1
                              ? "bg-blue-500"
                              : index === 2
                              ? "bg-orange-500"
                              : ""
                          }
                        >
                          #{index + 1}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getProviderColor(comp.provider)}>
                          {getProviderName(comp.provider)}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {comp.model}
                      </TableCell>
                      <TableCell className="text-sm">
                        {comp.description}
                      </TableCell>
                      <TableCell className="text-right font-bold">
                        ¥{comp.cost.toFixed(6)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm">
                        ¥{comp.input_price.toFixed(4)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm">
                        ¥{comp.output_price.toFixed(4)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 说明卡片 */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900">💡 价格说明</CardTitle>
        </CardHeader>
        <CardContent className="text-blue-800 space-y-2">
          <p>
            • <strong>价格单位</strong>: 元/1K tokens（每 1000 个 token 的价格）
          </p>
          <p>
            • <strong>输入价格</strong>: 发送给 AI 的文本（prompt）的价格
          </p>
          <p>
            • <strong>输出价格</strong>: AI 生成的文本（completion）的价格
          </p>
          <p>
            • <strong>缓存价格</strong>: 部分模型支持缓存，命中缓存时价格更低
          </p>
          <p>
            • <strong>实际成本</strong> = (输入tokens ÷ 1000 × 输入价格) + (输出tokens ÷ 1000 × 输出价格)
          </p>
          <p className="text-sm mt-4 text-blue-700">
            ⚠️ 注意：价格表定期更新，实际账单以云平台为准。建议定期同步云平台账单进行校准。
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

