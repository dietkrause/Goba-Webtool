from flask import Flask, url_for
from crypt import methods
from flask import Flask, jsonify,render_template,request,flash,redirect,send_file
import os
import json
from apis.twilio import send_mail
from ips import get_ip
import urllib.request

#from matplotlib.font_manager import json_load
from report_generator import create_from_dir,create_from_dir2
from utilities import options,get_location,send_message,database,validation,consult_comments,key_manage,update_client_file,manage_client_pendings,find_company
from twilio.rest import Client
import random
from apis.drive_api import upload_file
from utilities import *


app=Flask(__name__)
p=None
app.config["SECRET_KEY"] ="goba123"
#app.config["DOCUMENT_UPLOADS"]=os.path.abspath("docs")
app.config["DOCUMENT_UPLOADS"]=os.path.relpath("docs")

#--------- global variables ----------
cols_global=[]
from utilities import options_keys,data_list,multiple,doc_list,pms,wks,doc_options
push_code=None
push_sent=False
push_validated=False
error_code=""
push_attempts=0
element={}
mess=""
output=None
users_selected_to_verify=[]
options2=["Dietmar","Raul","Santiago","Ximena","Alejandro","Sebastian","Carlota","Jessica"]
menu=True
selected_pending=None
user=None
goba_update_maillist=["dietmark@gobacapital.com","krausebikes@gmail.com"]
#-------------------------------------

@app.route("/",methods=["POST","GET"] )
def display_menu():
    global push_code
    global push_attempts
    global push_validated
    global error_code
    global push_sent
    global users_selected_to_verify
    global selected_pending
    menu=True
    sandbox.update("B1","")
    push_code=None
    push_sent=False
    push_validated=False
    error_code=""
    push_attempts=0 
    users_selected_to_verify=[]
    selected_pending=None
    open_file_permissions()
    flash("Goba Capital")
    #handeling the storage, every time the menu is called, the uploaded and generated files are deleted.
    dir=os.listdir(app.config["DOCUMENT_UPLOADS"])
    if dir!=[]:
        for f in dir:
            if "keep" not in f:
                os.remove(os.path.join(app.config["DOCUMENT_UPLOADS"],f))
    dir=os.listdir("reports")
    if dir!=[]:
        for f in dir:
            if "keep" not in f:
                os.remove(os.path.join("reports",f))
    #------------------------------------------------
    return render_template("menu.html",menu=menu)
@app.route("/upload-document",methods=["POST","GET"])
def upload_document():
    global menu
    menu=False
    n_file=len(os.listdir(app.config["DOCUMENT_UPLOADS"]))
    if request.method=="POST":
        flash("Portfolio Report")
        if request.files:
            doc = request.files["document"]
            doc.save(os.path.join(app.config["DOCUMENT_UPLOADS"],doc.filename))
            print("Document has been saved")
            return redirect(request.url)

    return render_template("portfolio_report.html",n_file=n_file,menu=menu)

@app.route("/upload-document2",methods=["POST","GET"])
def upload_document2():
    global menu
    menu=False
    n_file=len(os.listdir(app.config["DOCUMENT_UPLOADS"]))
    if n_file!=0:
        ready="Report ready to download!"
    else:
        ready=''
    if request.method=="POST":
        flash("Minimum Outstanding Report")
        if request.files:
            doc = request.files["document"]
            doc.save(os.path.join(app.config["DOCUMENT_UPLOADS"],doc.filename))
            print("Document has been saved")
            return redirect(request.url)

    return render_template("min_out.html",ready=ready,menu=menu)

@app.route("/upload-document3",methods=["POST","GET"])
def upload_document3():
    # ------ HERE IS PENDING TO MANAGE THE IDENTIFICATION OF THE DIFFERENT FILES ACCORDING TO WHAT DOCS THE CLIENT IS MISSING
    #it would be a good idea to send a json object with the identificator
    #also you  have to create a function in utilities that handle the insertion of the link in te database
    #because of this, the json object must include the client mail and also the file identificator
    #you could create an onclick event on the confirm upload button that handles the json sending for every different file
    global goba_update_maillist
    global selected_pending
    global menu
    global doc_list
    global user
    menu=False
    #---------------------
    #user="krausebikes@gmail.com" #this should be dynamical
    #---------------------
    #pending=manage_client_pendings(user) #you could consult directly the google sheet database here
    pending=doc_list
    if request.method=="POST":
        if request.files:
            doc = request.files["document"]
            file_path=os.path.join(app.config["DOCUMENT_UPLOADS"],doc.filename)
            doc.save(file_path)
            file_name=doc.filename
            link = upload_file(file_name=file_name,file_path=file_path)
            dir=os.listdir(app.config["DOCUMENT_UPLOADS"])
            if dir!=[]:
                for f in dir:
                    if "keep" not in f:
                        os.remove(os.path.join(app.config["DOCUMENT_UPLOADS"],f))
            print("selected_pending ->",selected_pending)
            update_client_file(link=link,identification=selected_pending,user=user)
            text=''' <html>
                        <head><head>
                        <body>
                        <h3> {} modified the following document <h3> <br>
                        <h4> {} </h4>
                        <p>You can check the updated file here:</p> <a href={}> Go to file </a>
                        </body>

                    </html>'''.format(str(find_company(user)),selected_pending,link)
            send_mail("gobacapital.it@gmail.com",goba_update_maillist,subject="Client modification detected",html_content=text)
            selected_pending=None
            return redirect(request.url)

    return render_template("client_uploading.html",
                                        menu=menu,
                                        pending=pending,
                                        selected_pending=selected_pending)

