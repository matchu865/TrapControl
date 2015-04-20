package com.example.mattreat.trapclient;

import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;

import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.StringReader;
import java.net.Socket;
import java.net.UnknownHostException;

import android.os.AsyncTask;

//Document stuff
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import java.io.StringReader;

import javax.xml.parsers.ParserConfigurationException;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;
import org.w3c.dom.CharacterData;
import org.xml.sax.SAXException;



public class MainActivity extends ActionBarActivity {

    private static final String TAG = "MainActivity";

    //Server to connect to
    protected static final int TRAPCLIENT_PORT = 8000;
    protected static final String TRAPCLIENT_SERVER = "54.149.14.43";

    //networking
    Socket socket = null;
    BufferedReader in = null;
    PrintWriter out = null;
    boolean connected = false;

    //UI Elements
    Button bThrowHigh = null;
    Button bThrowLow = null;
    Button bThrowPair = null;

    Button bInfo = null;
    Button bFail = null;
    Button bPay = null;

    EditText etName = null;
    EditText etAccount = null;
    EditText etTrapNum = null;
    EditText etNumTargets = null;




    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //find UI elements in xml
        bThrowHigh = (Button) this.findViewById(R.id.bThrowHigh);
        bThrowLow = (Button) this.findViewById(R.id.bThrowLow);
        bThrowPair = (Button) this.findViewById(R.id.bThrowPair);

        bInfo = (Button) this.findViewById(R.id.bInfo);
        bFail = (Button) this.findViewById(R.id.bFail);
        bPay = (Button) this.findViewById(R.id.bPay);

        etName = (EditText) this.findViewById(R.id.etName);
        etAccount = (EditText) this.findViewById(R.id.etAccount);
        etTrapNum = (EditText) this.findViewById(R.id.etTrapNum);
        etNumTargets = (EditText) this.findViewById(R.id.etNumTargets);

        //assign OnClickListeners

        bThrowHigh.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v){
                Toast.makeText(getApplicationContext(),"High", Toast.LENGTH_SHORT).show();
                Log.i(TAG,generateXML("THROW", "H"));

                send(generateXML("THROW", "H"));
            }
        });

        bThrowLow.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v){
                Toast.makeText(getApplicationContext(),"Low", Toast.LENGTH_SHORT).show();
                Log.i(TAG,generateXML("THROW", "L"));

                send(generateXML("THROW", "L"));
            }
        });

        bThrowPair.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v){
                Toast.makeText(getApplicationContext(),"Pair", Toast.LENGTH_SHORT).show();
                Log.i(TAG,generateXML("THROW", "P"));

                send(generateXML("THROW", "P"));
            }
        });

        bInfo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v){
                Toast.makeText(getApplicationContext(),"INFO", Toast.LENGTH_SHORT).show();
                Log.i(TAG,generateXML("INFO", "P"));

                send(generateXML("INFO", "P"));
            }
        });

        bFail.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v){
                Toast.makeText(getApplicationContext(),"FAIL", Toast.LENGTH_SHORT).show();
                Log.i(TAG,generateXML("FAIL", "P"));

                send(generateXML("FAIL", "P"));
            }
        });

        bPay.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v){
                Toast.makeText(getApplicationContext(),"PAY", Toast.LENGTH_SHORT).show();
                Log.i(TAG,generateXML("PAY", "P"));

                send(generateXML("PAY", "P"));
            }
        });


        connect();

    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }



/************************************************************
 * ***************************NETWORKING*********************
 *************************************************************/

