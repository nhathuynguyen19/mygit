# Socket Client - Server cơ bản (Java)

Dự án học tập: lập trình Socket TCP Client - Server cơ bản bằng Java thuần
(không dùng thư viện ngoài), chạy được trên cả **Windows** và **Linux**.

## 1. Khái niệm cốt lõi

| Thành phần | Vai trò |
|---|---|
| `ServerSocket` | Bên Server dùng để **mở một cổng** và "lắng nghe" client kết nối tới |
| `Socket` | Đại diện cho **1 kết nối** cụ thể — cả Server lẫn Client đều dùng `Socket` để đọc/ghi dữ liệu sau khi đã kết nối |
| `InputStream` / `OutputStream` | Luồng byte thô để gửi/nhận dữ liệu qua mạng |
| `BufferedReader` + `PrintWriter` | Bọc lên trên stream thô để đọc/ghi theo **dòng text** cho dễ dùng |

Quy trình hoạt động (TCP):

1. Server tạo `ServerSocket(PORT)` và gọi `accept()` — lệnh này sẽ "đứng chờ" (blocking)
   cho tới khi có Client kết nối tới.
2. Client tạo `Socket(host, port)` để kết nối tới Server.
3. Sau khi kết nối thành công, cả 2 bên đọc/ghi dữ liệu qua `Socket` của mình.
4. Gõ `bye` để đóng kết nối và kết thúc chương trình.

**Về đa nền tảng:** Java (JVM) vốn "write once, run anywhere" — API `java.net.Socket` /
`ServerSocket` giống hệt nhau trên mọi hệ điều hành, không cần code gì đặc biệt.
Chỉ có lệnh compile/run trong terminal là hơi khác cú pháp giữa Windows và Linux
(xem phần 4).

## 2. Cấu trúc project

```
socket-client-server/
└── src/
    └── socketclientserver/
        ├── Server.java
        └── Client.java
```

Cấu trúc này theo kiểu **NetBeans Java Application cổ điển** (thư mục `src` là
source root, các class nằm trong package `socketclientserver`), nên có thể mở
trực tiếp bằng NetBeans hoặc build tay bằng `javac`/`java` trong terminal (Zed).

## 3. Đọc hiểu code

### `Server.java`

```java
ServerSocket serverSocket = new ServerSocket(PORT);   // mở cổng lắng nghe
Socket clientSocket = serverSocket.accept();          // chờ 1 client tới (blocking)
```

- `in.readLine()` → đọc 1 dòng dữ liệu Client gửi lên (chờ tới khi có dữ liệu).
- `out.println(...)` → gửi phản hồi (dùng `autoFlush = true` nên không cần gọi
  `flush()` thủ công).
- Đây là phiên bản đơn giản nhất: server chỉ xử lý **1 client** rồi dừng. Xem
  phần "Hướng mở rộng" bên dưới để nâng cấp thành xử lý nhiều client.

### `Client.java`

```java
Socket socket = new Socket(SERVER_HOST, SERVER_PORT);  // kết nối tới server
```

- Đọc input người dùng gõ từ bàn phím (`System.in`), gửi qua `out.println(message)`.
- Đọc phản hồi từ Server qua `in.readLine()`.
- Gõ `bye` để thoát.

## 4. Compile & chạy bằng terminal

### Trên Linux / macOS

```bash
cd socket-client-server
mkdir -p out
javac -d out src/socketclientserver/*.java
```

> Lưu ý: `javac -d out` **không tự tạo thư mục `out`** nếu nó chưa tồn tại (lệnh
> `mkdir -p out` sẽ báo lỗi `directory not found: out` nếu bạn quên bước này).
> `javac` chỉ tự tạo các thư mục con theo package (ví dụ `out/socketclientserver/`).

Mở 2 terminal (nhớ `cd` đúng vào thư mục `socket-client-server` trước, vì
đường dẫn `out` ở trên là tương đối):

```bash
# Terminal 1 - chạy Server
cd socket-client-server/out
java socketclientserver.Server
```

