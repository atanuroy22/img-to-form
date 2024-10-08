import io
import json
import cv2
import requests
import google.generativeai as genai
import os
from flask import Flask, render_template, request, redirect, url_for,jsonify  # Ensure redirect and url_for are imported
import shutil  # Add this import at the top of your file
from flask_cors import CORS

app = Flask(__name__)

# CORS configuration
CORS(app)  # Enable CORS for all routes

def extract_text_with_gemini(image_path):
    try:
        # Debugging: Check if the image path is correct
        print(f"Attempting to upload file: {image_path}")
        
        sample_file = genai.upload_file(path=image_path, display_name="Diagram")
        
        # Debugging: Check the response from the upload
        print(f"Upload response: {sample_file}")
        
        print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
        file = genai.get_file(name=sample_file.name)
        print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")
        
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content([sample_file, "Extract only key-value pairs from the text, keeping the headers as they appear in the form. Ensure each key-value pair is on a separate line, and if keys are repeated, append _1, _2, etc.  Do not include any non key-value pair texts. Scan row-wise. Keep all key-value pairs under their respective headers until the next header starts. Give the form number twice. Please ensure the output is accurate with correct spelling and follows the instructions precisely."])
        return response.text
    except Exception as e:
        print(f"Gemini extraction failed: {e}")
        return None
def extract_text_with_back_gemini(image_path):
    try:
        # Debugging: Check if the image path is correct
        print(f"Attempting to upload file: {image_path}")
        
        sample_file = genai.upload_file(path=image_path, display_name="Diagram")
        
        # Debugging: Check the response from the upload
        print(f"Upload response: {sample_file}")
        
        print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
        file = genai.get_file(name=sample_file.name)
        print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")
        
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content([sample_file, "Extract only key-value pairs from the text and dont forget the quota and all india rank , keeping the headers as they appear in the form. Ensure each key-value pair is on a separate line and Append '_2' after the keys 'NAME' and 'PRESENT ADDRESS'. Append '_3' after the keys 'MOBILE NO', 'EMAIL-ID', 'P.O.', 'P.S.', 'PINCODE', 'DISTRICT', 'STATE', and 'OCCUPATION'. Do not include any non key-value pair texts and add 'LOCAL GUARDIAN DETAILS:' at top in the output . Scan row-wise. Keep all key-value pairs under their respective headers until the next header starts. Please ensure the output is accurate with correct spelling and follows the instructions precisely."])
        
        return response.text
        # return False
    except Exception as e:
        print(f"Gemini extraction failed: {e}")
        return None

def extract_text_from_image(image_path):
    try:
        img = cv2.imread(image_path)
        file_bytes = io.BytesIO(cv2.imencode(".jpg", img)[1])
        url_api = "https://api.ocr.space/parse/image"
        result = requests.post(
            url_api,
            files={"image.jpg": file_bytes},
            data={
                "apikey": "K83686776688957",
                "language": "eng",
                "isOverlayRequired": True,
                "detectOrientation": True,
                "scale": True,
                "isTable": True,
                "OCREngine": 2
            }
        )

        result = result.content.decode()
        result = json.loads(result)
        parsed_results = result.get("ParsedResults")
        if parsed_results:
            text_detected = parsed_results[0].get("ParsedText")
        else:
            text_detected = ""
        return text_detected
    except Exception as e:
        print(f"OCR extraction failed: {e}")
        return ""

