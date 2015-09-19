package ca.pluszero.prototypr;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.Toast;

import com.google.api.client.extensions.android.http.AndroidHttp;
import com.google.api.client.googleapis.auth.oauth2.GoogleCredential;
import com.google.api.client.googleapis.media.MediaHttpUploader;
import com.google.api.client.googleapis.media.MediaHttpUploaderProgressListener;
import com.google.api.client.http.HttpTransport;
import com.google.api.client.http.InputStreamContent;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.api.services.storage.Storage;
import com.google.api.services.storage.StorageScopes;
import com.google.api.services.storage.model.ObjectAccessControl;
import com.google.api.services.storage.model.StorageObject;
import com.loopj.android.http.AsyncHttpClient;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.security.GeneralSecurityException;
import java.util.Arrays;
import java.util.Date;


public class MainActivity extends Activity {

    class UploadImagesTask extends AsyncTask<String, Void, Void> {

        protected void onPostExecute(Void v) {
            Toast.makeText(MainActivity.this, "Finished uploading images!", Toast.LENGTH_SHORT).show();
            progressBar.setVisibility(View.GONE);
            resetCounter();
        }

        @Override
        protected Void doInBackground(String... params) {
            try {
                uploadPictures();
            } catch (Exception e) {
//                Toast.makeText(MainActivity.this, "Failed to upload :(", Toast.LENGTH_SHORT).show();
                e.printStackTrace();
            }
            return null;
        }

        @Override
        protected void onProgressUpdate(Void... values) {
            super.onProgressUpdate(values);
        }
    }

    class CustomProgressListener implements MediaHttpUploaderProgressListener {
        public void progressChanged(MediaHttpUploader uploader) throws IOException {
            switch (uploader.getUploadState()) {
                case INITIATION_STARTED:
                    System.out.println("Initiation has started!");
                    break;
                case INITIATION_COMPLETE:
                    System.out.println("Initiation is complete!");
                    break;
                case MEDIA_IN_PROGRESS:
                    currentProgress = uploader.getProgress();
                    Toast.makeText(MainActivity.this, "" + uploader.getProgress(), Toast.LENGTH_SHORT).show();
                    break;
                case MEDIA_COMPLETE:
                    System.out.println("Upload is complete!");
            }
        }
    }

    private static AsyncHttpClient client = new AsyncHttpClient();
    public static final String BUCKET_NAME = "prototypr-images";
    private double currentProgress = 0.0;
    private ProgressBar progressBar;
    private static final int IMAGE_REQUEST_CODE = 1;
    private int counter = 0;
    private Button takePictureBtn;
    private Button doneBtn;
    private Button restartBtn;
    private LinearLayout imageListContainer;

    public void incrementCounter() {
        counter++;
    }

    public void resetCounter() {
        counter = 0;
    }

    private static Storage storageService;
    private static final JsonFactory JSON_FACTORY = JacksonFactory.getDefaultInstance();

