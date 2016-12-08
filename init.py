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
conn = psycopg2.connect(database='team4', user='team4');
cursor = conn.cursor();
dupset=set()
deleteDB = True;
if deleteDB:
        cursor.execute("truncate trial_data");
indexTD = 1;
'''indexDiseaseHist = 1;
indexTrialHist = 1;'''

listXml = os.listdir("/home/team4/Team4/XMLs");
#print len(listXml);

for i in listXml:
	i = '/home/team4/Team4/XMLs/' + i;
	#print i;
	e = xml.etree.ElementTree.parse(i).getroot()

	'''for spon in e.findall('sponsors'):
		for sponres in spon.findall('agency'):
			agency = sponres.text'''

	for enroll in e.findall('enrollment'):
		enrollCount = enroll.text

	'''for elig in e.findall('eligibility'):
		for gender in elig.findall('gender'):
			gender = gender.text

		for minAge in elig.findall('minimum_age'):
			minAge = minAge.text.split()[0]

		for maxAge in elig.findall('maximum_age'):
			maxAge = maxAge.text.split()[0]'''

	for loc in e.findall('location'):
		for fac in loc.findall('facility'):
			for name in fac.findall('name'):
				facility = name.text
                                a1 = difflib.get_close_matches(facility,dupset,1)
				if not a1:
                                   dupset.add(facility);
                                else:
                                   facility=a1[0];


			for add in fac.findall('address'):
				'''for city in add.findall('city'):
					city = city.text'''
				for state in add.findall('state'):
					state = state.text
				'''for zipcode in add.findall('zip'):
					zipcode = zipcode.text'''
				for country in add.findall('country'):
					country = country.text

	if country != "United States" :
		continue;
	
		
	'''for ph in e.findall('phase'):
		phase = int(ph.text.split()[1])'''


	'''if minAge == 'N/A':
		minAge = 0;
	if maxAge == 'N/A':
		maxAge = 0;'''
	if facility == 'N/A':
		facility = 'NF';
	if enrollCount == 'N/A':
		enrollCount = 0;
	'''if phase == 'N/A':
		phase = 0;'''

	#print indexTD 
	#print facility 
	#print state 
	'''print phase'''
	#print enrollCount

	cursor.execute("INSERT INTO trial_data (id, name, location, no_of_people) VALUES (%s, %s, %s, %s)",(indexTD, facility, state, enrollCount));
	indexTD = indexTD + 1;

	'''cursor.execute("INSERT INTO disease_history (id, region, age_min, age_max) VALUES (%s, %s, %s, %s)",(indexDiseaseHist, city, minAge, maxAge));
	indexDiseaseHist = indexDiseaseHist + 1;

	cursor.execute("INSERT INTO trial_history (id, n_people, region) VALUES (%s, %s, %s)", (indexTrialHist, enrollCount, city));
	indexTrialHist = indexTrialHist + 1;'''

'''cursor.execute("SELECT id, name, location, phase, no_of_people  from trial_data")
tdTable = cursor.fetchall()
for row in tdTable:
	print "ID = ", row[0]
	print "NAME = ", row[1]
	print "LOCATION = ", row[2]
	print "PHASE = ", row[3]
	print "ENROLL = ", row[4], "\n"'''

'''cursor.execute("SELECT id, region, age_min, age_max  from disease_history")
dhTable = cursor.fetchall()
for row in dhTable:
	print "ID = ", row[0]
	print "REGION = ", row[1]
	print "AGE_MIN = ", row[2]
	print "AGE_MAX = ", row[3], "\n"

cursor.execute("SELECT id, n_people, region  from trial_history")
thTable = cursor.fetchall()
for row in thTable:
	print "ID = ", row[0]
	print "N_PEOPLE = ", row[1]
	print "REGION = ", row[2], "\n"'''

t1=time.time()
cursor.execute("update trial_data set phase= case when (no_of_people >=0 and no_of_people <= 30 ) then 1 when (no_of_people >30 and no_of_people <= 210 )  then 2 else 3 end;")
cursor.execute("truncate reputation_factors");
cursor.execute("insert into reputation_factors (name, location,no_of_trials) select name, location, count(*) from trial_data group by name, location order by count(*) desc;");
allinstitutes={}
cursor.execute("select id,name from reputation_factors")
tdTable = cursor.fetchall();
for row in tdTable:
    allinstitutes[row[0]]=row[1]

