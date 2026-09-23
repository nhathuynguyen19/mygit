package socketclient;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;

/**
 * Chương trình CLIENT cơ bản (project riêng: socket-client).
 *
 * Client sẽ:
 *  1. Kết nối (Socket) tới địa chỉ IP + cổng của Server.
 *  2. Đọc dữ liệu người dùng gõ từ bàn phím.
 *  3. Gửi dữ liệu đó cho Server.
 *  4. Nhận và in ra phản hồi từ Server.
 *  5. Gõ "bye" để kết thúc.
 */
public class Client {

    // Nếu Server chạy trên cùng máy: dùng "127.0.0.1" hoặc "localhost".
    // Nếu Server chạy trên máy khác trong mạng LAN: thay bằng địa chỉ IP của máy đó, ví dụ "192.168.1.10".
    private static final String SERVER_HOST = "127.0.0.1";

    // Phải TRÙNG với PORT bên project socket-server.
    private static final int SERVER_PORT = 12345;

    public static void main(String[] args) {
        System.out.println("[CLIENT] Đang kết nối tới " + SERVER_HOST + ":" + SERVER_PORT + " ...");

        try (Socket socket = new Socket(SERVER_HOST, SERVER_PORT)) {

            System.out.println("[CLIENT] Đã kết nối thành công tới Server!");

            // Luồng gửi dữ liệu cho Server (Client -> Server)
            PrintWriter out = new PrintWriter(
                    new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8), true);

            // Luồng nhận dữ liệu từ Server (Server -> Client)
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));

            // Luồng đọc dữ liệu người dùng gõ từ bàn phím
            BufferedReader userInput = new BufferedReader(
                    new InputStreamReader(System.in));

            String message;
            while (true) {
                System.out.print("Nhập tin nhắn (gõ 'bye' để thoát): ");
                message = userInput.readLine();
                if (message == null) {
                    break;
                }

                out.println(message);

                String response = in.readLine();
                System.out.println("[CLIENT] Server trả lời: " + response);

                if ("bye".equalsIgnoreCase(message.trim())) {
                    break;
                }
            }

        } catch (UnknownHostException e) {
            System.err.println("[CLIENT] Không tìm thấy địa chỉ Server: " + e.getMessage());
        } catch (IOException e) {
            System.err.println("[CLIENT] Lỗi kết nối tới Server: " + e.getMessage());
            System.err.println("[CLIENT] Kiểm tra xem Server đã chạy chưa, và đúng địa chỉ/cổng chưa.");
        }

        System.out.println("[CLIENT] Đã đóng kết nối.");
    }
}
