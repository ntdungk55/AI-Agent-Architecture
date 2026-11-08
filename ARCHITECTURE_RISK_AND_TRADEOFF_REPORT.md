# BÁO CÁO ĐÁNH GIÁ ƯU NHƯỢC ĐIỂM, ĐÁNH ĐỔI & RỦI RO HỆ THỐNG (ARCHITECTURE RISK & TRADEOFF REPORT)

> **Dự án:** `AI Agent Architecture` (Strict 7-Module Core + 2 Optional Extensions)  
> **Phiên bản kiến trúc:** Phase 2 Final Consensus (`runtime_governance` hợp nhất)  
> **Quy tắc vận hành (Rule nội bộ phiên làm việc):** *Mỗi khi có bất kỳ thay đổi nào về kiến trúc/cấu trúc hệ thống, bắt buộc phải cập nhật phân tích **Ưu điểm – Nhược điểm – Rủi ro phát sinh – Giải pháp giảm thiểu** vào báo cáo này.*

---

## PHẦN 1: SO SÁNH ƯU / NHƯỢC ĐIỂM CỦA KIẾN TRÚC 7 MODULE LÕI HIỆN TẠI

Kiến trúc hiện tại giữ đúng **7 Module Lõi** (`1. llm_manager`, `2. prompt_manager`, `3. orchestrator`, `4. context_manager`, `5. memory_manager`, `6. tool_manager`, `7. runtime_governance`) và tách **2 thành phần phụ trợ ngoài lõi** (`extensions/external_coding_tools`, `extensions/outer_verification_harness`).

### 1.1. Bảng đối chiếu 3 phương án kiến trúc

| Tiêu chí | Hệ thống 7 Module Cơ bản (Chưa nâng cấp Module 7) | Hệ thống 12 Module (Tách rời ở Phase 1) | Hệ thống 7 Module Lõi Tối ưu (Chốt ở Phase 2 - Hiện tại) |
| :--- | :--- | :--- | :--- |
| **Độ gọn & Dễ theo dõi (Cognitive Load)** | Rất dễ hiểu, ít thư mục cấp cao. | Phức tạp ở cấp thư mục gốc (12 module ngang hàng dễ làm loãng bản chất AI Agent). | **Tối ưu:** Giữ nguyên 7 module cấp cao đúng bản chất; độ phức tạp được đóng gói kín bên trong `Module 7 (runtime_governance)`. |
| **Tính độc lập của Lõi Agent** | Cao nhưng thiếu bảo vệ thực thi. | Bị trộn lẫn công cụ phụ trợ (AST/LSP, CI Harness) vào chung với lõi. | **Tối ưu:** Lõi 7 module hoàn toàn tự chủ; thiếu AST/LSP hay CI Harness thì Agent vẫn hoạt động bình thường. |
| **Khả năng chống lỗi bảo mật (TOCTOU, Secret Leak, Prompt Injection)** | **Rất yếu:** `tool_manager` tự chạy lệnh trực tiếp, dễ lộ API key hoặc xóa nhầm file. | **Mạnh:** Có các cổng kiểm soát riêng biệt. | **Mạnh tương đương 12 Module:** Toàn bộ 6 chốt chặn (`policy_enforcement`, `isolation`, `transaction`, `secret_broker`, `content_safety`, `audit_observability`) nằm gọn trong `runtime_governance`. |
| **Rủi ro phụ thuộc vòng (Circular Dependency)** | Thấp. | Trung bình (nhiều module gọi chéo). | **Được kiểm soát chặt:** Nhờ `ToolPlanAndCodecPort` (Module 6 chỉ sinh Pure Data Plan) và `GovernedToolExecutionPort` (Module 7 thực thi). |

---

### 1.2. Ưu điểm cốt lõi của Cấu trúc 7 Module hiện tại (Pros)
1. **Giữ đúng bản chất nhận thức của AI Agent (Clean Mental Model):**
   - Nhìn từ cấp cao nhất (`src/agent_core/`), hệ thống chỉ có đúng 7 mảnh ghép kinh điển: *Não bộ (`llm`)*, *Chỉ dẫn (`prompt`)*, *Điều phối (`orchestrator`)*, *Ngữ cảnh (`context`)*, *Trí nhớ (`memory`)*, *Kế hoạch Công cụ (`tool`)* và *Quản trị Thực thi (`runtime_governance`)*.
