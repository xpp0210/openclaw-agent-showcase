package com.demo;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * RAG（检索增强生成）服务类
 *
 * 功能：
 * 1. 从向量存储中检索相关文档
 * 2. 将检索到的上下文与用户问题组合
 * 3. 调用 LLM 生成回答
 */
@Service
public class RagService {

    /**
     * 向量存储：用于检索相关文档片段
     */
    private final VectorStore vectorStore;

    /**
     * 聊天客户端：用于调用 LLM 生成回答
     */
    private final ChatClient chatClient;

    /**
     * 构造函数：通过依赖注入初始化组件
     *
     * @param vectorStore 向量存储实例
     * @param chatClient  聊天客户端实例
     */
    public RagService(VectorStore vectorStore, ChatClient.Builder chatClientBuilder) {
        this.vectorStore = vectorStore;
        this.chatClient = chatClientBuilder.build();
    }

    /**
     * 基于向量检索的问答方法
     *
     * 流程：
     * 1. 将问题转换为向量并检索相似的文档
     * 2. 提取文档内容作为上下文
     * 3. 将上下文和问题组合成提示词
     * 4. 调用 LLM 生成回答
     *
     * @param question 用户问题
     * @return AI 生成的回答
     */
    public String ask(String question) {
        // 1. 从向量存储中检索最相似的 3 个文档片段
        // SearchRequest 配置：topK=3 返回最相关的3个结果
        List<Document> documents = vectorStore.similaritySearch(
            SearchRequest.query(question).withTopK(3)
        );

        // 2. 将检索到的文档内容组合成上下文字符串
        String context = documents.stream()
            .map(Document::getContent)
            .collect(Collectors.joining("\n\n---\n\n"));

        // 3. 构建系统提示词：指示 AI 基于提供的上下文回答问题
        String systemPrompt = """
            你是一个专业的助手。请基于以下提供的上下文信息回答用户的问题。
            如果上下文中没有相关信息，请明确告知用户。

            上下文信息：
            %s
            """.formatted(context);

        // 4. 调用 ChatClient 生成回答
        // .system() 设置系统提示词
        // .user() 设置用户问题
        // .call() 发起调用
        // .content() 获取文本回答
        String answer = chatClient.prompt()
            .system(systemPrompt)
            .user(question)
            .call()
            .content();

        return answer;
    }

    /**
     * 添加文档到向量存储
     *
     * 注意：实际项目中通常通过定时任务或 API 批量加载文档
     *
     * @param texts 文档文本列表
     */
    public void addDocuments(List<String> texts) {
        // 将文本转换为 Document 对象
        List<Document> documents = texts.stream()
            .map(text -> new Document(text, Map.of("source", "manual")))
            .toList();

        // 将文档添加到向量存储
        // Spring AI 会自动调用嵌入模型将文本转换为向量
        vectorStore.add(documents);
    }
}
