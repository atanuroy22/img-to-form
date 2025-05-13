---

````markdown
# 🖼️ img-to-form

**img-to-form** is a smart web app that extracts structured data from uploaded images of forms or documents using OCR and enhances the results using Google Gemini 1.5. The application returns a JSON output with identified fields such as name, phone number, email, DOB, and more.


## 🚀 Features

- 📸 Upload images (JPG, PNG, etc.) of scanned forms or handwritten documents.
- 🔍 Extract raw text using **Tesseract OCR**.
- 🧠 Use **Google Gemini 1.5** to structure, clean, and understand the extracted text.
- 📋 Display the parsed results in a clean HTML view.
- 💾 Download structured output as a `data.json` file.

---

## 🛠️ Tech Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| Frontend      | HTML, CSS, JavaScript               |
| Backend       | Python, Flask                       |
| OCR Engine    | Tesseract OCR                       |
| LLM Engine    | Google Gemini 1.5 via Gemini API    |
| Data Format   | JSON                                |
| Hosting       | Apache / GCP / PythonAnywhere (as per setup) |

---

## 🔑 Environment Variables

Create a `.env` file in your root directory with:

```env
GEMINI_API_KEY=your_google_gemini_api_key
````

Ensure that this file is **not committed to GitHub**.

---

## 📂 Folder Structure

```
img-to-form/
├── app.py
├── requirement.txt
├── .env
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   └── js/
├── uploads/
├── extracted_text.txt
├── data.json
├── data_final.json
├── README.md
```

---

## 💻 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/atanuroy22/img-to-form.git
cd img-to-form
```

### 2. Create a virtual environment (optional)

```bash
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirement.txt
```

### 4. Add your Gemini API key

Create a `.env` file with your Google Gemini API key as shown earlier.

### 5. Run the app

```bash
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) to use the app.

---

## 🧠 How Gemini Works in This App

After extracting raw text from an image using Tesseract, the text is sent to **Gemini 1.5** with a prompt like:

```python
prompt = f"""
Extract the following fields from this OCR output: Name, Phone, Email, DOB.

OCR Text:
{text}

Respond in this JSON format:
{{
  "name": "",
  "phone": "",
  "email": "",
  "dob": ""
}}
"""
```

Gemini replies with structured JSON, which is then shown to the user and can be downloaded.

### Upload Page

![Upload Interface](images/upload_interface.png)

### Output Preview

![Extracted Data](images/output_result.png)


## 🤝 Contributing

Pull requests are welcome! If you want to contribute:

1. Fork the repository.
2. Create a branch: `git checkout -b my-feature`.
3. Make your changes.
4. Push to your fork and submit a PR.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Contact

Built by [Atanu Roy](https://github.com/atanuroy22)
📧 Email: [atanuroy22@example.com](mailto:atanuroy22@example.com)
🌐 GitHub: [github.com/atanuroy22](https://github.com/atanuroy22)

```

