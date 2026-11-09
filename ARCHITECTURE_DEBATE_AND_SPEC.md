# BIÊN BẢN PHẢN BIỆN 6 VÒNG (ANTIGRAVITY ⟷ CODEX CLI) & KIẾN TRÚC THAM CHIẾU CODING AGENT (12 MODULE / 4-PLANE / 5-RING)

Tài liệu này ghi lại toàn bộ 6 vòng thảo luận và phản biện thực tế giữa **Antigravity (Builder)** và **Codex CLI (Reviewer)** qua `open-agent-bridge`, tuân thủ nghiêm ngặt quy tắc tại [`agent_to_agent_rule.md`](file:///D:/Project%20Prompt/Conversation_rule/agent_to_agent_rule.md) và kết hợp nghiên cứu từ các Coding Agent hàng đầu hiện nay (**SWE-agent, OpenHands, Claude Code, Aider, LangGraph, DeepMind CaMeL**).

---

## PHẦN I: TRẢ LỜI TRỰC DIỆN CÂU HỎI CỐT LÕI CỦA USER

### 1. Mô hình 7 Module ban đầu đã đủ để tạo 1 AI Agent code dự án bất kỳ chưa?
- **Kết luận đồng thuận từ cả 2 Agent:** **CHƯA ĐỦ.**
- **Lý do:** 7 module ban đầu (`1. llm_manager`, `2. prompt_manager`, `3. orchestrator`, `4. context_manager`, `5. memory_manager`, `6. tool_manager`, `7. monitoring & validators`) mới chỉ tạo thành khung của một **General Conversational / Tool-Calling Agent** (trợ lý hỏi đáp và gọi hàm đơn lẻ). Khi áp vào bài toán **Autonomous Software Engineering (code dự án bất kỳ)**, nó thiếu môi trường thực thi cô lập, thiếu khả năng hiểu cấu trúc mã nguồn (AST/LSP/Build Graph), thiếu cơ chế giao dịch nhiều file (Transactional Patch/Rollback), thiếu bộ kiểm thử độc lập (Verification Harness) và lỗ hổng phân quyền rất lớn khi chạy lệnh shell/test.

### 2. Ưu điểm và Nhược điểm của 7 Module gốc

| Khía cạnh | Ưu điểm của 7 Module gốc | Nhược điểm khi dùng để Code dự án thực tế |
| :--- | :--- | :--- |
| **Kiến trúc tổng thể** | Tách biệt trực quan mặt phẳng suy luận (LLM, Prompt, Context), dữ liệu (Memory) và công cụ (Tool, Monitoring). Dễ hiểu, dễ theo dõi. | Thiết kế phẳng (Flat Modules), chưa phân tách **Deterministic Control Kernel** khỏi **Untrusted Stochastic LLM**. |
| **Module 3 (`orchestrator`)** | Đáp ứng tốt vòng lặp ReAct ngắn hạn. | Dễ rơi vào vòng lặp sửa lỗi vô hạn (infinite repair loop), thiếu DAG Task Scheduler, thiếu Event Log bền vững để resume sau khi crash. |
| **Module 4 & 5 (`context` & `memory`)** | Có cắt tỉa token và RAG cơ bản. | RAG vector truyền thống thất bại khi tìm kiếm call-graph/cross-file dependency; dễ bị **Indirect Prompt Injection** từ mã nguồn/README/log độc hại và nhiễm bẩn bộ nhớ (Memory Poisoning). |
| **Module 6 (`tool_manager`)** | Đăng ký và gọi tool qua JSON Schema linh hoạt. | Cho phép chạy lệnh bash/file trực tiếp trên máy thật hoặc phân quyền theo tên lệnh (`pytest`, `make`) cực kỳ nguy hiểm vì `pytest`/`conftest.py`/`setup.py` thực chất là **Arbitrary Code Execution**. |
| **Module 7 (`monitoring & validators`)** | Có kiểm duyệt Input/Tool/Output cơ bản. | Gộp chung Policy Enforcement, Quality Verification và Telemetry; nếu dùng cùng LLM để vừa code vừa chấm bài sẽ chia sẻ chung điểm mù (Shared Blind Spot). |

### 3. Năm (05) Module Mở Rộng Bắt Buộc (Nâng cấp từ 7 lên 12 Module trong 4 Plane & 5 Ring)

Để giữ nguyên 7 module gốc của bạn làm xương sống dễ theo dõi nhưng khắc phục toàn bộ nhược điểm trên, hệ thống được mở rộng thêm **5 module chuyên biệt cho Coding Agent** (tổng cộng **12 Module**):
- **Module 8 (`codebase_intelligence`):** Incremental Repo Map (Tree-sitter AST, LSP, Build/Schema Graph, Dependency Impact Analysis).
- **Module 9 (`workspace_sandbox`):** Môi trường thực thi cô lập (MicroVM / Container / OS Sandbox) với Layered Mount (`Immutable Source Lowerdir` + `Writable Scratch Upperdir`) và quản lý phiên bản theo Generation (`gen_<N>`).
- **Module 10 (`transaction_journal_and_secret_broker`):** Giao dịch áp dụng patch nhiều file (Multi-File Staging/Atomic Publication & Crash-Recoverable Undo/Redo WAL) + Secret Broker tiêm credential qua Egress Proxy không bao giờ lộ raw secret cho LLM.
- **Module 11 (`policy_engine_pep`):** Bộ thực thi chính sách tất định (Deterministic Out-of-LLM Policy Enforcement Point), quản lý Capability Token nguyên tử, Fencing Epoch và kiểm tra đường dẫn qua OS File Handle.
- **Module 12 (`verification_harness_and_attestation`):** Khung kiểm định độc lập nằm ngoài source tree (`Out-of-Tree Trusted Test Runner`), tách biệt hoàn toàn khỏi khóa ký (`DSSE / in-toto 2-of-2 KMS Attestation`).

---

## PHẦN II: BIÊN BẢN TRANH LUẬN & PHẢN BIỆN 6 VÒNG (ANTIGRAVITY ⟷ CODEX CLI)

### Vòng 1 (Round 1)
- **[ROUND 1 - BUILDER (Antigravity)]:**
  - Khẳng định 7 module chưa đủ; đề xuất bổ sung 5 thành phần: (1) Workspace Sandbox & Git Worktree Rollback, (2) Codebase Intelligence (AST/LSP), (3) Plan-Execute-Verify Loop, (4) Sub-Agent Delegation, (5) Phân quyền 3 cấp (`ALLOW`, `ASK_USER`, `DENY`) và Sub-agent `READ_ONLY`.
- **[ROUND 1 - REVIEWER (Codex CLI) — Trạng thái: `[CONTINUE]`]:**
  - **Phản biện 12 lỗ hổng:**
    1. *"Code dự án bất kỳ"* không có biên giới (Capability Envelope) thì không thể kiểm chứng (firmware/kernel khác hẳn web app).
    2. Phân quyền theo tên lệnh (`ALLOW` cho `pytest`/`make`) là **lỗ hổng chí mạng**: test runner và build script thực thi code tùy ý trong repo (`conftest.py`, `Makefile`).
    3. Sub-agent `READ_ONLY` vẫn có thể làm rò rỉ secret qua prompt injection hoặc output.
    4. Thiếu cơ chế chống xung đột khi nhiều Sub-agent sửa chung codebase.
    5. Gộp chung Policy Enforcement và Validator vào Module 7 làm mất tính độc lập.
  - **Đề xuất của Reviewer:** Tổ chức lại thành **4 Plane** (`Control`, `Knowledge`, `Execution`, `Assurance`), dùng **Capability Token ngắn hạn** kiểm tra ngoài LLM và **Transaction Journal** (`Reversible`, `Compensatable`, `Irreversible`).

---

### Vòng 2 (Round 2)
- **[ROUND 2 - BUILDER (Antigravity)]:**
  - Tiếp thu và thiết kế **Capability Envelope 3 Tier** (Tier 1 Full Autonomous, Tier 2 Assisted Remote/Simulator, Tier 3 Human-Gated).
  - Ánh xạ 7 module gốc + 5 module mới vào **4 Plane** kèm **Trust Boundaries (TB0–TB4)**.
  - Đưa ra **Durable State Machine** và **Ma trận Phân quyền theo Principal** (Main Orchestrator, Explorer, Coder chạy `--network=none` trên Git Worktree riêng, Verifier, Integration Agent, Human Operator).
- **[ROUND 2 - REVIEWER (Codex CLI) — Trạng thái: `[CONTINUE]`]:**
  - **Phản biện 15 lỗ hổng sâu hơn:**
    1. **Plane ≠ Trust Boundary:** Đặt `llm_manager` (stochastic, dễ bị injection) chung boundary với `orchestrator` (deterministic kernel) là sai.
    2. **Spotlighting (delimiter) không chặn được Indirect Prompt Injection:** Cần Taint/Provenance tracking.
    3. **`AST-parsed shell command` tạo cảm giác an toàn giả:** Phải dùng OS/Container syscall & binary digest allowlist.
    4. **`git worktree` không phải là ranh giới cô lập:** File `.git` của worktree trỏ về repo chính (hooks, config, objects dùng chung).
    5. **TOCTOU & Confused Deputy:** Kiểm tra đường dẫn bằng chuỗi bị lỗi Time-of-Check to Time-of-Use; Secret Broker có thể bị lừa qua HTTP redirect/SSRF.

---

### Vòng 3 (Round 3)
- **[ROUND 3 - BUILDER (Antigravity)]:**
  - Nâng cấp lên **5 Ring cô lập theo Process/Container/UID**:
    - `Ring 0`: Deterministic Control Kernel & PEP (0% LLM code).
    - `Ring 1`: Assurance & Evidence Store.
    - `Ring 2A (P-LLM)` & `Ring 2B (Q-LLM)`: Áp dụng mô hình **Google DeepMind CaMeL** tách luồng điều khiển khỏi dữ liệu nhiễm bẩn (`TAINTED_REPO`).
    - `Ring 3`: Ephemeral MicroVM/Container Sandbox.
  - Thay `git worktree` bằng CoW Snapshot; thay kiểm tra đường dẫn chuỗi bằng `openat2(RESOLVE_NO_SYMLINKS)`; thêm `fencing_epoch` và Bounded Repair Loop (`max_repair_attempts = 3`).
- **[ROUND 3 - REVIEWER (Codex CLI) — Trạng thái: `[CONTINUE]`]:**
  - **Phản biện 18 điểm mù hệ thống & mật mã:**
    1. **Ring 1 vừa chạy test vừa giữ khóa ký (`Evidence Attestation Key`) là lỗi nghiêm trọng:** Nếu test độc hại thoát sandbox, nó chiếm khóa ký và tự ký pass giả.
    2. **P-LLM hoàn toàn không đọc code thì không lập kế hoạch đúng được**, còn `TRUSTED_USER` nhầm lẫn giữa *Authority* (quyền ra lệnh) và *Data Integrity* (user có thể paste log chứa mã độc).
    3. **Capability Token ký số (Immutable) nhưng lại chứa trường `used_count` khả biến là mâu thuẫn:** Phải tách sang Atomic Consumption Ledger.
    4. **Gộp chung Commit và Release** làm hệ thống quá nặng khiến lập trình viên tìm cách tắt bảo mật.
    5. **Immutable Audit Log xung đột với quyền xóa dữ liệu (Right-to-Delete):** Cần cơ chế Crypto-Erasure.

---

### Vòng 4 (Round 4)
- **[ROUND 4 - BUILDER (Antigravity)]:**
  - Tách Ring 1 thành 3 mắt xích: `Untrusted Runner (Ring 3)` ➔ `Deterministic Evidence Validator (Ring 1A)` ➔ `HSM/KMS Minimal Signer (Ring 1B)`.
  - Thiết lập **Lattice 3 chiều (`Authority × Integrity/Provenance × Confidentiality`)**; cho phép P-LLM đọc code nhưng kế thừa nhãn `TAINTED` (cấm tự mở rộng Capability nếu không qua Step-Up Approval).
  - Đưa `used_count` vào **Atomic Consumption Ledger (CAS)** và bổ sung quy trình **Hard Kill (`SIGKILL` cgroup/VM + đóng socket + xoay vòng key)**.
  - Thiết kế **5 Progressive Gates (`G1 Checkpoint` ➔ `G2 Local Commit` ➔ `G3 Integration Merge` ➔ `G4 Release Candidate` ➔ `G5 Prod Deploy`)** và **3 Operational Profiles (`L1 Local Dev`, `L2 Team CI`, `L3 Enterprise Zero-Trust`)**.
- **[ROUND 4 - REVIEWER (Codex CLI) — Trạng thái: `[CONTINUE]`]:**
  - **Ghi nhận kiến trúc đã tiệm cận chuẩn tham chiếu, nhưng chỉ ra 4 Blocker cần chốt:**
    1. **Authority không phải thứ tự tuyến tính (`HUMAN > RING0`):** Phải là tập quyền trực giao + các Hard Invariants không ai được vượt qua. Taint ở mức từng token LLM không khả thi (gây taint explosion), phải gắn ở mức **Artifact**.
    2. **Evidence Trust Gap tại Ring 1A:** Runner có thể trả log giả mà không thực sự chạy test; phép nối chuỗi `||` khi ký dễ bị lỗi canonicalization (cần chuẩn **DSSE / in-toto v1.0**).
    3. **CAS từng file lẻ không đảm bảo tính nguyên tử cho toàn bộ Patch nhiều file** khi mất điện giữa chừng.
    4. **Profile L1 đang nới lỏng quá mức** (bỏ sót `.git/hooks`, CI workflows, Docker socket) và raw hash trong Crypto-Erasure có thể bị tấn công từ điển.

---

### Vòng 5 (Round 5)
- **[ROUND 5 - BUILDER (Antigravity)]:**
  - Giải quyết 4 Blocker: (1) **Orthogonal Capability Lattice + Hard Invariants + Artifact-Level Declassification**, (2) **Trusted Execution Supervisor (nằm ở Host/Hypervisor ngoài Guest) + DSSE/in-toto v1.0 (RFC 8785 JCS) + 2-of-2 Quorum Signing**, (3) **Multi-File Staging Transaction + Undo/Redo WAL + Cross-Platform Path Hardening (Unicode NFC, Case-fold, NTFS ADS/Reparse Point)**, (4) **Minimum Security Baseline cho cả L1–L3 + Keyed HMAC Commitments + Post-Deploy Canary + Quantitative Benchmark Suite**.
- **[ROUND 5 - REVIEWER (Codex CLI) — Trạng thái: `[CONTINUE]`]:**
  - **Chỉ ra 2 Blocker kỹ thuật cuối cùng trước khi đồng thuận:**
    1. **Trusted-Test Problem:** Supervisor thu exit code 0 từ ngoài VM vẫn chưa đủ nếu chính bộ test trong repo bị sửa để luôn `return 0` (hoặc xóa assertion). Cần **Out-of-Tree Trusted Test Harness & Expected-Test Manifest** độc lập với repo, đồng thời source tree cần **Layered Mount (Read-Only Lower + Writable Scratch Upper)** để trình biên dịch hoạt động được.
    2. **Atomic Visibility vs Crash-Recoverable Apply:** Trên ext4/NTFS thường, sửa tuần tự kèm WAL chỉ là *Crash-Recoverable*, không phải *Atomic Visibility* cho các tiến trình đọc đồng thời. Cần **Generation-Based Workspace Publication (`gen_<N>`)** cho Atomic Visibility và phân lớp **Normative Specification (`Core MUST` / `Profile Extensions` / `Optional`)**.

---

### Vòng 6 (Round 6 — Đạt Đồng Thuận Toàn Diện)
- **[ROUND 6 - BUILDER (Antigravity)]:**
  - Thiết lập **Out-of-Tree Trusted Verification Harness** (`/opt/ring1_trusted_harness` mount Read-Only từ Ring 1, kiểm tra `expected_test_manifest`, bytecode coverage trace và bộ Sealed Acceptance Tests độc lập) + **Overlay Mount (`lowerdir` RO + `upperdir` scratch)**.
  - Phân tách minh bạch **Mode 1: Generation-Based Immutable Tree Publication (`workspaces/gen_<N>` + atomic pointer switch + reader lease = True Atomic Visibility)** và **Mode 2: Crash-Recoverable In-Place Apply (Idempotent Checksummed WAL cho IDE ngoài)**.
  - Đổi tên `BOUNDED_VERIFIED_PATCH` thành `CAPABILITY_BOUNDED_CANDIDATE`, dùng Handle-Based Path Verification (`GetFinalPathNameByHandleW` / `openat2`), chuẩn hóa DSSE PAE + 2-of-2 Endorsement (`Supervisor AND Validator` ➔ `KMS Policy Signer`), `Bounded-Staleness Lease Abort (10s)`, tách Plaintext Structural Merkle Log khỏi Encrypted Blob Store (kèm Deletion SLO), và chia 3 tầng Normative (`Core MUST`, `Profile Extensions`, `Optional`).
- **[ROUND 6 - REVIEWER (Codex CLI) — Trạng thái: `[AGREED] [CONSENSUS_REACHED]`]:**
  - **Phán quyết của Reviewer:** *"Kiến trúc đã đạt mức **Reference Architecture hoàn chỉnh** và đủ điều kiện `[CONSENSUS_REACHED]`. Hai blocker cuối đã được giải quyết đúng hướng... Đây là kiến trúc phù hợp để làm **Normative Reference Specification** cho Coding Agent từ local developer assistant đến enterprise zero-trust."*

---

## PHẦN III: KIẾN TRÚC THAM CHIẾU TỐI ƯU NHẤT (NORMATIVE REFERENCE ARCHITECTURE)

```mermaid
flowchart TB
    subgraph Ring0["RING 0: DETERMINISTIC CONTROL KERNEL & PEP (0% LLM)"]
        M3["Module 3: Durable Event-Sourced Orchestrator & DAG Scheduler"]
        M11["Module 11 (Mới): Policy Engine (PEP) & Atomic Capability Ledger"]
        M10["Module 10 (Mới): Multi-File Transaction Manager & Secret Broker"]
    end

    subgraph Ring2["RING 2: STOCHASTIC LLM DECISION ZONE (CaMeL Dual-LLM)"]
        M1["Module 1: LLM Manager (Model Router, Key Pool, Quota Circuit Breaker)"]
        M2["Module 2: System Prompt, Signed Skills & Spec Contract"]
        M4["Module 4: Context Manager & Artifact-Level Taint Tracker"]
    end

    subgraph Knowledge["KNOWLEDGE PLANE (Taint-Aware Storage & Repo Graph)"]
        M5["Module 5: Memory Manager (Provenance-Tagged Episodic/RAG/Facts)"]
        M8["Module 8 (Mới): Codebase Intelligence (AST/LSP/Build & Schema Graph)"]
    end

    subgraph Ring3["RING 3: EPHEMERAL UNTRUSTED EXECUTION SANDBOX"]
        M6["Module 6: Tool Manager / Agent-Computer Interface (ACI)"]
        M9["Module 9 (Mới): Isolated Sandbox (Overlay RO Source + Scratch Upper)"]
    end

    subgraph Ring1["RING 1: INDEPENDENT ASSURANCE & EVIDENCE ATTESTATION"]
        M7["Module 7: Telemetry, Cost/Resource Watchdog & Merkle Audit Log"]
        M12A["Module 12A (Mới): Trusted Execution Supervisor & Out-of-Tree Test Harness"]
        M12B["Module 12B (Mới): Evidence Validator & KMS 2-of-2 DSSE Signer"]
    end

    M3 <-->|"Capability Request / State Transition"| M11
    M3 -->|"Schedule LLM Call"| M1
    M4 -->|"Assemble Prompt"| M2
    M4 <-->|"Retrieve Repo Graph & Memories"| M5
    M4 <-->|"Query AST/LSP/Impact"| M8
    M1 -->|" Emit Tainted Candidate Patch / Tool Call"| M11
    M11 -->|"Verify Handle, Lease & Epoch"| M6
    M6 -->|"Execute in Generation gen_N"| M9
    M12A -->|"Supervise Host Pipe & Sealed Tests"| M9
    M12A -->|"Endorse Execution"| M12B
    M12B -->|"Signed DSSE/in-toto Attestation"| M10
    M10 -->|"Atomic Generation Publish / WAL Commit"| M3
```


---

# PHẦN II: PHASE 2 DEBATE — TINH GỌN VỀ ĐÚNG 7 MODULE LÕI THEO QUYẾT ĐỊNH CỦA USER (5 ROUNDS ➔ `[CONSENSUS_REACHED]`)

## 1. Quyết định Kiến trúc Tối cao của User (Phase 2 Constraints)
1. **Giữ đúng 7 Module Lõi cho AI Agent (`src/agent_core/`):** Không mở rộng thành 12 module cấp cao.
2. **Mục 1 (`codebase_intelligence` - AST/LSP/Repo Map):** Tách ra làm **Công cụ hỗ trợ bên ngoài (`extensions/external_coding_tools`)** cắm vào `Module 6 (tool_manager)` hoặc `Module 5 (memory_manager)`. Thiếu nó, AI Agent 7 module vẫn hoạt động bình thường.
3. **Mục 2 (`sandbox`), Mục 3 (`transaction & secret`), Mục 4 (`policy_engine_pep`):** Gom toàn bộ vào **Module 7** và đổi tên Module 7 thành **`runtime_governance`**.
4. **Mục 5 (`verification_harness` - Out-of-tree CI/Eval/Attestation):** Đặt làm **Lớp vỏ bọc phụ trợ bên ngoài 7 module (`extensions/outer_verification_harness`)**. Không có lớp vỏ này, AI Agent vẫn làm việc độc lập bình thường.

---

## 2. Biên bản Tranh biện Trực tiếp Phase 2 (Antigravity `[BUILDER]` ⟷ Codex CLI `[REVIEWER]`)

### Vòng 1 (Phase 2 - Round 1)
- **`[PHASE 2 - ROUND 1 - BUILDER]` (Antigravity):**
  - Đề xuất giữ 7 module lõi, đổi tên Module 7 thành `guardrails_and_monitoring` (hoặc `security_governance_and_monitoring`), chia nội bộ Module 7 thành 4 sub-packages (`permission_pep`, `sandbox_isolation`, `transaction_and_secret`, `validators_and_telemetry`) và đưa `external_coding_tools` + `outer_verification_harness` ra `extensions/`.
- **`[PHASE 2 - ROUND 1 - REVIEWER]` (Codex CLI):**
  - **Đề xuất tên chuẩn cho Module 7:** **`runtime_governance`** — bao quát đúng 1 trách nhiệm cấp module (SRP): *"Quản trị mọi tương tác tại runtime đi qua trust boundary hoặc có side-effect"*, với interface chính `GovernedToolExecutor`.
  - **Phát hiện 8 điểm yếu:**
    1. Chia 4 sub-packages vẫn ghép gượng ép (`transaction_and_secret` và `validators_and_telemetry` có lý do thay đổi khác nhau) ➔ Cần tách thành **6 sub-packages có độ kết dính cao (High Cohesion)**: `policy_enforcement`, `isolation`, `transaction`, `secret_broker`, `content_safety`, `audit_observability`.
    2. Nguy cơ Circular Dependency giữa `Module 6 (tool_manager)` và `Module 7 (runtime_governance)` ➔ Giải quyết bằng **Dependency Inversion (Decorator Pattern)** qua contracts trung lập.
    3. `Module 3 (orchestrator)` biết quá nhiều chi tiết pipeline của Module 7.
    4. Filesystem WAL không thể rollback side-effect bên ngoài (gửi email, gọi API, shell) ➔ Cần phân loại side-effect.
    5. TOCTOU trong kiểm tra đường dẫn string.
    6. Không được mở WAL hay giữ lock khi đang chờ `ASK_USER`.
    7. Rò rỉ biến mật nếu đưa vào `ToolCallRequest` rồi mới redact ở đầu ra.
    8. Trùng quyền sở hữu nhãn Taint giữa `Module 4 (context_manager)` và `Module 7`.
  - **Trạng thái:** `[CONTINUE]`

### Vòng 2 (Phase 2 - Round 2)
- **`[PHASE 2 - ROUND 2 - BUILDER]` (Antigravity):**
  - Chốt tên `runtime_governance` với 6 sub-packages nội bộ.
  - Áp dụng Dependency Inversion qua `shared/contracts.py`.
  - Phân loại 4 `SideEffectClass` (`READ_ONLY`, `WORKSPACE_TRANSACTIONAL`, `EXTERNAL_COMPENSATABLE`, `EXTERNAL_IRREVERSIBLE`).
  - Thiết kế `PendingExecutionIntent` cho `ASK_USER` (không giữ lock/WAL khi chờ User) và giao quyền sở hữu duy nhất `TaintLabel` cho `Module 4 (context_manager)`.
- **`[PHASE 2 - ROUND 2 - REVIEWER]` (Codex CLI):**
  - **Phát hiện 8 edge cases sâu hơn:**
    1. Enum đơn `SideEffectClass` không biểu diễn được tool đa hiệu ứng (vừa sửa file, vừa gọi mạng, vừa đọc secret) và AST/LSP không mặc nhiên `READ_ONLY`.
    2. `reserve/commit/release` chưa xử lý được cửa sổ crash sau khi đã phát lệnh ra ngoài nhưng trước khi `commit` (`INDETERMINATE`).
    3. `workspace_digest` toàn cục gây false conflict khi file không liên quan thay đổi và chưa chặn được TOCTOU sát syscall.
    4. `SafeWorkspaceHandle` không áp dụng được cho mọi CLI/LSP bên ngoài tự mở file bằng pathname.
    5. Nguy cơ bypass governance nếu `RawToolExecutor` và `GovernedToolExecutor` dùng chung 1 kiểu `ToolExecutionPort`.
    6. Cần thu hẹp cam kết của `secret_broker` khi subprocess buộc phải đọc secret.
    7. Compensation bên ngoài là Saga (có thể lỗi một phần), không được gọi là atomic rollback.
    8. Một file `shared/contracts.py` duy nhất dễ biến thành coupling hub.
  - **Trạng thái:** `[CONTINUE]`

### Vòng 3 (Phase 2 - Round 3)
- **`[PHASE 2 - ROUND 3 - BUILDER]` (Antigravity):**
  - Tách `shared/` thành 3 bounded contracts (`execution_contracts.py`, `governance_contracts.py`, `audit_contracts.py`) và tách kiểu `RawToolBackendPort` vs `GovernedToolExecutionPort`.
  - Thay enum đơn bằng `EffectProfile` đa chiều + `PlannedEffects`.
  - Bổ sung máy trạng thái `PREPARED → DISPATCHED → CONFIRMED | INDETERMINATE` và ngữ nghĩa Saga (`COMPENSATED`, `PARTIALLY_COMPENSATED`, `COMPENSATION_FAILED`).
  - Thay digest toàn workspace bằng `ResourceVersionCondition` (CAS theo tài nguyên đích) và 3 mức `IsolationAssuranceLevel`.
- **`[PHASE 2 - ROUND 3 - REVIEWER]` (Codex CLI):**
  - **Phát hiện 5 điểm cần khóa chặt:**
    1. `Module 7` không được tin tưởng mù quáng vào `PlannedEffects` do chính tool/plugin (Module 6) tự khai báo ➔ Phải tách `DeclaredEffects` (không đáng tin) và `AuthorizedExecutionPlan` (do Module 7 lập dựa trên `OperatorApprovedToolManifestRegistry`).
    2. Mâu thuẫn quyền sở hữu Subprocess: Nếu `Module 6` trực tiếp chạy subprocess thì `Module 6` tất yếu thấy raw stdout/stderr và secret trước DLP ➔ Chốt phương án bảo mật mạnh: `Module 7` sở hữu Process Launcher, Sandbox, Secret Injection và Raw Streams; `Module 6` chỉ tạo `ToolInvocationPlan` và parse output đã scrub.
    3. `READ_ONLY` qua mạng không đồng nghĩa với `SAFE_RETRY` ➔ Cần trường `RetrySemantics` độc lập.
    4. Làm rõ giới hạn của Generation Lease trước các tiến trình ngoài sandbox (IDE/antivirus).
    5. Diễn đạt Type-Level Separation đúng bản chất là guardrail chống nối dây nhầm (accidental miswiring).
  - **Trạng thái:** `[CONTINUE]`

### Vòng 4 (Phase 2 - Round 4)
- **`[PHASE 2 - ROUND 4 - BUILDER]` (Antigravity):**
  - Tách `DeclaredEffects` và `AuthorizedExecutionPlan` dựa trên `OperatorApprovedToolManifestRegistry` thuộc `Module 7`.
  - Chuyển `Module 6 (tool_manager)` thành `ToolPlanAndCodecPort` (chỉ sinh `ToolInvocationPlan` và parse `ScrubbedExecutionOutput`); `Module 7` nắm giữ hoàn toàn Process Launcher, Sandbox, Secret Injection và DLP Scrubber.
  - Bổ sung `RetrySemantics` (`SAFE_RETRY`, `RETRY_WITH_IDEMPOTENCY_KEY`, `QUERY_STATUS_BEFORE_RETRY`, `NEVER_AUTO_RETRY`) và 3 mức `IsolationAssuranceLevel` (`HANDLE_ENFORCED`, `SNAPSHOT_AND_OVERLAY_ENFORCED`, `COOPERATIVE_WORKSPACE_LEASE`).
- **`[PHASE 2 - ROUND 4 - REVIEWER]` (Codex CLI):**
  - **Phát hiện điểm chặn cuối cùng:**
    1. `InProcessCallableSpec(handler_fn, ...)` chứa tham chiếu hàm Python (`handler_fn`) — đây là executable capability chứ không phải Pure Data DTO, cho phép plugin tuồn code chạy trực tiếp trong tiến trình đặc quyền của `Module 7`.
    2. Cần thay bằng Pure Data ID (`PureFunctionSpec(trusted_function_id, serialized_args)`) chỉ trỏ vào `TrustedInProcessPureRegistry` do `Module 7` sở hữu (chỉ dành cho hàm thuần không I/O trong TCB), và dùng `AuthorizedResourceSet` tối thiểu.
    3. Bổ sung ràng buộc ngữ nghĩa (`allowed_executable_digests`, `argv_schema_constraints`, `http_route_constraints`) + `DimensionEnforcementMode` vào `OperatorApprovedToolManifestRegistry`.
  - **Trạng thái:** `[CONTINUE]`

### Vòng 5 (Phase 2 - Round 5)
- **`[PHASE 2 - ROUND 5 - BUILDER]` (Antigravity):**
  - Loại bỏ hoàn toàn `handler_fn` khỏi `ToolInvocationPlan`. Mọi kế hoạch thực thi từ `Module 6` là 100% Pure Serializable Data (`WorkspaceFileOpSpec`, `SubprocessSpec`, `HttpEgressSpec`, `PureFunctionSpec` dùng `JsonValue` đóng).
  - Khóa `TrustedInProcessPureRegistry` và `AuthorizedResourceSet` bên trong `Module 7 (runtime_governance)`.
  - Bổ sung `DimensionEnforcementMode` (`ENFORCED_BY_RUNTIME_BOUNDARY`, `VERIFIED_BY_STATIC_CONSTRAINT`, `UNVERIFIABLE_SEMANTIC_EFFECT` ➔ tự động nâng lên `DENY`/`ASK_USER` + `NEVER_AUTO_RETRY`).
- **`[PHASE 2 - ROUND 5 - REVIEWER]` (Codex CLI):**
  - Xác nhận: `"[AGREED] Điểm chặn cuối đã được giải quyết: execution plan chỉ còn dữ liệu tuần tự hóa, plugin không thể đưa callable vào TCB, và semantic effects được cưỡng chế độc lập với khai báo của plugin... Trạng thái lượt: [CONSENSUS_REACHED]"`.

---

## 3. Sơ đồ Kiến trúc 7 Module Lõi + 2 Thành phần Phụ trợ (Bản Chốt Consensus Phase 2)

```
=====================================================================================
[PHỤ TRỢ B - NGOÀI LÕI] extensions/outer_verification_harness (Optional CI/Eval)
  (Chỉ gọi Public API của Orchestrator & kiểm định ExecutionReceipt / AuditEvent)
=====================================================================================
                                         │
                                         ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        LÕI AI AGENT: ĐÚNG 7 MODULE CHÍNH                          ┃
┃                              (src/agent_core/)                                    ┃
┃                                                                                   ┃
┃  ┌──────────────────────┐   ┌──────────────────────┐   ┌───────────────────────┐  ┃
┃  │ 1. llm_manager       │   │ 2. prompt_manager    │   │ 5. memory_manager     │  ┃
┃  │ - Model Registry     │   │ - App/User/Session   │   │ - Working History     │  ┃
┃  │ - API Key Pool       │   │ - Dynamic Skills     │   │ - Episodic / Semantic │  ┃
┃  │ - Token Budget       │   └──────────┬───────────┘   │ - Entity Fact Store   │  ┃
┃  │ - Fallback Chain     │              │               └───────────┬───────────┘  ┃
┃  └──────────▲───────────┘              ▼                           ▼              ┃
┃             │               ┌──────────────────────────────────────────────────┐  ┃
┃             │               │ 4. context_manager (Single Owner of TaintLabel)  │  ┃
┃             │               │ - Provenance Tagging & Sliding Window Compaction │  ┃
┃             │               └──────────────────────────▲───────────────────────┘  ┃
┃             │                                          │                          ┃
┃  ┌──────────┴──────────────────────────────────────────┴───────────────────────┐  ┃
┃  │ 3. orchestrator                                                             │  ┃
┃  │ - Durable Session State Machine                                             │  ┃
┃  │ - Chỉ phụ thuộc: GovernedToolExecutionPort & ConversationGovernancePort     │  ┃
┃  └─────────────────────────────────────┬───────────────────────────────────────┘  ┃
┃                                        │                                          ┃
┃                                        ▼                                          ┃
┃  ┌─────────────────────────────────────────────────────────────────────────────┐  ┃
┃  │ 7. runtime_governance (GovernedToolExecutor & ConversationGovernancePort)   │  ┃
┃  │   ├── 7.1 policy_enforcement (OperatorManifestRegistry, PEP, AttemptLedger) │  ┃
┃  │   ├── 7.2 isolation          (AuthorizedResourceSet, Sandbox/ProcessRunner) │  ┃
┃  │   ├── 7.3 transaction        (Resource CAS Lease, Workspace WAL, Ext Saga)  │  ┃
┃  │   ├── 7.4 secret_broker      (secret_ref:// Egress Proxy / Ephemeral FD)    │  ┃
┃  │   ├── 7.5 content_safety     (Input Guardrails & Raw Stream DLP Scrubber)   │  ┃
┃  │   └── 7.6 audit_observability(Signed ExecutionReceipt, Telemetry, Quotas)   │  ┃
┃  └─────────────────────────────────────┬───────────────────────────────────────┘  ┃
┃                                        │ gọi ToolPlanAndCodecPort (Pure Data)     ┃
┃                                        ▼                                          ┃
┃  ┌─────────────────────────────────────────────────────────────────────────────┐  ┃
┃  │ 6. tool_manager (ToolPlanAndCodecPort)                                      │  ┃
┃  │ - Tool Registry, JSON Schema, Pydantic Arg Validation                       │  ┃
┃  │ - prepare_invocation() -> Pure Data ToolInvocationPlan                      │  ┃
┃  │   (WorkspaceFileOpSpec | SubprocessSpec | HttpEgressSpec | PureFunctionSpec)│  ┃
┃  │ - parse_output(ScrubbedExecutionOutput) -> ToolResult                       │  ┃
┃  └─────────────────────────────────────▲───────────────────────────────────────┘  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                         │ (Cắm thêm khi cần, không có vẫn chạy)
=========================================┼===========================================
[PHỤ TRỢ A - NGOÀI LÕI] extensions/external_coding_tools (AST / LSP / Repo Graph MCP)
=====================================================================================
```


---

# PHẦN III: PHASE 3 DEBATE — KHÓA CHẶT CÁC NHƯỢC ĐIỂM, RỦI RO CỐT LÕI (`RISK-01..08`) & RỦI RO THỨ CẤP (`SEC-RISK-01..06`) (4 ROUNDS ➔ `[CONSENSUS_REACHED]`)

Toàn bộ phân tích chi tiết đã được chuẩn hóa và lưu tại [ARCHITECTURE_RISK_AND_TRADEOFF_REPORT.md](file:///d:/AI%20Agent%20Architecture/ARCHITECTURE_RISK_AND_TRADEOFF_REPORT.md):
- **Round 1/5 (`87b52c4`):** Đề xuất 6 cơ chế giảm thiểu cho `RISK-01..08` và phát hiện 6 rủi ro thứ cấp (`SEC-RISK-01..06`) cùng Bảng điều kiện hạ cấp (`Downgrade / Fallback Matrix`).
- **Round 2/5 (`684f1a6`):** Khóa chặt `SHADOW_STAGING` độc lập với `AuthorizedWriteSet` & `InputManifest`, `StatusProbeSpec` 4 trạng thái + Single-Writer Saga Lease, Streaming DLP mặc định hủy raw output, phân loại Preset `REPO_CODE_EXECUTION` cho `pytest`, bảo toàn `ProvenanceLineage` và Handle-walk đa nền tảng (`openat2` / `FILE_FLAG_OPEN_REPARSE_POINT` + `FileId`).
- **Round 3/5 (`4693da8`):** Tinh chỉnh 4 chi tiết kỹ thuật cuối: `empty_gitconfig_file` cho `GIT_CONFIG_GLOBAL`/`SYSTEM`, ngữ nghĩa `fencing_token` (local single-owner vs external duplicate residual risk), `Discard + Best-Effort Zeroization`, và bộ 7 thành phần `Full-Context Scoped Approval Binding`.
- **Round 4/5 (`[CONSENSUS_REACHED]`):** Codex CLI kiểm tra trực tiếp Git Commit `4693da8` và xác nhận đạt đồng thuận tuyệt đối (`[AGREED] ... [CONSENSUS_REACHED]`).


---

# PHẦN IV: PHASE 4 DEBATE — HOÀN THIỆN KIẾN TRÚC 6 MODULE CÒN LẠI (M1–M6) VÀ HỢP ĐỒNG XUYÊN MODULE (4 ROUNDS ➔ `[CONSENSUS_REACHED]`)

Sau khi `Module 7 (runtime_governance)` được đặc tả chặt chẽ ở Phase 2 và Phase 3, Phase 4 tập trung giải quyết toàn diện các hợp đồng, ranh giới và máy trạng thái của **6 Module còn lại (M1–M6)**.

## 1. Biên bản Tranh biện Phase 4 (Antigravity `[BUILDER]` ⟷ Codex CLI `[REVIEWER]`)

### Vòng 1 (Phase 4 - Round 1)
- **`[BUILDER]`:** Tự phát hiện và đề xuất giải quyết 6 lỗ hổng kiến trúc lớn của M1–M6:
  - *G1 (Ranh giới M2/M4/M5):* M2 chỉ giữ instruction template có version; M5 lưu/truy xuất memory; M4 là chủ sở hữu duy nhất của `ContextWindow` với token allocation theo section.
  - *G2 (Vòng điều khiển M3):* Event-sourced durable state machine với append-only `SessionControlLog`; ngân sách cứng phiên; loop detection.
  - *G3 (M1 fallback & replay):* `LLMProviderPort` chuẩn hóa; fallback chỉ giữa các model cùng `capability_profile`; phân loại retry.
  - *G4 (M5 write gate):* Phân 4 tầng nhớ (working, episodic, semantic, procedural); chặn tainted data ghi vào semantic/procedural nếu chưa xác minh.
  - *G5 (M6 tool retrieval):* `ToolCatalog` có version; chọn tool theo ngữ cảnh và budget; kết quả lớn lưu artifact.
  - *G6 (Hợp đồng shared):* Error envelope chung; telemetry trung lập; human channel qua M3.
- **`[REVIEWER]` (Codex CLI):** Phản biện 9 điểm: Tách `SessionControlLog` (M3) khỏi `AuditLog` (M7); state machine cần sub-state bất định; 3 lớp ngân sách độc lập (M3 tổng - M4 lần gọi - M1 giới hạn model); phân biệt tuyệt đối instruction vs data; mở rộng `capability_profile`; quy trình ghi memory 2 pha; chọn tool chỉ là discovery; telemetry vs audit tách riêng; đổi `VERIFYING` thành `SELF_REVIEWING` (heuristic).
- **Trạng thái:** `[CONTINUE]`

### Vòng 2 (Phase 4 - Round 2)
- **`[BUILDER]`:** Tiếp thu trọn vẹn 9 điểm, bổ sung 4 lỗ hổng mới: xử lý `ToolBatch` song song, ủy quyền sub-agent (không tạo module 8), tiến hóa schema event log bằng upcaster, và vị trí của Canonical Intermediate Representation (CIR).
- **`[REVIEWER]` (Codex CLI):** Phản biện 7 điểm chuyên sâu: Resume không được suy diễn `INDETERMINATE` chỉ từ việc thiếu receipt; `ToolBatch` cần DAG và failure policy; `delegate_task` là M3-native control primitive nhưng capability phải do M7 cấp; không được pin policy suốt phiên; upcaster phải fail-closed; CIR cần phân tách Authority × Integrity × Confidentiality; crypto-erasure phải giữ được envelope để fold state.
- **Trạng thái:** `[CONTINUE]`

### Vòng 3 (Phase 4 - Round 3)
- **`[BUILDER]`:** Chuẩn hóa: 4 trạng thái reconciliation khi resume; DAG cho `ToolBatch` dựa trên `AuthorizedResourceSet`; `delegate_task` là M3-native primitive với token phái sinh; dynamic policy re-check (`evaluation_policy_version` vs `current_enforcement_policy_version`); upcaster pure & fail-closed; CIR 3 chiều; crypto-erasure payload blob.
- **`[REVIEWER]` (Codex CLI):** Khóa 5 điểm biên cuối cùng: 4 trạng thái reconciliation phải bao phủ cả terminal failure (`TERMINAL_WITH_RECEIPT`); delegation grant do M7 cấp, token do M7 xác minh tại mọi dispatch; lineage không thể suy đoán nhân quả mà phải tách 3 tập (`exposure_set`, `context_influence_set`, `claimed_citations`); input user phân loại theo typed segments (`UserDirectiveSegment`, `QuotedTextSegment`, ...) và fallback `MIXED_USER_CONTENT`; crypto-erasure phải đưa phiên vào `HALTED_CONTENT_ERASED` nếu thiếu dữ liệu để tiếp tục.
- **Trạng thái:** `[CONTINUE]`

### Vòng 4 (Phase 4 - Round 4 — ĐẠT ĐỒNG THUẬN HOÀN TOÀN)
- **`[BUILDER]`:** Chốt chính xác 100% cả 5 điểm biên:
  1. 4 trạng thái reconciliation: `AUTHORITATIVELY_NOT_DISPATCHED`, `TERMINAL_WITH_RECEIPT` (tách `dispatch_state` và `outcome_state`), `QUERY_PENDING`, `UNKNOWN_AMBIGUOUS`.
  2. Delegation: M7 cấp `AuthorizedDelegationGrant`, composition root khởi tạo child session, token do M7 kiểm tra tại mọi dispatch.
  3. Phân định rõ 3 tập lineage: `exposure_set` (audit), `context_influence_set` (taint propagation), `claimed_citations` (UI giải thích).
  4. Typed segments cho user input, fallback an toàn `MIXED_USER_CONTENT` (kế thừa taint).
  5. Envelope chuẩn, CAS append linearizable, randomized blob ID + keyed commitment, trạng thái `HALTED_CONTENT_ERASED` khi blob bị xóa.
- **`[REVIEWER]` (Codex CLI):**
  > `[AGREED] Năm blocker cuối đã được giải quyết đúng ranh giới trách nhiệm M3/M4/M7 và không làm phát sinh module lõi thứ tám... Kiến trúc hiện đã hoàn thiện hợp đồng cho M1–M6, giữ đúng 7 module lõi, đồng thời bảo toàn các bất biến Phase 2–3.`
  > **Trạng thái lượt:** **`[CONSENSUS_REACHED]`**

---

## 2. Đặc tả Chi tiết Hợp đồng Toàn diện 7 Module Lõi (Consensus v4.0-complete)

### 2.1. Module 1: `llm_manager` (Execution & Adapter Layer)
- **Trách nhiệm:** Quản lý Model Registry, Key Pool (hạn mức, xoay vòng, cooldown, rate-limit), `EffectiveModelLimits` và Provider Adapters.
- **`LLMProviderPort`:** Chuẩn hóa CIR thành provider-specific request. Trả về cấu trúc thống nhất: message deltas, tool-call intent, usage/cost, `finish_reason`.
- **Nguyên tắc Fallback:** Chỉ fallback giữa các model cùng `capability_profile` (tool-calling version, JSON schema support, context length, streaming semantics). Chỉ fallback **trước** khi có token hiển thị ra ngoài hoặc phát lệnh tool; sau đó nếu lỗi phải trả `NeedsReplan` về cho M3.
- **Reproducible Reconstruction:** Mỗi lời gọi sinh `ModelInvocationRecord` gắn với content-addressed input blob, adapter version, tool catalog digest, policy version và model snapshot.

### 2.2. Module 2: `prompt_manager` (Instruction Artifact Repository)
- **Trách nhiệm:** Quản lý các Instruction Templates có phiên bản (`SystemPrompt`, `AppRolePrompt`, `SkillTemplates`).
- **Ranh giới:** Không truy xuất dữ liệu, không biết token budget, không chứa lịch sử hội thoại (lịch sử thuộc M3/M4).
- **Phân cấp Chỉ dẫn:** Hỗ trợ quy tắc ưu tiên và phát hiện xung đột: `system_invariant > app_role > user_directive > session_skill`.

### 2.3. Module 3: `orchestrator` (Durable Control Plane)
- **Trách nhiệm:** Vòng điều khiển suy luận – hành động, quản lý phiên làm việc (`AgentSession`), ngân sách tổng (`SessionBudgetLedger`) và điều phối sub-agent.
- **`SessionControlLog`:** Append-only log với CAS append trên `expected_seq` (bảo đảm linearizable write). State của phiên là kết quả fold(events).
- **Composite State Machine:**
  - Top-level: `IDLE → PLANNING → ACTING → OBSERVING → SELF_REVIEWING → FINALIZING → DONE | FAILED | HALTED`.
  - Trong `ACTING`: M3 theo dõi `ToolInvocationSubstate` do M7 công bố (`PREPARED → AWAITING_APPROVAL → AUTHORIZED → DISPATCHED → TERMINAL`).
- **Quản lý Sub-agent (Delegation):** Coi sub-agent là M3-native control primitive (không qua M7 như executable tool). M3 gửi `DelegationRequest` → M7 cấp `AuthorizedDelegationGrant` → Composition root tạo child session với budget escrow từ cha. Con cần vượt quyền thì chuyển `CHILD_AWAITING_PARENT_APPROVAL`.
- **Khôi phục sự cố (Reconciliation):** Khi resume mà intent chưa có observation, M3 đối soát với M7 theo 4 trạng thái (`AUTHORITATIVELY_NOT_DISPATCHED`, `TERMINAL_WITH_RECEIPT`, `QUERY_PENDING`, `UNKNOWN_AMBIGUOUS`).

### 2.4. Module 4: `context_manager` (Context Assembly & Token Budgeting)
- **Trách nhiệm:** Lắp ráp `ContextWindow`, phân bổ token theo `ContextManifest` phụ thuộc, nén cửa sổ trượt (Sliding Window Compaction) và là **Single Source of Truth** về Taint & Provenance.
- **Canonical Intermediate Representation (CIR):** Biểu diễn trung gian đa chiều có 2 kênh logic: `instruction_channel` và `data_channel`. Gắn nhãn 3 chiều độc lập: Authority × Integrity × Confidentiality cho từng segment.
- **Taint Propagation:** Dựa trên `context_influence_set` (toàn bộ dữ liệu thực tế đã đưa vào context để sinh đầu ra), không suy diễn nhân quả cảm tính.
- **Bảo toàn Invariant:** `Pinned Invariants` (quyết định của user, chính sách hệ thống) có quota cứng, không bao giờ bị nén. Nếu quota bắt buộc vượt giới hạn mô hình, trả về `ContextUnsatisfiable` để xin ý kiến User, không cắt tỉa âm thầm.

### 2.5. Module 5: `memory_manager` (Long-Term Knowledge & Fact Store)
- **Trách nhiệm:** Quản lý lưu trữ và truy xuất 4 tầng nhớ: `working` (phiên), `episodic` (lịch sử sự kiện), `semantic` (tri thức tra cứu), `procedural` (quy trình mẫu).
- **Two-Phase Write Gate:** Ghi vào dài hạn phải qua: `MemoryCandidate → Validation/Conflict-Check → Verification/Approval → CommittedMemoryRecord`. Dữ liệu có nhãn Taint không được tự ý ghi vào `semantic/procedural` nếu chưa qua Trusted Verifier hoặc User duyệt.
- **Truy xuất Đa chiều:** `MemoryQuery` hỗ trợ: tenant scope, time range, taint ceiling, record types, token budget và snapshot version.
- **Crypto-Erasure (`forget`):** Tiêu hủy khóa mã hóa (DEK) của payload blob và ghi nhận tombstone; structural metadata được giữ lại phục vụ tính toàn vẹn của audit.

### 2.6. Module 6: `tool_manager` (Tool Catalog & Codec Port)
- **Trách nhiệm:** Quản lý danh mục công cụ (`ToolCatalog`), thẩm định tham số đầu vào (`Pydantic`), chọn lọc công cụ theo ngữ cảnh (`select_tools` - discovery layer), chuyển đổi yêu cầu thành Pure Data `ToolInvocationPlan` và giải mã `ScrubbedExecutionOutput`.
- **Ranh giới Tuyệt đối:** Không sở hữu Process Launcher, không giữ OS file handle, không mở socket mạng, không nắm giữ Secret. Mọi kế hoạch đều là Pure Data Union (`WorkspaceFileOpSpec`, `SubprocessSpec`, `HttpEgressSpec`, `PureFunctionSpec`).

### 2.7. Module 7: `runtime_governance` (Execution Interceptor & TCB)
- **Trách nhiệm:** Cổng thực thi có quản trị duy nhất (`GovernedToolExecutor` & `ConversationGovernancePort`), nắm toàn bộ Trusted Computing Base (TCB) của hệ thống.
- **6 Sub-packages Độc lập (Tuân thủ DAG một chiều):**
  1. `policy_enforcement/`: Đối chiếu `OperatorApprovedToolManifestRegistry`, kiểm tra dynamic policy (`current_enforcement_policy_version`), cấp `AuthorizedDelegationGrant`, quản lý `AttemptLedger`.
  2. `isolation/`: Nắm giữ `AuthorizedResourceSet` (handle-walk chống symlink race trên POSIX/Windows), chạy tiến trình trong `SHADOW_STAGING` hermetic hoặc OS Container.
  3. `transaction/`: Quản lý CAS Resource Lease, `WorkspaceSnapshotWAL` all-or-nothing merge, và Single-Writer Saga Queue có `fencing_token`.
  4. `secret_broker/`: Bơm credential tại Egress Proxy (`EGRESS_PROXY_INJECTED`) hoặc Ephemeral FD; không để raw secret lọt vào M6/M3.
  5. `content_safety/`: Bounded Streaming DLP với cơ chế `Discard + Best-Effort Zeroization` khi phát hiện secret; kiểm duyệt Input Guardrails.
  6. `audit_observability/`: Ký số và xuất bản `ExecutionReceipt` (phân tách `dispatch_state` và `outcome_state`), bảo quản Audit Trail, giám sát Resource Quota.

---

## 3. Sơ đồ Luồng Điều khiển và Dữ liệu Hợp nhất (Unified 7-Module Architecture)

```
=============================================================================================
[EXTENSIONS] outer_verification_harness (CI/Eval)  |  external_coding_tools (AST/LSP MCP)
=============================================================================================
                                         │
                                         ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                              LÕI AI AGENT: ĐÚNG 7 MODULE                                  ┃
┃                                                                                           ┃
┃   [M2: prompt_manager]            [M5: memory_manager]                                    ┃
┃   - Versioned Instruction Repo    - 4-Tier Memory (Working/Episodic/Semantic/Procedural)  ┃
┃   - Template & Precedence Rules   - Two-Phase Write Gate & Crypto-Erasure                 ┃
┃            │                               │                                              ┃
┃            └───────────────┬───────────────┘                                              ┃
┃                            ▼                                                              ┃
┃               [M4: context_manager] (Single Source of Truth for Taint)                    ┃
┃               - ContextManifest Token Allocation (Strict Priority Quotas)                 ┃
┃               - Assembles Canonical Intermediate Representation (CIR: 3-D Lattice)        ┃
┃               - Calculates context_influence_set for Provenance Lineage                   ┃
┃                            │                                                              ┃
┃                            ▼                                                              ┃
┃   [M1: llm_manager] ◄──────────────► [M3: orchestrator] (Durable Control Plane)          ┃
┃   - LLMProviderPort (CIR-aware)      - Event-Sourced SessionControlLog (CAS Append)       ┃
┃   - Same-Profile Fallback Guard      - State Machine (with M7 ToolInvocationSubstate)     ┃
┃   - Model Limits & Usage Metric      - Native Sub-agent Delegation Controller             ┃
┃                                      - UserInteractionPort Mediator                       ┃
┃                                                    │                                      ┃
┃                                                    ▼                                      ┃
┃                          [M7: runtime_governance] (Sole Execution TCB)                    ┃
┃                          ├── 7.1 policy_enforcement (Dynamic Policy Check & Grants)       ┃
┃                          ├── 7.2 isolation (AuthorizedResourceSet, SHADOW_STAGING)        ┃
┃                          ├── 7.3 transaction (Resource CAS Lease, WAL, Saga DAG)          ┃
┃                          ├── 7.4 secret_broker (Egress Proxy / Ephemeral FDs)             ┃
┃                          ├── 7.5 content_safety (Streaming DLP Discard/Zeroize)           ┃
┃                          └── 7.6 audit_observability (Signed Terminal Receipts)           ┃
┃                                                    │                                      ┃
┃                                                    ▼ (calls ToolPlanAndCodecPort)         ┃
┃                          [M6: tool_manager] (Pure Data Catalog & Codec)                   ┃
┃                          - ToolCatalog & select_tools() Discovery                         ┃
┃                          - prepare_invocation() -> Pure Data ToolInvocationPlan           ┃
┃                          - parse_output(ScrubbedExecutionOutput) -> ToolResult            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```


---

## 4. Kiáº¿n trÃºc Váº­n hÃ nh Thá»±c táº¿ (Production Operational Architecture - Phase 5)

DÆ°á»›i Ä‘Ã¢y lÃ  Ä‘áº·c táº£ chi tiáº¿t 4 bÃ i toÃ¡n váº­n hÃ nh phá»©c táº¡p khi triá»ƒn khai 7 module lÃµi trÃªn há»‡ thá»‘ng production thá»±c táº¿, Ä‘Ã£ Ä‘Æ°á»£c hoÃ n thiá»‡n vÃ  Ä‘á»“ng thuáº­n qua tranh biá»‡n Ä‘a gÃ³c nhÃ¬n:

### 4.1 Cáº¡nh tranh TÃ i nguyÃªn Äa Agent/Äa PhiÃªn trÃªn Shared Workspace
1. **Hai Publication Mode TÃ¡ch Báº¡ch Tuyá»‡t Äá»‘i:**
   - **`GENERATION_PUBLICATION` (True Atomic Visibility):**
     - Ãp dá»¥ng cho cÃ¡c runtime/build tooling há»— trá»£ pointer-aware generation protocol.
     - Dá»¯ liá»‡u Ä‘Æ°á»£c ghi vÃ o thÆ° má»¥c báº¥t biáº¿n `gen_<N>`.
     - Quy trÃ¬nh báº£o Ä‘áº£m Ä‘á»™ bá»n vá»¯ng (Durability Protocol):
       - *POSIX:* (1) `fsync` toÃ n bá»™ file trong generation; (2) `fsync` cÃ¡c thÆ° má»¥c con tá»« dÆ°á»›i lÃªn (bottom-up); (3) `fsync` thÆ° má»¥c cha `gen_<N>`; (4) Táº¡o pointer táº¡m `current.new` vÃ  `fsync`; (5) Atomic rename thay tháº¿ `current` (hoáº·c `RENAME_EXCHANGE` cÃ³ cÆ¡ cháº¿ dá»n dáº¹p orphan); (6) `fsync` thÆ° má»¥c cha chá»©a pointer.
       - *Windows & Network Filesystem:* OS adapter cÃ´ng bá»‘ `FilesystemDurabilityMatrix` cho `FlushFileBuffers` vÃ  atomic metadata/rename. Náº¿u khÃ´ng Ä‘Ã¡p á»©ng, há»‡ thá»‘ng tá»± Ä‘á»™ng háº¡ cáº¥p durability contract vÃ  cáº£nh bÃ¡o operator.
     - Reader báº¯t buá»™c pháº£i pin `(generation_id, root_handle)` má»™t láº§n duy nháº¥t cho toÃ n bá»™ read transaction Ä‘á»ƒ duy trÃ¬ transaction isolation.
   - **`IN_PLACE_WAL_APPLY` (Crash-Recoverable cho MÃ´i trÆ°á»ng IDE / Filesystem ThÃ´ng thÆ°á»ng):**
     - Máº·c Ä‘á»‹nh cho cÃ¡c workspace thÃ´ng thÆ°á»ng cá»§a láº­p trÃ¬nh viÃªn.
     - Giá»¯ `WorkspaceGenerationLease` Ä‘á»ƒ phÃ¢n xá»­ thá»© tá»± ghi giá»¯a cÃ¡c Agent writer tuÃ¢n thá»§ protocol (khÃ´ng Ä‘áº¡i diá»‡n hay cáº¥m Ä‘oÃ¡n Ä‘Æ°á»£c thao tÃ¡c trá»±c tiáº¿p cá»§a User).
     - Thá»±c hiá»‡n CAS tá»«ng file ngay trÆ°á»›c khi ghi, ghi kÃ¨m durable undo/redo WAL cÃ³ `fencing_token`.
     - Cam káº¿t crash-recoverable, **khÃ´ng cam káº¿t atomic visibility** Ä‘á»‘i vá»›i quan sÃ¡t viÃªn bÃªn ngoÃ i.
     - **Báº£o tá»“n Dá»¯ liá»‡u NgÆ°á»i dÃ¹ng khi Recovery:** WAL undo chá»‰ Ä‘Æ°á»£c phÃ©p hoÃ n nguyÃªn khi tráº¡ng thÃ¡i hiá»‡n thá»i cá»§a file khá»›p chÃ­nh xÃ¡c vá»›i `expected_postimage` bao phá»§ toÃ n bá»™ footprint: `(object_identity, existence_state, content_digest, metadata_fingerprint, ACL_descriptor, xattr_hash, alternate_data_streams)`.
     - Náº¿u User Ä‘Ã£ sá»­a file lÃ m lá»‡ch footprint: Tuyá»‡t Ä‘á»‘i KHÃ”NG ghi Ä‘Ã¨ dá»¯ liá»‡u cá»§a User; giá»¯ nguyÃªn file hiá»‡n tráº¡ng, trÃ­ch xuáº¥t thay Ä‘á»•i cá»§a Agent thÃ nh `ConflictArtifact` bá»n vá»¯ng (`fsync`) vÃ  chuyá»ƒn phiÃªn sang `MERGE_CONFLICT_SUSPENDED`. Náº¿u khÃ´ng thá»ƒ ghi durable `ConflictArtifact`, há»‡ thá»‘ng giá»¯ cá» `RECOVERY_REQUIRED` vÃ  cháº·n Agent writer má»›i.

2. **Namespace Identity & KhÃ³a PhÃ¢n táº§ng TrÃ¡nh Lock Explosion:**
   - **Volume-Specific Comparison Semantics:** Loáº¡i bá» hÃ m chuá»—i chung nhÆ° `Path.lower()`. Namespace key báº¯t buá»™c dá»±a trÃªn handle Ä‘Ã£ xÃ¡c thá»±c `(workspace_root_identity, VolumeSerialNumber, FileId, workspace_generation)` vÃ  cÆ¡ cháº¿ so sÃ¡nh Ä‘áº·c thÃ¹ cá»§a volume/filesystem (NTFS Case-Preserving Case-Insensitive qua kernel uppercase table; Linux case-sensitive hoáº·c directory-level casefold).
   - **Hierarchical Intention Locking:** Thay vÃ¬ snapshot toÃ n bá»™ subtree handles gÃ¢y ná»• tÃ i nguyÃªn, há»‡ thá»‘ng dÃ¹ng Intent Lock phÃ¢n táº§ng (`IS` - Intent Shared, `IX` - Intent Exclusive) trÃªn cÃ¡c node tá»• tiÃªn káº¿t há»£p **Handle-Relative Traversal** (`openat` / `NtOpenFile`) vÃ  kiá»ƒm tra revalidation tÃ­nh toÃ n váº¹n cá»§a handle ngay trÆ°á»›c khi mutation.
   - **Ranh giá»›i Threat Model:** Handle identity phÃ¡t hiá»‡n vÃ  cháº·n TOCTOU giá»¯a cÃ¡c client tuÃ¢n thá»§ protocol trong threat model Ä‘Ã£ Ä‘á»‹nh nghÄ©a; khÃ´ng ngÄƒn cháº·n hÃ nh vi thay Ä‘á»•i cáº¥u trÃºc Ä‘Ä©a cá»§a cÃ¡c external actor ngoÃ i protocol.

3. **MÃ´ hÃ¬nh Há»£p nháº¥t PhÃ¢n táº§ng (Tiered Merge Model):**
   - **Táº§ng 1 (Auto-Apply):** Ãp dá»¥ng tá»± Ä‘á»™ng khi táº­p file thay Ä‘á»•i trong staging hoÃ n toÃ n khÃ´ng giao nhau vá»›i cÃ¡c thay Ä‘á»•i trÃªn workspace chÃ­nh tÃ­nh tá»« `base_workspace_generation`.
   - **Táº§ng 2 (Merge Proposal):** Khi cÃ³ thay Ä‘á»•i khÃ¡c dÃ²ng trÃªn cÃ¹ng file, cÃ´ng cá»¥ semantic merge chá»‰ sinh ra `MergeProposal` cÃ³ cáº¥u trÃºc (chá»©a diff, AST impact report vÃ  test validation evidence) Ä‘á»ƒ trÃ¬nh User, tuyá»‡t Ä‘á»‘i khÃ´ng tá»± Ã½ commit vÃ o workspace chÃ­nh.
   - **Táº§ng 3 (Mandatory Approval):** Khi thay Ä‘á»•i Ä‘á»¥ng vÃ o cÃ¹ng symbol/API contract, rename/delete, file generated hoáº·c file manifest phá»¥ thuá»™c (`pyproject.toml`, lockfiles) âž” Báº¯t buá»™c chuyá»ƒn sang `ASK_USER` kÃ¨m `MergeProposal`.
   - `ExecutionReceipt` lÆ°u trá»¯ Ä‘áº§y Ä‘á»§ `(base_digest, ours_digest, theirs_digest, result_digest, merger_version, validation_evidence)` vÃ  cÃ´ng bá»‘ minh báº¡ch residual risk ngá»¯ nghÄ©a.

---

### 4.2 Giao thá»©c Can thiá»‡p Thá»i gian thá»±c & Ngáº¯t Tiáº¿n trÃ¬nh An toÃ n
1. **MÃ¡y tráº¡ng thÃ¡i Can thiá»‡p Há»£p tÃ¡c (Cooperative Preemption State Machine):**
   - VÃ²ng Ä‘á»i: `REQUESTED â†’ ACKNOWLEDGED â†’ QUIESCING â†’ QUIESCED | CANNOT_CANCEL | OUTCOME_UNKNOWN`.
   - **`INTERRUPT_GRACEFUL`:** Äáº·t `graceful_timeout_ms`. Náº¿u quÃ¡ háº¡n mÃ  tool chÆ°a káº¿t thÃºc âž” phÃ¡t sá»± kiá»‡n `GRACEFUL_TIMEOUT_ESCALATING` Ä‘á»ƒ há»i User cÃ³ nÃ¢ng cáº¥p lÃªn ngáº¯t cÆ°á»¡ng bá»©c hay khÃ´ng.
   - **`INTERRUPT_ABORT_ACTION`:** Äá»‹nh danh chÃ­nh xÃ¡c lÃ  **Best-Effort Cancellation**, khÃ´ng cam káº¿t rollback external side-effect.
     - *TrÆ°á»›c `DISPATCHED`:* Há»§y bá» sáº¡ch, giáº£i phÃ³ng quota/lease vÃ  trá»Ÿ vá» tráº¡ng thÃ¡i an toÃ n.
     - *Sau `DISPATCHED`:* Gá»­i tÃ­n hiá»‡u kill tiáº¿n trÃ¬nh á»Ÿ M7 `isolation`, sau Ä‘Ã³ M7 gá»i `StatusProbeSpec` (vá»›i idempotency key). Náº¿u probe xÃ¡c nháº­n thÃ nh cÃ´ng âž” ghi nháº­n `TERMINAL_WITH_RECEIPT(SUCCEEDED)`; náº¿u probe xÃ¡c nháº­n chÆ°a cháº¡y âž” rollback WAL cá»¥c bá»™; náº¿u probe khÃ´ng xÃ¡c Ä‘á»‹nh Ä‘Æ°á»£c âž” chuyá»ƒn phiÃªn sang `HALTED_INDETERMINATE_SIDE_EFFECT`.
     - *Vá»›i LLM streaming:* M3 Ä‘Ã¡nh dáº¥u cÃ¡c token chÆ°a commit lÃ  `SUPERSEDED_IN_FLIGHT` vÃ  chá» ack há»§y tá»« provider adapter.

2. **Containment Admission Fail-Closed TrÆ°á»›c Khi Thá»±c Thi:**
   - Chá»‰ admit local execution khi containment profile Ä‘Æ°á»£c xÃ¡c minh trÆ°á»›c launch; náº¿u khÃ´ng Ä‘áº¡t, tá»« chá»‘i execution hoáº·c chuyá»ƒn thÃ nh external runner cÃ³ receipt riÃªng.
   - **TrÃªn Windows:** Tiáº¿n trÃ¬nh báº¯t buá»™c táº¡o á»Ÿ tráº¡ng thÃ¡i `CREATE_SUSPENDED`, gÃ¡n vÃ o Job Object Ä‘Æ°á»£c cáº¥u hÃ¬nh cáº¥m breakaway (bá» cá» `JOB_OBJECT_LIMIT_BREAKAWAY_OK`) vÃ  báº­t `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` trÆ°á»›c khi resume thread.
   - **TrÃªn Linux:** Khá»Ÿi táº¡o process cgroup chuyÃªn biá»‡t qua `clone3(CLONE_INTO_CGROUP)` hoáº·c launcher thÆ°á»ng trá»±c trong cgroup; tÆ°á»›c bá» Ä‘áº·c quyá»n `CAP_SYS_ADMIN` vÃ  cáº¥m sá»­a Ä‘á»•i `cgroup.procs`.
   - **Cháº·n Alternate Spawn Channels:** ChÃ­nh sÃ¡ch capability cá»§a M7 cáº¥m triá»‡t Ä‘á»ƒ viá»‡c tÆ°Æ¡ng tÃ¡c vá»›i cÃ¡c kÃªnh spawn giÃ¡n tiáº¿p (Windows WMI/RPC/Service Manager, D-Bus, container socket, systemd runner).
   - Náº¿u containment khÃ´ng thá»ƒ chá»©ng minh toÃ¡n há»c tÃ­nh kÃ­n cá»§a ranh giá»›i khi cÃ³ sá»± cá»‘ âž” Láº­p tá»©c chuyá»ƒn sang `HALTED_INDETERMINATE_SIDE_EFFECT`.

3. **TiÃªu chuáº©n Authoritative Cho Status Probe:**
   - Chá»‰ cháº¥p nháº­n tráº¡ng thÃ¡i `CONFIRMED_NOT_EXECUTED` khi cÃ³ receipt Ã¢m tÃ­nh cÃ³ tháº©m quyá»n (authoritative negative receipt) gáº¯n tá»‘i thiá»ƒu 4 chiá»u: `(provider_id, tenant_id, operation_id, idempotency_epoch)`.
   - Má»i káº¿t quáº£ timeout, khÃ´ng tÃ¬m tháº¥y hoáº·c chÆ°a Ä‘á»“ng bá»™ eventual consistency báº¯t buá»™c pháº£i lÃ  `PROBE_PENDING` hoáº·c `PROBE_AMBIGUOUS`.
   - WAL cá»¥c bá»™ reconcile Ä‘á»™c láº­p vá»›i external side-effect; khÃ´ng dÃ¹ng negative external receipt Ä‘á»ƒ suy diá»…n filesystem cá»¥c bá»™ Ä‘Ã£ sáº¡ch.

4. **Äiá»u hÆ°á»›ng Thá»i gian thá»±c (`STEER_IN_FLIGHT`):**
   - Append vÃ o `SessionControlLog` qua CAS trÃªn `expected_seq` vá»›i Ä‘áº§y Ä‘á»§: `directive_id, target_execution_epoch, target_step_id, authority, idempotency_key`.
   - M3 phÃ¢n xá»­: Náº¿u Ä‘áº¿n ká»‹p trÆ°á»›c dispatch epoch má»›i âž” tráº£ `SteeringReceipt(status=APPLIED)`; náº¿u bÆ°á»›c tiáº¿p theo Ä‘Ã£ dispatch âž” tráº£ `SteeringReceipt(status=DEFERRED | STALE)`.
   - KhÃ´ng há»“i tá»‘ hÃ nh Ä‘á»™ng Ä‘Ã£ dispatch; M4 tÃ¡i láº¯p rÃ¡p context theo chá»‰ Ä‘áº¡o cá»§a `SessionBudgetLedger` thuá»™c M3.

---

### 4.3 Ranh giá»›i IPC Hermetic cá»§a 2 Tiá»‡n Ã­ch Má»Ÿ rá»™ng (`extensions/`)
1. **`extensions/external_coding_tools` (AST/LSP Daemon):**
   - Daemon **tuyá»‡t Ä‘á»‘i khÃ´ng Ä‘á»c trá»±c tiáº¿p workspace sá»‘ng** Ä‘á»ƒ triá»‡t tiÃªu TOCTOU vÃ  quan sÃ¡t tráº¡ng thÃ¡i dá»Ÿ dang. M7 `isolation` cáº¥p **Read-Only Immutable CAS View / Snapshot** cho Daemon.
   - Cháº¡y trong sandbox khÃ´ng máº¡ng, khÃ´ng quyá»n ghi ra workspace (chá»‰ cÃ³ cache riÃªng cÃ³ quota, key theo snapshot digest).
   - Giao tiáº¿p qua Named Pipe / Domain Socket cÃ³: session authentication, version handshake, request timeout, backpressure, vÃ  schema validation.
   - ToÃ n bá»™ káº¿t quáº£ phÃ¢n tÃ­ch AST/LSP tráº£ vá» cho M6 Ä‘á»u mang nhÃ£n provenance/taint vÃ  Ä‘i qua DLP cá»§a M7 trÆ°á»›c khi Ä‘Æ°a vÃ o context.

2. **`extensions/outer_verification_harness` (Out-of-Tree CI Runner):**
   - M7 cáº¥p capability cÃ³ TTL Ä‘á»ƒ harness Ä‘á»c Immutable CAS Snapshot kÃ¨m `(test_plan_digest, lockfile_digest, toolchain_image_digest, network_policy_manifest)`.
   - Harness thá»±c thi sealed tests vÃ  táº¡o `AttestationReceipt` kÃ½ sá»‘ (chá»©a input/output/artifact digest, nonce, trust-root version).
   - **M7 lÃ  cá»•ng xÃ¡c minh duy nháº¥t:** M7 kiá»ƒm tra chá»¯ kÃ½ vÃ  tÃ­nh há»£p lá»‡ cá»§a Attestation, sau Ä‘Ã³ phÃ¡t `VerificationObservation` Ä‘Ã£ Ä‘Æ°á»£c xÃ¡c thá»±c sang M3. M3 tuyá»‡t Ä‘á»‘i khÃ´ng tá»± lÃ m cryptographic verifier.

---

### 4.4 Bounded-Pause Session Migration (Zero-Downtime Real-Time Upgrade)
1. **Äá»‹nh danh Semantics:** Chuáº©n hÃ³a lÃ  **Bounded-Pause Migration** (táº¡m dá»«ng cÃ³ giá»›i háº¡n thá»i gian táº¡i cá»­a sá»• cutover), khÃ´ng tuyÃªn bá»‘ zero-downtime tuyá»‡t Ä‘á»‘i.
2. **TiÃªu chuáº©n Safe Point ToÃ n Diá»‡n:** PhiÃªn chá»‰ Ä‘áº¡t Safe Point Ä‘á»ƒ báº¯t Ä‘áº§u cutover khi thá»a mÃ£n Ä‘á»“ng thá»i 3 Ä‘iá»u kiá»‡n:
   - KhÃ´ng cÃ²n báº¥t ká»³ tool, outbox message, hoáº·c status probe nÃ o á»Ÿ tráº¡ng thÃ¡i pending/unresolved.
   - KhÃ´ng cÃ³ báº¥t ká»³ workspace WAL hoáº·c recovery flow nÃ o Ä‘ang má»Ÿ (`RECOVERY_REQUIRED` = false).
   - KhÃ´ng cÃ²n báº¥t ká»³ registered callback nÃ o cÃ³ kháº£ nÄƒng phÃ¡t sinh side-effect.
3. **Quy trÃ¬nh Two-Phase Takeover:**
   - **Pha 1 (`PREPARE`):** Runtime má»›i shadow-fold log sá»± kiá»‡n tá»›i sequence `N` báº±ng pure deterministic upcasters khi runtime cÅ© váº«n Ä‘ang hoáº¡t Ä‘á»™ng.
   - **Pha 2 (`QUIESCE`):** YÃªu cáº§u runtime cÅ© dá»«ng phÃ¡t bÆ°á»›c má»›i táº¡i safe point. Náº¿u quÃ¡ deadline mÃ  chÆ°a Ä‘áº¡t safe point âž” chuyá»ƒn sang `MIGRATION_DEFERRED`, tuyá»‡t Ä‘á»‘i khÃ´ng cÆ°á»¡ng bá»©c takeover.
   - **Pha 3 (`CUTOVER`):** Runtime má»›i acquire `SessionOwnershipLease` má»›i, fence toÃ n bá»™ writer cÅ©, fold pháº§n delta `N+1...M`, cháº¡y dual-schema invariant checker vÃ  thá»±c hiá»‡n **CAS nguyÃªn tá»­ táº¡i sequence `M+1`**.
4. **NguyÃªn Tá»­ HÃ³a Cutover & TrÃ¡nh Crash Gap:**
   - `TakeoverEvent`, `new_schema_epoch`, vÃ  `compatibility_barrier` Ä‘Æ°á»£c Ä‘Ã³ng gÃ³i vÃ  ghi nguyÃªn tá»­ vÃ o `SessionControlLog` báº±ng **Má»˜T CAS duy nháº¥t táº¡i log sequence `M+1`**, loáº¡i bá» hoÃ n toÃ n khoáº£ng trá»‘ng crash gap.
   - Báº¯t buá»™c dÃ¹ng cÃ¹ng má»™t durable store cho Authoritative Epoch vÃ  `TakeoverEvent` (hoáº·c coordinator WAL 2PC vá»›i quy Ä‘á»‹nh participant khÃ´ng heuristic commit vÃ  M7 fail-closed trong má»i tráº¡ng thÃ¡i `PREPARED/IN_DOUBT`).
5. **M7 Capability Epoch Fencing & Xá»­ LÃ½ Stale Result Qua Quarantine Audit:**
   - M7 `isolation` vÃ  capability gate báº¯t buá»™c kiá»ƒm tra `(SessionOwnershipLease, fencing_token)` tuyáº¿n tÃ­nh táº¡i cáº£ lÃºc dispatch vÃ  lÃºc nháº­n káº¿t quáº£.
   - Má»i káº¿t quáº£ mang epoch cÅ© bá»‹ tá»« chá»‘i tiáº¿p nháº­n bá»Ÿi M3 control log nhÆ°ng **báº¯t buá»™c pháº£i ghi vÃ o `QuarantineAuditLog`**:
     - *Duplicate xÃ¡c minh Ä‘Æ°á»£c:* Deduplicate an toÃ n.
     - *Thao tÃ¡c Ä‘Ã£ cháº¡y trÃªn external service nhÆ°ng reconciliation chÆ°a xong:* Duy trÃ¬ probe/compensation workflow.
     - *KhÃ´ng xÃ¡c Ä‘á»‹nh Ä‘Æ°á»£c tÃ­nh an toÃ n:* Láº­p tá»©c kÃ­ch hoáº¡t `HALTED_INDETERMINATE_SIDE_EFFECT`.
   - Sau khi ghi sá»± kiá»‡n schema má»›i Ä‘áº§u tiÃªn, cáº¥m vÄ©nh viá»…n runtime cÅ© resume session nÃ y. Má»i approval cÅ© Ä‘á»u bá»‹ tÃ¡i kiá»ƒm tra tÃ­nh há»£p lá»‡ trÆ°á»›c khi Ä‘i tiáº¿p.


---

## 5. Háº¥p thá»¥ & Báº£n Ä‘á»‹a hÃ³a CÃ¡c TÃ­nh nÄƒng Äá»‰nh cao tá»« cÃ¡c AI Agent HÃ ng Ä‘áº§u (Phase 6 Consensus)

Nháº±m nÃ¢ng cao nÄƒng lá»±c giáº£i quyáº¿t tÃ¡c vá»¥ ká»¹ thuáº­t tÆ°Æ¡ng Ä‘Æ°Æ¡ng cÃ¡c há»‡ thá»‘ng thÆ°Æ¡ng máº¡i tiÃªn tiáº¿n nháº¥t (Claude Code, Devin, Cursor, Aider, LangGraph), 5 máº«u thiáº¿t káº¿ thá»±c chiáº¿n Ä‘á»‰nh cao Ä‘Ã£ Ä‘Æ°á»£c báº£n Ä‘á»‹a hÃ³a vÃ  tÃ­ch há»£p cháº·t cháº½ vÃ o Ä‘Ãºng 7 Module LÃµi:

### 5.1 Query-Biased Condensed Repo Map (Há»c tá»« Aider & Cursor âž” M4 `context_manager`)
1. **Luá»“ng Táº¡o & TiÃªu Thá»¥ Há»£p Nháº¥t (TuÃ¢n thá»§ DAG má»™t chiá»u):**
   - M3 gá»­i yÃªu cáº§u phÃ¢n tÃ­ch AST âž” M6 chuáº©n bá»‹ `ToolInvocationPlan` (pure data) âž” M7 cáº¥p Immutable CAS Snapshot vÃ  thá»±c thi hermetic daemon cá»§a `extensions/external_coding_tools` âž” M7 quÃ©t DLP âž” M6 giáº£i mÃ£ thÃ nh `RepoGraphArtifact` âž” M4 xáº¿p háº¡ng vÃ  láº¯p rÃ¡p vÃ o context.
   - M4 tuyá»‡t Ä‘á»‘i khÃ´ng tá»± gá»i extension hoáº·c network egress; M4 chá»‰ tiÃªu thá»¥ typed artifact.
2. **Äá»™ Bá»n Vá»¯ng & Minh Báº¡ch cá»§a Graph:**
   - `RepoGraphArtifact` gáº¯n cháº·t vá»›i `(workspace_snapshot_digest, graph_schema_version, parser_toolchain_digest)`.
   - Khai bÃ¡o rÃµ rÃ ng `(coverage_metrics, unknown_edges_ratio)` cho dynamic dispatch, reflection vÃ  generated code; khÃ´ng tuyÃªn bá»‘ graph pháº£n Ã¡nh 100% sá»± tháº­t.
3. **Canonical Arithmetic & Deterministic PageRank:**
   - Cam káº¿t má»©c Ä‘á»™ **`RANK_ORDER_DETERMINISTIC`**.
   - Thuáº­t toÃ¡n triá»ƒn khai theo Fixed-Point Arithmetic (Q16.16 hoáº·c Decimal Precision cá»‘ Ä‘á»‹nh 8 chá»¯ sá»‘) Ä‘á»ƒ triá»‡t tiÃªu sai sá»‘ trÃ´i ná»•i giá»¯a cÃ¡c CPU/trÃ¬nh biÃªn dá»‹ch khÃ¡c nhau; duyá»‡t graph theo Canonical Node Order (tá»« Ä‘iá»ƒn UTF-8) vÃ  sparse-matrix traversal báº¥t biáº¿n.
   - `SemanticScoreArtifact` (náº¿u dÃ¹ng embedding) báº¯t buá»™c pháº£i do M7 thá»±c thi trong sandbox (local model) hoáº·c qua M7 Egress Proxy cÃ³ kiá»ƒm tra DLP/secret-broker (remote model). Náº¿u cáº¥m egress vÃ  khÃ´ng cÃ³ local model âž” M4 tá»± Ä‘á»™ng háº¡ cáº¥p vá» **`STRUCTURAL_ONLY`** cÃ³ gáº¯n cá» minh báº¡ch trÃªn receipt.

---

### 5.2 Bounded Micro-Compaction & Semantic Lineage Preserving (Há»c tá»« Claude Code âž” M4 `context_manager`)
1. **Báº£o Tá»“n Báº±ng Chá»©ng Tuyá»‡t Äá»‘i (KhÃ´ng PhÃ¡ Há»§y Raw Output):**
   - Micro-compaction khÃ´ng lÃ m máº¥t kháº£ nÄƒng audit/replay. ToÃ n bá»™ raw tool outputs sau khi qua DLP cá»§a M7 Ä‘Æ°á»£c lÆ°u trá»¯ ngoÃ i context thÃ nh **`AuthoritativeObservationArtifact`** (mÃ£ hÃ³a tenant-scoped, gáº¯n khÃ³a báº±ng `randomized_blob_id + keyed_commitment`, tuÃ¢n thá»§ audit retention, khÃ´ng bá»‹ cache eviction).
   - `RehydratableLocalCache` (tÄƒng tá»‘c) cÃ³ TTL vÃ  cÃ³ thá»ƒ dá»n dáº¹p Ä‘á»™c láº­p.
2. **`CondensedObservationReceipt` Trong Context Window:**
   - Thay tháº¿ cÃ¡c khá»‘i output thÃ´ báº±ng receipt ngáº¯n gá»n chá»©a: `(raw_artifact_digest, tool_execution_receipt_id, extractor_version, exit_status, salient_facts, omitted_ranges, lineage_digest, rehydration_handle)`.
   - Chá»‰ Ä‘Æ°á»£c táº¡o sau khi sá»± kiá»‡n `ObservationCommitted` Ä‘Ã£ Ä‘Æ°á»£c append thÃ nh cÃ´ng vÃ o `SessionControlLog`.
   - Taint lineage vÃ  `context_influence_set` káº¿ thá»«a há»£p toÃ¡n há»c tá»« raw output, compaction khÃ´ng Ä‘Æ°á»£c tá»± Ã½ thu háº¹p taint.
3. **VÃ¹ng Cháº©n ÄoÃ¡n Báº£o Vá»‡ (`ProtectedDiagnosticSegment`):**
   - Lá»—i compiler, stack trace, assertion failures lÃ  dá»¯ liá»‡u `TAINTED`, tuyá»‡t Ä‘á»‘i khÃ´ng nÃ¢ng authority thÃ nh `Pinned Invariants`.
   - M4 cáº¥p háº¡n má»©c riÃªng (`diagnostic_token_quota`) chá»‰ giá»¯: `(failure_signature, exception_type, top_bottom_frames_max_3, source_location_ranges, assertion_expected_actual, raw_artifact_line_ref)`.
   - VÆ°á»£t quota âž” sinh `DiagnosticOverflowReceipt` cÃ³ rehydration handle; user approval chá»‰ tÄƒng quota cÃ³ giá»›i háº¡n chá»© khÃ´ng nÃ¢ng authority.

---

### 5.3 Hierarchical Goal-Tree & Checkpoint Time-Travel (Há»c tá»« Devin & LangGraph âž” M3 `orchestrator`)
1. **PhÃ¢n RÃ£ Káº¿ Hoáº¡ch Äa Chiá»u:**
   - TÃ¡ch biá»‡t rÃµ rÃ ng giá»¯a **`GoalTree`** (phÃ¢n rÃ£ má»¥c tiÃªu nghiá»‡p vá»¥: `Epic â†’ Task â†’ Subtask â†’ ActionStep`) vÃ  **`ExecutionDependencyDAG`** (rÃ ng buá»™c thá»© tá»± thá»±c thi vÃ  join synchronization).
2. **Time-Travel An ToÃ n (KhÃ´ng Ghi LÃ¹i Workspace Sá»‘ng):**
   - `SessionCheckpointId`: `(branch_id, log_seq, folded_state_digest, workspace_snapshot_digest, capability_epoch, budget_ledger_digest)`.
   - Khi ráº½ nhÃ¡nh (`PlanBranchFork`), M7 `isolation` materialize snapshot quÃ¡ khá»© thÃ nh má»™t **`BranchShadowWorkspace` hoÃ n toÃ n má»›i**; workspace chÃ­nh tuyá»‡t Ä‘á»‘i khÃ´ng bá»‹ ghi lÃ¹i vÃ  chá»‰ thay Ä‘á»•i tiáº¿n vá» phÃ­a trÆ°á»›c qua publication CAS.
   - Branch má»›i nháº­n `capability_epoch` má»›i, `budget_escrow` Ä‘á»™c láº­p, vÃ´ hiá»‡u hÃ³a User approvals cÅ©, vÃ  Ä‘Ã¡nh dáº¥u toÃ n bá»™ external side-effect trÆ°á»›c fork point lÃ  `NON_REVERSIBLE_ANCESTOR` (chá»‰ xá»­ lÃ½ báº±ng compensation).
   - Táº¡i má»™t thá»i Ä‘iá»ƒm chá»‰ cÃ³ 1 branch `ACTIVE`; cÃ¡c branch khÃ¡c lÃ  `ARCHIVED | CANDIDATE`.

---

### 5.4 Language-Aware Fuzzy Patch Codec (Há»c tá»« Aider âž” M6 `tool_manager` & M7 `runtime_governance`)
1. **PhÃ¢n Quyá»n RÃµ RÃ ng M1 - M6 - M7:**
   - M3/M6 quyáº¿t Ä‘á»‹nh `EditProtocol` (`SEARCH_REPLACE_BLOCK`, `UNIFIED_DIFF`, `WHOLE_FILE`); M1 chá»‰ serialize/negotiate theo Ä‘Ãºng protocol Ä‘Ã³.
   - M6 chá»‰ parse LLM output thÃ nh `PatchIntent` (pure data structures); M7 `transaction` phá»¥ trÃ¡ch write gate, CAS vÃ  apply patch vÃ o `BranchShadowWorkspace` do M7 `isolation` materialize.
2. **`LanguageEditPolicy` Kháº¯t Khe:**
   - Cáº¥m hoÃ n toÃ n fuzzy whitespace/indentation repair Ä‘á»‘i vá»›i cÃ¡c ngÃ´n ngá»¯ nháº¡y cáº£m khoáº£ng tráº¯ng (`Python`, `YAML`, `Makefile`, `Nim`) trá»« khi cÃ³ AST re-verification xÃ¡c nháº­n block structure khÃ´ng Ä‘á»•i.
   - File nhá»‹ phÃ¢n, minified, hoáº·c generated: Cáº¥m LLM whole-file máº·c Ä‘á»‹nh. File generated báº¯t buá»™c sá»­a source rá»“i regenerate; binary/unknown báº¯t buá»™c dÃ¹ng specialized byte-tool hoáº·c `ASK_USER`.
3. **Thang Báº­c Fuzzy Fail-Closed:**
   - Chá»‰ auto-apply khi cÃ³ DUY NHáº¤T 1 candidate thá»a mÃ£n ngÆ°á»¡ng chiá»u dÃ i/entropy vÃ  khÃ´ng cáº¯t qua symbol boundary. CÃ³ 0 hoáº·c $\ge 2$ candidates âž” Tráº£ `AMBIGUOUS_PATCH` Ä‘á»ƒ M3 replan.
   - Sinh `PatchApplicationReceipt` ghi rÃµ normalization Ä‘Ã£ dÃ¹ng, candidate span vÃ  post-apply AST verification.

---

### 5.5 Two-Phase Sealed Verification Gate & `CandidateChangeManifest` (Há»c tá»« Devin / SWE-bench âž” M7 `runtime_governance`)
1. **Nguá»“n Sá»± Tháº­t Duy Nháº¥t: `CandidateChangeManifest` (Thay Tháº¿ Git Diff):**
   - Git diff chá»‰ lÃ  view trÃ¬nh bÃ y cho Human/LLM; **`CandidateChangeManifest` do M7 `transaction` tÃ­nh toÃ¡n trá»±c tiáº¿p** giá»¯a `base_snapshot_digest` vÃ  `BranchShadowWorkspace` má»›i lÃ  Nguá»“n Sá»± tháº­t Duy nháº¥t cho verification vÃ  publication.
   - Bao phá»§ toÃ n diá»‡n: `(operation, tracked/untracked, content_digest, file_type, executable_bit, ACL_metadata, symlink_target, submodule_gitlink, generated_provenance)`.
   - Äá»‘i chiáº¿u tá»©c thÃ¬ vá»›i `AuthorizedWriteSet`; phÃ¡t hiá»‡n file láº¡ ngoÃ i táº­p cho phÃ©p âž” Há»§y candidate ngay láº­p tá»©c (`POLICY_VIOLATION_ABORTED`).
2. **Quy TrÃ¬nh Chá»n Impacted-Test Hai Pha (Two-Phase Impact Selection):**
   - *Pha 1 (`PreImplementationTestPlan`):* Sinh tá»« intended write set vÃ  khÃ³a (sealed) trÆ°á»›c khi sá»­a code.
   - *Pha 2 (`PostImplementationImpactPlan`):* Sinh tá»« `CandidateChangeManifest.digest` tháº­t sá»± sau khi sá»­a.
   - *Táº­p Test Cuá»‘i:* $\text{FinalTests} = \text{ReproductionTest} \cup \text{PrePlanSubset} \cup \text{PostImpactSubset} \cup \text{MandatorySecuritySmokeTests}$.
   - Selector manifest Ä‘Æ°á»£c M7 xÃ¡c minh hoáº·c outer harness kÃ½ attestation; Agent cáº¥m tá»± kÃ½.
3. **CÆ¡ Cháº¿ Fail-Closed Sang Full Test Suite:**
   - Báº¯t buá»™c cháº¡y 100% Full Test Suite khi: graph coverage < 80%, cÃ³ `unknown_dynamic_impact`, cháº¡m vÃ o dependencies/build configs (`pyproject.toml`, lockfiles), hoáº·c cháº¡m vÃ o `HighRiskWorkspaceSinks`.
4. **Structured Reproduction & Regression Enforcement:**
   - `ReproductionSpec` khÃ³a báº±ng CAS: test script ghim báº¥t biáº¿n, baseline pháº£i váº¥p pháº£i Ä‘Ãºng `expected_failure_signature` cÃ³ cáº¥u trÃºc (cháº·n lá»—i infrastructure/timeout).
   - Ãp dá»¥ng chÃ­nh sÃ¡ch `NO_NEW_REGRESSIONS` so vá»›i baseline; flaky test báº¯t buá»™c pháº£i cÃ³ Operator Waiver cÃ³ tháº©m quyá»n vÃ  expiry.