def replace_text(text):
    try:
        replacements = [
            "REG. OFFICE: A2/15, KALYANI, DIST: NADIA,", "REG. OFFICE: A2/15, KALYANI, DIST.: NADIA,", "ALL FOR EDUCATION, FUCATION FOR ALF", "PIN 741235, WEST BENGAL, INDIA", "RESPECTED SIR/MADAM,", "FURNISHED BELOW FOR YOUR KIND CONSIDERATION.", "MBBS COURSE IN SESSION:", "PARTICULARS ARE",
            "MAIL ID: INFO.JMNEDUR@GMAIL.COM", "CONTACT NO: +91 9831111817",
            "CAMPUS: UTTAR PANCHPOTA, P.O & P. S. CHAKDAHA,", "DIST. NADIPIP INSTALLA, PIN 741222, WEST BENGAL, INDIA",
            "DIST. NADIA, PIN 741222, WEST BENGAL, INDIA", "JMN", "ADMISSION FORM", "THE PRINCIPAL,", "JMN MEDICAL COLLEGE,",
            "UTTAR PANCHPOTA, P.O. & P.S. CHAKDAHA,", "DIST. NADIA, PINCODE - 741222,",
            "WEST BENGAL, INDIA.", "PASTE RECENT", "PASSPORT-SIZE", "COLOUR",
            "PHOTOGRAPH OF", "THE CANDIDATE", "AND SIGN ACROSS", "THE PHOTOGRAPH.",
            "RESPECTED SIR / MADAM,", "I HEREBY APPLY FOR ADMISSION TO THE MBBS COURSE IN SESSION",
            "PARTICULARS ARE FURNISHED BELOW FOR YOUR KIND CONSIDERATION.", "KINDLY USE CAPITAL LETTERS ONLY",
            "STUDENT DETAILS:", "PARENT DETAILS:", "JMN MEDICAL COLLEGE",
            "WWW.JMNMEDICALCOLLEGE.ORG.IN",
            "DATE OF BIRTH:", "PLACE OF BIRTH:", "NATIONALITY:", "CONTACT NO:",
            "MARITAL STATUS:", "RELIGION:", "CASTE:", "GENDER:", "MOTHERTOUNGE:",
            "PERMANENT ADDRESS:", "P.O.:", "PO.:", "P.S.:",
            "DISTRICT:", "STATE:", "PINCODE:", "FATHER'S NAME:", "OCCUPATION:", "_ OCCUPATION:",
            "EMAIL-ID: _", "EMAIL-ID:", "EMAILID:_", "EMAILID:", "EMAIL ID:", "MOTHER'S NAME:", "APPLICATION DATE:",
            "REG. NO.:", "REG. DATE:", "BLOOD GROUP:", "DATE OF BIRTH:",
            "PLACE OF BIRTH:", "MOBILE NO.:", "MOBILE NO:", "MOBILE NO. :", "NATIONALITY:", "PRESENT ADDRESS:",
            "OCCUPATION", "AT THIS COLLEGE. NECESSARY",
            "SEAT ALLOTMENT NO.:", "ACADEMIC SESSION:", "ACADEMIC SESSION: _", "PROGRAMME OF STUDY:", "•",
            "QUALIFICATION DETAILS:", "RELATIONSHIP WITH STUDENT:", "HOUSE NUMBER:", "BLOCK:", "STREET", "VILLAGE OR TOWN:", "ADDRESS DETAILS (PERMANENT ADDRESS):", "ADDRESS DETAILS (PRESENT ADDRESS):", "LOCAL GUARDIAN DETAILS: (IN CASE OF OUTSTATION STUDENT)", "NEET UG DETAILS:", "PERCENTAGE (%)", "BIOLOGY", "CHEMISTRY", "PHYSICS", "SUBJECT", "CLASS XII DETAILS:", "YEAR OF PASSING", "%/CGPA|", "%/CGPA", "CLASS XII", "CLASS X", "INSTITUTE/BOARD", "PREVIOUS ACADEMIC QUALIFICATION:", "QUOTA:", "CATEGORY:", "ALL INDIA RANK:", "PERCENTILE:", "TOTAL MARKS OBTAINED:", "MARKS OBTAINED", "ROLL NO.:", "APPLICATION NO.:", "TOTAL MARKS:", "EXAMINATION", "TOTAL :", "DISTRICT:"
        ]

        cleaned_text = text
        for replacement in replacements:
            if replacement == "•":
                cleaned_text = cleaned_text.replace(replacement, ".")
            else:
                cleaned_text = cleaned_text.replace("MEDICAL COLLEGE", "").replace("ALL FOR EDUCATION, EDUCATION FOR ALL", "").replace("REG. OFFICE: A2/15, KALYANI, DIST.: NADIA,", "").replace("REG. OFFICE: A2/15, KALYANI, DIST: NADIA,", "").replace("ALL FOR EDUCATION, FUCATION FOR ALF", "").replace("RESPECTED SIR/MADAM,", "").replace("PARTICULARS ARE", "").replace("FURNISHED BELOW FOR YOUR KIND CONSIDERATION.", "").replace("PIN 741235, WEST BENGAL, INDIA", "").replace("MAIL ID: INFO.JMNEDUR@GMAIL.COM", "").replace("CONTACT NO: +91 9831111817", "").replace("CAMPUS: UTTAR PANCHPOTA, P.O & P. S. CHAKDAHA,", "").replace("DIST. NADIPIP INSTALLA, PIN 741222, WEST BENGAL, INDIA", "").replace("DIST. NADIA, PIN 741222, WEST BENGAL, INDIA", "FORM-START").replace("JMN", "").replace("ADMISSION FORM", "").replace("THE PRINCIPAL,", "").replace("JMN MEDICAL COLLEGE,", "").replace("UTTAR PANCHPOTA, P.O. & P.S. CHAKDAHA,", "").replace("DIST. NADIA, PINCODE - 741222,", "").replace("WEST BENGAL, INDIA.", "").replace("PASTE RECENT", "").replace("PASSPORT-SIZE", "").replace("COLOUR", "").replace("PHOTOGRAPH OF", "").replace("THE CANDIDATE", "").replace("AND SIGN ACROSS", "").replace("THE PHOTOGRAPH.", "").replace("RESPECTED SIR / MADAM,", "").replace("I HEREBY APPLY FOR ADMISSION TO THE MBBS COURSE IN SESSION", "MBBS COURSE IN SESSION:").replace("PARTICULARS ARE FURNISHED BELOW FOR YOUR KIND CONSIDERATION.", "").replace("KINDLY USE CAPITAL LETTERS ONLY", "").replace("JMN MEDICAL COLLEGE", "").replace("WWW.JMNMEDICALCOLLEGE.ORG.IN", "").replace("WWW.MEDICALCOLLEGE.ORG.IN", "").replace("AT THIS COLLEGE. NECESSARY", "").replace("@@", "@").replace("@GIMAIIL.COM", "@GMAIL.COM").replace("@GMIL.CO", "@GMAIL.COM").replace("P.O.:", "P.O.:").replace("P.O. :", "P.O.:").replace("PO:", "P.O.:").replace("P.O :", "P.O.:").replace("P.O:", "P.O.:").replace("P.S.:", "P.S.:").replace("P.S. :", "P.S.:").replace("PS.:", "P.S.:").replace("PS:", "P.S.:").replace("P.S :", "P.S.:").replace("P.S:", "P.S.:").replace("•", ".").replace("MOBILE NO.:", "MOBILE NO:").replace("MOBILE NO :", "MOBILE NO:").replace("WWW.JMMMEDICALCOLLEGE.ORG.IN", "") #.replace("STUDENT DETAILS:", "").replace("PARENT DETAILS:", "").replace("LOCAL GUARDIAN DETAILS: (IN CASE OF OUTSTATION STUDENT)", "").replace("QUALIFICATION DETAILS:", "")
                cleaned_text = cleaned_text.replace(replacement, "\n" + replacement)

        cleaned_lines = [line for line in cleaned_text.splitlines() if line.strip() != "" and line.strip() != "TO" and line.strip() != ","]
        cleaned_text = "\n".join(cleaned_lines)

        return cleaned_text
    except Exception as e:
        print(f"Text replacement failed: {e}")
        return text

