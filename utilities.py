from typing import Dict
import gspread
import os
import requests
from twilio.rest import Client
import time
from apis.twilio import send_mail
import random
from apis.drive_api import set_permission,get_service



options_keys={"Bussines name":["Business_name","B_name_int"],
        "TAX ID":["TAX_ID"],
        "US - Based":["us_based"],
        "Nature of the business":["Nat_business","N_Business_int"],
        "Country":["Country"],
        "Address":["Address","Address_int"],
        "City":["City","City_int"],
        "State":["State"],
        "Zip Code":["Zip_Code","Zipcode_int"],
        "Line Required":["Line_Req"],
        "Required or not similar services in the past (Y/N)":["Fac_before_yn"],
        "Explanation if yes":["If_yes_context"],
        "Amount if yes":["If_yes_amount"],
        "If it has taxes past due":["Tax_pd"],
        "If it has experienced bankruptcy":["Bankruptcy"],
        "If it has experienced a lawsuit":["lawsuit_yn"],
        "Excel file with the business information":["excel"],
        "Legal name of who filled the form":["leg_name"],
        "Title of who filled the form":["Title"],
        "Email of who filled the form":["Email"],
        "Phone of who filled the form":["Phone"],
        "Date in which the disclousure was filled":["Date"],
        "Signs of the beneficial owners":["sign"],
        "IDs of the beneficial owners":["id_pic"],
        "Corporate presentation of the company":["corp_pres","corp_pres_int"],
        "Certificate of good standing":["good_standing","good_standing_eq"],
        "Articles of incorporation":["a_inc","Bconstitution_eq"],
        "Present year financial statements":["pres_year_FE"],
        "If the financial statements were not audited":["if_no_audited"],
        "1 year old financial statement":["one_year_FE"],
        "2 year old financial statement":["2_year_FE"],
        "Interim financial statements":["interim_FE"],
        "Account receivable/ account payable aging report":["AR_aging"],
        "Tax return":["Tax_return"],
        "Examples of operations the client wants to finance":["examples"],           
}
doc_options=["Excel file with the business information",
               "Signs of the beneficial owners",
               "IDs of the beneficial owners",
               "Corporate presentation of the company",
                "Certificate of good standing",
                "Articles of incorporation",
                "Present year financial statements",
                "1 year old financial statement",
                "2 year old financial statement",
                "Interim financial statements",
                "Account receivable/ account payable aging report",
                "Tax return",
                "Examples of operations the client wants to finance"
                ]
letters=["A",'B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA']
key_dict={"B":"Articles of Incorporation",
            "D":"Certificate of Good Standing",
            "F":"Corporate presentation",
            "H":"Excel file with business information",
            "J":"1 year Financial Statements",
            "L":"2 year Financial Statements",
            "N":"3 year Financial Statements",
            "P":"Most Recent Interim Finantial Statements",
            "R":"AR report (if factoring) / AP report (if supli-credit)",
            "T":"Tax Return",
            "V":"Examples of the operations you want to finance",
            "X":"IDs of every beneficial owner",
            "Z":"Sign of every beneficial owner"}

key_dict2_us={"AB":"Articles of Incorporation",
            "AA":"Certificate of Good Standing",
            "Z":"Corporate presentation",
            "Q":"Excel file with business information",
            "AC":"1 year Financial Statements",
            "AE":"2 year Financial Statements",
            "AF":"3 year Financial Statements",
            "AG":"Most Recent Interim Finantial Statements",
            "AH":"AR report (if factoring) / AP report (if supli-credit)",
            "AI":"Tax Return",
            "AJ":"Examples of the operations you want to finance",
            "Y":"IDs of every beneficial owner",
            "X":"Sign of every beneficial owner"}
key_dict2_not_us={"AT":"Articles of Incorporation",
            "AU":"Certificate of Good Standing",
            "AK":"Corporate presentation",
            "Q":"Excel file with business information",
            "AC":"1 year Financial Statements",
            "AE":"2 year Financial Statements",
            "AF":"3 year Financial Statements",
            "AG":"Most Recent Interim Finantial Statements",
            "AH":"AR report (if factoring) / AP report (if supli-credit)",
            "AI":"Tax Return",
            "AJ":"Examples of the operations you want to finance",
            "Y":"IDs of every beneficial owner",
            "X":"Sign of every beneficial owner"}
