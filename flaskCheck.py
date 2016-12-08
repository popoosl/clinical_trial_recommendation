import psycopg2
import xml.etree.ElementTree
import subprocess
import os
import difflib
import csv
import collections
from re import sub
from decimal import Decimal
import time
import operator

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from models import Test
from models import ReputationFactor
from models import TrialDatum
from models import CostByState

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://team4:ge7hooVu@localhost:9003"
app.debug = True
db = SQLAlchemy(app)
db.create_all()
db.session.commit()

#_location = "New York"
_institution = "ABCD"
#w1 = int(1)
#w2 = int(1)
#w3 = int(1)
#w4 = int(1)
#w5 = int(1)

@app.route("/")
def main():
	return render_template('main.html')


@app.route('/action',methods=['POST'])
def actions():
	_phase = int(request.form['phase'])
	_location = str(request.form['location'])
	print _location
	# _institution = request.form['institution']
	w1 = int(request.form['w1'])
	w2 = int(request.form['w2'])
	w3 = int(request.form['w3'])
	w4 = int(request.form['w4'])
	w5 = int(request.form['w5'])
	repo_dict = dict()
	reputation_score_dict = dict()

	trial_data = db.session.query(TrialDatum).all()
	repo_factor = db.session.query(ReputationFactor).all()
	cost_state = db.session.query(CostByState).all()
	
	
	for repo in repo_factor :
		repo.no_of_trials_per_phase = float(0);
		repo.avg_people_per_phase = float(0);

	for trial in trial_data :
		if trial.phase == _phase :
			repo_dict.setdefault(trial.name + trial.location, []).append(trial.no_of_people)

	
	for keys in repo_dict :
		for repo in repo_factor :
			count = 0;
			if keys == repo.name + repo.location :
				repo.no_of_trials_per_phase = len(repo_dict[keys])
				#print repo_dict[keys]
				for i in repo_dict[keys] :
					count = count + i

				repo.avg_people_per_phase = float(count / repo.no_of_trials_per_phase);
				#print repo.avg_people_per_phase
				
	# for keys in repo_factor :
	# 	if keys.avg_people_per_phase != float(0) :
	# 		print "avg_people_per_phase : "
	# 		print keys.avg_people_per_phase
	# 		print "count : "
	# 		print keys.no_of_trials_per_phase

	

	fmaxtrials = float(db.session.query(db.func.max(ReputationFactor.no_of_trials)).scalar())
	fmaxavgppl = float(db.session.query(db.func.max(ReputationFactor.avg_people_per_phase)).scalar())
	fmaxtrialsperphase = float(db.session.query(db.func.max(ReputationFactor.no_of_trials_per_phase)).scalar())
	fmaxgrants = float(db.session.query(db.func.max(ReputationFactor.grants)).scalar())
	fmaxpublcn = float(db.session.query(db.func.max(ReputationFactor.publication_count)).scalar())

	fmintrials = float(db.session.query(db.func.min(ReputationFactor.no_of_trials)).scalar())
	fminavgppl = float(db.session.query(db.func.min(ReputationFactor.avg_people_per_phase)).scalar())
	fmintrialsperphase = float(db.session.query(db.func.min(ReputationFactor.no_of_trials_per_phase)).scalar())
	fmingrants = float(db.session.query(db.func.min(ReputationFactor.grants)).scalar())
	fminpublcn = float(db.session.query(db.func.min(ReputationFactor.publication_count)).scalar())

	
	# print fmaxtrials, fmaxavgppl, fmaxtrialsperphase, fmaxgrants, fmaxpublcn
	# print fmintrials, fminavgppl, fmintrialsperphase, fmingrants, fminpublcn
	

	for repo in repo_factor :
		trial_score = w1 * (float(repo.no_of_trials) - fmintrials) / (fmaxtrials - fmintrials)
		avg_people_per_phase_score = w2 * (float(repo.avg_people_per_phase) - fminavgppl) / (fmaxavgppl - fminavgppl)
		no_of_trials_per_phase_score = w3 * (float(repo.no_of_trials_per_phase) - fmintrialsperphase) / (fmaxtrialsperphase - fmintrialsperphase)
		grants_score = w4 * (float(repo.grants) - fmingrants) / (fmaxgrants - fmingrants)
		publication_count_score = w5 * (float(repo.publication_count) - fminpublcn) / (fmaxpublcn - fminpublcn)
		
		reputation_score = trial_score + avg_people_per_phase_score + no_of_trials_per_phase_score + grants_score + publication_count_score
		reputation_score_dict.setdefault(repo.name + "," + repo.location, []).append(reputation_score)

	sorted_x = sorted(reputation_score_dict.items(), key=operator.itemgetter(1), reverse = True)


	output = dict()
	counter = 0;

	#location = "Texas"

	if _location != "N/A" :
		priorOut = dict()
		for i in sorted_x :
			if counter > 4 :
				break;
			for stat in cost_state :
				if  stat.state == i[0].split(",")[1] and str(_location) == str(i[0].split(",")[1]) :
					if _phase == 1 :
						counter = counter + 1;
						priorOut[i[0].split(",")[0] + "," + i[0].split(",")[1]] = stat.phase1
					if _phase == 2 :
						counter = counter + 1;
						priorOut[i[0].split(",")[0] + "," + i[0].split(",")[1]] = stat.phase2
					if _phase == 3 :
						counter = counter + 1;
						priorOut[i[0].split(",")[0] + "," + i[0].split(",")[1]] = stat.phase3

	counter = 0;

	for i in sorted_x :
		if counter > 4 :
				break;
		for stat in cost_state :
			if  stat.state == i[0].split(",")[1] :
				if _phase == 1 :
					counter = counter + 1;
					output[i[0].split(",")[0] + "," + i[0].split(",")[1]] = stat.phase1
				if _phase == 2 :
					counter = counter + 1;
					output[i[0].split(",")[0] + "," + i[0].split(",")[1]] = stat.phase2
				if _phase == 3 :
					counter = counter + 1;
					output[i[0].split(",")[0] + "," + i[0].split(",")[1]] = stat.phase3
			
	#print output

	htmlcode = "<html><body><table><p>" + "User Requested top 5" + "</p>"

	for i in priorOut :
		print i
		htmlcode = htmlcode + "<tr><td>"+ i.split(",")[0] + "</td><td>" + i.split(",")[1] + "</td><td>" + str(priorOut[i]) + "</td></tr>"

	htmlcode = htmlcode + "</table><p>" + "Recommended top 5" + "</p><table>"
	print "Another"

	for i in output :
		print i
		htmlcode = htmlcode + "<tr><td>"+ i.split(",")[0] + "</td><td>" + i.split(",")[1] + "</td><td>" + str(output[i]) + "</td></tr>"

	htmlcode = htmlcode + "</table></body></html>"

	#print htmlcode
	return htmlcode



if __name__ == "__main__":
    app.run()
