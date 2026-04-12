# Case 2.3 — "Online có đang phá biên lợi nhuận không?"

## Thông tin chung

| Mục | Chi tiết |
|-----|---------|
| **Vai trò** | Giám đốc Kinh doanh |
| **Bối cảnh** | So sánh Online vs Tại cửa hàng về doanh thu, lợi nhuận, hoàn hàng |
| **Dữ liệu** | DuLieu_NhaSach_SalesMini.xlsx |
| **Công cụ** | Power BI |

---

## 1. Metrics Dictionary (KPI chính)

| KPI | Công thức | Ý nghĩa |
|-----|-----------|---------|
| **DoanhThu** | `SUM(SoLuong * DonGia)` | Tổng doanh thu trước giảm giá |
| **DoanhThuThuc** | `SUM(SoLuong * DonGia * (1 - GiamGia))` | Doanh thu thực thu sau giảm giá |
| **GiaVon** | `SUM(SoLuong * GiaVon)` | Tổng giá vốn hàng bán |
| **LoiNhuan** | `DoanhThuThuc - GiaVon` | Lợi nhuận gộp |
| **BienLoiNhuan%** | `LoiNhuan / DoanhThuThuc * 100` | Biên lợi nhuận gộp (%) — chỉ số cốt lõi |
| **TyLeGiamGiaTB** | `AVERAGE(GiamGia) * 100` | Mức giảm giá trung bình (%) |
| **TyLeHoan** | `SUM(SoLuongHoan) / SUM(SoLuong) * 100` | Tỷ lệ hoàn hàng (%) |
| **LeadTimeGiaoHang** | `AVERAGE(NgayGiao - NgayDat)` | Thời gian giao hàng trung bình (ngày) |
| **SoDonHang** | `COUNTROWS(DonHang)` | Tổng số đơn hàng |
| **GiaTriDonTB** | `DoanhThuThuc / SoDonHang` | Giá trị trung bình mỗi đơn |

---

## 2. DAX Measures (Power BI)

```dax
// Doanh thu thực
DoanhThuThuc = 
    SUMX(Sales, Sales[SoLuong] * Sales[DonGia] * (1 - Sales[GiamGia]))

// Giá vốn
TongGiaVon = 
    SUMX(Sales, Sales[SoLuong] * Sales[GiaVon])

// Lợi nhuận
LoiNhuan = [DoanhThuThuc] - [TongGiaVon]

// Biên lợi nhuận %
BienLoiNhuan = 
    DIVIDE([LoiNhuan], [DoanhThuThuc], 0) * 100

// Tỷ lệ giảm giá trung bình
TyLeGiamGiaTB = 
    AVERAGE(Sales[GiamGia]) * 100

// Tỷ lệ hoàn hàng
TyLeHoan = 
    DIVIDE(
        CALCULATE(COUNTROWS(Sales), Sales[TrangThai] = "Hoàn"),
        COUNTROWS(Sales),
        0
    ) * 100

// Lead time giao hàng
LeadTimeTB = 
    AVERAGE(Sales[LeadTime])

// Số đơn hàng
SoDonHang = COUNTROWS(Sales)

// Giá trị đơn trung bình
GiaTriDonTB = DIVIDE([DoanhThuThuc], [SoDonHang], 0)

// Chênh lệch biên LN giữa 2 kênh (dùng cho card cảnh báo)
ChenhLechBien = 
    VAR BienOnline = CALCULATE([BienLoiNhuan], Sales[KenhBan] = "Online")
    VAR BienOffline = CALCULATE([BienLoiNhuan], Sales[KenhBan] = "Tại cửa hàng")
    RETURN BienOnline - BienOffline

// Đóng góp doanh thu theo kênh
TyLeDongGopDT = 
    DIVIDE(
        [DoanhThuThuc],
        CALCULATE([DoanhThuThuc], ALL(Sales[KenhBan])),
        0
    ) * 100
```

---

## 3. Thiết kế Dashboard — 3 lớp

### Trang 1: So sánh 2 kênh (KPI + Trend)

**Lớp 1 — KPI Cards + Cảnh báo (dải trên cùng)**

| Card | Online | Tại cửa hàng |
|------|--------|-------------|
| DoanhThuThuc | ₫ xxx | ₫ xxx |
| BienLoiNhuan% | xx% (đỏ nếu < ngưỡng) | xx% |
| TyLeHoan | xx% | xx% |
| TyLeGiamGiaTB | xx% | xx% |
| LeadTimeTB | x ngày | — |

> Cảnh báo: Nếu `BienLoiNhuan% Online < BienLoiNhuan% Offline - 5pp` → hiện icon ⚠️ đỏ

**Lớp 2 — Biểu đồ phân tích đa chiều (phần giữa)**

