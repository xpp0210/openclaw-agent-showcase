package com.demo;

import lombok.Data;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * RAG REST 控制器
 *
 * 提供以下接口：
 * - POST /ask：基于向量检索的问答
 * - POST /documents：添加文档到向量存储
 */
@RestController
@RequestMapping("/api")
public class RagController {

    /**
     * RAG 服务实例
     */
    private final RagService ragService;

    /**
     * 构造函数：通过依赖注入初始化服务
     *
     * @param ragService RAG 服务实例
     */
    public RagController(RagService ragService) {
        this.ragService = ragService;
    }

    /**
     * 问答接口
     *
     * 功能：
     * - 接收用户问题
     * - 从向量存储中检索相关文档
     * - 调用 LLM 生成回答
     *
     * 示例请求：
     * POST /api/ask
     * {
     *   "question": "什么是 Spring AI？"
     * }
     *
     * @param request 问答请求对象
     * @return AI 生成的回答
     */
    @PostMapping("/ask")
    public ResponseEntity<AskResponse> ask(@RequestBody AskRequest request) {
        // 调用 RAG 服务处理问题
        String answer = ragService.ask(request.getQuestion());

        // 构建响应对象
        AskResponse response = new AskResponse();
        response.setQuestion(request.getQuestion());
        response.setAnswer(answer);

        // 返回 200 OK
        return ResponseEntity.ok(response);
    }

    /**
     * 添加文档接口
     *
     * 功能：
     * - 接收文档文本列表
     * - 将文档添加到向量存储
     * - 自动生成向量索引
     *
     * 示例请求：
     * POST /api/documents
     * {
     *   "texts": [
     *     "Spring AI 是一个用于构建 AI 应用的框架",
     *     "RAG 是检索增强生成的缩写"
     *   ]
     * }
     *
     * @param request 文档添加请求对象
     * @return 操作结果
     */
    @PostMapping("/documents")
    public ResponseEntity<DocumentResponse> addDocuments(@RequestBody DocumentRequest request) {
        // 调用 RAG 服务添加文档
        ragService.addDocuments(request.getTexts());

        // 构建响应对象
        DocumentResponse response = new DocumentResponse();
        response.setCount(request.getTexts().size());
        response.setMessage("成功添加 " + request.getTexts().size() + " 个文档");

        // 返回 200 OK
        return ResponseEntity.ok(response);
    }

    /**
     * 问答请求对象
     */
    @Data
    public static class AskRequest {
        /**
         * 用户问题
         */
        private String question;
    }

    /**
     * 问答响应对象
     */
    @Data
    public static class AskResponse {
        /**
         * 用户问题（回显）
         */
        private String question;

        /**
         * AI 生成的回答
         */
        private String answer;
    }

    /**
     * 文档添加请求对象
     */
    @Data
    public static class DocumentRequest {
        /**
         * 文档文本列表
         */
        private List<String> texts;
    }

    /**
     * 文档添加响应对象
     */
    @Data
    public static class DocumentResponse {
        /**
         * 添加的文档数量
         */
        private Integer count;

        /**
         * 操作结果消息
         */
        private String message;
    }
}
