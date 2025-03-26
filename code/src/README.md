# **Steps to Execute the Anomaly Detection API in PyCharm**

##### 1. Install Required Libraries

Before running the program, install the necessary dependencies. Open PyCharm Terminal or Command Prompt (cmd) and run:

pip install fastapi uvicorn pandas joblib openpyxl yagmail

##### 2. Save the Python Script

Open PyCharm
Create a new Python file (e.g., app.py)

##### **3. ️Run the FastAPI Server**

Now, start the server. In PyCharm:

Open Terminal inside PyCharm
Run this command:
uvicorn app:app --reload
If everything is correct, you should see:
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

##### 4. Test the API in Swagger UI

FastAPI automatically generates an interactive UI for testing.

Open your browser
Go to http://127.0.0.1:8000/docs
Click "Try it out" on the /detect_anomalies/ API
Upload a CSV/XLSX file and enter your email
Click "Execute"
🚀 Your file will be processed & email will be sent! 🚀

##### 5. **Download the Processed File**

After API execution, check the JSON response. It will have a download_url, like:
{
  "summary": {
    "total_records": 100,
    "anomalies_found": 15,
    "anomaly_percentage": "15.0%",
    "message": "File processed successfully. Download the processed file."
  },
  "download_url": "http://127.0.0.1:8000/download/processed_data.csv"
}
Copy the download_url
Paste it into your browser
The file will be downloaded! ✅

##### 6. **Verify Email**

Check your Gmail inbox
Look for an email with "Anomaly Detection Report"
Open it → The processed file should be attached!

### 🔧 Troubleshooting:

✅ If API doesn’t start:

Ensure Python is installed (python --version)
Ensure PyCharm's terminal uses the correct environment

✅ If email fails:

Check if App Password is correct
Try logging into Gmail using the App Password

✅ If file doesn’t download:

Ensure the file exists in the project folder
Check the download_url for typos
