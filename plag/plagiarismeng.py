from difflib import SequenceMatcher
from django.conf import settings 
from googlesearch import search
import pyttsx3
import PyPDF2
import requests
import os 
import uuid
import fitz
import pytesseract
from PIL import Image
import spacy
from io import BytesIO


speaker = pyttsx3.init()
# Load the pre-trained English language model
nlp = spacy.load("en_core_web_sm")

# def plag_check(request, text):
#     # Retrieve related works
#     related_works = retrieve_related_works(text)
#     num_related_works = min(len(related_works), 5)
#     # Calculate text size
#     text_size = len(text)
    
#     # Analyze text similarity with related works using spaCy
#     similarity_percentages = []
#     for work in related_works:
#         similarity = nlp(text).similarity(nlp(work['title']))
#         similarity_percentages.append({'title': work['title'], 'link': work['link'], 'similarity_percent': similarity * 100})

#     plagiarism_percent = round(sum(work['similarity_percent'] for work in similarity_percentages) / len(similarity_percentages), 1) if similarity_percentages else 0
    
#     # Return the results
#     results = {'text_size': text_size, 'related_works': similarity_percentages, 'plagiarism_percent':plagiarism_percent, 'num_related_works':num_related_works}
#     return results

def plag_check(request, text):
    try:
        # Retrieve related works
        related_works = retrieve_related_works(text)
        num_related_works = min(len(related_works), 5)
        # Calculate text size
        text_size = round(len(text.encode('utf-8')) / 1024, 2)

        # Analyze text similarity with related works using spaCy
        similarity_percentages = []
        for work in related_works:
            similarity = nlp(text).similarity(nlp(work['title']))
            similarity_percentages.append({'title': work['title'], 'link': work['link'], 'similarity_percent': similarity * 100})

        plagiarism_percent = round(sum(work['similarity_percent'] for work in similarity_percentages) / len(similarity_percentages), 1) if similarity_percentages else 0

        # Return the results
        results = {'text_size': text_size, 'related_works': similarity_percentages, 'plagiarism_percent':plagiarism_percent, 'num_related_works':num_related_works}
        return results
    except requests.exceptions.Timeout:
        # Handle timeout error
        error_message = "Timeout error: Could not fetch related works due to a connection timeout."
        return {'error': error_message}
    except Exception as e:
        # Handle other exceptions
        error_message = "An error occurred: {}".format(str(e))
        return {'error': error_message}


def retrieve_related_works(query):
    related_works = []

    try:
        # Perform a Google search
        results = search(query)
                     
        for i, result in enumerate(results):
            if i >= 5:  # Limit the number of results to 5
                break
            related_works.append({'title': result, 'link': result})
        
    except Exception as e:
        print("Error fetching data:", e)
    
    return related_works

def speak(words):
    try:
        speaker = pyttsx3.init()
        voice = speaker.getProperty('voices')
        speaker.setProperty('voices', voice[1])
        speaker.say(words)
        speaker.runAndWait()
        speaker.stop()
    except Exception as e:
        print("An error occurred:", e)
    finally:
        speaker.stop()

def extract_pdf_text(pdf_file):
    directory = settings.MEDIA_ROOT
   
    if not os.path.isdir(directory):
        raise ValueError(f"'{directory}' is not a directory.")

    pdf_path = os.path.join(directory, pdf_file)
    if not os.path.isfile(pdf_path):
        text = "PDF not found"
        return text
        

    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    return text

def upload_file(request):
    if request.method == 'POST' and 'u_file' in request.FILES:
        uploaded_file = request.FILES['u_file']

        filename = str(uuid.uuid4()) + os.path.splitext(uploaded_file.name)[1]
        
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)   
        return  file_path
    

# def read_pdf(file_path):
    
#     try:
#         with open(file_path, 'rb') as pdf_file:
#             pdf_reader = PyPDF2.PdfReader(pdf_file)
#             text = ''
#             for page in pdf_reader.pages:
#                 text += page.extract_text()
#             return text
#     except FileNotFoundError:
#         print("File not found.")
#         return None
#     except Exception as e:
#         print("An error occurred:", e)
#         return None
    

def extract_text_from_image(image):
    try:
        # Use pytesseract to perform OCR on the image
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print("An error occurred during OCR:", e)
        return ''

# def read_pdf(file_path):
#     try:
#         with open(file_path, 'rb') as pdf_file:
#             pdf_reader = PyPDF2.PdfReader(pdf_file)
#             text = ''
#             for page_number in range(len(pdf_reader.pages)):
#                 page = pdf_reader.pages[page_number]
                
#                 # Extract text from images within the page
#                 for obj in page['/Resources']:
#                     if '/XObject' in page['/Resources'][obj]:
#                         x_object = page['/Resources'][obj]['/XObject'].getObject()
#                         for key in x_object:
#                             if x_object[key]['/Subtype'] == '/Image':
#                                 image_stream = BytesIO(x_object[key].getData())
#                                 image = Image.open(image_stream)
#                                 text += extract_text_from_image(image)
                
#                 # Extract text from the page
#                 text += page.extract_text()
                
#             return text
#     except FileNotFoundError:
#         print("File not found.")
#         return None
#     except Exception as e:
#         print("An error occurred:", e)
#         return None

def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page_number in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_number]
                
                # Extract text from images within the page
                if '/XObject' in page['/Resources']:
                    x_object = page['/Resources']['/XObject']
                    for obj in x_object:
                        try:
                            if x_object[obj]['/Subtype'] == '/Image':
                                image_stream = BytesIO(x_object[obj].get_data())
                                image_text = extract_text_from_image(image_stream)
                                text += image_text
                        except Exception as e:
                            print("An error occurred while processing image:", e)
                
                # Extract text from the page
                text += page.extract_text()
                
            return text
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None