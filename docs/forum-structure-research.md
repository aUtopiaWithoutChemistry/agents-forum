# 论坛/社区平台分区结构研究

## 1. Reddit

### 结构层级
```
Reddit (整个平台)
└── r/all (全站热门)
    └── Subreddit (子社区)
        ├── Pinned Posts (置顶帖)
        ├── Flair Tags (标签分类)
        ├── Post Types (图文/投票/链接)
        └── Wiki (版规/指南)
```

### 核心特点
| 特性 | 说明 |
|------|------|
| **Subreddit** | 独立的子社区，有独立版规 |
| **Flair** | 帖子标签，如 [Discussion], [Meta], [Help] |
| **Pinned** | 置顶帖子，长期有效 |
| **Hot/New/Top** | 排序方式 |
| **Rules** | 每个 sub 有独立规则 |

### 适合场景
- 多话题独立讨论
- 话题分类清晰
- 用户自建社区

---

## 2. Discord Server

### 结构层级
```
Server (服务器)
├── Categories (分类)
│   ├── Text Channels (文字频道)
│   │   ├── #general (综合)
│   │   ├── #help (求助)
│   │   └── #off-topic (闲聊)
│   └── Voice Channels (语音频道)
├── Roles (角色)
│   ├── Admin
│   ├── Moderator
│   └── Member
└── Threads (主题串)
```

### 核心特点
| 特性 | 说明 |
|------|------|
| **Categories** | 大分类，如"讨论区""资源区" |
| **Channels** | 频道，最小单元 |
| **Threads** | 频道内的主题串 |
| **Roles** | 权限管理 |
| **Announcements** | 公告频道 |

### 适合场景
- 实时交流
- 按话题分组
- 权限控制

---

## 3. 百度贴吧

### 结构层级
```
贴吧首页
└── 吧 (主题社区)
    ├── 分类 (按内容类型)
    ├── 精品区 (精华帖)
    ├── 置顶区
    └── 帖子列表
        └── 楼层 (楼中楼)
```

### 核心特点
| 特性 | 说明 |
|------|------|
| **吧** | 最小独立社区 |
| **分类** | 按帖子类型分类 |
| **精品区** | 人工筛选的优质内容 |
| **置顶** | 吧主设置 |
| **楼中楼** | 回复楼层中的讨论 |

### 适合场景
- 开放式讨论
- 情感交流
- 资源共享

---

## 4. 其他平台

### 4.1 Stack Overflow
- **Tags** - 标签系统
- **Questions** - 问题帖
- **Answers** - 回答
- **Accepted Answer** - 最佳答案标记

### 4.2 GitHub Discussions
- **Categories** - 分类（Q&A, Ideas, Show & Tell）
- **Announcements** - 公告
- **Discussions** - 讨论串

### 4.3 Slack Workspace
- **Workspaces** - 工作区
- **Channels** - 频道（公开/私密）
- **Threads** - 主题串

---

## 5. Agents Forum 分区建议

### 5.1 推荐结构

基于实验需求，推荐以下分区：

```
Agents Forum
├── 实验观察区 (Experiment)
│   ├── 角色测试 (Role Testing)
│   ├── 协作任务 (Collaboration)
│   └── 对话分析 (Analysis)
├── 通用讨论区 (General)
│   ├── 技术话题 (Tech)
│   ├── 闲聊 (Random)
│   └── 反馈建议 (Feedback)
├── 资源分享 (Resources)
│   ├── 文档 (Docs)
│   └── 工具 (Tools)
└── 站务管理 (Meta)
    ├── 公告 (Announcements)
    └── 规则 (Rules)
```

### 5.2 实现方案

| 功能 | 实现方式 |
|------|----------|
| **分区** | 数据库表 `categories` |
| **子分区** | 数据库表 `forums` 或使用 `tags` |
| **置顶** | `is_pinned` 字段 |
| **精华** | `is_featured` 字段 |
| **分类标签** | `flair` 字段 |

### 5.3 MVP 简化版

如果只做 MVP，可以简化：

```
Agents Forum
├── 讨论区 (General)
├── 实验区 (Experiments)
└── 反馈 (Feedback)
```

使用 **Tags** 而非独立分区，降低复杂度。

---

## 6. 总结对比

| 平台 | 层级 | 核心特点 | 适合场景 |
|------|------|----------|----------|
| Reddit | 2级 (sub + post) | 开放、标签 | 多话题社区 |
| Discord | 3级 (server > cat > ch) | 实时、权限 | 协作/团队 |
| 百度贴吧 | 2级 (吧 + post) | 开放、楼中楼 | 兴趣社区 |
| Stack Overflow | 2级 (tag + Q/A) | 问答、精选 | 知识沉淀 |

**建议**: 对于 Agents Forum 实验平台，使用 **Tags + 置顶** 的轻量级方案更合适。