    /**
     * Returns an authenticated Storage object used to make service calls to Cloud Storage.
     */
    private static Storage getService() throws IOException, GeneralSecurityException {
        if (null == storageService) {
            InputStream resourceAsStream = MainActivity.class.getClassLoader().getResourceAsStream("res/raw/helloworld.json");
            GoogleCredential credential = GoogleCredential.fromStream(resourceAsStream);
            // Depending on the environment that provides the default credentials (e.g. Compute Engine,
            // App Engine), the credentials may require us to specify the scopes we need explicitly.
            // Check for this case, and inject the Bigquery scope if required.
            if (credential.createScopedRequired()) {
                credential = credential.createScoped(StorageScopes.all());
            }
            HttpTransport httpTransport = AndroidHttp.newCompatibleTransport();
            storageService = new Storage.Builder(httpTransport, JSON_FACTORY, credential)
                    .setApplicationName("prototypr").build();
        }
        return storageService;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        progressBar = (ProgressBar) findViewById(R.id.progress_bar);

        imageListContainer = (LinearLayout) findViewById(R.id.image_list);
        takePictureBtn = (Button) findViewById(R.id.take_picture_btn);
        takePictureBtn.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                Intent imageIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                incrementCounter();
                File imagesFolder = new File(Environment.getExternalStorageDirectory(), "MyImages");
                imagesFolder.mkdirs();
                File image = new File(imagesFolder, "image_00" + counter + ".jpg");
                Uri uriSavedImage = Uri.fromFile(image);
                imageIntent.putExtra(MediaStore.EXTRA_OUTPUT, uriSavedImage);
                startActivityForResult(imageIntent, IMAGE_REQUEST_CODE);
            }
        });
        doneBtn = (Button) findViewById(R.id.done_btn);
        doneBtn.setOnClickListener(new View.OnClickListener() {


            @Override
            public void onClick(View v) {
                progressBar.setVisibility(View.VISIBLE);
                new UploadImagesTask().execute();
                hideDoneAndReset();
                imageListContainer.removeAllViews();
            }
        });
        restartBtn = (Button) findViewById(R.id.reset_btn);
        restartBtn.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                resetCounter();
                hideDoneAndReset();
                imageListContainer.removeAllViews();
            }
        });
    }

    private void uploadPictures() throws IOException, GeneralSecurityException {
        String timeString = "" + new Date().getTime();
        for (int i = 1; i <= counter; i++) {
            try {
                Log.d("Anojh" , "uploading image " + i);
                File imagesFolder = new File(Environment.getExternalStorageDirectory(), "MyImages");
                File imageFile = new File(imagesFolder, "image_00" + i + ".jpg");
                String contentType = "image/jpeg";
                String name = getNameForImage(timeString, i);
                uploadStream(name, contentType, new BufferedInputStream(new FileInputStream(imageFile)), BUCKET_NAME);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
        }
    }

    private String getNameForImage(String timeString, int i) {
        return timeString + " - " + i;
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        if (requestCode == IMAGE_REQUEST_CODE) {
            if (resultCode == Activity.RESULT_OK) {
                if (counter == 1) {
                    showDoneAndReset();
                }
                showAndCreateImage();
            } else {
                counter--;
                if (counter == 0) {
                    hideDoneAndReset();
                }
            }
        }
        super.onActivityResult(requestCode, resultCode, intent);
    }

    private void showAndCreateImage() {
        File imagesFolder = new File(Environment.getExternalStorageDirectory(), "MyImages");
        File image = new File(imagesFolder, "image_00" + counter + ".jpg");

        if(image.exists()) {
            Bitmap myBitmap = BitmapFactory.decodeFile(image.getAbsolutePath());

            ViewGroup.LayoutParams params = new ViewGroup.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            ImageView imgView = new ImageView(this);
            imgView.setImageBitmap(myBitmap);
            imgView.requestLayout();
            imageListContainer.addView(imgView, params);
            imgView.getLayoutParams().height = 800;
            imgView.getLayoutParams().width = 200;
            imgView.setOnClickListener(new View.OnClickListener(){

                @Override
                public void onClick(View v) {
                    File imagesFolder = new File(Environment.getExternalStorageDirectory(), "MyImages");
                    imagesFolder.mkdirs();
                    File image = new File(imagesFolder, "image_00" + counter + ".jpg");
                    Intent intent = new Intent();
                    intent.setAction(android.content.Intent.ACTION_VIEW);
                    intent.setDataAndType(Uri.fromFile(image), "image/png");
                    startActivity(intent);
                }
            });
        }
    }

    private void showDoneAndReset() {
        doneBtn.setVisibility(View.VISIBLE);
        restartBtn.setVisibility(View.VISIBLE);
    }

    private void hideDoneAndReset() {
        doneBtn.setVisibility(View.INVISIBLE);
        restartBtn.setVisibility(View.INVISIBLE);
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

    public static void uploadStream(String name, String contentType, InputStream stream, String bucketName)
            throws IOException, GeneralSecurityException {
        InputStreamContent contentStream = new InputStreamContent(contentType, stream);
        StorageObject objectMetadata = new StorageObject()
                // Set the destination object name
                .setName(name)
                        // Set the access control list to publicly read-only
                .setAcl(Arrays.asList(
                        new ObjectAccessControl().setEntity("allUsers").setRole("READER")));

        // Do the insert
        Storage client = getService();
        Storage.Objects.Insert insertRequest = client.objects().insert(
                bucketName, objectMetadata, contentStream);

        insertRequest.execute();
    }

//    public static List<StorageObject> listBucket(String bucketName)
//            throws IOException, GeneralSecurityException {
//        Storage client = getService();
//        Storage.Objects.List listRequest = client.objects().list(bucketName);
//
//        List<StorageObject> results = new ArrayList<>();
//        Objects objects;
//
//        // Iterate through each page of results, and add them to our results list.
//        do {
//            objects = listRequest.execute();
//            // Add the items in this page of results to the list we'll return.
//            results.addAll(objects.getItems());
//
//            // Get the next page, in the next iteration of this loop.
//            listRequest.setPageToken(objects.getNextPageToken());
//        } while (null != objects.getNextPageToken());
//
//        return results;
//    }
}