def extract_human_picture(image_path):
    try:
        # Load the image
        img = cv2.imread(image_path)
        
        # Enhance the image to reduce haze and improve quality
        denoise_strength = 3  # Customizable denoise strength
        img = cv2.fastNlMeansDenoisingColored(img, None, denoise_strength, denoise_strength, 7, 21)  # Denoising to reduce haze
        # Increase contrast
        contrast_alpha = 1  # Customizable contrast control (1.0-3.0)
        brightness_beta = 5.5  # Customizable brightness control (0-100)
        img = cv2.convertScaleAbs(img, alpha=contrast_alpha, beta=brightness_beta) 
        
        # Load the pre-trained Haar Cascade classifier for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Convert the image to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        # If a face is detected, extract the first one
        if len(faces) > 0:
            (x, y, w, h) = faces[0]  # Get the coordinates of the first detected face
            
            # Extend the cropping area to include the full human picture
            x_extended = max(0, x - int(w * 0.5))  # Extend left by 50% of the width(extend left)
            y_extended = max(0, y - int(h * 0.5))  # Extend top by 50% of the height(extend Top)
            w_extended = int(w * 2.10)  # New width: 210% of the original width(extend Right)
            h_extended = int(h * 2.75)  # New height: 275% of the original height (extend down)
            
            face_image = img[y_extended:y_extended + h_extended, x_extended:x_extended + w_extended]  # Crop the full human picture from the image
            
            # Save the extracted face image
            cv2.imwrite('extracted/extracted_face.jpg', face_image)
            return 'extracted/extracted_face.jpg'
        return None  # No face detected
    except Exception as e:
        print(f"Face extraction failed: {e}")
        return None
    
def extract_signature(image_path):
    try:
        # Load the image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding for better signature detection
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours of the signature
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours based on area to find the signature
        if contours:
            # Sort contours by their y-coordinate (bottom-most first)
            sorted_contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1], reverse=True)
            
            # Iterate through sorted contours to find the signature
            for contour in sorted_contours:
                area = cv2.contourArea(contour)
                # Adjust the threshold based on the image size
                threshold = int(img.shape[0] * img.shape[1] * 0.001)  # 0.1% of the image area
                if area > threshold:
                    x, y, w, h = cv2.boundingRect(contour)
                    # Reduce the border crop by adjusting the cropping dimensions
                    border_reduction = 0.05  # Reduce the border by 10%
                    x_extended = int(x - w * (border_reduction - 0.07))  # Extend left by 20% of the width
                    y_extended = int(y + h * border_reduction)
                    w_extended = int(w * (1 - border_reduction))  # Reduce width by 5%
                    h_extended = int(h * (1 - 2 * border_reduction))
                    signature_image = img[y_extended:y_extended + h_extended, x_extended:x_extended + w_extended]  # Crop the signature
                    
                    # Save the extracted signature image
                    cv2.imwrite('extracted/extracted_signature.jpg', signature_image)
                    return 'extracted/extracted_signature.jpg'
        return None  # No signature detected
    except Exception as e:
        print(f"Signature extraction failed: {e}")
        return None
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Delete the uploads directory if it exists
        if os.path.exists('./uploads'):
            shutil.rmtree('./uploads')
        
        # Create a new uploads directory
        os.makedirs('./uploads')

        # Set API key for front upload
        os.environ['GEMINI_AI_API_KEY_1'] = 'AIzaSyDdfo2NmJDEzzPcnfdUyn9LD4NAFUE2efI'#
        os.environ['GEMINI_AI_API_KEY_2'] = 'AIzaSyDdfo2NmJDEzzPcnfdUyn9LD4NAFUE2efI'#
        API_KEY_1 = os.environ['GEMINI_AI_API_KEY_1']
        API_KEY_2 = os.environ['GEMINI_AI_API_KEY_2']
        genai.configure(api_key=API_KEY_1)
        
        # Get the image file and key from the request
        file = request.files.get('file_1')  # Ensure the key matches what Postman sends
        key = request.form.get('key_1')  # Get the key from the form data

        if file and key:
            file_path = f"./uploads/{file.filename}"
            file.save(file_path)

        # Get the image data from the request
        # image_data = request.get_data()
        #print(image_data)
        
        # # # Save the image data to a temporary file
        # file_path = f"./uploads/temp_image.jpg"
        # with open(file_path, 'wb') as f:
        #     f.write(image_data)
            
            # Extract human picture from the uploaded image
            extracted_face_path = extract_human_picture(file_path)
            if extracted_face_path:
                print(f"Extracted face image saved at: {extracted_face_path}")

            # Save the extracted image with the key's text name to external path
            #Save in production
            #new_file_path = f"/home/sigmaproductsco/public_html/jmn/production/public/uploads/student_image/{key}_img.jpg"
            #Save in Sit
            #new_file_path = f"/home/sigmente/public_html/sit/jmn/public/uploads/student_image/{key}_img.jpg"
            #Save in local
            new_file_path = f"C:/Users/Atanu Roy/Downloads/laravel/face/{key}_img.jpg"

            shutil.copy(extracted_face_path, new_file_path)  # Copy the extracted image to the new path

            # Debugging: Check if the file is saved
            print(f"File saved at: {new_file_path}")
            
            # First try to extract text using Gemini
            text = extract_text_with_gemini(file_path)
            if text and ':' in text:  # Check if Gemini extraction is successful and contains ':'
                #print(text)
                text = text.upper()
                if text:
                    print(text)
                    replaced_text = replace_text(text)
                    with open('extracted_text.txt', 'w', encoding='utf-8') as text_file:
                        text_file.write(replaced_text)
                    with open('extracted_text.txt', 'r', encoding='utf-8') as text_file:
                        cleaned_text = text_file.read().splitlines()
                    print(cleaned_text)
                    save_as_json(cleaned_text)  # Process and save as JSON
                    # Scan the data file and return the data
                    # with open('data.json', 'r', encoding='utf-8') as data_file:
                    #     data_content = json.load(data_file)
                    return jsonify({"status": 200, "message": {'msg':'First page uploaded successfully!'}}), 200 #, "data": data_content
            else:   
                # Switch to the second API key if the first one fails
                genai.configure(api_key=API_KEY_2)
                text = extract_text_with_gemini(file_path)
                if text and ':' in text:
                    #print(text)
                    text = text.upper()
                    if text:
                        print(text)
                        replaced_text = replace_text(text)
                        with open('extracted_text.txt', 'w', encoding='utf-8') as text_file:
                            text_file.write(replaced_text)
                        with open('extracted_text.txt', 'r', encoding='utf-8') as text_file:
                            cleaned_text = text_file.read().splitlines()
                        print(cleaned_text)
                        save_as_json(cleaned_text)  # Process and save as JSON
                        # Scan the data file and return the data
                        # with open('data.json', 'r', encoding='utf-8') as data_file:
                        #     data_content = json.load(data_file)
                        return jsonify({"status": 200,"img": {'img': new_file_path }, "message": {'msg':'First page uploaded successfully!'}}), 200 #, "data": data_content
                else:
                    print("Gemini extraction failed or no valid text found. Falling back to OCR Space.")
                    # Fallback to OCR Space if both keys fail
                    text = extract_text_from_image(file_path)
                    #print(text)
                    text = text.upper()
                    if text:
                        print(text)
                        print("OCR Space extraction successful.")
                        replaced_text = replace_text(text)
                        with open('extracted_text.txt', 'w', encoding='utf-8') as text_file:
                            text_file.write(replaced_text)
                        with open('extracted_text.txt', 'r', encoding='utf-8') as text_file:
                            cleaned_text = text_file.read().splitlines()
                        print(cleaned_text)
                        save_as_json(cleaned_text)  # Process and save as JSON
                        # Scan the data file and return the data
                        # with open('data.json', 'r', encoding='utf-8') as data_file:
                        #     data_content = json.load(data_file)
                        return jsonify({"status": 200,"img": {'img': new_file_path }, "message": {'msg':'First page uploaded successfully!'}}), 200 #, "data": data_content
                    else:
                        # Delete the uploads directory if it exists    
                        if os.path.exists('./uploads'):  
                            shutil.rmtree('./uploads')
                        return jsonify({"status": 400, "message": {'msg':'Failed to extract text from OCR Space.'}}), 400
                        
        else:
            return jsonify({"status": "500","data": [],"message": {"msg": "Select Page 1"}}), 200
    except Exception as e:
        print(f"Error during extraction: {e}")
        if os.path.exists(file_path):  # Delete the uploaded file if it exists
            os.remove(file_path)
        # Delete the uploads directory if it exists    
        if os.path.exists('./uploads'):  
            shutil.rmtree('./uploads')
        return jsonify({"status": 400, "message": {'msg':'An error occurred during processing.'}}), 500
            
    finally:
        # Delete the temporary image file after processing
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        # Delete the uploads directory if it exists    
        if os.path.exists('./uploads'):  
            shutil.rmtree('./uploads')