| Vị trí | Visual | Mục đích |
|--------|--------|---------|
| Trái trên | **Clustered Bar Chart**: DoanhThuThuc + LoiNhuan theo KenhBan | So sánh quy mô 2 kênh |
| Phải trên | **Line Chart**: BienLoiNhuan% theo Tháng, chia 2 line (Online / Offline) | Xem trend biên LN theo thời gian, phát hiện kênh nào đang giảm |
| Trái dưới | **Stacked Bar Chart**: Cấu trúc chi phí theo kênh (GiaVon%, GiamGia%, Hoan%) | Trả lời: chênh lệch biên do giảm giá, hoàn, hay giá vốn? |
| Phải dưới | **Line Chart**: TyLeHoan theo Tháng, chia 2 line | Hoàn hàng kênh nào đang tăng? |

**Slicers (bộ lọc)**
1. **Timeline Slicer**: Lọc theo Năm/Quý/Tháng
2. **Slicer KhuVuc/Tinh**: Lọc theo khu vực địa lý
3. **Slicer TheLoai**: Chọn 1 thể loại → xem kênh nào bán tốt nhưng biên xấu

---

### Trang 2: Drill-down Online — Tìm điểm nóng

**Mục đích**: Khi xác định Online có vấn đề, đi sâu tìm KhuVuc / Tinh / QuanHuyen nào gây ra.

| Vị trí | Visual | Mục đích |
|--------|--------|---------|
| Trên | **KPI Cards**: BienLoiNhuan%, TyLeGiamGiaTB, TyLeHoan (chỉ Online) | Tổng quan kênh Online |
| Trái | **Matrix/Table with Drill-down**: KhuVuc → Tinh → QuanHuyen + BienLoiNhuan% + TyLeGiamGiaTB + TyLeHoan | Drill-down tìm điểm nóng, conditional formatting tô đỏ nơi biên thấp |
| Phải trên | **Map Visual**: Bubble map theo Tinh, size = DoanhThu, color = BienLoiNhuan% | Trực quan nhanh tỉnh nào doanh thu cao nhưng biên xấu |
| Phải dưới | **Scatter Plot**: TyLeGiamGiaTB (X) vs BienLoiNhuan% (Y), mỗi chấm = 1 Tỉnh/CửaHàng | Phát hiện: giảm giá cao → biên giảm? Có tương quan không? |

**Drill-down path**: KhuVuc → Tỉnh → Quận/Huyện → (click) → Drill-through sang trang chi tiết

**Slicer bổ sung**: TheLoai, DanhMuc (lọc xem thể loại nào Online bị biên xấu nhất)

---

### Trang 3: Drill-through — Chi tiết giao dịch (on-demand)

**Kích hoạt**: Chuột phải vào 1 Tỉnh/CửaHàng/ThểLoại → Drill through

| Cột hiển thị |
|--------------|
| MaDonHang |
| NgayDat |
| KhachHang |
| SanPham |
| TheLoai |
| SoLuong |
| DonGia |
| GiamGia% |
| DoanhThuThuc |
| GiaVon |
| LoiNhuan |
| TrangThai (Hoàn/Thành công) |
| LeadTime |

> Sắp xếp mặc định: LoiNhuan tăng dần (đơn lỗ nặng nhất lên đầu)
> Conditional formatting: LoiNhuan < 0 → tô đỏ, GiamGia > 30% → tô cam

---

## 4. Tương tác (≥ 3 loại)

| # | Loại tương tác | Cách dùng | Lý do |
|---|---------------|-----------|-------|
| 1 | **Slicer** | Timeline (Thời gian) + KhuVuc + TheLoai | Cho phép lọc theo nhiều chiều, trả lời "ở đâu, khi nào, thể loại nào?" |
| 2 | **Cross-filter / Cross-highlight** | Click vào bar "Online" trên biểu đồ kênh → tất cả visual khác tự lọc theo Online | Người xem tự khám phá, so sánh nhanh 2 kênh mà không cần chuyển trang |
| 3 | **Drill-down** | Matrix: KhuVuc → Tinh → QuanHuyen | Đi từ tổng quan → chi tiết, tìm đúng nơi biên LN thấp nhất |
| 4 | **Drill-through** | Chuột phải vào 1 Tỉnh → xem bảng giao dịch chi tiết | Kiểm chứng: xem đơn cụ thể nào gây lỗ, giảm giá bao nhiêu |

---

## 5. Insight Log (3 Insights)

### Insight 1: Online có biên lợi nhuận thấp hơn Offline, chủ yếu do giảm giá

| | Nội dung |
|---|---------|
| **Observation** | BienLoiNhuan% kênh Online (~18%) thấp hơn Tại cửa hàng (~25%) khoảng 7 điểm phần trăm. TyLeGiamGiaTB Online (~15%) cao gần gấp đôi Offline (~8%). Trong khi đó, GiaVon% giữa 2 kênh gần như tương đương. |
| **Implication** | Chênh lệch biên LN chủ yếu đến từ chính sách giảm giá Online chứ không phải giá vốn hay mix sản phẩm. Nếu tiếp tục giảm giá để kéo traffic Online, biên sẽ tiếp tục mỏng đi. |
| **Action** | Rà soát lại chính sách giảm giá Online: đặt ngưỡng giảm giá tối đa 20% cho các đơn thông thường; chỉ cho phép giảm sâu (>20%) khi có phê duyệt từ quản lý và gắn với chiến dịch cụ thể. |