doc_list=["Articles of Incorporation",
            "Corporate presentation",
           "Corporate presentation",
            "Excel file with business information",
            "1 year Financial Statements",
            "2 year Financial Statements",
            "3 year Financial Statements",
            "Most Recent Interim Finantial Statements",
            "AR report (if factoring) / AP report (if supli-credit)",
            "Tax Return",
            "Examples of the operations you want to finance",
            "IDs of every beneficial owner",
            "Sign of every beneficial owner"
            ]
pms=['44412', '90753', '34833', '89453', '34696', '91868', '73450', '82958', '81618', '65312', '90020', '99703', '76903', '38290', '30469', '24238', '39229', '95552', '47906', '51102', '45319', '83731', '47300', '61316', '85431', '83789', '53303', '86885', '28245', '17289', '79951', '41111', '90175', '85378', '70507', '92452', '74778', '26589', '68515', '75823', '91077', '28764', '11564', '32519', '81497', '60727', '74613', '57392', '95995', '30817', '66253', '47298', '90146', '86772', '41312', '52488', '44502', '63455', '76105', '92046', '26493', '25503', '29341', '62843', '59505', '52228', '64074', '50663', '83294', '15445', '32239', '84105', '75227', '65717', '99480', '72618', '85916', '62152', '19826', '14145', '41947', '16400', '10148', '34323', '82381', '81845', '17824', '27111', '64097', '93600', '62824', '39410', '29642', '74321', '88968', '32911', '76316', '92810', '44298', '53270']
def get_location(ip):
    ip_address = ip
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data

def send_message(TO,MESS):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    
    message = client.messages \
                .create(
                     body=MESS,
                     from_=os.environ["TWILIO_NUM"],
                     to=TO
                 )
sa=gspread.service_account(os.environ['SERVICE_ACCOUNT'])
sh=sa.open("application_form")
wks= sh.worksheet("form_responses")
database=sh.worksheet("database")
sandbox=sh.worksheet("sandbox")

data_list=wks.get_all_records()

options=[]
first=True
for opt in options_keys:
    if first:
        first=False
        continue
    else:
        options.append(opt)

dic={'Marca temporal': '27/6/2022 17:17:56', 'Business_name': 'Dietmar LLC', 'DATE': '27/6/2022', 'TAX_ID': '207779148', 'Nat_business': 'Software Development', 'Address': '560 Lincoln St.', 'City': 'EVANSTON', 'State': 'Illinois', 'Zip_Code': '60208', 'Line_Req': '1000000', 'Fac_before_yn': 'No', 'If_yes_context': '', 'If_yes_amount': '', 'Tax_pd': 'No', 'bankruptcy': 'No', 'lawsuit_yn': 'No', 'excel': 'https://drive.google.com/open?id=1QQsXOnta9sENo8upKd12CnF53MYQcNzR', 'leg_name': 'Dietmar Luther Krause Gutierrez', 'Title': 'CTO', 'Email': 'DIETMARKRAUSE2025@U.NORTHWESTERN.EDU', 'Phone': '18728105429', 'Date': '27/6/2022', 'legal_dis': 'I certify that the information provided is correct, and I assume the legal implications of providing fake information.', 'sign': 'https://drive.google.com/open?id=1l7Hde2l8ak7CrKldTBc2_eeze7kVrFil', 'id_pic': 'https://drive.google.com/open?id=1jm-um0Drr5Hr0YQuokTxfMCSlDOe_NIX', 'corp_pres': '', 'good_standing': 'https://drive.google.com/open?id=1Sx0v1vcDNcszDjznYfChNsqZk6nOsGPs', 'a_inc': 'https://drive.google.com/open?id=1zFIngVUB_GdYLkMhVg6JSxoRUnwPLxKz', 'pres_year_FE': 'https://drive.google.com/open?id=1twvwR3qRi9Pz7zzpxQD_Y4hz65gPZyAt', 'if_no_audited': 'I didn’t had time for it', 'one_year_FE': 'https://drive.google.com/open?id=1gBVo9e_N3JOcbR0U2AEWImEzXZanQk08', '2_year_FE': 'https://drive.google.com/open?id=1I76BvqrVuHe2O1nl43V7vHoTKFcM5srL', 'interim_FE': 'https://drive.google.com/open?id=1FLsn0r6YAnxII4AEu_F_l-s5lhH_BC-X', 'AR_aging': 'https://drive.google.com/open?id=1Cq3HmwbhflbPB0Wk0s1TICalDenkF8Gz', 'Tax_return': 'https://drive.google.com/open?id=12iAY1UOEDTs1gJ01Pw5Sp3bMayXMVAcc, https://drive.google.com/open?id=17hDmKYtS5qL3K3rMuzu5645I2TyzkDWa', 'examples': 'https://drive.google.com/open?id=1pTOoujpPpjQxKNyxtO3p0-taCzh-sUm_', 'corp_press_int': 'https://drive.google.com/open?id=1UFVSii7YalD5EcKiQWCsmwhd-f8tOgYU', 'US_based': 'Yes', 'B_name_int': '', 'Date_int': '', 'N_Business_int': '', 'Country': '', 'City_int': '', 'Address_int': '', 'Zipcode_int': '', 'Bconstitution_eq': '', 'good_standing_eq': ''}
def normalize_key(key:str,dic):
    for k in dic:
        if k==key:
            if "," in dic[k]:
                l=dic[k].split(",")
                dic[k]=l
            else:
                dic[k]=[dic[k]]
    return dic