@app.route('/upload_back', methods=['POST'])
def upload_back():
    try:
        # Delete the uploads directory if it exists
        if os.path.exists('./uploads'):
            shutil.rmtree('./uploads')
        
        # Create a new uploads directory
        os.makedirs('./uploads')

        # Set API key for back upload
        os.environ['GEMINI_AI_API_KEY_1'] = 'AIzaSyDdfo2NmJDEzzPcnfdUyn9LD4NAFUE2efI'#
        os.environ['GEMINI_AI_API_KEY_2'] = 'AIzaSyDdfo2NmJDEzzPcnfdUyn9LD4NAFUE2efI'#
        API_KEY_1 = os.environ['GEMINI_AI_API_KEY_1']
        API_KEY_2 = os.environ['GEMINI_AI_API_KEY_2']
        genai.configure(api_key=API_KEY_1)

        # Get the image file and key from the request
        file = request.files.get('file_2')  # Ensure the key matches what Laravel sends
        key = request.form.get('key_2')  # Get the key from the form data

        if file and key:
            file_path = f"./uploads/back_{file.filename}"
            file.save(file_path)
        
        # Get the image data from the request
        # image_data = request.get_data()
        
        # # Save the image data to a temporary file
        # file_path = f"./uploads/temp_image.jpg"
        # with open(file_path, 'wb') as f:
        #     f.write(image_data)
            
            # Extract signature from the uploaded image
            extracted_signature_path = extract_signature(file_path)
            if extracted_signature_path:
                print(f"Extracted signature image saved at: {extracted_signature_path}")

            # Save the extracted signature image with the key's text name
            #Save in production
            #new_file_path = f"/home/sigmaproductsco/public_html/jmn/production/public/uploads/student_signature/{key}_sig.jpg"
            #Save in Sit
            #new_file_path = f"/home/sigmente/public_html/sit/jmn/public/uploads/student_signature/{key}_sig.jpg"
            #Save in local
            new_file_path = f"C:/Users/Atanu Roy/Downloads/laravel/sig/{key}_img.jpg"

            shutil.copy(extracted_signature_path, new_file_path)  # Copy the extracted image to the new path

            # Debugging: Check if the file is saved
            print(f"Signature file saved at: {new_file_path}")

            # First try to extract text using Gemini
            text = extract_text_with_back_gemini(file_path)
            if text and ':' in text:  # Check if Gemini extraction is successful and contains ':'
                #print(text)
                text = text.upper()
                if text:
                    print(text)
                    replaced_text = replace_text_back(text)  # Get cleaned text
                    with open('extracted_text_back.txt', 'w', encoding='utf-8') as text_file:  # Specify encoding
                        text_file.write(replaced_text)
                    with open('extracted_text_back.txt', 'r', encoding='utf-8') as text_file:  # Specify encoding
                        cleaned_text = text_file.read().splitlines()
                    print(cleaned_text)
                    save_as_json_back(cleaned_text)  # Save processed data as JSON
                    
                    # Check if the JSON file exists and is not empty
                    with open('data.json', 'r', encoding='utf-8') as json_file:
                        json_content = json_file.read()
                        if json_content.strip():  # Check if the content is not empty
                            loaded_json = json.loads(json_content)
                            # response_data = {
                            #                 "status": 200,
                            #                 "message": {'msg':'Data loaded successfully'},
                            #                 "data": loaded_json
                            #                 }
                            # return jsonify(response_data), 200
                        else:
                            print("JSON file is empty.")
                            return jsonify({"status": 400, "message": {'msg':'JSON file is empty.'}}), 400
                else:
                    return jsonify({"status": 400, "message": {'msg':'Failed to process text.'}}), 400
            else:
                # Switch to the second API key if the first one fails
                genai.configure(api_key=API_KEY_2)
                text = extract_text_with_back_gemini(file_path)
                if text and ':' in text:
                    #print(text)
                    text = text.upper()
                    if text:
                        print(text)
                        replaced_text = replace_text_back(text)  # Get cleaned text
                        with open('extracted_text_back.txt', 'w', encoding='utf-8') as text_file:  # Specify encoding
                            text_file.write(replaced_text)
                        with open('extracted_text_back.txt', 'r', encoding='utf-8') as text_file:  # Specify encoding
                            cleaned_text = text_file.read().splitlines()
                        print(cleaned_text)
                        save_as_json_back(cleaned_text)  # Save processed data as JSON
                        
                        # Check if the JSON file exists and is not empty
                        with open('data.json', 'r', encoding='utf-8') as json_file:
                            json_content = json_file.read()
                            if json_content.strip():  # Check if the content is not empty
                                loaded_json = json.loads(json_content)
                                # response_data = {
                                #             "status": 200,
                                #             "message": {'msg':'Data loaded successfully'},
                                #             "data": loaded_json
                                #             }
                                # return jsonify(response_data), 200
                            else:
                                print("JSON file is empty.")
                                return jsonify({"status": 400, "message": {'msg':'JSON file is empty.'}}), 400
                    else:
                        return jsonify({"status": 400, "message": {'msg':'Failed to process text.'}}), 400
                else:
                    print("Gemini extraction failed or no valid text found. Falling back to OCR Space.")
                    # Fallback to OCR Space if both keys fail
                    text = extract_text_from_back_image(file_path)
                    #print(text)
                    text = text.upper()
                    if text:
                        print(text)
                        print("OCR Space extraction successful.")
                        replaced_text = replace_text_back(text)  # Get cleaned text
                        with open('extracted_text_back.txt', 'w', encoding='utf-8') as text_file:  # Specify encoding
                            text_file.write(replaced_text)
                        with open('extracted_text_back.txt', 'r', encoding='utf-8') as text_file:  # Specify encoding
                            cleaned_text = text_file.read().splitlines()
                        print(cleaned_text)
                        save_as_json_back(cleaned_text)  # Save processed data as JSON
                        
                        # Check if the JSON file exists and is not empty
                        with open('data.json', 'r', encoding='utf-8') as json_file:
                            json_content = json_file.read()
                            if json_content.strip():  # Check if the content is not empty
                                loaded_json = json.loads(json_content)
                                # response_data = {
                                #             "status": 200,
                                #             "message": {'msg':'Data loaded successfully'},
                                #             "data": loaded_json
                                #             }
                                # return jsonify(response_data), 200
                            else:
                                print("JSON file is empty.")
                                return jsonify({"status": 400, "message": {'msg':'JSON file is empty.'}}), 400
                    else:
                        # Delete the uploads directory if it exists    
                        if os.path.exists('./uploads'):  
                            shutil.rmtree('./uploads')
                        return jsonify({"status": 400, "message": {'msg':'Failed to extract text from OCR Space.'}}), 400
        else:
            return jsonify({"status": "500","data": [],"message": {"msg": "Select Page 2"}}), 200
    except Exception as e:
        print(f"Error during extraction: {e}")
        # Delete the uploaded file if it exists
        if os.path.exists(file_path):  
            os.remove(file_path)
        # Delete the uploads directory if it exists    
        if os.path.exists('./uploads'):  
            shutil.rmtree('./uploads')
        return jsonify({"status": 400, "message": {'msg':'An error occurred during processing.'}}), 500
    finally:
        # Delete the temporary image file after processing
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        # Delete the uploads directory if it exists    
        if os.path.exists('./uploads'):  
            shutil.rmtree('./uploads')
        if file and key:
            with open('data.json', 'r', encoding='utf-8') as json_file:
                loaded_json = json.load(json_file)
                for item in loaded_json.values():  # Change to iterate over values

                    if 'FORM NO.' in item:
                        item['form_no'] = item.pop('FORM NO.')
                    if 'NAME' in item:
                        item['student_name'] = item.pop('NAME')
                    if 'BLOOD GROUP' in item:
                        item['student_blood_group'] = item.pop('BLOOD GROUP')
                    if 'DATE OF BIRTH' in item:
                        item['student_dob'] = item.pop('DATE OF BIRTH')
                    if 'PLACE OF BIRTH' in item:
                        item['student_place_of_dob'] = item.pop('PLACE OF BIRTH')
                    if 'CONTACT NO' in item:
                        item['student_contact_no'] = item.pop('CONTACT NO')
                    if 'CONTACT NO.' in item:
                        item['student_contact_no'] = item.pop('CONTACT NO.')
                    if 'NATIONALITY' in item:
                        item['student_nationality'] = item.pop('NATIONALITY')
                    if 'MARITAL STATUS' in item:
                        item['student_marital'] = item.pop('MARITAL STATUS')
                    if 'CASTE' in item:
                        item['student_cast'] = item.pop('CASTE')
                    if 'GENDER' in item:
                        item['student_gender'] = item.pop('GENDER')
                    if 'RELIGION' in item:
                        item['student_religion'] = item.pop('RELIGION')
                    if 'MOTHER' in item:  
                        item['student_mothertounge'] = item.pop('MOTHERTOUNGE') if 'MOTHERTOUNGE' in item else item.pop('MOTHERTONGUE',     None)
                    if 'MOTHERTONGUE' in item:  
                        item['student_mothertongue'] = item.pop('MOTHERTONGUE')
                    if 'MOTHERTOUNGE' in item:  
                        item['student_mothertongue'] = item.pop('MOTHERTOUNGE')
                    if 'EMAIL ID' in item:
                        item['student_email'] = item.pop('EMAIL ID')
                    if 'PERMANENT ADDRESS' in item:
                        item['permenent_address'] = item.pop('PERMANENT ADDRESS')  
                    if 'P.O.' in item:
                        item['permenent_post_office'] = item.pop('P.O.')  
                    if 'P.S.' in item:
                        item['permenent_police_station'] = item.pop('P.S.')  
                    if 'DISTRICT' in item:
                        item['permenent_district'] = item.pop('DISTRICT')  
                    if 'STATE' in item:
                        item['permenent_state'] = item.pop('STATE')  
                    if 'PINCODE' in item:
                        item['permenent_pincode'] = item.pop('PINCODE')
                    if 'PRESENT ADDRESS' in item:
                        item['present_address'] = item.pop('PRESENT ADDRESS')
                    if 'P.O._2' in item:
                        item['present_post_office'] = item.pop('P.O._2')
                    if 'P.S._2' in item:
                        item['present_police_station'] = item.pop('P.S._2')
                    if 'DISTRICT_2' in item:
                        item['present_district'] = item.pop('DISTRICT_2')
                    if 'STATE_2' in item:
                        item['present_state'] = item.pop('STATE_2')
                    if 'PINCODE_2' in item:
                        item['present_pincode'] = item.pop('PINCODE_2')
                    if "FATHER'S NAME" in item:
                        item['father_name'] = item.pop("FATHER'S NAME")
                    if 'OCCUPATION' in item:
                        item['father_occupation'] = item.pop('OCCUPATION')
                    if 'MOBILE NO' in item:
                        item['father_mobile_no'] = item.pop('MOBILE NO')
                    if 'EMAIL-ID' in item: 
                        item['father_email_id'] = item.pop('EMAIL-ID')
                    if 'EMAIL ID' in item:
                        item['father_email_id'] = item.pop('EMAIL ID')
                    if "MOTHER'S NAME" in item:
                        item['mother_name'] = item.pop("MOTHER'S NAME")
                    if 'OCCUPATION_2' in item:
                        item['mother_occupation'] = item.pop('OCCUPATION_2')
                    if 'MOBILE NO_2' in item:
                        item['mother_mobile_no'] = item.pop('MOBILE NO_2')
                    if 'EMAIL-ID_2' in item:
                        item['mother_email_id'] = item.pop('EMAIL-ID_2')
                    if 'EMAIL ID_2' in item:
                        item['mother_email_id'] = item.pop('EMAIL ID_2')
                    if 'NAME_2' in item:
                        item['guardian_name'] = item.pop('NAME_2')
                    if 'RELATIONSHIP WITH STUDENT' in item:
                        item['guardian_relationship'] = item.pop('RELATIONSHIP WITH STUDENT')
                    if 'MOBILE NO_3' in item:
                        item['guardian_mobile'] = item.pop('MOBILE NO_3')
                    if 'EMAIL-ID_3' in item:
                        item['guardian_email'] = item.pop('EMAIL-ID_3')
                    if 'EMAIL ID_3' in item:
                        item['guardian_email'] = item.pop('EMAIL ID_3')
                    if 'PRESENT ADDRESS_2' in item:
                        item['guardian_address'] = item.pop('PRESENT ADDRESS_2')
                    if 'OCCUPATION_3' in item:
                        item['guardian_occupation'] = item.pop('OCCUPATION_3')
                    if 'P.O._3'  in item:
                        item['guardian_post_office'] = item.pop('P.O._3')
                    if 'P.O_3'  in item:
                        item['guardian_post_office'] = item.pop('P.O_3')    
                    if 'P.S._3' in item:
                        item['guardian_police_station'] = item.pop('P.S._3')
                    if 'P.S_3' in item:
                        item['guardian_police_station'] = item.pop('P.S_3')
                    if 'DISTRICT_3' in item:
                        item['guardian_district'] = item.pop('DISTRICT_3')
                    if 'STATE_3' in item:
                        item['guardian_state'] = item.pop('STATE_3')
                    if 'PINCODE_3' in item:
                        item['guardian_pincode'] = item.pop('PINCODE_3')
                    if 'APPLICATION DATE' in item:
                        item['application_date'] = item.pop('APPLICATION DATE')
                    if 'ACADEMIC SESSION' in item:
                        item['accademic_session'] = item.pop('ACADEMIC SESSION')
                    if 'PROGRAMME OF STUDY' in item:
                        item['programme_study'] = item.pop('PROGRAMME OF STUDY')
                    if 'SEAT ALLOTMENT NO.' in item:
                        item['seat_allotment'] = item.pop('SEAT ALLOTMENT NO.')
                    if 'SEAT ALLOTMENT NO' in item:
                        item['seat_allotment'] = item.pop('SEAT ALLOTMENT NO')
                    if 'APPLICATION NO.' in item:
                        item['neet_application_no'] = item.pop('APPLICATION NO.')
                    if 'APPLICATION NO' in item:
                        item['neet_application_no'] = item.pop('APPLICATION NO')
                    if 'ROLL NO.' in item:
                        item['neet_roll_no'] = item.pop('ROLL NO.')
                    if 'ROLL NO' in item:
                        item['neet_roll_no'] = item.pop('ROLL NO')
                    if 'TOTAL MARKS OBTAINED' in item:
                        item['neet_total_marks'] = item.pop('TOTAL MARKS OBTAINED')
                    if 'PERCENTILE' in item:
                        item['neet_percentile'] = item.pop('PERCENTILE')
                    if 'CATEGORY' in item:
                        item['neet_category'] = item.pop('CATEGORY')
                    if 'QUOTA' in item:
                        item['neet_quota'] = item.pop('QUOTA')
                    if 'ALL INDIA RANK' in item:
                        item['neet_rank'] = item.pop('ALL INDIA RANK')
                    if 'INSTITUTE/BOARD' in item:
                        item['board_1'] = item.pop('INSTITUTE/BOARD')
                    if '%/CGPA' in item:    
                        item['cgpa_1'] = item.pop('%/CGPA')
                    if 'YEAR OF PASSING' in item:
                        item['year_of_pass_1'] = item.pop('YEAR OF PASSING')
                    if 'INSTITUTE/BOARD_2' in item:
                        item['board_0'] = item.pop('INSTITUTE/BOARD_2')
                    if '%/CGPA_2' in item:
                        item['cgpa_0'] = item.pop('%/CGPA_2')
                    if 'YEAR OF PASSING_2' in item:
                        item['year_of_pass_0'] = item.pop('YEAR OF PASSING_2')
                    if 'MARKS OBTAINED' in item:
                        item['marks_0'] = item.pop('MARKS OBTAINED')
                    if 'TOTAL MARKS' in item:
                        item['total_marks_0'] = item.pop('TOTAL MARKS')
                    if 'PERCENTAGE(%)' in item:
                        item['percentage_0'] = item.pop('PERCENTAGE(%)')
                    if 'MARKS OBTAINED_2' in item:
                        item['marks_1'] = item.pop('MARKS OBTAINED_2')
                    if 'TOTAL MARKS_2' in item:
                        item['total_marks_1'] = item.pop('TOTAL MARKS_2')
                    if 'PERCENTAGE(%)_2' in item:
                        item['percentage_1'] = item.pop('PERCENTAGE(%)_2')
                    if 'MARKS OBTAINED_3' in item:
                        item['marks_2'] = item.pop('MARKS OBTAINED_3')
                    if 'TOTAL MARKS_3' in item:
                        item['total_marks_2'] = item.pop('TOTAL MARKS_3')
                    if 'PERCENTAGE(%)_3' in item:
                        item['percentage_2'] = item.pop('PERCENTAGE(%)_3')
                    if 'SIGNATURE OF THE CANDIDATE' in item:
                        item['candidate_signature'] = item.pop('SIGNATURE OF THE CANDIDATE')
                    if 'DATE OF SUBMISSION' in item:
                        item['submission_date'] = item.pop('DATE OF SUBMISSION')



            # Save the updated data to data_final.json
            with open('data_final.json', 'w', encoding='utf-8') as final_json_file:
                json.dump(loaded_json, final_json_file, ensure_ascii=False, indent=4)

            response_data = {
                "status": 200,
                "message": {'msg':'Second page uploaded successfully!'},
                "img": {'img': f"public/uploads/student_image/{key}_img.jpg" },
                "sig": {'sig': f"public/uploads/student_signature/{key}_sig.jpg" },
                "data": loaded_json
            }
            # with open('data_final.json', 'w', encoding='utf-8') as final_json_file:
            #     json.dump({}, final_json_file, ensure_ascii=False, indent=4)  # Empty the data_final.json
            # with open('data.json', 'w', encoding='utf-8') as final_json_file:
            #     json.dump({}, final_json_file, ensure_ascii=False, indent=4)  # Empty the data.json
            # Get the key from the form data
            #key = request.form.get('key')  # Ensure the key is retrieved from the form data
            if key:  # Check if the key is provided
                # Scan the loaded JSON data and create a new file in the specified directory
                os.makedirs('extracted/json', exist_ok=True)  # Create the directory if it doesn't exist
                with open(f'extracted/json/{key}.json', 'w', encoding='utf-8') as json_file:
                    json.dump(loaded_json, json_file, ensure_ascii=False, indent=4)

            return jsonify(response_data), 200
        else:
            return jsonify({"status": "500","data": [],"message": {"msg": "Select Page 2"}}), 200

