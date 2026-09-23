package socketclientserver;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

/**
 * Chương trình SERVER cơ bản.
 *
 * Server sẽ:
 *  1. Mở một "cổng lắng nghe" (ServerSocket) trên máy của mình.
 *  2. Chờ (accept) cho tới khi có 1 Client kết nối tới.
 *  3. Đọc từng dòng văn bản Client gửi lên, in ra màn hình.
 *  4. Trả lời lại Client (viết hoa nội dung nhận được).
 *  5. Khi Client gõ "bye" thì đóng kết nối và server dừng lại.
 */
public class Server {

    // Cổng (port) mà server sẽ lắng nghe. Có thể chọn số bất kỳ từ 1024-65535.
    private static final int PORT = 12345;

    public static void main(String[] args) {
        System.out.println("[SERVER] Đang khởi động, lắng nghe ở cổng " + PORT + " ...");

        // try-with-resources: ServerSocket sẽ tự động được đóng khi kết thúc khối try
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {

            System.out.println("[SERVER] Sẵn sàng. Đang chờ Client kết nối...");

            // accept() sẽ "đứng chờ" (blocking) cho tới khi có client kết nối tới
            try (Socket clientSocket = serverSocket.accept()) {

                System.out.println("[SERVER] Đã có Client kết nối từ: "
                        + clientSocket.getInetAddress() + ":" + clientSocket.getPort());

                // Luồng đọc dữ liệu Client gửi tới (Client -> Server)
                BufferedReader in = new BufferedReader(
                        new InputStreamReader(clientSocket.getInputStream(), StandardCharsets.UTF_8));

                // Luồng ghi dữ liệu để gửi cho Client (Server -> Client)
                // autoFlush = true để dữ liệu được gửi đi ngay sau mỗi lần println()
                PrintWriter out = new PrintWriter(
                        new OutputStreamWriter(clientSocket.getOutputStream(), StandardCharsets.UTF_8), true);

                String line;
                // readLine() sẽ chờ cho tới khi nhận được 1 dòng dữ liệu, hoặc trả về null nếu Client ngắt kết nối
                while ((line = in.readLine()) != null) {
                    System.out.println("[SERVER] Nhận được: " + line);

                    if ("bye".equalsIgnoreCase(line.trim())) {
                        out.println("Server: Tạm biệt!");
                        break;
                    }

                    String response = "Server đã nhận: " + line.toUpperCase();
                    out.println(response);
                }
            }

            System.out.println("[SERVER] Client đã ngắt kết nối. Server dừng lại.");

        } catch (IOException e) {
            System.err.println("[SERVER] Lỗi: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
