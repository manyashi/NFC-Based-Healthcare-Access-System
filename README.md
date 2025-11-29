# NFC- Based Healthcare Access System

This project implements a full-stack, security-conscious system for managing sensitive patient medical records. It utilizes a **Two-Factor Authentication (2FA)** approach blending **Google OAuth** for user identity with **NFC tokens** for rapid, time-sensitive patient record access by hospital staff.

The system emphasizes **security-by-design** through role-based access control (RBAC), end-to-end HTTPS communication, and **Fernet encryption at rest** for all critical patient data.

## Key Features

* **Role-Based Access Control (RBAC):** Separate user flows for Patients and Staff (Doctors, Nurses).
* **Authentication (2FA):** Google OAuth for identity verification plus NFC for context-aware access.
* **Time-Limited Access:** Staff access to a patient's record is granted only for **24 hours** after the patient's NFC scan, then automatically revoked.
* **Immutable Records:** Medical history is append-only; past entries cannot be modified, ensuring audit integrity.
* **Encryption at Rest:** Sensitive patient data is encrypted in the PostgreSQL database using **Fernet symmetric encryption**.
* **Accountability:** Every medical entry logs the Staff ID and the Hospital Name where the action was taken.
* **IoT Integration:** Custom Arduino/ESP8266 hardware bridge for NFC scanning over HTTPS.

## Architecture Overview

The system follows a classic decoupled architecture:

1.  **Frontend (React):** A Single Page Application (SPA) for patient/staff dashboards, managing session state via Context API.
2.  **Backend (Flask):** Provides RESTful APIs, handles authentication, session management, RBAC, and manages the Fernet encryption/decryption layer.
3.  **Database (PostgreSQL):** Hosted database used for persistence, containing encrypted binary data fields.
4.  **Hardware Bridge:** Arduino Uno + ESP8266 + PN532 acts as a secure external client, sending NFC data to the Flask API via HTTPS.

## Project Setup

Follow these steps to get the entire stack running locally.

### Prerequisites

Ensure you have the following installed:

* **Python 3.8+** and **pip**
* **Node.js 18+** and **npm** or **yarn**
* **PostgreSQL** (running locally or accessible remotely)
* **Arduino IDE** with **ESP8266** board definitions installed.

---

### Step 1: Database Setup

1.  **Create Database:** Ensure your PostgreSQL server is running and create a database (e.g., `patient_db`).
2.  **Configure Environment:** Create the `.env` file in the `backend/` directory.

    ```ini
    # backend/.env
    # --- SECURITY KEYS ---
    # Generate this via: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY=YOUR_FLASK_SESSION_SECRET_KEY
    # Generate this via: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    FERNET_KEY=YOUR_32-BYTE_FERNET_ENCRYPTION_KEY
    IOT_DEVICE_SECRET=Hospital-Scanner-Unit-V1-X99

    # --- DATABASE ---
    # NOTE: Use 'postgresql://' not 'postgres://' for SQLAlchemy 
    DATABASE_URL=postgresql://postgres:password@localhost:5432/patient_db

    # --- GOOGLE OAUTH ---
    GOOGLE_CLIENT_ID=YOUR_CLIENT_ID
    GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET
    ```

---

### Step 2: Backend (Flask) Installation

1.  Navigate to the backend directory and activate the virtual environment:
    ```bash
    cd backend
    source venv/bin/activate  # Mac/Linux
    # venv\Scripts\activate   # Windows
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Server:** This will automatically create all necessary tables via `db.create_all()`.
    * *Note: Ensure your Flask app listens on your local network IP (e.g., 0.0.0.0) so the hardware can connect.*
    ```bash
    python run.py 
    ```
    (The API will run on `https://127.0.0.1:5000` or `https://[YOUR_IP]:5000`)

---

### Step 3: Frontend (React) Installation

1.  Navigate to the frontend directory:
    ```bash
    cd ../frontend
    npm install
    ```
2.  Start the development server:
    ```bash
    npm run dev
    ```
    (The frontend will run on `http://localhost:5173`)

---

### Step 4: Hardware Setup (Arduino/ESP8266)

The hardware acts as a secure client, sending NFC data to the `/api/nfc/scan` endpoint.

1.  **Wiring:** Follow the [Two-Brain Architecture](#two-brain-architecture):
    * **PN532 (I2C):** SDA → A4, SCL → A5 (on Arduino Uno).
    * **ESP8266 (Serial):** TX → Pin 2, RX → Pin 3 (on Arduino Uno).
    * *Safety: **ESP8266 VCC must be 3.3V**.*
2.  **Update Configuration:** Edit the variables in the Arduino sketch (`.ino` file):
    * Set `ssid`, `password` (use a mobile hotspot if you have network issues).
    * Set `server` to your **Laptop's IP Address** (e.g., `192.168.1.45`).
    * Set `deviceSecret` to match the `IOT_DEVICE_SECRET` from your `.env` file.
3.  **Flash Code:** Select the correct board (**NodeMCU 1.0 / ESP-12E**) and COM port, then upload the sketch.

<a id="two-brain-architecture"></a>
## Two-Brain Architecture (Uno + ESP8266)

This setup is required because the Arduino Uno controls the NFC reader, and the ESP8266 only provides a WiFi connection via AT commands.

| Component | Connected To | Purpose | Notes |
| :--- | :--- | :--- | :--- |
| **PN532 SDA** | **Arduino A4** | NFC Reader (I2C) | |
| **PN532 SCL** | **Arduino A5** | NFC Reader (I2C) | |
| **ESP8266 TX** | **Arduino D2** | Serial Comms (RX) | Uses `SoftwareSerial` |
| **ESP8266 RX** | **Arduino D3** | Serial Comms (TX) | **Requires 3.3V Logic** |

## Security & Access Flows

### Google OAuth Flow

This project uses the **Authorization Code Flow** to secure identity.

1.  **Initiation:** Patient/Staff clicks the "Login with Google" button on the React Frontend.
2.  **Redirection:** Frontend hits Flask endpoint (`/auth/login`).
3.  **Authentication:** Flask redirects to Google, which validates the user.
4.  **Callback:** Google redirects back to Flask (`/auth/callback`) with a code.
5.  **Token Exchange:** Flask exchanges the code for a profile token, extracts the email/sub, sets the user's role (`staff` or `patient`), and creates a secure, time-limited session cookie.
6.  **Redirect to Dashboard:** Flask redirects the browser back to the React App (`/auth-success`), which then loads the protected dashboard based on the session role. 


### NFC Access Flow

NFC is used for authorization, not identity.

1.  **Staff Login:** Hospital staff (Doctor/Nurse) must first be logged in via Google OAuth.
2.  **Patient Scan:** The patient taps their phone/tag on the PN532 reader.
3.  **Hardware Request:** The Arduino reads the unique tag UID, constructs a JSON payload, adds the secure `X-Device-API-Key` header, and sends an **HTTPS POST** request to `/api/nfc/scan`.
4.  **Backend Verification:**
    * Flask verifies the `X-Device-API-Key` matches the `IOT_DEVICE_SECRET`.
    * Flask resolves the UID hash to a `patient_id`.
    * Flask updates the `PatientProfile.last_scanned_at` timestamp to `NOW()`.
5.  **Staff Access:** The Staff Dashboard automatically shows the patient's name as **"Active Access"** for the next 24 hours. Any API request to view or add data is blocked by the backend if this 24-hour window has expired.