@app.route("/client-login",methods=["POST","GET"])
def client_login():
    flash("Client login")
    global user
    return render_template("client_login.html")

@app.route("/login-verification",methods=["POST","GET"])
def login_verification():
    global doc_list
    global pms
    global user
    global selected_pending
    mail=request.form["email"].lower()
    pm=request.form["pm"]
    #pending=doc_list
    pending=manage_client_pendings(mail)
    if pm in pms:
        pm_val=True
        if wks.find(mail)!=None:
            mail_val=True
            user=mail
            return render_template("client_uploading.html",user=user,pending=pending,selected_pending=selected_pending)
        else:
            mail_val=False
    else:
        pm_val=False

    return render_template("client_login.html",pm_val=pm_val,mail_val=mail_val)


@app.route("/select-pending",methods=["POST","GET"])
def confirm_upload():
    global selected_pending
    data=request.get_json()
    global menu
    menu=False
    data=request.get_json()
    data=data[0]["id"]
    selected_pending=data
    return ("/")

@app.route("/download-document",methods=["POST","GET"])
def download_document():
    create_from_dir(app.config["DOCUMENT_UPLOADS"],"reports")
    p=os.path.abspath("reports/Portfolio_Report.xlsx")
    print("document has been succesfully download")
    return send_file(p,as_attachment=True)

@app.route("/download-document2",methods=["POST","GET"])
def download_document2():
    create_from_dir2(app.config["DOCUMENT_UPLOADS"],"reports")
    p=os.path.abspath("reports/Minimum_Outstanding.xlsx")
    print("document has been succesfully download")
    return send_file(p,as_attachment=True)

@app.route("/verification-client-search",methods=["POST","GET"])
def verification_client_search():
    global users_selected_to_verify
    global push_sent
    global push_validated
    global error_code
    global options2
    global menu
    val=sandbox.acell("B1").value
    if val!=None:
        users_selected_to_verify=val.split(",")
        print(users_selected_to_verify)
    menu=False
    len_users=len(users_selected_to_verify)
    flash("Verify your identity")
    return render_template("verification_client_search.html",push_sent=push_sent,
                                                            push_validated=push_validated,
                                                            error_code=error_code,
                                                            options=options2,
                                                            users_selected_to_verify=users_selected_to_verify,
                                                            len_users=len_users,
                                                            menu=menu)
@app.route("/receive-users",methods=["POST","GET"])
def receive_users():
    global sandbox
    global push_sent
    global push_validated
    global error_code
    global options2
    global menu
    global users_selected_to_verify
    len_users=len(users_selected_to_verify)
    users_selected_to_verify=[] 
    users=request.get_json()
    for i in users:
        users_selected_to_verify.append(i["id"])
    v=""
    for us in users_selected_to_verify:
        v+=str(us)+","
    sandbox.update("B1",v[0:len(v)-1])
    return render_template("verification_client_search.html",push_sent=push_sent,
                                                            push_validated=push_validated,
                                                            error_code=error_code,
                                                            options=options2,
                                                            users_selected_to_verify=users_selected_to_verify,
                                                            len_users=len_users,
                                                            menu=menu)

@app.route("/send-push",methods=["POST","GET"])
def send_push():
    global users_selected_to_verify
    global push_sent
    global menu
    menu=False
    numbers={"Dietmar":"DIETMAR_NUM",
                "Raul":"RAUL_NUM",
                "Santiago":"SANTIAGO_NUM",
                "Ximena":"XIMENA_NUM",
                "Alejandro":"ALEJANDRO_NUM",
                "Sebastian":"SEBASTIAN_NUM",
                "Carlota":"CARLOTA_NUM",
                "Jessica":"JESSICA_NUM"}
    if not push_sent:
        key_manage()
        push_sent=True
    flash("Verify your identity")
    mess="Your verification code is: {}".format(key_manage(True))
    for user in users_selected_to_verify:
        send_message(os.environ[numbers[user]],mess)
    sandbox.update("B1","")
    return render_template("push_verification.html",
                            push_validated=push_validated,
                            menu=menu)

@app.route("/ip-display",methods=["POST","GET"])
def ip_display():
    return render_template("map.html")

