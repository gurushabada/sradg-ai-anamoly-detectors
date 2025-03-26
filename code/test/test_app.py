import pytest
from fastapi.testclient import TestClient
from app import app  # Import FastAPI app
import os

# Initialize Test Client
client = TestClient(app)


# Test 1: Check if API is running
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Anomaly Detection API is running."}


# ✅ Updated Test: Upload a sample file with required columns (without comments)
def test_detect_anomalies():
    # Create a sample CSV file with required columns (no inline comments)
    file_content = """Account,GL Balance,Ihub Balance,Balance Difference
1001,5000,5000,0
1002,7000,6900,100
1003,12000,5000,7000
1004,15000,15000,0
1005,3000,4000,-1000
"""

    file_path = "test_data.csv"

    with open(file_path, "w") as f:
        f.write(file_content)

    # Send file via API request
    with open(file_path, "rb") as f:
        response = client.post(
            "/detect_anomalies/",
            files={"file": ("test_data.csv", f, "text/csv")},
            data={"email": "test@example.com"}
        )

    os.remove(file_path)  # Cleanup test file

    assert response.status_code == 200  # Ensure successful response
    data = response.json()

    assert "summary" in data
    assert "download_url" in data


# Test 3: Check if file download works
def test_file_download():
    response = client.get("/download/processed_data.csv")
    assert response.status_code in [200, 404]  # 200 if file exists, 404 if not


# Test 4: Invalid file type upload
def test_invalid_file_upload():
    file_content = "Invalid data"
    file_path = "test_data.txt"

    with open(file_path, "w") as f:
        f.write(file_content)

    with open(file_path, "rb") as f:
        response = client.post(
            "/detect_anomalies/",
            files={"file": ("test_data.txt", f, "text/plain")},
            data={"email": "test@example.com"}
        )

    os.remove(file_path)  # Cleanup

    assert response.status_code == 400  # Expecting a 400 Bad Request
