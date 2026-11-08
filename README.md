# Kiến trúc AI Agent 7 Module (Clean Architecture - Python)

Bộ khung (Skeleton) chuẩn hóa cho hệ thống **AI Agent** được chia tách rõ ràng thành **7 module độc lập**, giúp dễ dàng theo dõi luồng chạy (data flow), mở rộng từng thành phần và kiểm thử tự động.

---

## 1. Cấu trúc thư mục dự án

```text
d:\AI Agent Architecture\
├── pyproject.toml                        # Cấu hình package & dependencies (Pydantic, Pytest)
├── main.py                               # Kịch bản chạy thử nghiệm toàn bộ 7 module end-to-end
├── tests/
│   └── test_agent_flow.py                # Bộ kiểm thử tự động cho cả 7 module
└── src/
    └── agent_core/
        ├── bootstrap.py                  # Dependency Injection Container kết nối 7 module
        ├── shared/                       # DTOs (Message, TokenUsage) & Exceptions dùng chung
        ├── llm_manager/                  # [Module 1] Quản lý Model, API Key, Hạn dùng, Token, Settings
        ├── prompt_manager/               # [Module 2] Quản lý App/User/Session Prompt & Skills
        ├── orchestrator/                 # [Module 3] Quản lý phiên (Session) & Vòng lặp ReAct
        ├── context_manager/              # [Module 4] Thu thập, lắp ghép & tối ưu cửa sổ Context
        ├── memory_manager/               # [Module 5] Quản lý các Data Sources (Working, RAG, Facts)
        ├── tool_manager/                 # [Module 6] Quản lý đăng ký, phân quyền & thực thi Tools
        └── monitoring/                   # [Module 7] Guardrail Validators & Telemetry Tracing
```

---

## 2. Phân tích trách nhiệm 7 Module & Sự phân tách ranh giới

| STT | Module | Trách nhiệm cốt lõi | Điểm khác biệt / Ranh giới quan trọng |
| :--- | :--- | :--- | :--- |
| **1** | **`llm_manager`** | Quản lý danh mục Model (`ModelSpec`), kiểm tra hạn sử dụng model/API key (`APIKeyCredential`), xoay vòng key (`APIKeyPool`), tự động chuyển đổi sang Fallback Model, cài đặt thông số (`GenerationSettings`) và theo dõi ngân sách Token (`TokenBudgetTracker`). | Chỉ nhận `LLMRequest` đã đóng gói sẵn và trả về `LLMResponse`. Không tự ý truy vấn DB hay ghép prompt. |
| **2** | **`prompt_manager`** | Quản lý 4 tầng chỉ dẫn: **App System Prompt** -> **User System Prompt** -> **Chat Session Prompt** -> **Dynamic Skills** (`SkillDefinition` tự kích hoạt theo từ khóa hoặc chỉ định). | Chỉ chịu trách nhiệm biên dịch chỉ dẫn hệ thống (`Role.SYSTEM`), không lưu trữ lịch sử chat. |
| **3** | **`orchestrator`** | Nhạc trưởng quản lý vòng đời phiên (`AgentSession`) và điều khiển vòng lặp suy luận **ReAct** (`Think -> Validate -> Act -> Observe`). | Điều phối thứ tự gọi giữa 6 module còn lại; không chứa logic chi tiết của từng module. |
| **4** | **`context_manager`** | Thu thập System Prompt (từ Module 2), các mảnh ký ức/RAG & lịch sử chat (từ Module 5), sau đó **tối ưu hóa cửa sổ Token** (Sliding Window Compaction) để không bao giờ tràn `max_context_tokens`. | **Context ≠ Memory**: Context Manager quyết định *"những gì được đưa vào cửa sổ suy luận của 1 lượt gọi LLM"*. |
| **5** | **`memory_manager`** | Quản lý các **Data Sources** lưu trữ ngắn hạn và dài hạn: `WORKING` (lịch sử phiên), `EPISODIC` (ký ức phiên trước), `SEMANTIC_RAG` (Vector DB / tài liệu), `ENTITY_FACT` (hồ sơ người dùng). | **Memory = Storage & Retrieval**: Chịu trách nhiệm lưu trữ bền vững và tìm kiếm đa nguồn dữ liệu. |
| **6** | **`tool_manager`** | Đăng ký công cụ (`BaseTool`), xuất chuẩn JSON Schema cho LLM, phân quyền (`ToolPermissionLevel`) và thực thi bất đồng bộ có giới hạn thời gian (`timeout`) kèm cơ chế cô lập lỗi. | Đảm bảo lỗi từ API/hệ thống bên ngoài luôn được bắt gọn thành `ToolExecutionResult`, không làm sập Agent. |
| **7** | **`monitoring`** | Gồm 2 trụ cột: **Validators / Guardrails** (chặn Prompt Injection ở đầu vào, chặn Tool nguy hiểm như `delete_database`, che giấu API Key bị rò rỉ ở đầu ra) và **Telemetry Tracer** (ghi vết từng bước chạy). | Bảo vệ an toàn ở cả 3 chốt chặn (`Input`, `ToolCall`, `Output`) và xuất bảng nhật ký chi tiết theo từng `session_id`. |

---

## 3. Hướng dẫn chạy thử và kiểm thử

```powershell
# 1. Chạy kịch bản minh họa luồng hoạt động 7 module
python main.py

# 2. Chạy toàn bộ Unit & Integration Tests
python -m unittest discover -s tests -v
```
