package com.omghil.quicknotes;

import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private static final String LOCAL_URL = "http://127.0.0.1:5000/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // تشغيل مفسّر بايثون المدمج (مرة واحدة فقط)
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        // تمرير مسار التخزين الخاص بالتطبيق على الهاتف
        // (كل البيانات تُحفظ هنا، لا يوجد أي اتصال بسيرفر خارجي)
        final String dataDir = getFilesDir().getAbsolutePath();

        new Thread(() -> {
            Python py = Python.getInstance();
            PyObject mobileMain = py.getModule("mobile_main");
            mobileMain.callAttr("start", dataDir);
        }).start();

        webView = findViewById(R.id.webview);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());

        // تأخير بسيط لإعطاء خادم Flask وقتاً كافياً للإقلاع قبل تحميل الصفحة
        webView.postDelayed(() -> webView.loadUrl(LOCAL_URL), 1500);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
