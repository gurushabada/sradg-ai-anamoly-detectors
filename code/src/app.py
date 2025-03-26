from fastapi import FastAPI, File, UploadFile, Form, Response
import pandas as pd
import joblib
import os
import yagmail
import logging
from io import BytesIO
from fastapi.responses import JSONResponse
from io import BytesIO

from sklearn.ensemble import IsolationForest

# Initialize FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Anomaly Detection API is running."}

# Load historical data
historical_file_path = "sampledata.ods" # Update with actual file path
historical_data = pd.read_excel(historical_file_path, engine="odf")
# Preprocess data
historical_data["As of Date"] = pd.to_datetime(historical_data["As of Date"], errors="coerce")
historical_data.dropna(subset=["As of Date"], inplace=True)
# Select relevant features
features = ["GL Balance", "Ihub Balance", "Balance Difference"]
X_historical = historical_data[features]
# Train anomaly detection model
iso_forest = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
iso_forest.fit(X_historical)
# Save model
joblib.dump(iso_forest, "anomaly_model.pkl")

#new

# Load the trained anomaly detection model
model_file = "anomaly_model.pkl"
if os.path.exists(model_file):
    model = joblib.load(model_file)
else:
    raise FileNotFoundError("Anomaly model not found. Train and save the model first.")


# Function to determine anomaly reason
def get_anomaly_comment(gl_balance, ihub_balance, balance_difference):
    if balance_difference > 50000:
        return "[Large Positive Balance Difference] - May indicate missing postings."
    elif balance_difference < -50000:
        return "[Large Negative Balance Difference] - Possible duplicate postings."
    elif gl_balance == 0 or ihub_balance == 0:
        return "[Zero Balance Detected] - Potential missing entry."
    else:
        return "[Unusual Transaction Pattern] - Review reconciliation records."

# Function to send email with file attachment
def send_email_with_attachment(email, subject, message, file_path):
    sender_email = "hackathon896@gmail.com"  # Update with your Gmail
    app_password = "syxq ends jrge jcwg"  # Replace with your App Password

    try:
        yag = yagmail.SMTP(sender_email, app_password)
        yag.send(
            to=email,
            subject=subject,
            contents=message,
            attachments=[file_path]
        )
        print(f"✅ Email sent successfully to {email} with file attachment.")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

# API endpoint to process file upload, detect anomalies, return summary & file
@app.post("/detect_anomalies/")
async def detect_anomalies(file: UploadFile = File(...), email: str = Form(...)):
    logging.info(f"Received file: {file.filename}")
    try:
        # Read uploaded file
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file, engine="openpyxl")
        else:
            return JSONResponse(content={"error": "Unsupported file format. Please upload a CSV or Excel file."}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": f"File processing error: {e}"}, status_code=400)

    # Ensure required columns exist
    required_columns = ["Account", "GL Balance", "Ihub Balance", "Balance Difference"]
    if not all(col in df.columns for col in required_columns):
        return JSONResponse(content={"error": f"Missing required columns. Expected: {required_columns}"}, status_code=400)

    # Extract features and apply anomaly detection
    X_real_time = df[["GL Balance", "Ihub Balance", "Balance Difference"]]
    predictions = model.predict(X_real_time)

    # Add anomaly, reason, and action columns
    df["Anomaly"] = predictions == -1
    df["Comment"] = df.apply(lambda row: get_anomaly_comment(row["GL Balance"], row["Ihub Balance"], row["Balance Difference"]) if row["Anomaly"] else "No anomaly detected", axis=1)
    df["Action"] = df["Anomaly"].apply(lambda x: "Review & correct data" if x else "No action needed")

    # Convert to Python int & string to avoid JSON serialization errors
    total_records = int(len(df))
    anomaly_count = int(df["Anomaly"].sum())
    anomaly_percentage = f"{round((anomaly_count / total_records) * 100, 2)}%"

    summary = {
        "total_records": total_records,
        "anomalies_found": anomaly_count,
        "anomaly_percentage": anomaly_percentage,
        "message": "File processed successfully. Download the processed file."
    }

    # Create file buffer
    excel_buffer = BytesIO()
    output_filename = f"processed_{file.filename}"

    if file.filename.endswith(".csv"):
        df.to_csv(excel_buffer, index=False)
        mime_type = "text/csv"
    else:
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    excel_buffer.seek(0)  # Reset buffer position

    # Save locally for email attachment
    with open(output_filename, "wb") as f:
        f.write(excel_buffer.getvalue())

    # Send email with attachment
    subject = "🔔 Anomaly Detection Report"
    message = f"Please find the anomaly detection report attached.\nTotal Records: {total_records}\nAnomalies Found: {anomaly_count}\nAnomaly Percentage: {anomaly_percentage}"
    send_email_with_attachment(email, subject, message, output_filename)

    # Return JSON response with summary + file download URL
    return JSONResponse(
        content={
            "summary": summary,
            "download_url": f"http://127.0.0.1:8000/download/{output_filename}"
        },
        status_code=200
    )

# API to serve the downloadable file
@app.get("/download/{filename}")
async def download_file(filename: str):
    try:
        file_path = os.path.abspath(filename)
        with open(file_path, "rb") as f:
            content = f.read()

        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if filename.endswith(".xlsx") else "text/csv"
        headers = {"Content-Disposition": f"attachment; filename={filename}"}

        return Response(content=content, media_type=mime_type, headers=headers)
    except Exception as e:
        return JSONResponse(content={"error": f"File not found: {e}"}, status_code=404)
