# 🧠 Mô tả cách hoạt động của thuật toán (chi tiết)

Tài liệu này giải thích **bằng lời** cách các thuật toán AI trong dự án hoạt động. Mục tiêu là dễ đọc, dễ kể lại, và hiểu được “vì sao Ghost đi như vậy” trong từng tình huống.

---

## 📑 Mục lục

1. [Tổng quan](#-tổng-quan)
2. [Mê cung và cách biểu diễn](#-mê-cung-và-cách-biểu-diễn)
3. [DFS — Tạo mê cung](#-1-dfs--tạo-mê-cung)
4. [BFS — Tìm đường theo chiều rộng](#-2-bfs--tìm-đường-theo-chiều-rộng)
5. [A\* — Tìm đường có định hướng](#-3-a--tìm-đường-có-định-hướng)
6. [GBFS — Tìm đường tham lam](#-4-gbfs--tìm-đường-tham-lam)
7. [Dijkstra — Tìm đường theo chi phí](#-5-dijkstra--tìm-đường-theo-chi-phí)
8. [So sánh 4 thuật toán tìm đường](#-so-sánh-4-thuật-toán-tìm-đường)
9. [5 hành vi của Ghost (Behavior)](#-5-hành-vi-của-ghost-behavior)
10. [Ghost quyết định nước đi mỗi frame](#-ghost-quyết-định-nước-đi-mỗi-frame)
11. [Xem minh hoạ trực quan](#-xem-minh-hoạ-trực-quan)

---

## 🌐 Tổng quan

Trong dự án có 2 nhóm thuật toán:

- **Tạo mê cung**: dùng **DFS (Randomized DFS / Recursive Backtracking)**. Chạy 1 lần khi khởi tạo map.
- **Tìm đường cho Ghost**: mỗi frame Ghost cần tìm đường tới “mục tiêu”. Có 4 lựa chọn: **BFS, A\*, GBFS, Dijkstra**.

Ngoài thuật toán tìm đường, mỗi Ghost có một **hành vi (behavior)** để quyết định **mục tiêu (target)**. Có thể hiểu đơn giản:

> **Hành vi chọn đích** (target) + **thuật toán tìm đường** (path) ⇒ Ghost di chuyển.

---

## 🧩 Mê cung và cách biểu diễn

Để hiểu thuật toán tìm đường, cần hiểu dự án đang coi mê cung là gì.

### 1) Lưới ô (grid)

- Map được xem như một **lưới** gồm các ô (cell).
- Mỗi ô có trạng thái: **tường** hoặc **đường đi**.
- Ghost và Pacman chỉ được đứng trên ô “đường đi”.

### 2) Di chuyển hợp lệ

- Mỗi bước, Ghost/Pacman chỉ đi theo **4 hướng**: lên, xuống, trái, phải.
- Một bước chỉ hợp lệ nếu ô tiếp theo **không phải tường** và nằm trong biên map.

### 3) “Explored” và “Path” là gì?

Khi chạy thuật toán, ta thường ghi lại hai thứ để minh hoạ:

- **explored**: tập các ô mà thuật toán đã “mở”/đã xét.
- **path**: đường đi cuối cùng (một danh sách các ô) từ vị trí xuất phát tới target.

Đường đi thường được dựng lại nhờ một bảng “truy vết” (thường gọi là `came_from`): mỗi ô sẽ nhớ “mình đi tới đây từ ô nào”. Khi đến đích, ta lần ngược lại để ra path.

### 4) Nếu không có đường thì sao?

Trong mê cung hợp lệ thường luôn có đường, nhưng về mặt thuật toán:

- Nếu mục tiêu bị bao kín bởi tường hoặc nằm ngoài vùng có thể tới, thuật toán sẽ duyệt hết khả năng rồi kết luận **không có path**.
- Khi đó Ghost có thể đứng yên hoặc chuyển sang hành vi khác tuỳ cách triển khai.

---

## 🏗️ 1. DFS — Tạo mê cung

DFS trong dự án dùng để **tạo map**, không phải để Ghost “tìm đường đuổi”.

### DFS tạo mê cung làm gì?

Ý tưởng là tạo ra một hệ thống hành lang liên thông bằng cách “đào đường” theo kiểu đi sâu:

1. Chọn một ô bắt đầu.
2. Từ ô hiện tại, nhìn các ô lân cận “chưa thăm” (thường theo các bước cách nhau để đảm bảo có tường ngăn).
3. Chọn **ngẫu nhiên** một hướng, phá tường và đi sang ô mới.
4. Nếu bị ngõ cụt, quay lại ô trước đó và thử hướng khác.
5. Lặp đến khi thăm hết.

### Vì sao DFS tạo nhiều ngõ cụt?

Vì DFS luôn ưu tiên “đi sâu một mạch” nên nó tạo ra các nhánh dài. Khi quay đầu (backtrack), nó mới rẽ nhánh khác. Kết quả có nhiều đoạn cụt dài — tạo cảm giác mê cung rõ rệt.

### Vì sao dự án phá thêm tường?

Mê cung DFS “thuần” thường chỉ có 1 đường chính giữa hai điểm, ít đường tắt. Dự án phá thêm một phần tường (ví dụ 15%) để:

- giảm cảm giác bị “khóa cứng” trong ngõ cụt,
- tạo nhiều lựa chọn cho người chơi,
- khiến thuật toán tìm đường của Ghost có nhiều phương án cạnh tranh hơn.

---

## 🔵 2. BFS — Tìm đường theo chiều rộng

BFS tìm đường bằng cách mở rộng dần ra xung quanh từ điểm xuất phát.

### BFS chạy như thế nào (từng bước)

1. Bắt đầu từ ô xuất phát (vị trí Ghost).
2. Đưa ô này vào hàng đợi.
3. Lấy lần lượt từng ô ra khỏi hàng đợi, rồi đẩy các ô kề hợp lệ (chưa thăm) vào cuối hàng.
4. Khi gặp được ô mục tiêu, dừng lại và dựng lại path bằng `came_from`.

### Vì sao BFS luôn ra đường ngắn nhất?

Vì BFS thăm theo lớp khoảng cách: nó thăm tất cả ô cách 1 bước trước, rồi tới 2 bước, 3 bước… nên lần đầu chạm target chắc chắn là số bước ít nhất.

### Điểm mạnh / điểm yếu trong game

- Mạnh: đường đi ngắn, ổn định, dễ dự đoán.
- Yếu: thường duyệt nhiều ô, có thể tốn thời gian hơn A\* trong map lớn.

---

## 🟢 3. A\* — Tìm đường có định hướng

A\* là lựa chọn “tổng quát tốt” trong game vì nó vừa nhanh vừa thường ra đường tối ưu.

### Trực giác của A\*

Khi đứng ở một ô, A\* không chỉ hỏi “đi sang ô nào được”, mà còn ước lượng “đi sang ô đó thì có vẻ gần mục tiêu hơn không”.

Trong dự án, ước lượng này dùng **khoảng cách Manhattan** (đi ngang + đi dọc trên lưới 4 hướng). Manhattan phù hợp vì Ghost/Pacman không đi chéo.

### A\* ưu tiên ô nào?

A\* ưu tiên ô có “tổng điểm” nhỏ: vừa không đi vòng quá xa so với xuất phát, vừa tiến gần mục tiêu. Vì vậy A\* thường:

- ít duyệt các nhánh “đi ngược hướng mục tiêu”,
- tập trung vào hành lang hướng về phía target,
- nhanh hơn BFS/Dijkstra trong đa số tình huống.

### Tình huống A\* thể hiện rõ lợi thế

Nếu target ở xa và mê cung có nhiều ngã rẽ, BFS/Dijkstra sẽ loang rộng. A\* sẽ sớm dồn lực về phía target nên số ô explored thường ít hơn đáng kể.

---

## 🟣 4. GBFS — Tìm đường tham lam

GBFS (Greedy Best-First Search) ưu tiên “tiến gần mục tiêu” càng nhanh càng tốt.

### GBFS khác A\* ở đâu?

- A\* vừa quan tâm quãng đường đã đi (tránh đi vòng), vừa quan tâm tới mục tiêu.
- GBFS gần như **chỉ** quan tâm tới mục tiêu: ô nào “có vẻ gần target hơn” thì được ưu tiên.

### Vì sao GBFS có thể đi vòng?

Trong mê cung, “gần mục tiêu theo đường thẳng” không đồng nghĩa “gần mục tiêu theo đường có thể đi”. Nếu có bức tường lớn chắn ngang, GBFS có thể tiến về phía tường cho tới khi buộc phải vòng, khiến path dài.

### Khi nào nên dùng GBFS trong game?

- Khi cần phản hồi rất nhanh và chấp nhận đường đi không tối ưu.
- Khi map không quá phức tạp hoặc khi hành vi khiến target thay đổi liên tục (cần thuật toán nhẹ).

---

## 🟠 5. Dijkstra — Tìm đường theo chi phí

Dijkstra mở rộng giống BFS nhưng dựa trên “chi phí tích lũy”.

### Dijkstra hữu ích khi nào?

Nếu mỗi ô hoặc mỗi bước đi có chi phí khác nhau (ví dụ ô nguy hiểm, ô chậm, ô bẫy…), Dijkstra sẽ chọn đường có tổng chi phí nhỏ nhất.

### Trong dự án hiện tại

Hiện tại mỗi bước đi có chi phí như nhau (mỗi bước = 1). Trong trường hợp này:

- BFS và Dijkstra thường cho path có độ dài tương tự.
- Dijkstra vẫn là lựa chọn tốt để minh hoạ/để mở rộng sau này.

---

## 📊 So sánh 4 thuật toán tìm đường

| Tiêu chí | BFS | A\* | GBFS | Dijkstra |
|:---------|:---:|:---:|:----:|:--------:|
| Đảm bảo đường ngắn nhất? | ✅ | ✅ | ❌ | ✅ |
| Có định hướng về phía mục tiêu? | ❌ | ✅ | ✅ | ❌ |
| Số ô thường phải duyệt | Nhiều | Ít | Rất ít | Nhiều |
| Ổn định trong mê cung khó | ✅ | ✅ | ⚠️ | ✅ |
| Gợi ý dùng trong game | Dễ hiểu | **Tổng quát tốt** | Phản hồi nhanh | Map có chi phí |

Gợi ý nhanh:

- Nếu chọn 1 thuật toán “đi đâu cũng ổn”: **A\***.
- Nếu cần nhanh nhất, chấp nhận đôi lúc đi vòng: **GBFS**.
- Nếu muốn đơn giản và luôn tối ưu theo số bước: **BFS**.
- Nếu về sau có trọng số/chi phí khác nhau: **Dijkstra**.

---

## 👻 5 hành vi của Ghost (Behavior)

Hành vi quyết định **mục tiêu** mà Ghost hướng tới. Cùng thuật toán nhưng đổi hành vi ⇒ target đổi ⇒ đường đi đổi.

Để hành vi chạy ổn định, mục tiêu thường cần:

- nằm trong map,
- ưu tiên rơi vào ô “đường đi” (nếu rơi vào tường có thể cần điều chỉnh/“clamp” sang ô hợp lệ gần nhất),
- thay đổi theo thời gian (ví dụ Patrol, Random) hoặc theo trạng thái Pacman (Chase, Predict, Flank).

### 🔴 Chase — Đuổi thẳng

- **Mục tiêu**: vị trí hiện tại của Pacman.
- **Cảm giác chơi**: bị bám sát, áp lực liên tục.
- **Khi kết hợp tốt**: với A\* hoặc BFS để Ghost bám rất “chặt”.

### 🩷 Predict — Chặn đầu

- **Mục tiêu**: một điểm ở phía trước Pacman vài ô theo hướng đang đi.
- **Cảm giác chơi**: dễ bị “đón đầu”, nhất là khi chạy hành lang thẳng.
- **Lưu ý**: nếu Pacman đang sát tường/biên map thì target có thể bị đẩy ra ngoài; cần giới hạn target trong vùng hợp lệ.

### 🩵 Flank — Đánh sau

- **Mục tiêu**: một điểm phía sau Pacman vài ô (ngược hướng di chuyển).
- **Cảm giác chơi**: bị ép hướng di chuyển, đặc biệt khi có thêm một Ghost Chase.
- **Ý nghĩa chiến thuật**: tạo tình huống “kẹp” (một con đuổi, một con chặn đường lui).

### 🟠 Patrol — Tuần tra

- **Mục tiêu**: thay đổi theo chu kỳ (ví dụ đi 4 góc theo thứ tự).
- **Cảm giác chơi**: tạo “vùng nguy hiểm” cố định, buộc người chơi tính đường tránh.
- **Lưu ý**: hành vi này thường không cần thuật toán quá nhanh, vì mục tiêu ít thay đổi theo Pacman.

### 🎲 Random — Ngẫu nhiên

- **Mục tiêu**: một ô bất kỳ (hoặc một mục tiêu ngẫu nhiên theo thời gian).
- **Cảm giác chơi**: khó đoán, đôi lúc tạo tình huống bất ngờ.
- **Lưu ý**: để so sánh công bằng giữa các thuật toán trong notebook/GIF, thường cần cố định seed ngẫu nhiên để các thuật toán nhận cùng một target.

---

## ⚙️ Ghost quyết định nước đi mỗi frame

Mỗi frame, mỗi Ghost thường làm 4 bước:

1. **Tính mục tiêu (target)** theo hành vi.
2. **Tìm đường** từ vị trí Ghost đến target bằng một trong 4 thuật toán.
3. **Chọn bước kế tiếp**: lấy ô đầu tiên của path (hoặc nếu path rỗng thì đứng yên/đổi hướng tuỳ triển khai).
4. **Di chuyển**.

### Vì sao phải tính lại liên tục?

Vì Pacman di chuyển liên tục (và có thể đổi hướng bất kỳ lúc nào). Nếu Ghost giữ nguyên path cũ quá lâu, nó sẽ đuổi theo “đích cũ” và trở nên kém thông minh. Do đó nhiều game/đồ án sẽ tính lại thường xuyên (mỗi frame hoặc mỗi vài frame).

### Ví dụ minh hoạ (mô tả)

Giả sử Ghost đang ở góc phải trên, Pacman ở phía trái:

- Với **Chase**, target luôn là vị trí Pacman ⇒ Ghost bám sát.
- Với **Predict**, target nằm trước mặt Pacman ⇒ Ghost có xu hướng lao tới “đầu đường” mà Pacman sắp chạy qua.
- Với **Flank**, target nằm sau Pacman ⇒ Ghost thường vòng để cắt đường lùi.

---

## 📌 Xem minh hoạ trực quan

- Notebook so sánh: [`algorithm_comparison.ipynb`](algorithm_comparison.ipynb)
- GIF demo: thư mục [`demos/`](demos/)