2. **Không còn vùng xám trách nhiệm giữa Module 6 và Module 7:**
   - `Module 6 (tool_manager)` hoàn toàn thuần khiết: chỉ quản lý Schema, validate tham số và sinh bản kế hoạch dữ liệu tuần tự hóa (`ToolInvocationPlan`: `WorkspaceFileOpSpec` / `SubprocessSpec` / `HttpEgressSpec` / `PureFunctionSpec`).
   - `Module 7 (runtime_governance)` nắm giữ toàn bộ Trusted Computing Base (TCB): đối chiếu `OperatorApprovedToolManifestRegistry`, mở OS File Descriptor (`AuthorizedResourceSet`), chạy Sandbox/Subprocess, gắn Secret tại Egress/FD và lọc DLP trước khi trả kết quả về.
3. **Một nguồn sự thật duy nhất (Single Source of Truth) cho Taint/Provenance:**
   - Chỉ `Module 4 (context_manager)` mới có quyền gắn nhãn nguồn gốc dữ liệu (`USER_ASSERTED`, `TAINTED_REPO`, `TAINTED_EXTERNAL`); `Module 7` chỉ đọc nhãn này để cưỡng chế chính sách, không sinh ra 2 hệ thống nhãn mâu thuẫn nhau.
4. **Cắm rút linh hoạt các công cụ phụ trợ (`extensions/`):**
   - Khi làm tác vụ văn phòng/chat thông thường: không cần nạp `external_coding_tools` (AST/LSP) hay `outer_verification_harness`.
   - Khi làm tác vụ Coding tự động quy mô lớn: chỉ cần cắm thêm 2 phần phụ trợ này vào mà không phải sửa bất kỳ dòng code nào trong 7 module lõi.

---

### 1.3. Nhược điểm & Sự đánh đổi của Cấu trúc 7 Module hiện tại (Cons / Trade-offs)
1. **Tập trung độ phức tạp cao vào bên trong `Module 7 (runtime_governance)`:**
   - Dù đã tách thành 6 sub-packages nội bộ (`policy_enforcement`, `isolation`, `transaction`, `secret_broker`, `content_safety`, `audit_observability`), `runtime_governance` vẫn là module nặng nhất hệ thống (chiếm khoảng 40–45% khối lượng logic kỹ thuật). Nếu lập trình viên viết code không tuân thủ ranh giới giữa 6 sub-packages này, `Module 7` có nguy cơ thoái hóa thành "God Package" nội bộ.
2. **Chi phí độ trễ thực thi (Latency & Serialization Overhead):**
   - Việc bắt buộc `Module 6` xuất ra Pure Serializable Data (`ToolInvocationPlan`), đi qua kiểm tra Manifest, mở CAS Lease/Snapshot, khởi chạy Subprocess tách biệt và quét DLP ở `Module 7` sẽ làm tăng độ trễ mỗi lần gọi Tool thêm khoảng **5ms – 50ms** (tùy loại tool) so với việc gọi thẳng hàm Python trong bộ nhớ.
3. **Hạn chế đối với các thư viện Python bên thứ ba cần chạy In-Process có I/O:**
   - Do quy tắc bảo mật cấm truyền `handler_fn` (arbitrary Python callable có I/O) vào `ToolInvocationPlan`, mọi công cụ có I/O (đọc/ghi file đặc thù, gọi SDK bên ngoài không qua HTTP chuẩn) buộc phải được viết thành CLI/Worker Subprocess riêng hoặc phải được Operator phê duyệt đưa thẳng vào TCB, làm tăng công sức viết Adapter cho Tool mới.