```bash
# Terminal 2 - chạy Client
cd socket-client-server/out
java socketclientserver.Client
```

### Trên Windows (CMD hoặc PowerShell)

```powershell
cd socket-client-server
mkdir out
javac -d out src\socketclientserver\*.java
```

```powershell
# Cửa sổ 1 - chạy Server
cd socket-client-server\out
java socketclientserver.Server
```

```powershell
# Cửa sổ 2 - chạy Client
cd socket-client-server\out
java socketclientserver.Client
```

> Khác biệt duy nhất giữa 2 hệ điều hành là dấu `/` với `\` trong đường dẫn, và
> dấu phân tách classpath `:` (Linux) với `;` (Windows) khi project có nhiều
> thư viện `.jar` — với project đơn giản này thì không cần quan tâm.

Gõ vài dòng tin nhắn ở Client, xem Server nhận và trả lời (viết hoa nội dung).
Gõ `bye` ở Client để đóng kết nối và dừng cả 2 chương trình.

## 5. Tạo / mở project trong Apache NetBeans IDE 12.2

**Cách 1 — Tạo project mới rồi copy code vào:**

1. Mở NetBeans → **File → New Project...**
2. Chọn **Java with Ant** → **Java Application** → **Next**
3. Điền:
   - **Project Name**: `SocketClientServer`
   - **Project Location**: thư mục cha (nơi bạn muốn NetBeans tạo `nbproject/`)
   - Bỏ chọn **"Create Main Class"** (vì sẽ tự tạo 2 class riêng)
   - Bấm **Finish**
4. Chuột phải vào **Source Packages** → **New → Java Package...** → đặt tên
   `socketclientserver` → **Finish**
5. Chuột phải vào package `socketclientserver` → **New → Java Class...** → đặt
   tên `Server` → **Finish**. Copy nội dung từ `src/socketclientserver/Server.java`
   (trong repo này) dán đè vào.
6. Lặp lại bước 5 để tạo class `Client`, dán nội dung từ `Client.java`.
7. **Chạy Server**: chuột phải vào `Server.java` → **Run File** (`Shift+F6`).
8. **Chạy Client**: chuột phải vào `Client.java` → **Run File** (`Shift+F6`) —
   NetBeans sẽ mở tab Output riêng, cho phép chạy song song và gõ tương tác ở
   từng tab.

**Cách 2 — Mở trực tiếp thư mục này bằng NetBeans:**

Nếu NetBeans không tự nhận diện thư mục `socket-client-server` (vì thiếu file
cấu hình `nbproject/`), dùng Cách 1 nhưng đặt **Project Location** là thư mục
cha của `socket-client-server`, sau đó copy 2 file `.java` vào package như trên.
Cả 2 cách cho ra cùng kết quả chạy được.

## 6. Chạy thật giữa 2 máy / 2 hệ điều hành khác nhau

- Nếu Client và Server chạy **cùng 1 máy**: giữ nguyên `127.0.0.1`.
- Nếu chạy **2 máy khác nhau trong cùng mạng LAN** (ví dụ Server trên Linux,
  Client trên Windows):
  1. Trên máy chạy Server, tìm địa chỉ IP bằng `ip addr` (Linux) hoặc
     `ipconfig` (Windows).
  2. Sửa hằng số `SERVER_HOST` trong `Client.java` thành IP đó, ví dụ
     `"192.168.1.15"`.
  3. Trên Windows, có thể cần cho phép Firewall cho `java.exe` hoặc mở cổng
     12345 (Windows Defender Firewall → Allow an app).
  4. Trên Linux, nếu dùng `ufw`: `sudo ufw allow 12345/tcp`.

## 7. Hướng mở rộng tiếp theo

1. **Server xử lý nhiều client cùng lúc** — dùng vòng lặp
   `while (true) { accept(); new Thread(...).start(); }` để mỗi client được
   xử lý trên 1 thread riêng.
2. **Giao thức có cấu trúc hơn** — dùng JSON hoặc định dạng riêng thay vì text
   thô.
3. **Giao diện đồ họa (GUI)** — dùng Swing/JavaFX thay vì console.