multiple=['Tax return',"Signs of the beneficial owners","IDs of the beneficial owners","Examples of operations the client wants to finance"]
def normalize_dic(l:list,dic):
    for k in l:
        try:
            dic=normalize_key(options_keys[k][0],dic)
        except KeyError:
            dic=normalize_key(options_keys[k][1],dic)
    return dic

def normalize_list(l,l_dic):
    n_list=[]
    for dic in l_dic:
        n_list.append(normalize_dic(l,dic))
    return n_list

data_list=normalize_list(multiple,data_list)


test_list=[['B', True, ' Previous comment'], ['D', True, ' Previous comment 2 modificated'], ['F', 'pending', ' Previous comment 3'], ['H', 'pending', ' Previous comment 4'], ['J', 'pending', ' Previous comment 5'], ['L', 'pending', ' Previous comment 6'], ['N', 'pending', ' Previous comment 7'], ['P', 'pending', ' Previous comment 8'], ['R', 'pending', ' Previous comment 9'], ['T', 'pending', ' Previous comment 10'], ['V', 'pending', ' Previous comment 11'], ['X', 'pending', ' Previous comment 12'], ['Z', 'pending', ' Previous comment 13'], 'DIETMARKRAUSE2025@U.NORTHWESTERN.EDU']

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)


