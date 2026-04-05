# Spring AI RAG Demo

基于 Spring Boot 3.3 + Spring AI 1.0.0-M5 的 RAG（检索增强生成）示例项目。

## 项目结构

```
spring-ai-rag-demo/
├── pom.xml                          # Maven 配置文件
├── src/
│   └── main/
│       ├── java/com/demo/
│       │   ├── Application.java     # Spring Boot 启动类
│       │   ├── RagService.java      # RAG 服务（向量检索 + LLM 生成）
│       │   └── RagController.java   # REST API 控制器
│       └── resources/
│           └── application.yml      # 应用配置文件
└── README.md
```

## 技术栈

- **Spring Boot**: 3.3.5
- **Spring AI**: 1.0.0-M5
- **Java**: 17+
- **Maven**: 3.6+

## 核心功能

1. **向量检索**：基于用户问题从向量存储中检索相关文档
2. **LLM 生成**：将检索结果作为上下文，调用 OpenAI 生成回答
3. **REST API**：提供问答和文档添加接口

## 快速开始

### 1. 设置 OpenAI API Key

```bash
# Linux/Mac
export OPENAI_API_KEY=your-actual-api-key

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-actual-api-key"
```

### 2. 启动应用

```bash
# 进入项目目录
cd ~/.openclaw/workspace-coding/projects/spring-ai-rag-demo

# 使用 Maven 启动
mvn spring-boot:run

# 或打包后运行
mvn clean package
java -jar target/spring-ai-rag-demo-1.0.0.jar
```

### 3. 添加文档到向量存储

```bash
curl -X POST http://localhost:8080/api/documents \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Spring AI 是一个用于构建 AI 应用的框架",
      "RAG（检索增强生成）结合了信息检索和文本生成",
      "向量存储用于快速查找相似的文档片段",
      "嵌入模型将文本转换为高维向量"
    ]
  }'
```

### 4. 提问

```bash
curl -X POST http://localhost:8080/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是 RAG？"
  }'
```

## API 文档

### POST /api/ask

问答接口

**请求体：**
```json
{
  "question": "用户问题"
}
```

**响应：**
```json
{
  "question": "用户问题",
  "answer": "AI 生成的回答"
}
```

### POST /api/documents

添加文档接口

**请求体：**
```json
{
  "texts": ["文档1", "文档2"]
}
```

**响应：**
```json
{
  "count": 2,
  "message": "成功添加 2 个文档"
}
```

## 配置说明

application.yml 关键配置：

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}  # OpenAI API Key
      chat:
        options:
          model: gpt-4o-mini       # 对话模型
      embedding:
        options:
          model: text-embedding-3-small  # 嵌入模型
```

## 生产环境建议

1. **向量存储**：替换为 Redis 或 PostgreSQL（pgvector）
2. **文档加载**：实现定时任务批量加载文档
3. **API 安全**：添加认证和限流
4. **日志监控**：集成 ELK 或 Prometheus
5. **缓存优化**：对高频问答结果进行缓存

## 常见问题

**Q: 如何切换到国内大模型？**

A: 修改 application.yml 中的 `spring.ai.openai.api-key` 为国内厂商 API，并指定对应的模型名称。

**Q: 向量存储使用什么？**

A: 默认使用内存向量存储（简单向量存储），生产环境建议配置 Redis 或 PostgreSQL。

**Q: 如何批量加载文档？**

A: 实现 `CommandLineRunner` 或 `@PostConstruct` 方法，在应用启动时加载文档。

## 参考资料

- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)
- [Spring AI GitHub](https://github.com/spring-projects/spring-ai)
- [OpenAI API 文档](https://platform.openai.com/docs)
