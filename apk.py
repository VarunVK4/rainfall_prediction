
from flask import Flask,render_template,url_for,request,jsonify
from flask_cors import cross_origin
import pandas as pd
import numpy as np
import datetime
import pickle
import smtplib
import getpass
HOST = "smtp.gmail.com"
PORT = 587

smtp = smtplib.SMTP(HOST,PORT)
smtp.starttls()	
FROM_EMAIL = "farmeralert2025@gmail.com"
PASSWORD = "vpep ridd kguq svrl"
smtp.login(FROM_EMAIL, PASSWORD)


import pymysql
mydb = pymysql.connect(host="localhost", user="root", password="12345", database="users")
mycursor = mydb.cursor()



MESSAGE_RAIN ="""\
Subject: Weather Advisory and Farming Tips for Rainy Days

Dear farmer,

As we anticipate rainy weather in your area tomorrow, we wanted to offer some suggestions to help you prepare for the rain and its impact on your farm:

1.Field Preparation: Ensure proper drainage in your fields to prevent waterlogging. Check that your ditches and drains are clear of debris.

2.Crop Protection: If you have young or vulnerable crops, consider using covers or shelters to protect them from heavy rain and wind.

3.Equipment Check: Inspect your farming equipment, especially machinery used for irrigation and drainage, to ensure they are in good working condition.

4.Animal Shelter: If you have livestock, make sure they have adequate shelter to protect them from the rain and cold.

5.Soil Management: Be cautious of soil erosion. Consider planting cover crops or using mulch to protect the soil from heavy rain.

6.Harvest Preparation: If you have crops ready for harvest, consider harvesting them before the rain to prevent damage and ensure quality.

We hope these tips help you prepare for the rainy weather ahead. If you have any specific concerns or need further assistance, please feel free to reach out to us.

Stay safe and best of luck with your farming endeavors!

Warm regards,

FarmTuner."""
MESSAGE_SUNNY ="""\
Subject: Farming Tips for Sunny Weather

Dear farmer,

With sunny weather forecasted in your area tomorrow, we wanted to share some tips to help you make the most of the sunshine and keep your farm thriving:

1. Hydration for Crops and Livestock: Ensure your crops and livestock have an adequate water supply. Irrigate your fields early in the morning or late in the evening to minimize water loss from evaporation.

2. Sun Protection: If you're working outdoors, protect yourself from the sun's rays by wearing a hat, sunglasses, and sunscreen. Consider using sun shades on your equipment to prevent overheating.

3. Crop Care: Monitor your crops closely for signs of heat stress. Provide shade or cover for sensitive plants if necessary. Mulching can also help retain soil moisture and keep roots cool.

4. Livestock Comfort: Ensure your livestock have access to shaded areas and plenty of fresh, clean water to stay cool and hydrated.

5. Equipment Maintenance: Check your equipment regularly to prevent breakdowns due to overheating. Keep engines well-lubricated and ensure cooling systems are functioning properly.

6. Harvest Timing: Plan your harvests for early morning or late evening when temperatures are cooler to minimize heat stress on you and your workers.

7. Soil Moisture Management: Monitor soil moisture levels closely and adjust irrigation schedules as needed to prevent drought stress in your crops.

8. Fire Safety: With dry conditions, be vigilant about fire safety. Avoid activities that could spark fires, and have fire extinguishers or water sources readily available.

We hope these tips help you manage your farm effectively during sunny weather. If you have any specific concerns or need further assistance, please feel free to reach out to us.

Wishing you a successful and productive season!

Warm regards,

FarmTuner."""
smtp = smtplib.SMTP(HOST, PORT)

smtp.ehlo()
smtp.starttls()
smtp.login(FROM_EMAIL, PASSWORD)

app = Flask(__name__, template_folder="template")
model = pickle.load(open("./models/catml.pkl", "rb"))
print("Model Loaded")

