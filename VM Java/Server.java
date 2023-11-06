import java.net.*;
import java.io.*;
 
public class Server
{
    //initialize socket and input stream
    private Socket          socket   = null;
    private ServerSocket    server   = null;
    private DataInputStream in       =  null;
 
    // constructor with port
    public Server(int port)
    {
        // starts server and waits for a connection
        try
        {
            server = new ServerSocket(port);
            System.out.println("Server started");
 
            System.out.println("Waiting for a client ...");
 
            socket = server.accept();
            System.out.println("Client accepted");
 
            // takes input from the client socket
            in = new DataInputStream(
                new BufferedInputStream(socket.getInputStream()));
	    	PrintWriter writer = new PrintWriter(socket.getOutputStream()); 
            String line = "";
 
            // reads message from client until "Over" is sent
            while (!line.equals("Over"))
            {
                try
                {
                    line = in.readUTF();
                    System.out.println(line);
	String nstr = "";
      for (int i=0; i<line.length(); i++)
      {
        char ch= line.charAt(i); //extracts each character
        nstr= ch+nstr; //adds each character in front of the existing string
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
 
            // close connection
            // writer.close();
            socket.close();
            in.close();
        }
        catch(IOException i)
        {
            System.out.println(i);
        }
    }

}