t3=time.time()
#print ("Time for getting top 25 %s",(t3-t2))
file=open("/home/team4/Team4/LungCancerResearch/pubmed_result_big.xml","r+");
institutes={}
contents=file.read();
for item in contents.split("</Affiliation>"):
    if "<Affiliation>" in item:
      #institutes.extend(item [ item.find("<Affiliation>")+len("<Affiliation>") : ].split(','))
       listOfInstitutes=item [ item.find("<Affiliation>")+len("<Affiliation>") : ].split(',')
       for insti in listOfInstitutes:
            if insti in institutes:
               institutes[insti]= institutes[insti]+ 1
            else:
               institutes[insti] = 1
           
t4=time.time()
print ("Time for parsed the publcncnt file %s",(t4-t3))
for no in allinstitutes:
    institute=allinstitutes[no]
    a1 = difflib.get_close_matches(institute,institutes,1)
    if not a1:
        publcns=0
    else:
        publcns=institutes[a1[0]]
    cursor.execute("update reputation_factors set publication_count = %s where id= %s",(publcns,no));
t5=time.time()
print ("Time for updating  with the publcncnt part %s",(t5-t4))
repcount={}
with open('/home/team4/Team4/LungCancerResearch/LungCancerGrantsMSDOS.csv') as input_file:
  for row in csv.reader(input_file, delimiter=',' ):
        if(row[1]=='Organization Name'):
           continue
        intstitute=row[1]
        tc=row[3]
        tsc=row[4]
        if tc == '': amount=0
        else : amount=int(tc)
        if tsc !='': amount=amount+int(tsc)
        
        if intstitute in repcount:
               repcount[intstitute]= repcount[intstitute]+ amount
        else:
             repcount[intstitute] = amount        
t6=time.time()
print ("Time for parsed the grants file %s",(t6-t5))

for no in allinstitutes:
    institute = allinstitutes[no]
    a1 = difflib.get_close_matches(institute.upper(),repcount,1)
    if not a1:
        grants=0
    else:
        grants=repcount[a1[0]]
    cursor.execute("update reputation_factors set grants= %s where id= %s",(grants,no));
t7=time.time()
print ("Time for done the grants part %s",(t7-t6))

###########Code for the cost table###########################
reader = csv.reader(open('raw_data.csv', 'r'))
d = {}
count = 0
    
nat_avg = 0.0
    
for row in reader:
   count = count + 1
    
   if len(row) == 0 :
      break    
        
   if count > 4:
      
      each = row[1].split('$');
             
      d[row[0]] = float(each[1])
      if row[0] == 'United States':
        nat_avg = float(each[1])
    
    
    
per_dif = {}
    
for i in d.keys():
   if i != 'United States': 
       per_dif[i]=(d[i]-nat_avg)/nat_avg
   
    #print per_dif    
    

reader = csv.reader(open('Phase_Cost.csv', 'r'))
count = 0
for row in reader:
        
   if count == 0:
        col_head = row
            
   if row[0] == 'Oncology':
          d2 = row
          break
        
   count = count+1
    #print d2
    #print col_head
    
col_nos = {}
count = 0
row_no = 0
for j in col_head:
     if j == 'PHASE 1' or j == 'PHASE 2' or j == 'PHASE 3' or j == 'PHASE 4':
          col_nos[count] = row_no
          count = count + 1
     row_no = row_no + 1
    
p1_avg = float(d2[col_nos.values()[0]].split(' ')[0][1: ])
p2_avg = float(d2[col_nos.values()[1]].split(' ')[0][1: ])
p3_avg = float(d2[col_nos.values()[2]].split(' ')[0][1: ])
p4_avg = float(d2[col_nos.values()[3]].split(' ')[0][1: ])
    
sd1 = 2.5
sd2 = 5
sd3 = 17.5
sd4 = 30
count = 0
    #print type(p1_avg)
for k in per_dif.items():
        #print k[0]
    
     P1 = p1_avg + k[1]*sd1
     P2 = p2_avg + k[1]*sd2
     P3 = p3_avg + k[1]*sd3
     P4 = p4_avg + k[1]*sd4
     cursor.execute("INSERT INTO Cost_By_State (state,phase1,phase2,phase3,phase4) VALUES (%s,%s, %s, %s, %s)",(k[0],P1,P2,P3,P4))        
     count = count + 1

conn.commit();
