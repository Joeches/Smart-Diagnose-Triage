# Step 1: Set up the necessary libraries and dependencies
import openai
# from datetime import datetime
import streamlit as st
import sqlite3
# import pandas as pd
# import plotly.express as px
import matplotlib.pyplot as plt
# import seaborn as sns
import pyttsx3
import threading
from PIL import Image
import base64
import os
from dotenv import load_dotenv
#from pytube import YouTube
#from pydub import AudioSegment
from moviepy.editor import *

# Load environment variables from .env file
load_dotenv()

# Access your API key
openai_api_key = os.getenv('OPENAI_API_KEY')

# Add your logo
logo = Image.open("logo.png")
st.image(logo, width=200)


def add_bg_from_local(image_file):
    # Encode the image file
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    # Add CSS code for background image and color
    st.markdown(
        f"""
        <style>
        /* Set the background image */
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string.decode()});
            background-size: cover;
        }}

        /* Set the background color of the container to light gray */
        .container {{
            background-color: #f2f2f2;
            padding: 20px;
        }}

        /* Set the font size and color of the heading */
        h1 {{
            font-size: 36px;
            color: #FF4136;
            text-align: center;
            margin-top: 0;
            margin-bottom: 20px;
        }}

        /* Set the color of all other text to light green */
        body,
        input,
        select,
        label,
        textarea,
        button {{
            color: #B0E0E6;
            font-weight: 100;
        }}

        /* Set the hover color for buttons */
        button:hover {{
            background-color: #f2f2f2;

             }}

        /* Set the color of select options */
        select {{
            color: #757575 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Call the add_bg_from_local function and pass in the image file path
add_bg_from_local('chatbot.png')


# Define the function to initialize the text-to-speech engine
def init_engine():
    engine = pyttsx3.init()
    rate = engine.getProperty("rate")
    engine.setProperty("rate", rate - 500)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
    return engine

 # Start pyttsx3 in a separate thread
    pyttsx3_thread = threading.Thread(target=run_pyttsx3)
    pyttsx3_thread.start()


# Define the function to speak the diagnosis
is_speaking = False




def speak(text):
    global is_speaking
    if is_speaking:
        return
    else:
        is_speaking = True
        engine = init_engine()
        engine.say(text)
        engine.runAndWait()
        is_speaking = False


# Step 2: Create a SQLite database to store patient information
conn = sqlite3.connect('static/patient_data.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS patients 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             name Text, age INTEGER, symptoms TEXT, 
             symptom_duration TEXT, gender TEXT,smoking_status TEXT, state TEXT)''')
conn.commit()

# Step 3: Build the chatbot interface using Streamlit
st.title("Smart Diagnose Triage (S.D.T).")

if not st.session_state.get('diagnosis_done', False):
    speak("Hello, I am your medical Smart Diagnose Triage. How may I help you today?")
    speak("Input your symptoms information below. I will use your input for your symptoms diagnosis.")
    speak("Input the following data: Name. Age. Symptoms. Symptoms duration. Gender. And patient's smoking status")
    st.session_state['diagnosis_done'] = True

name = st.text_input("Enter patient name: ")
age = st.slider("Select your age", 0, 120)
symptoms = st.text_input("Enter your symptoms")
symptom_duration = st.selectbox("Select your symptom duration",
                                ["0 to 6 hours", "6 to 12 hours", "24 to 48 hours",
                                 "48 to 72 hours", "72 to 89 hours", "89 to 99+ hours"])
gender = st.selectbox("Select your gender", ["Male", "Female", "Other"])
smoking_status = st.checkbox("Is the patient a smoker?")
if st.button("Get Diagnosis"):
    speak("Please be patient while I perform your diagnosis using text-Davinci-002.")

    # Step 4: Use OpenAI's GPT-3 API to generate a diagnosis
    openai.api_key = openai_api_key
    prompt = f"Patient name: {name}\nage: {age}\nSymptoms: {symptoms}\nSymptom duration: {symptom_duration}\nGender: {gender}\nsmoking_status: {smoking_status}\n"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1024,
        n=1,
        stop=None,
        timeout=10,
    )
    diagnosis = response.choices[0].text

    # Step 5: Retrieve the diagnosis result and medical expert recommendations from the OpenAI API
    st.write("Diagnosis:", diagnosis)

    # display medical expert recommendation
    expert_response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="A patient with age " + str(
            age) + " and symptoms: " + symptoms + "symptoms duration:" + symptom_duration +
               " is seeking a medical expert recommendation. Please recommend a medical expert and their location."
    ).get("choices")[0].get("text")
    st.write("Medical Expert Recommendation: " + expert_response)

    # Play the diagnosis and recommendations using text-to-speech
    speak(diagnosis)
    speak("Here are the medical expert recommendations based on the diagnosis:")
    speak(expert_response)

    # Set session state to indicate diagnosis is done
    st.session_state.diagnosis_done = False

    # plot histogram of patient ages and symptom duration
    st.set_option('deprecation.showPyplotGlobalUse', False)
    ages = [age]
    duration = [symptom_duration]
    plt.hist(ages, bins=1, alpha=0.5, label='Age')
    plt.hist(duration, bins=1, alpha=0.5, label='Symptom Duration')
    plt.xlabel('Age/Symptom Duration')
    plt.ylabel('Count')
    plt.title('Distribution of Patient Ages and Symptoms Duration')
    plt.legend(loc='upper right')
    st.pyplot()
    speak("Diagnosis Distribution by Age and Symptoms Duration")

    # Set the diagnosis_done session state variable to True to indicate that a diagnosis has been made
    st.session_state.diagnosis_done = True

# Dummy data for Nigerian states
nigeria_states = ['Abia',
                  'Adamawa',
                  'Akwa Ibom',
                  'Anambra',
                  'Bauchi',
                  'Bayelsa',
                  'Benue',
                  'Borno',
                  'Cross River',
                  'Delta',
                  'Ebonyi',
                  'Edo',
                  'Ekiti',
                  'Enugu',
                  'Gombe',
                  'Imo',
                  'Jigawa',
                  'Kaduna',
                  'Kano',
                  'Katsina',
                  'Kebbi',
                  'Kogi',
                  'Kwara',
                  'Lagos',
                  'Nasarawa',
                  'Niger',
                  'Ogun',
                  'Ondo',
                  'Osun',
                  'Oyo',
                  'Plateau',
                  'Rivers',
                  'Sokoto',
                  'Taraba',
                  'Yobe',
                  'Zamfara',
                  'Abuja']

# Dummy data for medical experts in Nigeria
medical_experts = [
    {
        "name": "RILMARK Healthcare Specialist Clinic & Cardiology Centre",
        "specialty": "Cardiologist",
        "related_symptoms": ["Chest pain", "Shortness of breath", "Dizziness",
                             "Irregular Heart Beat"
                             "Atrial Fibrillation"
                             "Endocarditis"
                             "High cholesterol levels"
                             "Hypertension (high blood pressure)"
                             "Pericarditis"
                             "Valvular heart diseases"],

        "state": "Lagos",
        "phone": "0808 383 3196",
        "facility address": "1 Ma-ba-de'je Street Ikorodu, 104101 Lagos Nigeria.",
        "email": "dr@realmarkhealthcare.com",
        "appointments": [
            {"day": "Sunday", "start_time": "Sunday	14:00", "end_time": "18:00"},
            {"day": "Monday", "start_time": "09:00", "end_time": "17:00"},
            {"day": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "12:00"}
        ]
    },
    {
        "name": "Doctor. Ada Geraldine",
        "specialty": "Gynecologist",
        "related_symptoms": ["Menstrual pain", "Painful periods", "Irregular periods", "Vaginal bleeding", ],
        "state": "Abuja",
        "phone": "0805 564 3702",
        "facility address": "132 Independence Ave, Central Business District 900103, Abuja, Federal Capital Territory, Nigeria",
        "email": "dr@realmarkhealthcare.com",
        "appointments": [
            {"day": "Monday", "start_time": "09:00", "end_time": "16:00"},
            {"day": "Wednesday", "start_time": "12:00", "end_time": "17:00"},
            {"day": "Thursday", "start_time": "09:00", "end_time": "13:00"}
        ]
    },
    {
        "name": "Unicare Skin Clinic",
        "specialty": "Dermatologist",
        "related_symptoms": ["Skin rash", "Itching", "Acne"],
        "state": "Kano",
        "phone": "0803 652 6837",
        "facility address": "XGJV+P8Q, Dr Bala Muhammad Rd, Jaoji 700102, Kano",
        "email": "dr@dermatologist.com",
        "appointments": [
            {"day": "Tuesday", "start_time": "13:00", "end_time": "17:00"},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
            {"day": "Thursday", "start_time": "14:00", "end_time": "17:00"}
        ]
    },
    {
        "name": "University of Calabar Teaching Hospital (UCTH) - Orthopaedic Surgery Dept",
        "specialty": "Orthopaedic",
        "related_symptoms": ["Neck Pain", " Shoulder Pain", "Trouble Climbing Stairs"],
        "state": "Cross River",
        "phone": "+234 87 232 055",
        "facility address": "5 Court Rd, Duke Town 540281, Calabar, Cross River State, Nigeria",
        "email": "info@ucthcalabar.gov.ng",
        "appointments": [
            {"day": "Monday", "start_time": "8:00", "end_time": "16:00"},
            {"day": "Tuesday", "start_time": "8:00", "emd_time": "16:00"},
            {"day": "Wednesday", "start_time": "12:00", "end_time": "16:00"},
            {"day": "Thursday", "start_time": "8:00", "end_time": "16:00"},
            {"day": "Thursday", "start_time": "8:00", "end_time": "16:00"},
        ]
    },
    {
        "name": "Delta State University Teaching Hospital - (DELSUTH)",
        "specialty": "Hepatologist and Gastroenterologist",
        "related_symptoms": ["abdominal pain", "fatigue", "diarrhoea"],
        "state": "Delta",
        "phone": "No phone number available use the email address, Email: info@delsuth.com.ng",
        "facility address": "Otefe Road, off Benin-Warri Express Way,Oghara, Delta StateP.O.Box: 07 Delta State",
        "email": " info@delsuth.com.ng",
        "appointments": [
            {"day": "Monday", "start_time": "11 am", "end_time": "12:00"},
            {"day": "Tuesday", "start_time": "11 am", "end_time": "12:00"},
            {"day": "Wednesday", "start_time": "11 am", "end_time": "12:00"},
            {"day": "Thursday", "start_time": "11:00", "end_time": "12:00"},
            {"day": "Tuesday", "start_time": "11 am", "end_time": "12:00"},
        ]
    },
    {
        "name": "Poplar Hospital and Orthopaedic Clinics- Poplar Healthcare ltd - Bone cancer: Teenagers and young adults",
        "specialty": "oncologists and radiation oncologists, orthopedic surgeon, Cardiologit and rheumatologist",
        "related_symptoms": ["Feeling extra tired (fatigue)", "Unexplained swelling", "Difficulty moving around."],
        "state": "Oyo",
        "phone": "08180393240 and 08132696876",
        "facility address": "18, 7up Road, Oluyole Estate, Ring Road, Ibadan. Oyo State.",
        "email": "info@poplarhospital.com emergency@poplarhospital.com",
        "appointments": [
            {"day": "Monday	Open 24 hours"},
            {"day": "Tuesday Open 24 hours"},
            {"day": "Wednesday	Open 24 hours"},
            {"day": "Thursday	Open 24 hours"},
            {"day": "Friday(Good Friday)"},
            {"day": "Saturday Open 24 hours"},
            {"day": "Sunday	Open 24 hours"},
        ]
    },
    {
        "name": "Federal Neuro-Psychiatric Hospital Benin City - Mental Disorders",
        "specialty": "Psychiatrist",
        "state": "Edo",
        "phone": "+234 8032 231 189; +234 815 1130 304",
        "facility address": "Urora Road, Off Iduomwinna. #39 Uselu, before Medical Junction, and Benin-Agbor Roads, Benin City.",
        "email": "contactus@fnphbenin.gov.ng",
        "appointments": [
            {"day": "Monday	Open 24 hours"},
            {"day": "Tuesday Open 24 hours"},
            {"day": "Wednesday	Open 24 hours"},
            {"day": "Thursday	Open 24 hours"},
            {"day": "Friday(Good Friday)"},
            {"day": "Saturday Open 24 hours"},
            {"day": "Sunday	Open 24 hours"},
            {"day": "(Easter Monday) Hours might differ"},
        ]
    },
    {
        "name": "Bladder cancer",
        "specialty": "Urologists",
        "related_symptoms": ["a need to urinate on a more frequent basis", "sudden urges to urinate",
                             "a burning sensation when passing urine", "bone pain", "pelvic pain",
                             "unintentional weight loss", "swelling of the legs"],
        "state": "kogi state",
        "phone": "",
        "facility address": "",
        "email": "",
        "appointments": [
            {"day": "Tuesday", "start_time": "13:00", "end_time": "17:00"},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
            {"day": "Thursday", "start_time": "14:00", "end_time": "17:00"}
        ]
    },
    {
        "name": "Unicare Skin Clinic",
        "specialty": "Dermatologist",
        "related_symptoms": ["Skin rash", "Itching", "Acne"],
        "state": "Kano",
        "phone": "0803 652 6837",
        "facility address": "Address: XGJV+P8Q, Dr Bala Muhammad Rd, Jaoji 700102, Kano",
        "email": "dr@dermatologist.com",
        "appointments": [
            {"day": "Tuesday", "start_time": "13:00", "end_time": "17:00"},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
            {"day": "Thursday", "start_time": "14:00", "end_time": "17:00"}
        ]
    },
    {
        "name": "Unicare Skin Clinic",
        "specialty": "Dermatologist",
        "related_symptoms": ["Skin rash", "Itching", "Acne"],
        "state": "Kano",
        "phone": "0803 652 6837",
        "facility address": "Address: XGJV+P8Q, Dr Bala Muhammad Rd, Jaoji 700102, Kano",
        "email": "dr@dermatologist.com",
        "appointments": [
            {"day": "Tuesday", "start_time": "13:00", "end_time": "17:00"},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
            {"day": "Thursday", "start_time": "14:00", "end_time": "17:00"}
        ]
    },
    {
        "name": "Unicare Skin Clinic",
        "specialty": "Dermatologist",
        "state": "Kano",
        "phone": "0803 652 6837",
        "facility address": "Address: XGJV+P8Q, Dr Bala Muhammad Rd, Jaoji 700102, Kano",
        "email": "dr@dermatologist.com",
        "appointments": [
            {"day": "Tuesday", "start_time": "13:00", "end_time": "17:00"},
            {"day": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
            {"day": "Thursday", "start_time": "14:00", "end_time": "17:00"}
        ]
    }
]

st.title("Get Live Medical Expert Recommendation")

# Select box for patient to choose their current state
current_state = st.selectbox("Select your current state", options=nigeria_states)
speak("Please, Select your current state, to search for the nearest medical expert around your current location.")

# Get all medical experts in the patient's current state
experts_in_state = [expert for expert in medical_experts if expert["state"] == current_state]

if len(experts_in_state) == 0:
    st.warning("No medical expert available in your current state.")
    speak("No medical expert available in your current state.")
else:
    st.success(f"Found {len(experts_in_state)} medical expert in {current_state}.")
    speak((f"Found {len(experts_in_state)} medical expert in {current_state}."))
    for expert in experts_in_state:
        st.write("Name:", expert["name"])
        speak(("Name:", expert["name"]))
        st.write("Specialty:", expert["specialty"])
        speak(("Specialty:", expert["specialty"]))
        #st.write("Related Symptoms:", expert["related_symptoms"])
        st.write("Phone:", expert["phone"])
        speak(("Phone:", expert["phone"]))
        st.write("Facility Address:", expert["facility address"])
        speak(("Facility Address:", expert["facility address"]))
        speak("Please, click the Button bellow to listen to a well-wish voice note")


        def well_wish_voice_note():
            # Add a checkbox that lets the user choose whether they want to hear the message or not
            listen_to_message = st.checkbox("Listening to well-wish voice note")

            # Define the message to be played
            speak("Hello " + name)
            speak(
                "This is your friendly medical Smart Diagnose Triage, and I wanted to take a moment to wish you well after receiving information from our life medical expert. First and foremost, I hope that you are doing okay and that you are taking care of yourself. Remember, your health is incredibly important, and it's always better to be safe than sorry. Our life medical expert provided you with valuable information and contacts that can help you in your journey to recovery. I encourage you to reach out to them if you have any further questions or concerns. They are experts in their field and can provide you with the guidance and support you need to get back to feeling your best. Don't hesitate to take advantage of the resources available to you. Your health is worth investing in, and you deserve to have all the tools you need to feel your best, Take care, and remember that we are always here to support you on your health journey.")

            # If the user chooses to listen, play the message
            if listen_to_message:
                st.write(f"Playing message")


        # Add a button that calls the well_wish_voice_note function
        st.button("listen to a well-wish voice note", on_click=well_wish_voice_note)


if __name__ == '__main__':
    video_url = "https://www.youtube.com/watch?v=dZIpH19KTkA>"
    video_title = "Introduction to Smart Diagnose Triage (S.D.T)."
    video_description = "Watch this video to get a better understanding of how to use the Smart Diagnose Triage (S.D.T)."
    st.video(video_url, start_time=0)
    st.header(video_title)
    st.write(video_description)



