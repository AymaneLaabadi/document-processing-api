# 🌟 Backend API for Document Processing

This is a **Flask-based backend API** that extracts and processes information from **Letters of Credit (LC)** using AI-powered text extraction.

---

## 🚀 **Features**
- 📝 **Extract key details** from Letters of Credit.
- 📁 **Process required documents** and verification points.
- 📝 **Fill document templates** with extracted data.
- 🌐 **REST API** with multiple endpoints for document processing.

---

## 🛠️ **Setup Instructions**

### 1️⃣ **Clone the Repository**
```sh
git clone https://github.com/your-repo/document-processing-api.git
cd document-processing-api
```

### 2️⃣ **Set Up Virtual Environment**
```sh
python3 -m venv venv
source venv/bin/activate  # For Linux/MacOS
# Windows: venv\Scripts\activate
```

### 3️⃣ **Install Dependencies**
```sh
pip install -r requirements.txt
```

### 4️⃣ **Set Up Environment Variables**
Create a `.env` file in the project root:
```ini
OPENAI_API_KEY=your-openai-api-key
SPACY_MODEL=en_core_web_sm
```

### 5️⃣ **Run the Backend**
```sh
python src/main.py
```
The API will be available at:  
🔗 `http://localhost:5000`

---

## 📞 **API Endpoints**

### 📌 1. **Upload and Extract LC Data**
#### **`POST /convert`**
**Description:** Upload a **Letter of Credit (LC) text file**, extract key details, and process relevant documents.

🔹 **Request:**
```http
POST /convert
Content-Type: multipart/form-data
```
```json
{
  "lc_file": "<Upload a .txt file>" 
}
```

🔹 **Response (Success):**
```json
{
  "message": "Document processed successfully!",
  "document_filename": "Bill_of_Lading_123456.docx",
  "BOL Extraction": { "Freight payment type": "Prepaid" },
  "Verification Points": "- BL must match LC terms",
  "Required Documents": "- Commercial Invoice (3 copies)"
}
```

🔹 **Response (Failure):**
```json
{
  "error": "No file provided. Please upload a valid .txt file."
}
```

---

### 📌 2. **List Processed Files**
#### **`GET /files`**
**Description:** Retrieve a list of previously processed files.

🔹 **Request:**
```http
GET /files
```

🔹 **Response (Success):**
```json
[
  {
    "id": "123456",
    "name": "Bill_of_Lading_123456.docx",
    "size": 204800,
    "date": 1700000000,
    "path": "data/output/Bill_of_Lading_123456.docx"
  }
]
```

---

### 📌 3. **Download Processed Document**
#### **`GET /download-document`**
**Description:** Download the **latest generated document**.

🔹 **Request:**
```http
GET /download-document
```

🔹 **Response (File Download)**  
- Returns the **latest generated `.docx` file**.

🔹 **Response (Failure):**
```json
{
  "error": "No processed documents found."
}
```

---

## 📖 **Code Structure**
```
📂 backend/
│   ├── .env                # Environment variables
│   ├── requirements.txt    # Python dependencies
│   ├── setup.sh            # Setup script
│   ├── README.md           # API Documentation
│
├─── data/
│   ├── input/              # Input templates & samples
│   ├── output/             # Generated documents
│   ├── config/             # Configuration files
│
├─── src/
│   ├── models/             
│   │   ├── bill_of_lading_parser.py
│   │   ├── letter_of_credit_parser.py
│   │   ├── required_documents_extractor.py
│   │   ├── verification_points_extractor.py
│   │   ├── template_document_filler.py
│   ├── api.py              # Flask API
│   ├── config.py           # Configuration settings
│   ├── main.py             # Processing pipeline
│   ├── paragraph_matcher.py
│   ├── preprocessor.py
```

---

## 🛠 **Tech Stack**
- **Python 3.x**
- **Flask** (API framework)
- **OpenAI API** (for text extraction)
- **SpaCy** (NLP processing)
- **scikit-learn** (Machine Learning for text matching)
- **Python-docx** (Document generation)

---

## 📌 **Next Steps**
- ✅ **Improve logging & error handling**
- ✅ **Add authentication for API endpoints**
- ✅ **Integrate Postman Collection for easy testing**
- ✅ **Deploy API to a cloud platform**

---

## 🤝 **Contributing**
- Fork the repository 🍔  
- Create a new branch 🌿  
- Make your changes & test 🛠️  
- Open a Pull Request 📌  

---

## 📄 **License**
This project is licensed under **MIT License**.

---

### 🎉 **Happy Coding!**
🚀 **For questions or feedback, reach out via GitHub Issues!**

