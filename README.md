# PACMAN KEY HUNT - AI Edition

Game Pacman kết hợp mê cung ngẫu nhiên và trí tuệ nhân tạo. Ghost sử dụng các thuật toán tìm đường AI để truy đuổi người chơi. Được phát triển cho môn học Nhập môn Trí tuệ nhân tạo tại Đại học Bách Khoa Hà Nội.

## Luật chơi

- Điều khiển **Pacman** bằng phím mũi tên
- Thu thập **3 chìa khóa** (Vàng, Xanh, Đỏ) rải trong mê cung
- Đến **cửa EXIT** (góc dưới-phải) sau khi có đủ chìa khóa để chiến thắng
- Tránh bị **Ghost** bắt — Ghost dùng AI tìm đường đuổi theo bạn

## Tính năng

- Mê cung ngẫu nhiên mỗi lần chơi (DFS generation + phá tường tạo nhiều đường đi)
- Tùy chỉnh kích thước bản đồ (8-28 × 6-18) và số ghost (1-4)
- Cấu hình AI cho từng ghost riêng biệt:
  - **3 thuật toán tìm đường**: BFS, A\*, DFS
  - **5 hành vi**: Chase, Predict, Flank, Random, Patrol
  - **Tốc độ**: 5-40 (tùy chỉnh mỗi ghost)
- 15 tổ hợp AI khác nhau (3 algorithm × 5 behavior)

## Thuật toán AI áp dụng

### Thuật toán tìm đường (Pathfinding)

| Thuật toán | Mô tả |
|-----------|-------|
| **BFS** (Breadth-First Search) | Tìm đường ngắn nhất, ghost đi tối ưu |
| **A\*** (A-Star Search) | Dùng heuristic Manhattan distance, hiệu quả hơn BFS |
| **DFS** (Depth-First Search) | Đường đi không dự đoán được, random shuffle hướng đi |

### Hành vi Ghost (Behavior)

| Hành vi | Mô tả |
|---------|-------|
| **Chase** | Đuổi thẳng đến vị trí Pacman (Blinky) |
| **Predict** | Nhắm 2 ô phía trước theo hướng Pacman đang đi (Pinky) |
| **Flank** | Chặn 3 ô phía sau Pacman, tạo thế gọng kìm (Inky) |
| **Patrol** | Tuần tra 4 góc bản đồ theo vòng lặp |
| **Random** | Di chuyển ngẫu nhiên, 70% giữ hướng cũ |

### Tạo mê cung (Maze Generation)

- **Randomized DFS** (Recursive Backtracking): Tạo mê cung cơ bản
- **Extra Path Removal**: Phá thêm 15-20% tường để tạo nhiều đường đi

## Cài đặt

1. Clone repository:

```bash
git clone https://github.com/Sper-il/Pacman-v2.git
cd Pacman-v2
```

2. Cài đặt thư viện:

```bash
pip install pygame
```

## Cách sử dụng

1. Chạy game:

```bash
python src/main.py
```

2. Điều khiển:
   - **Phím mũi tên**: Di chuyển Pacman
   - **Menu**: Chỉnh Map Size, số Ghost, nhấn PLAY GAME
   - **Ghost Settings**: Chỉnh Speed / Algorithm / Behavior cho từng ghost

## Cấu trúc dự án

```
Pacman-v2/
├── src/
│   ├── main.py           # Game loop, UI, event handling
│   ├── cell.py           # Ghost AI, Pacman, Cell classes
│   ├── config.py         # Hằng số cấu hình
│   ├── utils.py          # Hàm tiện ích mê cung
│   └── search/           # Thuật toán giải mê cung (legacy demo)
│       ├── bfs.py
│       └── dfs.py
├── images/
│   ├── logo.png
│   └── logo1.png
├── .gitignore
└── README.md
```

## Công nghệ sử dụng

- Python 3.x
- Pygame

## Tác giả

- Tạ Hồng Phúc ([@andrew-taphuc](https://github.com/andrew-taphuc))
- Nguyễn Mạnh Tùng ([@nmtun](https://github.com/nmtun))
- Bùi Quang Hưng ([@Gnuhq26](https://github.com/Gnuhq26))
- Nguyễn Đức Quang ([@ndquang21](https://github.com/ndquang21))

Sinh viên ngành CNTT Việt - Nhật, Đại học Bách Khoa Hà Nội

## Giấy phép

Dự án này được phát triển cho mục đích học tập và nghiên cứu.
