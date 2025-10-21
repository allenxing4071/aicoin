# Git工作流

**文档编号**: AICOIN-DEV-004  
**文档版本**: v1.0.0  
**创建日期**: 2025-10-22

---

## 1. 分支策略

```
main (生产)
  │
  ├─ develop (开发主分支)
  │   │
  │   ├─ feature/ai-decision-engine
  │   ├─ feature/trading-executor
  │   └─ feature/frontend-dashboard
  │
  └─ hotfix/critical-bug (紧急修复)
```

---

## 2. 工作流程

### 2.1 开发新功能
```bash
# 1. 从develop创建feature分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 开发并提交
git add .
git commit -m "feat: 实现新功能"

# 3. 推送到远程
git push origin feature/new-feature

# 4. 创建Pull Request
# 5. Code Review通过后合并到develop
```

### 2.2 发布到生产
```bash
# 1. develop合并到main
git checkout main
git merge develop

# 2. 打tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main --tags
```

---

## 3. Commit规范

参考 [编码规范 (AICOIN-DEV-002)](./02-编码规范.md#3-git提交规范)

---

**文档结束**

