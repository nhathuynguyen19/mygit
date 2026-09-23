# Socket Server (project riêng)

Đây là project **Server** trong cặp bài tập Socket Client - Server, tách thành
2 project độc lập:

- `socket-server` (project này) — chứa `Server.java`
- `socket-client` (project riêng bên cạnh) — chứa `Client.java`

Cả 2 giao tiếp với nhau qua TCP Socket ở cổng `12345`. Đây là 2 project Java
**hoàn toàn tách biệt** (có thể mở bằng 2 cửa sổ NetBeans khác nhau, hoặc 2
tab terminal Zed khác nhau).

## Cấu trúc project

```
socket-server/
└── src/
    └── socketserver/
        └── Server.java
```

## Server hoạt động thế nào

```java
ServerSocket serverSocket = new ServerSocket(PORT);   // mở cổng lắng nghe (12345)
Socket clientSocket = serverSocket.accept();          // chờ 1 client tới (blocking)
```

- `in.readLine()` → đọc 1 dòng dữ liệu Client gửi lên.
- `out.println(...)` → gửi phản hồi (viết hoa nội dung nhận được).
- Đây là bản đơn giản: chỉ xử lý **1 client** rồi dừng. Muốn phục vụ nhiều
  client cùng lúc thì cần thêm Thread (xem mục "Hướng mở rộng" cuối file).

> **Quan trọng:** hằng số `PORT` trong `Server.java` phải **trùng** với
> `SERVER_PORT` trong `Client.java` bên project `socket-client`.

## Compile & chạy

### Linux / macOS

```bash
cd socket-server
mkdir -p out
javac -d out src/socketserver/*.java
cd out
java socketserver.Server
```

### Windows (CMD / PowerShell)

```powershell
cd socket-server
mkdir out
javac -d out src\socketserver\*.java
cd out
java socketserver.Server
```

**Luôn chạy Server trước**, sau đó mới chạy Client (ở project `socket-client`)
— vì `accept()` cần Server đã lắng nghe sẵn thì Client mới kết nối được.

## Tạo project trong Apache NetBeans IDE 12.2

1. **File → New Project...** → chọn **Java with Ant** → **Java Application** → Next
2. Đặt **Project Name**: `SocketServer`, chọn **Project Location** tùy ý,
   **bỏ chọn "Create Main Class"** → **Finish**
3. Chuột phải **Source Packages** → **New → Java Package...** → đặt tên
   `socketserver` → Finish
4. Chuột phải package `socketserver` → **New → Java Class...** → đặt tên
   `Server` → Finish. Copy nội dung từ `src/socketserver/Server.java` (trong
   repo này) dán đè vào.
5. Chuột phải `Server.java` → **Run File** (`Shift+F6`) để chạy.

> Mở project `socket-client` bằng **một cửa sổ NetBeans khác** (hoặc instance
> NetBeans thứ 2) để chạy song song Server và Client — xem README trong project
> `socket-client` để biết chi tiết.

## Chạy thật giữa 2 máy khác nhau

1. Trên máy chạy Server, tìm địa chỉ IP: `ip addr` (Linux) hoặc `ipconfig`
   (Windows).
2. Bên project `socket-client`, sửa `SERVER_HOST` thành IP đó (thay vì
   `127.0.0.1`).
3. Windows: cho phép Firewall cho `java.exe` hoặc mở cổng 12345 (Windows
   Defender Firewall → Allow an app).
4. Linux: nếu dùng `ufw`: `sudo ufw allow 12345/tcp`.

## Hướng mở rộng

- **Xử lý nhiều client cùng lúc**: đổi vòng lặp thành
  `while (true) { Socket s = serverSocket.accept(); new Thread(() -> handle(s)).start(); }`
  để mỗi client chạy trên 1 thread riêng, không phải chờ client trước đóng
  kết nối mới nhận client sau.
- **Giao thức có cấu trúc hơn**: dùng JSON thay vì text thô.