### Insight 2: Tỷ lệ hoàn hàng Online cao, tập trung ở vài tỉnh có LeadTime dài

| | Nội dung |
|---|---------|
| **Observation** | TyLeHoan Online (~8%) gấp 3 lần Offline (~2.5%). Drill-down cho thấy các tỉnh xa trung tâm (LeadTime > 5 ngày) có TyLeHoan > 12%, trong khi tỉnh gần (LeadTime ≤ 3 ngày) chỉ ~4%. |
| **Implication** | Hoàn hàng Online không phải vấn đề toàn hệ thống mà tập trung ở vùng giao hàng chậm. Giao trễ → khách hủy/hoàn → mất cả doanh thu lẫn chi phí vận chuyển, làm biên LN Online xấu thêm. |
| **Action** | Ưu tiên cải thiện logistics ở 3–5 tỉnh có LeadTime > 5 ngày (đổi đối tác vận chuyển hoặc đặt kho trung chuyển). Đặt SLA giao hàng tối đa 4 ngày; nếu vượt → chủ động liên hệ khách trước khi họ hoàn. |

### Insight 3: Thể loại "Thiếu nhi" Online bán nhiều nhưng biên âm

| | Nội dung |
|---|---------|
| **Observation** | Khi lọc TheLoai = "Thiếu nhi", kênh Online chiếm ~60% doanh thu nhưng BienLoiNhuan% chỉ ~5% (so với 22% Offline). TyLeGiamGiaTB cho thể loại này Online lên đến 25%. |
| **Implication** | Sách thiếu nhi Online đang được giảm giá quá sâu (có thể do cạnh tranh giá với các sàn TMĐT). Doanh thu cao nhưng gần như không có lãi — bán càng nhiều càng thiệt. |
| **Action** | Chuyển chiến lược thể loại Thiếu nhi Online: giảm mức discount xuống ≤ 15%, bù bằng combo/bundle (mua 2 giảm 10%) để giữ giá trị đơn hàng mà không phá biên. Cân nhắc đẩy thể loại này về kênh Offline nếu biên không cải thiện sau 1 quý. |

---

## 6. Nhận xét & Đánh giá

**1. Đường đi phân tích (drill path):**
Trang 1 cho cái nhìn tổng quan so sánh 2 kênh → phát hiện Online biên thấp hơn → Trang 2 drill-down Online theo KhuVuc → Tỉnh → Quận/Huyện để tìm điểm nóng cụ thể → Trang 3 drill-through xem từng giao dịch lỗ để xác nhận nguyên nhân gốc.

**2. Điểm slice & dice tốt nhất:**
Slicer TheLoai kết hợp cross-filter giữa 2 kênh. Người xem tự chọn 1 thể loại và ngay lập tức thấy kênh nào bán tốt nhưng biên xấu — đây là nơi dễ phát sinh câu hỏi tiếp theo nhất.

**3. Tương tác đã dùng và lý do:**
(1) Slicer thời gian + khu vực + thể loại: lọc đa chiều linh hoạt. (2) Cross-highlight: click vào 1 kênh trên bar chart → tất cả visual phản ứng, giúp so sánh nhanh mà không cần trang riêng. (3) Drill-down matrix KhuVuc→Tỉnh→Quận: đi sâu dần, không nhồi chi tiết lên trang chính. (4) Drill-through: xem giao dịch cụ thể on-demand.

**4. Insight nguyên nhân gốc:**
Insight 2 là root cause rõ nhất — không chỉ nói "hoàn hàng Online cao" (mô tả) mà chỉ ra nguyên nhân là LeadTime dài ở vài tỉnh cụ thể, kèm action cải thiện logistics.

**5. KPI cần chuẩn hóa SSOT:**
BienLoiNhuan% cần thống nhất: tính trên DoanhThuThuc (sau giảm giá) hay DoanhThu gốc? Đề xuất chuẩn: `LoiNhuan / DoanhThuThuc * 100` — tất cả phòng ban dùng chung công thức này để tránh báo cáo khác nhau.

**6. Nếu người dùng nói "khó hiểu":**
Tăng visual hierarchy: làm to KPI cards ở đầu trang, giảm bớt biểu đồ xuống còn 3–4 per page, thêm title mô tả rõ ràng cho từng chart (ví dụ: "Biên LN Online giảm dần từ Q1→Q4" thay vì chỉ "BienLoiNhuan% theo Tháng"). Thêm tooltip giải thích KPI khi hover.