def notificate(user,errors,pending,validated,updated):
    t1=""
    t2=""
    t3=""
    if errors==[] and pending==[]:
        content="<center> <p> Congratulations! </p> </center><br> <center> <p>All your documents have been validated, one of our executives is going to get in touch soon <p> </center><br>"
        t="<html>"+"<head></head><body>"+content+"</body></html>"
        send_mail("gobacapital.it@gmail.com",[user],subject="Goba Update",html_content=content)
    else:
        if errors!=[]:
                t1+= " <center><p> <h3> <u> The following issues were detected in your document submission </u> </h3> </p></center> <br>"
        t11=""
        e_c=1
        for error in errors:
            if error[0] not in updated:
                t11+="<center><p style='color:red;'>{}) {} </p> <p> \t comment : {} </p></center> <br>".format(e_c,error[0],error[1])
            else:
                t11+="<center><p> <h4 style='color:red;'> {}) {} <u>(UPDATED)</u> </h4></p> <p> comment : {} </p> </center><br>".format(e_c,error[0],error[1])
            e_c+=1
        t1+=t11  

        if pending!=[]:
                t2+= "<center><p><h3> <u> The following elements are pending to be approved</u> </h3> </p> </center> <br>"
        t22=""
        e_c=1
        for p in pending:
            if p not in updated:
                t22+="<center><p style='color:orange;'>{}) {} </p> </center><br> ".format(e_c,p)
            else:
                t22+="<center><p> <h4 style='color:orange;'> {}) {} <u>(UPDATED)</u> </h4> </p></center> <br> ".format(e_c,p)
            e_c+=1
        t2+=t22

        if validated!=[]:
                t3+= "<center><p> <h3> <u>The following elements were approved by our executives </u> </h3> </p> <center><br>"
        t33=""
        e_c=1
        for p in validated:
            if p not in updated:
                t33+="<center><p style='color:green;'> {}) {} </p> </center><br> ".format(e_c,p)
            else:
                t33+="<center><p> <h4 style='color:green;'> {}) {} <u>(UPDATED)</u> </h4> </p></center> <br> ".format(e_c,p)
            e_c+=1
        t3+=t33
        permission=pms[random.randint(0,100)]
        pm="<br><br><center><h2><u> Permission number : {} </u></h2></center>".format(permission)
        url="https://gobawebtool.herokuapp.com/client-login"
        style='''display: block;
                line-height: 25px;
                position: relative;
                width: 280px;
                height: 50px;
                border-radius: 25px;
                background: linear-gradient(40deg, #568203, #568203);
                box-shadow: 0 4px 7px rgba(0, 0, 0, 0.4);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #fff;
                font-weight: bold;
                cursor: pointer;
                transition: transform .2s ease-out;
                text-align: center;
                -moz-box-align: center;
                font-style: white;'''
                
        button="<br> <center> <a type='button' href={} style='{}' > <center> Update documents </center></a></center>".format(url,style)
        if updated==[]:
            t="<html>"+"<head></head><body>"+t1+t2+t3+pm+"Click below to update your documents: <br>"+button+"</body></html>"
            send_mail("gobacapital.it@gmail.com",[user],subject="Goba Update",html_content=t)
        else:
            t="<html>"+"<head></head><body>"+ "<p><h2><u> Some of your documents have been re-checked </u></h2></p> <br>"+t1+t2+t3+pm+"Click below to update your documents: <br>"+button+"</body></html>"
            send_mail("gobacapital.it@gmail.com",[user],subject="Updated revision",html_content=t)

    return None

def validation(output,database):
    global letters
    notify=output.pop()
    user=output.pop()
    cell=database.find(user)
    errors=[]
    pending=[]
    validated=[]
    if cell==None:
        updated=[]
        next_row = next_available_row(database)
        database.update("A{}".format(next_row),str(user).lower())
        counter=0
        for i in range(1,len(output)+1):
            c1=str(letters[i+counter])+str(next_row)
            c2=str(letters[i+1+counter])+str(next_row)
            database.update(c1,str(output[i-1][1]))
            time.sleep(0.001)
            database.update(c2,str(output[i-1][2]))
            time.sleep(0.001)
            counter+=1
        for field in output:
            val=field[1]
            if val==False:
                errors.append([key_dict[field[0]],field[2]])
            elif val=="pending":
                pending.append(key_dict[field[0]])
            else:
                validated.append(key_dict[field[0]])
        if notify:
            notificate(user,errors,pending,validated,updated)

    else:
        updated=[]
        row=cell.row
        counter=0
        for i in range(1,len(output)+1):
            c1=str(letters[i+counter])+str(row)
            c2=str(letters[i+1+counter])+str(row)
            if database.acell(c1).value !=str(output[i-1][1]) or database.acell(c2).value !=str(output[i-1][2]):
                database.update(c1,str(output[i-1][1]))
                time.sleep(0.001)
                database.update(c2,str(output[i-1][2]))
                time.sleep(0.001)
                updated.append(key_dict[str(letters[i+counter])])
            counter+=1
        for field in output:
            val=field[1]
            if val==False:
                errors.append([key_dict[field[0]],field[2]])
            elif val=="pending":
                pending.append(key_dict[field[0]])
            else:
                validated.append(key_dict[field[0]])
        if notify:
            notificate(user,errors,pending,validated,updated)

    return None

