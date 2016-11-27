import os
from google.appengine.ext import db
from flask import Flask, request, render_template
from twilio.rest import TwilioRestClient
from twilio import twiml
import datetime
import json
app = Flask(__name__)


class User(db.Model):
	phonenumber = db.StringProperty(required=True)
	week=db.IntegerProperty(required=True)

def find_week_formatted(d):
	d = str(d)
	due_day = int(d[0:2])
	due_month = int(d[3:5])
	due_year = int(d[6:])
	duedate=datetime.date(due_year,due_month,due_day)
	today = datetime.date.today()
	difference = duedate-today
	days_elapsed = 280-difference.days
	week = (days_elapsed//7)+1
	return week


def queryjson(numweeks):
	data_file = open('symptoms.json', 'r')
	js = data_file.read()
	js = unicode(js, errors='ignore')

	data = json.loads(js)
	if str(numweeks) in data.keys():
		return "Physical: " + data[str(numweeks)]["Physical"] + "Precautions: " + data[str(numweeks)]["Precautions"]
	else:
		return None
def sendmessage(phonenumber,symptoms):
	account_sid = "AC0bdf8036e6590c7833e0766423192f3f"
	auth_token = "4f9a0e84bbee241ea73ad380f9255925"
	n = "6476949837"
	client = TwilioRestClient(account_sid, auth_token)
	client.messages.create(to = phonenumber,from_ = n,
        body = symptoms)
@app.route("/smsnew",methods=['GET','POST'])
def hello():
		resp = twiml.Response()
		if request.method=="POST":
			phonenumber = request.form['From']
			week = find_week_formatted(str(request.form['Body']))
		#	database = db.GqlQuery('select * from User where phonenumber = :user ', user=(phonenumber))
			flag = 0
			#for data in database:
			#	flag = 1
			if flag==0:
				newuser=User(phonenumber = phonenumber, week = week)
				newuser.put()
			resp.message("Welcome")
			return str(resp)
		resp.message("get")
		return str(resp)


@app.route("/smsupdate",methods=['GET'])
def update():
	database = db.GqlQuery('select * from User')
	for data in database:
		print data.week
		phonenumber = data.phonenumber
		week = data.week
		symptoms = queryjson(week)
		if symptoms:
			print symptoms
			sendmessage(phonenumber, symptoms)
	return 'Success'	
@app.route("/",methods=['GET'])
def mainpage():
	return render_template("index.html")
if __name__ == "__main__":
    app.run()