4. **Gánh nặng cấu hình `OperatorApprovedToolManifestRegistry`:**
   - Vì hệ thống không tin tưởng hoàn toàn vào `DeclaredEffects` do plugin tự khai báo, người vận hành (Operator/Developer) phải khai báo trước Manifest (binary digest, ràng buộc `argv`, HTTP route, `allowed_upper_bound`) cho từng công cụ mới. Nếu chưa khai báo, công cụ sẽ liên tục bị chặn hoặc hỏi `ASK_USER`.

---

## PHẦN 2: DANH MỤC RỦI RO CÒN TỒN TẠI (RESIDUAL RISKS) & GIẢI PHÁP GIẢM THIỂU

Ngay cả khi đã đạt đồng thuận kiến trúc (`[CONSENSUS_REACHED]`) với đầy đủ 6 lớp bảo vệ trong `Module 7`, một hệ thống chạy trong thế giới thực vẫn luôn tồn tại **8 rủi ro kỹ thuật và vận hành** dưới đây:

| Mã Rủi Ro | Tên Rủi Ro & Thành phần liên quan | Mức độ (Severity) | Nguyên nhân gốc rễ (Root Cause) | Giải pháp Giảm thiểu (Mitigation Strategy) |
| :--- | :--- | :---: | :--- | :--- |
| **RISK-01** | **Giới hạn cô lập OS Sandbox trên môi trường Windows Local (`COOPERATIVE_WORKSPACE_LEASE`)**<br>*(Module 7.2 `isolation`)* | **CAO (High)** | Trên máy Windows cá nhân không bật Docker/WSL2 hoặc không cấu hình AppContainer phức tạp, các CLI bên ngoài (như `git`, `pytest`, `node`) chạy trực tiếp trên host filesystem. Tiến trình ngoài (IDE, Antivirus) hoặc chính CLI đó vẫn có thể chạm vào file ngoài dự kiến hoặc gây race condition (TOCTOU) giữa lúc kiểm tra CAS và syscall thực tế. | 1. Ghi rõ `assurance_level = COOPERATIVE_WORKSPACE_LEASE` trong `ExecutionReceipt` (không báo cáo sai sự thật).<br>2. Với các thao tác rủi ro cao trên host local, tự động nâng chính sách lên `ASK_USER` hoặc bắt buộc chạy qua Docker/WSL2 sandbox (`SNAPSHOT_AND_OVERLAY_ENFORCED`). |
| **RISK-02** | **Trạng thái treo `INDETERMINATE` khi Crash giữa chừng với Side-Effect bên ngoài**<br>*(Module 7.1 `policy_enforcement` & 7.3 `transaction`)* | **CAO (High)** | Nếu Agent gửi một request ra hệ thống ngoài (ví dụ tạo PR, gửi thông báo, thanh toán) và tiến trình Agent bị sập nguồn/kill đúng vào мили-giây sau khi gói tin rời card mạng nhưng trước khi ghi `CONFIRMED` xuống đĩa, không một kiến trúc cục bộ nào biết chắc chắn phía server đích đã xử lý hay chưa. | 1. Bắt buộc dùng `ExecutionAttemptState = INDETERMINATE`.<br>2. Cấm tuyệt đối auto-retry với `NEVER_AUTO_RETRY`.<br>3. Đóng băng phiên ở trạng thái `HALTED_INDETERMINATE_SIDE_EFFECT` và yêu cầu hàm `QUERY_STATUS_BEFORE_RETRY` hoặc User kiểm tra thủ công trước khi đi tiếp. |
| **RISK-03** | **Thất bại một phần trong Giao dịch Bù trừ Bên ngoài (`PARTIALLY_COMPENSATED` / `COMPENSATION_FAILED`)**<br>*(Module 7.3 `transaction` - Saga)* | **TRUNG BÌNH - CAO (Med-High)** | Khác với file trong workspace có thể rollback nguyên tử bằng `WorkspaceSnapshotWAL`, các hành động bên ngoài dùng mẫu **Saga** (chạy hàm đảo ngược khi bước sau lỗi). Nếu chính hàm đảo ngược bị lỗi mạng hoặc quyền hạn bị thu hồi giữa chừng, hệ thống bên ngoài sẽ ở trạng thái dở dang. | 1. Tách biệt hoàn toàn báo cáo `SagaCompensationReport` khỏi `ATOMIC_WORKSPACE_ROLLBACK`.<br>2. Ghi log bền vững danh sách các bước bù trừ thất bại kèm `idempotency_key` để thực hiện đối soát/chạy lại (reconciliation) và cảnh báo ngay cho User. |
| **RISK-04** | **Rò rỉ khóa mật qua kênh phụ hoặc bộ nhớ của Subprocess (`EPHEMERAL_SUBPROCESS_SECRET`)**<br>*(Module 7.4 `secret_broker` & 7.5 `content_safety`)* | **TRUNG BÌNH (Medium)** | Khi một CLI bên ngoài bắt buộc phải nhận API key/token qua biến môi trường hoặc File Descriptor (không thể dùng `EgressProxy`), tiến trình con đó nắm giữ secret thật trong RAM. Nếu CLI đó bị mã độc kiểm soát hoặc cố tình mã hóa (base64/hex) secret rồi in ra `stdout`, bộ lọc DLP regex thông thường có thể không nhận diện được. | 1. Ưu tiên tối đa chế độ `EGRESS_PROXY_INJECTED` (CLI không bao giờ giữ secret thật).<br>2. Chỉ cấp `EPHEMERAL_SUBPROCESS_SECRET` cho binary nằm trong `allowed_executable_digests`, khóa cứng `network_egress` theo allowlist host, và áp dụng cả bộ lọc Entropy/Transformation-aware DLP ở đầu ra. |
| **RISK-05** | **Hiệu ứng ngữ nghĩa không thể xác minh (`UNVERIFIABLE_SEMANTIC_EFFECT`) trên các công cụ đa năng**<br>*(Module 7.1 `policy_enforcement`)* | **TRUNG BÌNH (Medium)** | Các công cụ tổng quát (như `python -c ...`, `powershell`, hoặc một GraphQL endpoint dùng chung 1 hàm `POST /graphql` cho cả đọc và xóa dữ liệu) khiến tầng OS/HTTP Proxy không thể phân biệt chính xác hiệu ứng chỉ qua method hay đường dẫn. | 1. Gắn nhãn `DimensionEnforcementMode.UNVERIFIABLE_SEMANTIC_EFFECT`.<br>2. Không tin vào `DeclaredEffects` của plugin; tự động áp mức rủi ro trần (`WRITE_IRREVERSIBLE`) và buộc qua cổng `ASK_USER` (Step-Up Approval) hoặc `DENY`. |
| **RISK-06** | **Mất mát ngữ cảnh tinh tế khi Nén cửa sổ Token (`Sliding Window Compaction`)**<br>*(Module 4 `context_manager`)* | **TRUNG BÌNH (Medium)** | Khi phiên làm việc kéo dài hàng chục lượt, `context_manager` phải tóm tắt/nén các lượt hội thoại cũ để không vượt `TokenBudget`. Quá trình tóm tắt bằng LLM hoặc cắt bớt có thể làm rơi các ràng buộc ngầm hoặc chi tiết kỹ thuật nhỏ mà User đã dặn ở đầu phiên. | 1. Tách riêng các quyết định bất biến của User vào `Entity Fact Store` trong `Module 5 (memory_manager)` và `Session Prompt` trong `Module 2 (prompt_manager)` — hai phần này được ghim cố định (Pinned), không bao giờ bị nén bởi Sliding Window. |
| **RISK-07** | **Lây nhiễm nhãn Taint quá mức (Over-Tainting / Alert Fatigue)**<br>*(Module 4 `context_manager` & Module 7.1 `policy_enforcement`)* | **THẤP - TRUNG BÌNH (Low-Med)** | Khi Agent đọc một file code hoặc tài liệu từ repo bên ngoài (`TAINTED_REPO`), nếu toàn bộ ngữ cảnh phiên bị đánh dấu `TAINTED` vĩnh viễn thì mọi lệnh gọi tool sau đó đều bị chặn và hỏi `ASK_USER`, gây mệt mỏi cho người dùng (Alert Fatigue) dẫn đến thói quen bấm "Approve" mù quáng. | 1. Quản lý Taint theo phạm vi từng mảnh dữ liệu (`Message/Artifact-scoped Provenance`) thay vì tô đen vĩnh viễn toàn phiên.<br>2. Cho phép cơ chế `Sanitize / Declassify` có kiểm soát đối với các thao tác đọc thông tin cấu trúc đã qua parser an toàn. |
| **RISK-08** | **Phình to nội bộ `Module 7 (runtime_governance)` theo thời gian**<br>*(Module 7 `runtime_governance`)* | **THẤP - TRUNG BÌNH (Low-Med)** | Do gộp 6 trách nhiệm bảo mật/quản trị vào chung Module 7 để giữ đúng con số 7 module lõi, nếu thêm tính năng mới mà không giữ kỷ luật kiến trúc, các sub-package bên trong `runtime_governance` có thể gọi chéo lẫn nhau tạo thành khối code rối rắm. | 1. Cố định pipeline một chiều giữa 6 sub-packages thông qua `GovernedToolExecutor`.<br>2. Viết **Architecture Unit Tests** trong `tests/` để kiểm tra tự động: cấm import ngược từ `Module 3` sang `Module 6`, và cấm các sub-package trong `Module 7` gọi vòng tròn lẫn nhau. |

