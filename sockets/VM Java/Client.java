import java.io.*;
import java.net.*;

public class Client {
    // initialize socket and input output streams
    private Socket s = null;
    private DataInputStream input = null;
    private DataOutputStream out = null;
private InputStreamReader streamReader = null;
 
    // constructor to put ip address and port
    public Client(String address, int port)
    {
        // establish a connection
        try {
            s = new Socket(address, port);
            System.out.println("Connected");
 
            // takes input from terminal
            input = new DataInputStream(System.in);
 
            // sends output to the socket
            out = new DataOutputStream(
                s.getOutputStream());
		streamReader = new InputStreamReader(s.getInputStream());
        }
        catch (UnknownHostException u) {
            System.out.println(u);
            return;
        }
        catch (IOException i) {
            System.out.println(i);
            return;
        }
 
        // string to read message from input
        String line = "";
 
    
        BufferedReader reader = new BufferedReader(streamReader);
        // keep reading until "Over" is input
        while (!line.equals("Over")) {
            try {
                line = input.readLine();
                out.writeUTF(line);

        String responseMessage = reader.readLine();
        System.out.println(responseMessage);

            }
            catch (IOException i) {
                System.out.println(i);
            }
        }
 
        // close the connection
        try {
            input.close();
            out.close();
            s.close();
        }
        catch (IOException i) {
            System.out.println(i);
        }
    }

}