def extract_text_from_back_image(image_path):
    try:
        # Implement your specific text extraction logic for the back page here
        # For example, using a different OCR API or method
        img = cv2.imread(image_path)
        file_bytes = io.BytesIO(cv2.imencode(".jpg", img)[1])
        url_api = "https://api.ocr.space/parse/image"
        result = requests.post(
            url_api,
            files={"image.jpg": file_bytes},
            data={
                "apikey": "K83686776688957",
                "language": "eng",
                "isOverlayRequired": True,
                "detectOrientation": True,
                "scale": True,
                "isTable": True,
                "OCREngine": 2
            }
        )

        result = result.content.decode()
        result = json.loads(result)
        parsed_results = result.get("ParsedResults")
        if parsed_results:
            text_detected = parsed_results[0].get("ParsedText")
        else:
            text_detected = ""
        return text_detected
    except Exception as e:
        print(f"Back image extraction failed: {e}")
        return ""

def replace_text_back(text):
    try:
        cleaned_text = text
        replacements = [
            "MEDICAL COLLEGE", "ALL FOR EDUCATION, LAUCATION FOR ALL", "REG. OFFICE: A2/15, KALYANI, DIST.: NADIA,", "PIN 741235, WEST BENGAL, INDIA", "MAIL ID: INFO.JMNEDUR@GMAIL.COM", "CAMPUS: UTTAR PANCHPOTA, P.O & P. S. CHAKDAHA,", "DIST. NADIA, PIN 741222, WEST BENGAL, INDIA","ROLLNO:","PERCENTILE:","CATEGORY:","TOTAL MARKS OBTAINED:","PERCENTILE:"
        ]
        cleaned_text = text
        for replacement in replacements:
            if replacement == "•":
                cleaned_text = cleaned_text.replace(replacement, ".")
            else:
                cleaned_text = cleaned_text.replace("MEDICAL COLLEGE", "").replace("ALL FOR EDUCATION, LAUCATION FOR ALL", "").replace("REG. OFFICE: A2/15, KALYANI, DIST.: NADIA,", "").replace("PIN 741235, WEST BENGAL, INDIA", "").replace("MAIL ID: INFO.JMNEDUR@GMAIL.COM", "").replace("MAIL ID: INFO.EDUR@GMAIL.COM", "").replace("CONTACT NO: +91 9831111817", "").replace("CAMPUS: UTTAR PANCHPOTA, P.O & P. S. CHAKDAHA,", "").replace("DIST. NADIA, PIN 741222, WEST BENGAL, INDIA", "").replace("I SOLEMNLY DECLARE THAT -", "").replace("I SOLEMNLY DECLARE THAT-", "").replace("A. ALL INFORMATION GIVEN ABOVE IS TRUE AND CORRECT TO THE BEST OF MY KNOWLEDGE.", "").replace("B. I HAVE NOT SUBMITTED ANY OTHER APPLICATION THROUGH AN ONLINE SYSTEM.", "").replace("C. IN CASE ANY OF THE DOCUMENTS ARE SUBSEQUENTLY DETECTED FAKE OR FALSE, MY ADMISSION MAY BE", "").replace("CANCELLED BY THE COLLEGE AUTHORITY AT ANY TIME.", "").replace("D. I HAVE RETAINED A SUFFICIENT NUMBER OF HARD COPIES AND SOFT COPIES OF ALL THE ORIGINAL CERTIFICATES", "").replace("THAT WILL BE KEPT IN THE CUSTODY OF THE COLLEGE ADMINISTRATION SINCE IT IS DIFFICULT FOR THE LATTER TO", "").replace("GET THESE DOCUMENTS EVERY NOW AND THEN FOR OFFICIAL USE.", "").replace("I SHALL ABIDE BY THE ACTIONS/DECISIONS TAKEN BY THE COLLEGE ADMINISTRATION.", "").replace("WWW.JMMMEDICALCOLLEGE.ORG.IN", "").replace("JMN MEDICAL COLLEGE", "").replace("CLASS XII DETAILS::", "").replace("CLASS XII DETAILS:", "").replace("P.O.:", "P.O._3:").replace("P.O. :", "P.O._3:").replace("PO:", "P.O._3:").replace("P.O :", "P.O._3:").replace("P.O:", "P.O._3:").replace("P.S.:", "P.S._3:").replace("P.S. :", "P.S._3:").replace("PS.:", "P.S._3:").replace("PS:", "P.S._3:").replace("P.S :", "P.S._3:").replace("P.S:", "P.S._3:").replace("•", ".").replace("% CGPA", "%/CGPA").replace("%CGPA", "%/CGPA").replace("EMAIL-ID:", "EMAIL-ID_3:")
                cleaned_text = cleaned_text.replace(replacement, "\n" + replacement)

        cleaned_lines = [line for line in cleaned_text.splitlines() if line.strip() != "" and line.strip() != "TO" and line.strip() != "," and line.strip() != "JMN"]

        cleaned_text = "\n".join(cleaned_lines)

        return cleaned_text
    except Exception as e:
        print(f"Back text replacement failed: {e}")
        return text

