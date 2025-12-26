from flask import Flask, url_for, redirect, render_template, request, session
import mysql.connector, os, re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import StackingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import VotingClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from imblearn.over_sampling import SMOTE
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


app = Flask(__name__)
app.secret_key = 'admin'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='db'
)

mycursor = mydb.cursor()

def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return

def retrivequery1(query,values):
    mycursor.execute(query,values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['c_password']
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (email, password) VALUES (%s, %s)"
                values = (email, password)
                executionquery(query, values)
                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID is already exists!")
        return render_template('register.html', message="Conform password is not match!")
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                global user_email
                user_email = email

                return render_template('home.html')
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


# @app.route('/load', methods=["GET", "POST"])
# def load():
#     data = None
#     message = None
#     if request.method == "POST":
#         file = request.files['file']
#         if file.filename.endswith('.csv'):
#             data = pd.read_csv(file)
#         elif file.filename.endswith(('.xls', '.xlsx')):
#             data = pd.read_excel(file)
#         else:
#             message = "Unsupported file format. Please upload a CSV or Excel file."
#         message = "Dataset Uploaded Successfully!"
#     return render_template('load.html', data=data, message=message)



# @app.route('/algorithm', methods=["GET", "POST"])
# def algorithm():
#     if request.method == "POST":
#         algorithm = request.form['algorithm']
#         if algorithm == "stacking_classifier":
#             accuracy_score = 90.67
#             algorithm = "Stacking Classifier"

#         elif algorithm == "voting_classifier":
#             accuracy_score = 90.67
#             algorithm = "Voting Classifier"

#         return render_template('algorithm.html', accuracy_score = accuracy_score, algorithm = algorithm)
#     return render_template('algorithm.html')


# @app.route('/prediction', methods=["GET", "POST"])
# def prediction():
#     result = None
#     if request.method == "POST":
#         Gender = int(request.form['Gender'])
#         Age = int(request.form['Age'])
#         Occupation = int(request.form['Occupation'])
#         Sleep_Duration = float(request.form['Sleep_Duration'])
#         Quality_of_Sleep = int(request.form['Quality_of_Sleep'])
#         Physical_Activity_Level = int(request.form['Physical_Activity_Level'])
#         Stress_Level = int(request.form['Stress_Level'])
#         BMI_Category = request.form['BMI_Category']
#         systolic = int(request.form['systolic'])
#         diastolic = int(request.form['diastolic'])
#         Heart_Rate = int(request.form['Heart_Rate'])
#         Daily_Steps = int(request.form['Daily_Steps'])

#         # Concatenate Blood Pressure
#         Blood_Pressure = systolic / diastolic  # Change this to a numeric representation that makes sense

#         # Preparing the input dictionary
#         input_dict = {
#             'Gender': Gender,
#             'Age': Age,
#             'Occupation': Occupation,
#             'Sleep Duration': Sleep_Duration,
#             'Quality of Sleep': Quality_of_Sleep,
#             'Physical Activity Level': Physical_Activity_Level,
#             'Stress Level': Stress_Level,
#             'BMI Category': BMI_Category,
#             'Blood Pressure': Blood_Pressure,
#             'Heart Rate': Heart_Rate,
#             'Daily Steps': Daily_Steps
#         }
        
#         # Convert the single input to a DataFrame
#         input_df = pd.DataFrame([input_dict])

#         # Encode categorical variables as was done in training
#         categorical_mappings = {
#             'Gender': {'Male': 0, 'Female': 1},
#             'Occupation': {'Teacher': 0, 'Engineer': 1, 'Doctor': 2},  # Example mappings
#             'BMI Category': {'Underweight': 0, 'Normal': 1, 'Overweight': 2, 'Obese': 3}  # Example mappings
#         }

#         for column, mapping in categorical_mappings.items():
#             input_df[column] = input_df[column].map(mapping)

#         # Handle any missing mappings or NaNs
#         input_df.fillna(-1, inplace=True)

#         # Load the scaler and feature selector
#         with open(r'Models\scaler.pkl', 'rb') as f:
#             scaler = pickle.load(f)
#         with open(r'Models\k_best_selector.pkl', 'rb') as f:
#             k_best = pickle.load(f)

#         # Standardize the features and select K-best
#         input_scaled = scaler.transform(input_df)
#         input_k_best = k_best.transform(input_scaled)

#         # Load the model and predict
#         with open(r'Models\Random Forest_model_k_best.pkl', 'rb') as f:
#             model = pickle.load(f)
#         prediction = model.predict(input_k_best)
#         result = 'Sleeping disorder' if prediction[0] == 1 else 'No sleeping disorder'
    
    
#     # Load the dataset
#     df = pd.read_csv(r"Dataset\Sleep_health_and_lifestyle_dataset.csv")

#     # Drop columns
#     columns_to_drop = ['Sleep Disorder', 'Blood Pressure']
#     df = df.drop(columns=columns_to_drop)

#     # Replace spaces in column names with underscores
#     df.columns = [re.sub(r'\s+', '_', col) for col in df.columns]

#     # Define object columns to be encoded
#     object_columns = df.select_dtypes(include=['object']).columns

#     # Store label counts before encoding
#     labels = {col: df[col].value_counts().to_dict() for col in object_columns}

#     # Initialize LabelEncoder
#     le = LabelEncoder()

#     # Encode categorical columns and store the encoded value counts
#     encodes = {}
#     for col in object_columns:
#         df[col] = le.fit_transform(df[col])
#         value_counts = df[col].value_counts().to_dict()
#         encodes[col] = value_counts

#     dic = {}

#     for key in labels.keys():
#         dic[key] = []
#         for sub_key, value in labels[key].items():
#             for id_key, id_value in encodes[key].items():
#                 if value == id_value:
#                     dic[key].append((sub_key, id_key))
#                     break

#     return render_template('prediction.html', data=dic, prediction=result)







@app.route('/prediction', methods=["GET", "POST"])
def prediction():
    result = None
    if request.method == "POST":
        Gender = int(request.form['Gender'])
        Age = int(request.form['Age'])
        Occupation = int(request.form['Occupation'])
        Sleep_Duration = float(request.form['Sleep_Duration'])
        Quality_of_Sleep = int(request.form['Quality_of_Sleep'])
        Physical_Activity_Level = int(request.form['Physical_Activity_Level'])
        Stress_Level = int(request.form['Stress_Level'])
        BMI_Category = request.form['BMI_Category']
        systolic = int(request.form['systolic'])
        diastolic = int(request.form['diastolic'])
        Heart_Rate = int(request.form['Heart_Rate'])
        Daily_Steps = int(request.form['Daily_Steps'])

        # Concatenate Blood Pressure
        Blood_Pressure = f"{systolic}/{diastolic}" 

        # Load the scaler
        with open(r'Models\scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)

        # Load the feature selector
        with open(r'Models\k_best_selector.pkl', 'rb') as f:
            k_best = pickle.load(f)

        # Load the stacking classifier model
        model_path = r'Models\Random Forest_model_k_best.pkl'
        with open(model_path, 'rb') as f:
            stacking_classifier = pickle.load(f)


        single_input = {
            'Gender': Gender,
            'Age': Age,
            'Occupation': Occupation,
            'Sleep Duration': Sleep_Duration,
            'Quality of Sleep': Quality_of_Sleep,
            'Physical Activity Level': Physical_Activity_Level,
            'Stress Level': Stress_Level,
            'BMI Category': BMI_Category,
            'Blood Pressure': Blood_Pressure,
            'Heart Rate': Heart_Rate,
            'Daily Steps': Daily_Steps
        }

        # Convert the single input to a DataFrame
        input_df = pd.DataFrame([single_input])

        print(input_df)

        # # Encode categorical variables using the same encoding as the training data
        # input_df['Gender'] = input_df['Gender'].map({'Male': 0, 'Female': 1})
        # input_df['Occupation'] = pd.Categorical(input_df['Occupation']).codes
        # input_df['BMI Category'] = pd.Categorical(input_df['BMI Category']).codes
        input_df['Blood Pressure'] = input_df['Blood Pressure'].str.split('/').apply(lambda x: int(x[0]))

        # Reorder the DataFrame to match the order during training
        columns_order = ['Gender', 'Age', 'Occupation', 'Sleep Duration', 
                        'Quality of Sleep', 'Physical Activity Level', 'Stress Level', 
                        'BMI Category', 'Blood Pressure', 'Heart Rate', 'Daily Steps']
        input_df = input_df[columns_order]

        # Standardize the features
        input_scaled = scaler.transform(input_df)

        # Select K-best features
        input_k_best = k_best.transform(input_scaled)

        # Predict using the stacking classifier model
        prediction = stacking_classifier.predict(input_k_best)

        # Map prediction to class labels
        class_labels = {0: 'No sleeping disorder', 1: 'Sleeping disorder'}
        result = class_labels[prediction[0]]

    
    # Load the dataset
    df = pd.read_csv(r"Dataset\Sleep_health_and_lifestyle_dataset.csv")

    # Drop columns
    columns_to_drop = ['Sleep Disorder', 'Blood Pressure']
    df = df.drop(columns=columns_to_drop)

    # Replace spaces in column names with underscores
    df.columns = [re.sub(r'\s+', '_', col) for col in df.columns]

    # Define object columns to be encoded
    object_columns = df.select_dtypes(include=['object']).columns

    # Store label counts before encoding
    labels = {col: df[col].value_counts().to_dict() for col in object_columns}

    # Initialize LabelEncoder
    le = LabelEncoder()

    # Encode categorical columns and store the encoded value counts
    encodes = {}
    for col in object_columns:
        df[col] = le.fit_transform(df[col])
        value_counts = df[col].value_counts().to_dict()
        encodes[col] = value_counts

    dic = {}

    for key in labels.keys():
        dic[key] = []
        for sub_key, value in labels[key].items():
            for id_key, id_value in encodes[key].items():
                if value == id_value:
                    dic[key].append((sub_key, id_key))
                    break

    return render_template('prediction.html', data=dic, prediction=result)




































































if __name__ == '__main__':
    app.run(debug = True)