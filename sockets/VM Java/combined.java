import java.io.*;
import java.net.*;



// Client 


public class Client {
    private Socket s = null;
    private DataInputStream input = null;
    private DataOutputStream out = null;
private InputStreamReader streamReader = null;
 

    public Client(String address, int port)
    {

        try {
            s = new Socket(address, port);
            System.out.println("Connected");

            input = new DataInputStream(System.in);
 
  
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
 

        String line = "";
 
    
        BufferedReader reader = new BufferedReader(streamReader);

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

public class Tcp {
 
    public static void main(String args[])
    {
        Client client = new Client("127.0.0.1", 5000);
    }
}

// Server

public class Server
{

    private Socket          socket   = null;
    private ServerSocket    server   = null;
    private DataInputStream in       =  null;

    public Server(int port)
    {

        try
        {
            server = new ServerSocket(port);
            System.out.println("Server started");
 
            System.out.println("Waiting for a client ...");
 
            socket = server.accept();
            System.out.println("Client accepted");

            in = new DataInputStream(
                new BufferedInputStream(socket.getInputStream()));
	    	PrintWriter writer = new PrintWriter(socket.getOutputStream()); 
            String line = "";
 

            while (!line.equals("Over"))
            {
                try
                {
                    line = in.readUTF();
                    System.out.println(line);
	String nstr = "";
      for (int i=0; i<line.length(); i++)
      {
        char ch= line.charAt(i); 
        nstr= ch+nstr;
      }
            			String response = "Response : " + nstr;
           	 writer.println(response);
			writer.flush();
 
                }
                catch(IOException i)
                {
System.out.println("Shit exception only");
                    System.out.println(i);
                }
            }
            System.out.println("Closing connection");
 

            socket.close();
            in.close();
        }
        catch(IOException i)
        {
            System.out.println(i);
        }
    }

}


public class Run
{
 
    public static void main(String args[])
    {
        Server server = new Server(5000);
    }
}