def save_as_json(data):
    try:
        json_data = {
            "formStart": {},
            "studentDetails": {},
            "permenent": {},
            "present": {},
            "parentDetails": {}
        }
        current_section = None
        count_dict = {}

        for item in data:
            item = item.strip()

            if ("FORM NO.:" in item or "FORM-START" in item or "FORM" in item or "FORM START" in item) and current_section != "formStart":
                current_section = "formStart"
                continue
            elif "ADDRESS DETAILS (PERMANENT ADDRESS)" in item or "(PERMANENT ADDRESS)" in item:
                current_section = "permenent"
                continue
            elif "ADDRESS DETAILS (PRESENT ADDRESS)" in item or "(PRESENT ADDRESS)" in item:
                current_section = "present"
                continue
            elif "STUDENT DETAILS" in item or "## STUDENT" in item:
                current_section = "studentDetails"
                continue
            elif "PARENT DETAILS" in item or "## PARENT DETAILS" in item:
                current_section = "parentDetails"
                continue


            if current_section:
                if ':' in item:
                    key, value = item.split(':', 1)
                    value = value.replace('\t', '').replace('_\t', '').replace('-\t', '').replace('\t_', '')
                    if key.strip() in count_dict:
                        count_dict[key.strip()] += 1
                        key = f"{key.strip()}_{count_dict[key.strip()]}"
                    else:
                        count_dict[key.strip()] = 1
                    json_data[current_section][key.strip()] = value.strip()

        # Ensure the JSON file is saved correctly
        with open('data.json', 'w') as json_file:
            json.dump(json_data, json_file, indent=4)  # Ensure proper indentation for readability
    except Exception as e:
        print(f"Error saving JSON: {e}")