@app.route("/push-verification",methods=["POST","GET"])
def push_verification():
    global push_code
    global push_sent
    global push_validated
    global error_code
    global push_attempts
    global options2
    global menu
    global users_selected_to_verify
    global goba_update_maillist
    len_users=len(users_selected_to_verify)
    menu=False
    flash("Verify your identity")
    code=request.form["code"]
    if code==key_manage(True):
        sandbox.update("B1","")
        push_validated=True
        push_attempts=0
    else:
        push_sent=False
        push_attempts+=1
        error_code="Ups !, the submitted code was not correct, try sending another push"

        if push_attempts>=2:
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                ip_address=request.environ['REMOTE_ADDR']
            else:
                ip_address=request.environ['HTTP_X_FORWARDED_FOR']

            get_ip(ip_address,goba_update_maillist)
            link="https://gobawebtool.herokuapp.com/ip-display"
            mess="Someone is trying to access to the system. \n details: {}".format(link)
            send_message(os.environ["DIETMAR_NUM"],mess)
        return render_template("verification_client_search.html",
        push_sent=push_sent,
        error_code=error_code,
        push_attempts=push_attempts,
        options=options2,
        menu=menu,
        users_selected_to_verify=users_selected_to_verify,
        len_users=len_users
        )
    return render_template("push_verification.html",
                            push_validated=push_validated,
                            options=options2,
                            menu=menu,
                            users_selected_to_verify=users_selected_to_verify,
                            len_users=len_users)
                                                            
@app.route("/search_clients",methods=["GET","POST"])
def search_clients():
    global doc_options
    global multiple
    global cols_global
    global options
    global options_keys
    global data_list
    global push_validated
    push_validated=False # JUST CHECKING IF THIS WORKS
    len_data_list=len(data_list)
    http="http"
    flash("Search for clients information")
    #options=["opt1","opt2","opt3","opt4","opt5"]
    return render_template("search_clients.html",
                            options=options,
                            cols_global=cols_global,
                            options_keys=options_keys,
                            data_list=data_list,
                            len_data_list=len_data_list,
                            multiple=multiple,
                            doc_options=doc_options)

@app.route("/portfolio-report",methods=["POST","GET"])
def report_generator():
    global menu
    menu=False
    n_file=len(os.listdir(app.config["DOCUMENT_UPLOADS"])) - 1   ## to check if I casn fix the counter
    flash("Portfolio Report")
    return render_template("portfolio_report.html",
                            n_file=n_file,
                            menu=menu)

@app.route("/minimum-outstanding-report",methods=["POST","GET"])
def min_out():
    global menu
    menu=False
    n_file=len(os.listdir(app.config["DOCUMENT_UPLOADS"]))
    if n_file>1:
        ready="Report ready to download!"
    else:
        ready='There is not selected documents'
    flash("Minimum Outstanding Report")
    return render_template("min_out.html",
                            ready=ready,
                            menu=menu)

@app.route("/Processinfo",methods=["POST"])
def Processinfo():
    global cols_global
    output=request.get_json()
    cols_local=[]
    for i in output:
        cols_local.append(i["id"])
    cols_global=cols_local
    return("/")

@app.route("/look-client",methods=["POST","GET"])
def look_client():
    global output
    global data_list
    global element
    output=request.get_json()
    output=int(output)
    element=data_list[output]
    return ("/")

@app.route("/look-client-view",methods=["POST","GET"])
def look_client_view():
    global element
    global options_keys
    global multiple
    global mess
    global data_list
    global output
    if output!=None:
        element=data_list[output]
    try:
        mess=element[options_keys["Bussines name"][0]]
    except KeyError:
        try:
            mess=element[options_keys["Bussines name"][1]]
        except KeyError:
            mess=mess
    try:
        mail=element[options_keys["Email of who filled the form"][0]]
    except KeyError:
        try:
            mail=element[options_keys["Email of who filled the form"][1]]
        except IndexError:
            mail=None
    flash(mess)
    formated_element={}
    ##-------------- I HAVE TO FIX THIS LOGIC TO SELECT THE REQUIRED FIELD (INTERNATIONAL VS US-BASED) -----------------
    if mail!= None:
        for key in options_keys:
            if len(options_keys[key])>1:
                if element[options_keys[key][0]]=='' and element[options_keys[key][1]]=='':
                    formated_element[key]=element[options_keys[key][0]]
                elif element[options_keys[key][0]]!='' and element[options_keys[key][1]]=='':
                    formated_element[key]=element[options_keys[key][0]]
                elif element[options_keys[key][0]]=='' and element[options_keys[key][1]]!='':
                    formated_element[key]=element[options_keys[key][1]]
                else:
                    formated_element[key]=None
            else:
                formated_element[key]=element[options_keys[key][0]]

        formated_element['Marca temporal']=element['Marca temporal']
        comments=consult_comments(mail)
    else:
        comments=None
    empty=[]
    states=display_validation_state(mail)

    return render_template("look_client.html",formated_element=formated_element,
                                                mail=mail,
                                                multiple=multiple,
                                                comments=comments,
                                                empty=empty,
                                                states=states)

@app.route("/update-client-information",methods=["POST","GET"])
def update_client_information():
    output=request.get_json()
    if len(output)==1:
        return ("/")
    validation(output=output,database=database)
    return render_template('menu.html')

@app.route("/client-uploading",methods=["POST","GET"])
def client_uploading():
    return render_template("client_uploading.html")

#this allow me to run the server by just clicking run 
if __name__ =="__main__":
    app.run(debug=True)