---

## PHẦN 3: NHẬT KÝ THAY ĐỔI KIẾN TRÚC (ARCHITECTURE CHANGE LOG)

> *Mọi thay đổi về kiến trúc trong tương lai sẽ được ghi nối tiếp vào bảng dưới đây kèm đánh giá Ưu – Nhược – Rủi ro.*

| Phiên bản / Thời điểm | Nội dung Thay đổi Kiến trúc | Ưu điểm (Pros) | Nhược điểm (Cons) | Rủi ro Phát sinh & Cách xử lý |
| :--- | :--- | :--- | :--- | :--- |
| **v1.0 (Khởi tạo)** | Kiến trúc 7 Module cơ bản (`llm`, `prompt`, `orchestrator`, `context`, `memory`, `tool`, `monitoring`). | Đơn giản, dễ dựng khung code ban đầu, chạy nhanh. | `monitoring` chỉ kiểm tra chuỗi cơ bản; `tool_manager` tự chạy lệnh trực tiếp không có sandbox, WAL hay secret broker. | Rủi ro cao về TOCTOU, lộ secret, xóa nhầm file khi chạy tác vụ thực tế. |
| **v2.0-draft (Phase 1 Debate)** | Mở rộng lên 12 Module (thêm 5 module: `codebase_intelligence`, `sandbox`, `transaction_secret`, `policy_pep`, `verification_harness`). | Chốt chặn đầy đủ mọi lỗ hổng bảo mật và kiểm thử tự động. | Làm phình số lượng module cấp cao từ 7 lên 12; trộn lẫn công cụ phụ trợ (AST/LSP, CI Harness) vào lõi AI Agent. | Làm phức tạp hóa cấu trúc thư mục gốc và khó theo dõi đối với người thiết kế hệ thống. |
| **v2.1-final (Phase 2 Consensus - Hiện tại)** | **Giữ đúng 7 Module Lõi:**<br>- Đổi tên Module 7 thành `runtime_governance` (chứa 6 sub-packages).<br>- Tách AST/LSP và Verification Harness ra `extensions/` ngoài lõi.<br>- Chuyển `Module 6` thành `ToolPlanAndCodecPort` (Pure Serializable Data). | Giữ trọn vẹn sự tinh gọn của 7 module lõi; lõi hoạt động độc lập không phụ thuộc công cụ ngoài; bảo mật và chống lỗi ngang bằng bản 12 module. | `Module 7` gánh nhiều logic nội bộ hơn; tăng nhẹ độ trễ do tách Pure Data Plan và Subprocess/DLP boundary. | Đã nhận diện và gắn cơ chế giảm thiểu cho 8 Residual Risks (`RISK-01` đến `RISK-08`) tại Phần 2 của báo cáo này. |
