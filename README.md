# TeleGenius Pro - Telegram 智能用户管理系统  
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-username/telegenius-pro)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


## 🚀 软件简介  
TeleGenius Pro 是一款专为 Telegram 设计的智能用户管理工具，支持自动抓取用户信息、基于知识库的智能沟通、用户分类及差异化处理。通过分析用户资料（昵称、电话、国家等），结合预设的产品知识库，主动发起精准对话，并根据聊天内容动态分类用户：优质用户自动转接人工客服，其他用户按规则智能处理，助力高效客户管理与营销转化。


## 🌟 核心功能  

### 1. 智能资料分析  
- 基于用户属性（国家、语言、行为标签等）构建用户画像  
- 识别潜在高价值用户特征（如地域匹配度、联系方式完整性等）  

### 2. 自动化主动沟通  
- 预设多套聊天模板，结合产品知识库智能匹配话术  
- 支持定时发送、个性化问候（如根据用户时区、语言适配内容）  

### 3. 动态用户分类  
- 基于聊天内容实时分析（关键词识别、回复积极性等）  
- 自定义分类标签（优质用户、普通用户、无效用户等）  

### 4. 人机协作流程  
- 优质用户自动标记并推送至人工客服工作台  
- 非优质用户按预设规则自动回复或归档  


## 📦 安装与配置  
### 环境要求  
- Python 3.8+  
- 依赖库：（通过 `pip install -r requirements.txt` 安装）  

### 快速部署  
1. **克隆项目**  
   ```bash  
   git clone https://github.com/Anning01/telegenius-pro.git  
   cd telegenius-pro  
   ```

2. **配置文件**  
   项目路径下创建 `.env` 复制 `.env.example` 内容到 `.env`：  
   ```.env  
   # 环境设置
   ENV=development
   
   # PostgreSQL配置
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=password
   POSTGRES_DB=telegenius
   POSTGRES_PORT=5432
   
   # API配置
   BACKEND_CORS_ORIGINS=["http://localhost:8000", "http://localhost:3000"]
   ```  

3. **初始化知识库**  
   将产品信息导入 `knowledge_base.csv`（格式：`问题,答案,优先级`）  
   产品知识库依赖MaxKB，需要自行配置，具体请参考MaxKB文档。


## 🛠 使用指南  
### 1. 启动程序  
```bash  
python main.py  
```  

### 2. 功能模块说明  

#### ▶️ 主动沟通  
系统自动根据用户画像匹配 `templates/` 目录下的话术模板，支持变量替换（如 `{username}` 替换为用户昵称）。  

#### ▶️ 用户分类结果  
分类报告生成至 `reports/` 目录，包含：  
- 优质用户列表（`premium_users.csv`）  
- 普通用户统计（`user_classification.json`）  

## 开发

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行测试
```bash
python -m unittest
```

### 3. 代码风格检查
```bash
flake8 .
```

### 4. 代码格式化
```bash
black .
```

### 5. 构建requirements.txt
```bash
pip-compile -i https://mirrors.aliyun.com/pypi/simple
```


## ⚠ 注意事项  
1. **合规声明**  
   - 严格遵守 Telegram [API 使用政策](https://core.telegram.org/api/terms)，避免高频抓取或滥用消息接口  
   - 确保用户数据处理符合 GDPR 等隐私保护法规

2. **更新维护**  
   - 通过 `git pull` 获取最新版本  
   - 知识库和话术模板支持热更新，无需重启程序  


## 🤝 贡献与反馈  
欢迎提交 Issue 或 Pull Request 改进项目：  
- [问题反馈](https://github.com/your-username/telegenius-pro/issues/new)  
- [代码贡献指南](CONTRIBUTING.md)  


## 📄 许可证  
本项目采用 [MIT 许可证](LICENSE)，允许自由修改和商业使用，但需保留版权声明。  