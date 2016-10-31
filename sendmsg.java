package com.example.kye.app;

import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import android.os.AsyncTask;
import java.io.*;
/**
 * Created by KYE on 2016-10-25.
 */

public class SendMessage extends AsyncTask<String, Void, Void> {
    private Exception exception;
    @Override
    protected Void doInBackground(String... params){
        try{
            try{

                Socket socket = new Socket("10.10.0.114",8889);
                PrintWriter outToServer = new PrintWriter(
                        new OutputStreamWriter(
                                socket.getOutputStream()));
                outToServer.print(params[0]);
                outToServer.flush();


            } catch (IOException e){
                e.printStackTrace();
            }
        } catch (Exception e){
            this.exception = e;
            return null;
        }
        return null;
    }
}