void connect() {

    new AsyncTask<Void, Void, String>() {

        String errorMsg = null;

        @Override
        protected String doInBackground(Void... args) {
            Log.i(TAG, "Connect task started");
            try {
                connected = false;
                socket = new Socket(TRAPCLIENT_SERVER, TRAPCLIENT_PORT);
                Log.i(TAG, "Socket created");
                in = new BufferedReader(new InputStreamReader(
                        socket.getInputStream()));
                out = new PrintWriter(socket.getOutputStream());

                connected = true;
                Log.i(TAG, "Input and output streams ready");

            } catch (UnknownHostException e1) {
                errorMsg = e1.getMessage();
            } catch (IOException e1) {
                errorMsg = e1.getMessage();
                try {
                    if (out != null) {
                        out.close();
                    }
                    if (socket != null) {
                        socket.close();
                    }
                } catch (IOException ignored) {
                }
            }
            Log.i(TAG, "Connect task finished");
            return errorMsg;
        }

        @Override
        protected void onPostExecute(String errorMsg) {
            if (errorMsg == null) {
                Toast.makeText(getApplicationContext(),
                        "Connected to server", Toast.LENGTH_SHORT).show();

                // start receiving
                receive();

            } else {
                Toast.makeText(getApplicationContext(),
                        "Error: " + errorMsg, Toast.LENGTH_SHORT).show();
                // can't connect: close the activity
                finish();
            }
        }
    }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
}

    void receive() {
        new AsyncTask<Void, String, Void>() {

            @Override
            protected Void doInBackground(Void... args) {
                Log.i(TAG, "Receive task started");
                try {
                    while (connected) {
                        String header = in.readLine();
                        String msg = in.readLine();
                        if (msg == null) { // other side closed the
                            // connection
                            break;
                        }
                        publishProgress(msg);
                    }

                } catch (UnknownHostException e1) {
                    Log.i(TAG, "UnknownHostException in receive task");
                } catch (IOException e1) {
                    Log.i(TAG, "IOException in receive task");
                } finally {
                    connected = false;
                    try {
                        if (out != null)
                            out.close();
                        if (socket != null)
                            socket.close();
                    } catch (IOException e) {
                    }
                }
                Log.i(TAG, "Receive task finished");
                return null;
            }

            @Override
            protected void onProgressUpdate(String... lines) {
                // the message received from the server is
                // guaranteed to be not null
                String msg = lines[0];

                //Handling message
                processInput(msg);
                return;

            }

        }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
    }


    void disconnect() {
        new Thread() {
            @Override
            public void run() {
                if (connected) {
                    connected = false;
                }
                // make sure that we close the output, not the input
                if (out != null) {
                    out.print("BYE");
                    out.flush();
                    out.close();
                }
                // in some rare cases, out can be null, so we need to close the socket itself
                if (socket != null)
                    try { socket.close();} catch(IOException ignored) {}

                Log.i(TAG, "Disconnect task finished");
            }
        }.start();
    }

    /**
     * Send a one-line message to the server over the TCP connection. This
     * method is safe to call from the UI thread.
     *
     * @param msg
     *            The message to be sent.
     * @return true if sending was successful, false otherwise
     */
    boolean send(String msg) {
        if (!connected) {
            Log.i(TAG, "can't send: not connected");
            return false;
        }

        new AsyncTask<String, Void, Boolean>() {

            @Override
            protected Boolean doInBackground(String... msg) {
                Log.i(TAG, "sending: " + msg[0]);
                out.println(msg[0]);
                return out.checkError();
            }

            @Override
            protected void onPostExecute(Boolean error) {
                if (!error) {
                    Toast.makeText(getApplicationContext(),
                            "Message sent to server", Toast.LENGTH_SHORT)
                            .show();
                } else {
                    Toast.makeText(getApplicationContext(),
                            "Error sending message to server",
                            Toast.LENGTH_SHORT).show();
                }
            }
        }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR, msg);

        return true;
    }

    /**
     * Generates the appropriate message to send the server when called
     * @param request
     * @param target
     * @return
     */
    String generateXML(String request, String target){
        String outputStr = "<?xml version=\"1.0\" encoding=\"utf-8\"?><user><name>" +
                etName.getText().toString() + "</name><account>" +
                etAccount.getText().toString() + "</account><request>" +
                request + "</request><trap>" +
                etTrapNum.getText().toString() + "</trap><target>" +
                target + "</target></user>" + "\r";

        return outputStr;
    }

    void processInput(String msg){
        try {
            DocumentBuilder db = DocumentBuilderFactory.newInstance().newDocumentBuilder();
            InputSource is = new InputSource();
            is.setCharacterStream(new StringReader(msg));

            Document doc = db.parse(is);
            NodeList _numTargets = doc.getElementsByTagName("numTargets");
            NodeList _response = doc.getElementsByTagName("response");

            String response_data= ((CharacterData)_response.item(0).getFirstChild()).getData();
            if(response_data.equals("SUCCESS") || response_data.equals("INFO")){
                String numTargets_data = ((CharacterData)_numTargets.item(0).getFirstChild()).getData();
                etNumTargets.setText(numTargets_data, TextView.BufferType.EDITABLE);
                Toast.makeText(getApplicationContext(),"SUCCESS!" + numTargets_data ,Toast.LENGTH_SHORT).show();
            }else{
                Toast.makeText(getApplicationContext(),"TRAP BUSY",Toast.LENGTH_SHORT).show();
            }


        } catch (ParserConfigurationException pce){
            Toast.makeText(getApplicationContext(),"ParserException", Toast.LENGTH_SHORT).show();
        } catch (Exception e){
            Toast.makeText(getApplicationContext(),"Invalid Request", Toast.LENGTH_SHORT).show();
        }
    }

}



