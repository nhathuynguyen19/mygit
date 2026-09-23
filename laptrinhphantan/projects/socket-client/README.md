# Socket Client (project riêng)

Đây là project **Client** trong cặp bài tập Socket Client - Server, tách thành
2 project độc lập:

- `socket-client` (project này) — chứa `Client.java`
- `socket-server` (project riêng bên cạnh) — chứa `Server.java`

Cả 2 giao tiếp với nhau qua TCP Socket ở cổng `12345`. Đây là 2 project Java
**hoàn toàn tách biệt** (có thể mở bằng 2 cửa sổ NetBeans khác nhau, hoặc 2
tab terminal Zed khác nhau).

## Cấu trúc project

```
socket-client/
└── src/
    └── socketclient/
        └── Client.java
```

## Client hoạt động thế nào

```java
Socket socket = new Socket(SERVER_HOST, SERVER_PORT);  // kết nối tới server
```

- Đọc input người dùng gõ từ bàn phím (`System.in`), gửi qua `out.println(message)`.
- Đọc phản hồi từ Server qua `in.readLine()`.
- Gõ `bye` để thoát.

> **Quan trọng:** `SERVER_HOST` / `SERVER_PORT` trong `Client.java` phải trỏ
> đúng tới địa chỉ và cổng mà `Server.java` (project `socket-server`) đang
> lắng nghe.

## Compile & chạy

**Server phải được chạy trước** (xem README trong project `socket-server`),
sau đó mới chạy Client.

### Linux / macOS

```bash
cd socket-client
mkdir -p out
javac -d out src/socketclient/*.java
cd out
java socketclient.Client
```

### Windows (CMD / PowerShell)

```powershell
cd socket-client
mkdir out
javac -d out src\socketclient\*.java
cd out
java socketclient.Client
```

Gõ vài dòng tin nhắn, xem Server nhận và trả lời (viết hoa nội dung). Gõ `bye`
để đóng kết nối và dừng cả 2 chương trình.

## Tạo project trong Apache NetBeans IDE 12.2

1. **File → New Project...** → chọn **Java with Ant** → **Java Application** → Next
2. Đặt **Project Name**: `SocketClient`, chọn **Project Location** tùy ý,
   **bỏ chọn "Create Main Class"** → **Finish**
3. Chuột phải **Source Packages** → **New → Java Package...** → đặt tên
   `socketclient` → Finish
4. Chuột phải package `socketclient` → **New → Java Class...** → đặt tên
   `Client` → Finish. Copy nội dung từ `src/socketclient/Client.java` (trong
   repo này) dán đè vào.
5. Chuột phải `Client.java` → **Run File** (`Shift+F6`) để chạy.

> Vì Client cần nhập liệu tương tác qua bàn phím (`System.in`), hãy dùng đúng
> cửa sổ **Output** mà NetBeans mở ra cho `Client.java` để gõ tin nhắn.

### Chạy song song 2 project trong NetBeans

NetBeans 12.2 cho phép mở nhiều project cùng lúc trong 1 cửa sổ (**File → Open
Project...** rồi chọn cả `SocketServer` lẫn `SocketClient`, cả 2 sẽ hiện trong
cây **Projects**). Bạn chỉ cần:

1. Chuột phải `Server.java` (project `SocketServer`) → **Run File**
2. Chuột phải `Client.java` (project `SocketClient`) → **Run File**

Mỗi lần "Run File" sẽ mở 1 tab Output riêng, cho phép cả 2 chạy song song và
gõ tương tác độc lập.

## Chạy thật giữa 2 máy khác nhau

1. Trên máy chạy Server, tìm địa chỉ IP: `ip addr` (Linux) hoặc `ipconfig`
   (Windows).
2. Sửa `SERVER_HOST` trong `Client.java` thành IP đó (thay vì `127.0.0.1`).
3. Windows: cho phép Firewall cho `java.exe` hoặc mở cổng 12345 (Windows
   Defender Firewall → Allow an app).
4. Linux: nếu dùng `ufw`: `sudo ufw allow 12345/tcp`.

## Hướng mở rộng

- **Vòng lặp chat liên tục** thay vì thoát sau mỗi phiên (đã có sẵn ở bản
  này — client giữ kết nối cho tới khi gõ `bye`).
- **Giao diện đồ họa (GUI)** — dùng Swing/JavaFX thay vì console.
- **Kết nối lại tự động** nếu Server bị mất kết nối giữa chừng.