@app.route("/",methods=['GET'])
@cross_origin()
def home():
	return render_template("index.html")
    

@app.route("/predict",methods=['GET', 'POST'])
@cross_origin()
def predict():
	if request.method == "POST":
		# DATE
		date = request.form['date']
		day = float(pd.to_datetime(date).day)
		month = float(pd.to_datetime(date).month)
		# MinTemp
		minTemp = float(request.form['mintemp'])
		# MaxTemp
		maxTemp = float(request.form['maxtemp'])
		# Rainfall
		rainfall = float(request.form['rainfall'])
		# Evaporation
		evaporation = float(request.form['evaporation'])
		# Sunshine
		sunshine = float(request.form['sunshine'])
		# Wind Gust Speed
		windGustSpeed = float(request.form['windgustspeed'])
		
		# Humidity 9am
		humidity = float(request.form['humidity9am'])
	
		# Pressure 9am
		pressure= float(request.form['pressure9am'])
		# Pressure 3pm
	
		# Temperature 9am
		temp = float(request.form['temp9am'])
		# Temperature 3pm
		
		location = float(request.form['location'])
		# Cloud 9am
		
		cloud = float(request.form['cloud9am'])
		# Cloud 3pm
	    
		# Wind Gust Dir
		windGustDir = float(request.form['windgustdir'])
		# Rain Today
		rainToday = float(request.form['raintoday'])

		input_lst = [location, minTemp , maxTemp , rainfall , evaporation , sunshine ,
					 windGustDir , windGustSpeed ,
					 humidity , pressure,  cloud ,  temp , 
					 rainToday , month , day]
		
		if location == 0:
			loc='Arakkonam'
		elif location == 1:
			loc='Aruppukottai'
		elif location == 2:
			loc='Avadi'
		elif location == 3:
			loc='Chengalpattu'
		elif location == 4:
			loc='Chennai'
		elif location == 5:
			loc='Coimbatore'
		elif location == 6:
			loc='Cuddalore'
		elif location == 7:
			loc='Dindigul'
		elif location == 8:
			loc='Erode'
		elif location == 9:
			loc='Gudiyatham'
		elif location == 10:
			loc='Hosur'	

		pred = model.predict(input_lst)
		output = pred
		query= "SELECT email FROM informations WHERE location =%s"
		mycursor.execute(query, (loc,))
		recipients = mycursor.fetchall()
        
        # --- NEW CONNECTION CODE START ---
        # Establish a new SMTP connection for this specific request
		smtp_session = smtplib.SMTP(HOST, PORT)
		smtp_session.ehlo()
		smtp_session.starttls()
		smtp_session.login(FROM_EMAIL, PASSWORD)
        # --- NEW CONNECTION CODE END ---
        
		if output == 0:
			for recipient in recipients:
				smtp_session.sendmail(FROM_EMAIL, recipient[0], MESSAGE_SUNNY)
			smtp_session.quit() # Quit the session we just created
			return render_template("after_sunny.html")
		    
		else:
			for recipient in recipients:
				smtp_session.sendmail(FROM_EMAIL, recipient[0], MESSAGE_RAIN)
			smtp_session.quit() # Quit the session we just created
			return render_template("after_rainy.html")
		    
	return render_template("predictor.html")


@app.route("/insert",methods=['GET','POST'])
@app.route("/insert",methods=['GET','POST'])
@cross_origin()
def insert():
	if request.method == "POST":
		name = request.form['name']
		email=request.form['email']
		location=request.form['location']
		
		try:
			mycursor.execute("INSERT INTO informations(name,email,location) VALUES (%s,%s,%s)",(name,email,location))
			mydb.commit()
			return "Data inserted successfully!" 
		except Exception as e:
			print(f"Database Insertion Error: {e}") 
			return f"Failed to insert data. Error: {e}" 
        
	return render_template("insert.html")
app.run()
if __name__=='__main__':
	app.run(debug=True)