def save_as_json_back(data):
    try:
        json_data = {

            "localGuardian": {},
            "qualification": {},
            "netug": {},
            "xii": {},
            "x": {},
            "physics": {},
            "chemistry": {},
            "biology": {},
            "declaration": {}
        }
        current_section = None
        count_dict = {}
        collecting_institute_board = False
        institute_board_value = ""

        for item in data:
            item = item.strip()

            if "LOCAL GUARDIAN DETAILS:" in item or "(IN CASE OF OUTSTATION STUDENT)" in item:
                current_section = "localGuardian"
                continue
            elif "QUALIFICATION DETAILS" in item or "## QUALIFICATION DETAILS" in item:
                current_section = "qualification"
                continue
            elif "NEET UG DETAILS" in item or "NEET UG" in item:
                current_section = "netug"
                continue
            elif "ACADEMIC QUALIFICATION OF CLASS XII" in item or "## ACADEMIC QUALIFICATION OF CLASS XII" in item:
                current_section = "xii"
                continue
            elif "ACADEMIC QUALIFICATION OF CLASS X" in item or "## ACADEMIC QUALIFICATION OF CLASS X" in item:
                current_section = "x"
                continue
            elif "PHYSICS" in item:
                current_section = "physics"
                continue
            elif "CHEMISTRY" in item:
                current_section = "chemistry"
                continue
            elif "BIOLOGY" in item:
                current_section = "biology"
                continue
            elif "DECLARATION" in item:
                current_section = "declaration"
                continue
            if current_section:
                if collecting_institute_board:
                    if '%/CGPA:' in item or '% CGPA:' in item or 'CGPA' in item:
                        json_data[current_section]['INSTITUTE/BOARD:'] = institute_board_value.strip()
                        collecting_institute_board = False
                    else:
                        institute_board_value += " " + item
                        continue

            if ':' in item:
                    key, value = item.split(':', 1)
                    value = value.replace('\t', '').replace('_\t', '').replace('-\t', '').replace('\t_', '')
                    if key.strip() == 'INSTITUTE/BOARD:':
                        collecting_institute_board = True
                        institute_board_value = value.strip()
                        continue
                    if key.strip() in count_dict:
                        count_dict[key.strip()] += 1
                        key = f"{key.strip()}_{count_dict[key.strip()]}"
                    else:
                        count_dict[key.strip()] = 1
                    json_data[current_section][key.strip()] = value.strip()

        # Ensure the JSON file is saved correctly
        try:
            with open('data.json', 'r+', encoding='utf-8') as json_file:
                # Load existing data
                existing_data = json.load(json_file)
                # Update existing data with new data
                existing_data.update(json_data)
                # Move the cursor to the beginning of the file
                json_file.seek(0)
                # Write updated data back to the file
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
                # Truncate the file to the new size
                json_file.truncate()
        except Exception as e:
            print(f"Error saving JSON: {e}")
    except Exception as e:
        print(f"Error saving back JSON: {e}")

@app.route('/')
def index():
    try:
        return render_template('index.php')
    except Exception as e:
        print(f"Error rendering index: {e}")
        return "An error occurred", 500
@app.route('/favicon.ico')
def favicon():
    return '', 200  

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6003)