def consult_comments(mail):
    global letters
    global database
    cell=database.find(mail)
    result={}
    if cell==None:
        counter=1
        for l in letters:
            if counter==1:
                counter+=1
                continue
            else:
                if counter%2!=0:
                    result[l]=""
            counter+=1
    else:
        counter=1
        row=cell.row
        for l in letters:
            if counter==1:
                counter+=1
                continue
            else:
                if counter%2!=0:
                    c="{}{}".format(l,row)
                    result[l]=database.acell(c).value 
            counter+=1
    return result

def key_manage(consult:bool=False):
    global sandbox
    if not consult:
        sandbox.update("A1",str(random.randint(1000,9999)))
    else:
        return sandbox.acell("A1").value


def update_client_file(user:str,link:str,identification:str):
    global database
    global wks
    global doc_list
    cell=wks.find(user)
    if cell==None:
        cell=wks.find(user.upper())
        if cell==None:
            cell=wks.find(user.lower())

    if cell!=None:
        row=cell.row
        if str(wks.acell(("AL{}".format(row))).value).lower() =="yes":
            key_dict2=key_dict2_us
        else:
            key_dict2=key_dict2_not_us
        for key in key_dict2:
            if key_dict2[key]==identification:
                c="{}{}".format(key,row)
                if identification in multiple:
                    new="{},{}".format(wks.acell(c).value,link)
                    wks.update(c,new)
                else:
                    new=str(link)
                    wks.update(c,new)
        

    return None

def find_company(user:str):
    cell=wks.find(user)
    if cell==None:
        cell=wks.find(user.upper())
        if cell==None:
            cell=wks.find(user.lower())
    if cell!=None:
        row=cell.row
        company=wks.acell(("B{}".format(row))).value
        if company==None:
            company=wks.acell(("AM{}".format(row))).value
    return str(company)

def  display_validation_state(user):
    states={}
    global database
    global letters
    cell=database.find(user)
    if cell==None:
        cell=database.find(user.upper())
        if cell==None:
            cell=database.find(user.lower())
            if cell==None:
                for i in range(1,len(letters)):
                    if i%2==0:
                        continue
                    else: 
                        states[letters[i]]= "- Not reviewed it - "
    if cell!=None:
        print(cell.row)
        line=database.row_values(cell.row)
        print("line -->", line)
        for i in range(1,len(letters)):
            if i%2==0:
                continue
            else:
                value=line[i]
                if value=="True":
                    state="Validated"
                    states[letters[i]]=state
                elif value=="pending":
                    state="Pending"
                    states[letters[i]]=state
                elif value=="False":
                    state="Previously Rejected"
                    states[letters[i]]=state
    return states

def  manage_client_pendings(user):
    global database
    global letters
    cell=database.find(user)
    print(cell)
    pend_doc_list=[]
    if cell==None:
        cell=wks.find(user.upper())
        if cell==None:
            cell=wks.find(user.lower())
    if cell!=None:
        line=database.row_values(cell.row)
        for i in range(1,len(letters)):
            if i%2==0:
                continue
            else:
                value=line[i]
                if value=="pending" or value=="False":
                    pend_doc_list.append(key_dict[letters[i]])           
    return pend_doc_list

#This function should be implemented everytime the menu is called
def open_file_permissions():
    global wks
    service=get_service(
                api_name='drive',
                api_version='v3',
                scopes=['https://www.googleapis.com/auth/drive.metadata.readonly',
                "https://www.googleapis.com/auth/drive",
                ],
                key_file_location=os.environ["SERVICE_ACCOUNT"])
    for dic in wks.get_all_records():
        for key in dic:
            if "/view" not in str(dic[key]):
                if "google.com" in str(dic[key]):
                    if "," not in str(dic[key]):
                        try:
                            id=str(dic[key]).strip(" ").split("?")[1].strip(" ").split("=")[1]
                            set_permission(service,id)
                        except IndexError:
                            print(dic[key])
                    else:
                        for url in str(dic[key]).strip(" ").split(","):
                            id=url.split("?")[1].strip(" ").split("=")[1]
                            set_permission(service,id)        
    return None




            


