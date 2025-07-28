# 部署到Streamlit Cloud指南

## 什么是Streamlit Cloud？

Streamlit Cloud是Streamlit官方提供的免费托管服务，可以将你的应用部署到公网，获得类似 `https://your-app-name.streamlit.app/` 的网址。

## 部署步骤

### 1. 准备代码仓库

首先需要将代码上传到GitHub：

1. **创建GitHub仓库**

   - 访问 https://github.com
   - 点击 "New repository"
   - 仓库名称建议：`quantitative-structure-analysis`
   - 选择 "Public"（免费版需要公开仓库）
2. **上传代码到GitHub**

   ```bash
   # 在项目目录下执行
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/quantitative-structure-analysis.git
   git push -u origin main
   ```

### 2. 部署到Streamlit Cloud

1. **访问Streamlit Cloud**

   - 打开 https://share.streamlit.io/
   - 使用GitHub账号登录
2. **创建新应用**

   - 点击 "New app"
   - 选择你的GitHub仓库
   - 选择分支（通常是main）
   - 设置主文件路径：`streamlit_app.py`
   - 应用名称：`quantitative-structure-analysis`（或你想要的名称）
3. **部署设置**

   - 点击 "Deploy!"
   - 等待部署完成（通常需要几分钟）

### 3. 获得公网地址

部署成功后，你会获得类似这样的地址：

```
https://quantitative-structure-analysis.streamlit.app/
```

## 文件结构要求

确保你的项目包含以下文件：

```
your-project/
├── streamlit_app.py          # 主应用文件
├── judge_strategy.py         # 策略分析文件
├── requirements.txt          # 依赖包列表
├── .streamlit/
│   └── config.toml          # Streamlit配置
└── README.md                # 项目说明
```

## 注意事项

### 1. 依赖包限制

- 确保所有依赖包都在 `requirements.txt` 中
- 避免使用过大的包或系统级依赖
- 使用 `akshare` 作为数据源，更稳定可靠

### 2. 数据访问

- 应用会从qstock获取实时数据
- 确保网络连接正常

### 3. 文件存储

- Streamlit Cloud是只读环境
- 不能保存文件到服务器
- 图表和数据下载功能仍然可用

### 4. 免费版限制

- 应用在15分钟无访问后会自动休眠
- 重新访问时需要等待几秒钟启动
- 每月有使用时间限制

## 自定义域名（可选）

如果你想要自定义域名，可以：

1. 购买域名
2. 在Streamlit Cloud设置中添加自定义域名
3. 配置DNS解析

## 更新应用

每次更新代码后：

1. 推送到GitHub
2. Streamlit Cloud会自动重新部署
3. 几分钟后新版本生效

## 监控和日志

- 在Streamlit Cloud控制台可以查看应用状态
- 可以查看访问日志和错误信息
- 支持设置通知

## 故障排除

### 常见问题

1. **部署失败**

   - 检查 `requirements.txt` 是否正确
   - 确保主文件路径正确
   - 查看部署日志
2. **应用无法启动**

   - 检查代码语法错误
   - 确保所有依赖包都可用
   - 查看错误日志
3. **数据获取失败**

   - 检查网络连接
   - 确认数据源可用性

## 示例部署地址

部署成功后，你的应用地址将类似：

```
https://your-app-name.streamlit.app/
```

这样你就可以在任何地方通过这个网址访问你的定量结构公式分析系统了！
