package com.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Spring Boot 应用主启动类
 *
 * 功能：
 * - 启动 Spring Boot 应用
 * - 自动配置 Spring AI 组件
 * - 扫描 com.demo 包下的所有组件
 */
@SpringBootApplication
public class Application {

    /**
     * 应用入口方法
     *
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        // 启动 Spring Boot 应用
        SpringApplication.run(Application.class, args);

        System.out.println("""

            ========================================
            Spring AI RAG Demo 已启动成功！

            访问地址：http://localhost:8080

            API 接口：
            - POST /api/ask            : 问答接口
            - POST /api/documents     : 添加文档接口

            示例（使用 curl）：
            1. 添加文档：
               curl -X POST http://localhost:8080/api/documents \\
                    -H "Content-Type: application/json" \\
                    -d '{"texts": ["Spring AI 是一个 AI 应用框架", "RAG 结合了检索和生成"]}'

            2. 提问：
               curl -X POST http://localhost:8080/api/ask \\
                    -H "Content-Type: application/json" \\
                    -d '{"question": "什么是 RAG？"}'

            注意：请先设置环境变量 OPENAI_API_KEY
            ========================================
            """);
    }
}
