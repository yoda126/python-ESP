#p2025845
#Chian ZhengHang
#DISM 1B/01

import sys#Library to exit code anytime
import socket#Library for socket
import threading#Library to do multi-threading
import datetime#for the data and time of
import time#Library to add delay
import smtplib#For sending invoice email
import ssl#For sending invoice email

#Path for txt files
log_txt_path = "C:/PSEC/server/admin/logs.txt"
rawlog_txt_path = "C:/PSEC/server/admin/rawlogs.txt"
services_txt_path = "C:/PSEC/server/data/serviceslist.txt"
invoice_num_txt_path = "C:/PSEC/server/data/Invoicenum.txt"
invoice_tracking_txt_path = "C:/PSEC/server/data/Invoicetracking.txt"
maintenance_txt_path = "C:/PSEC/server/data/maintenance.txt"
adminaccounts_txt_path = "C:/PSEC/server/admin/adminaccounts.txt"

#become a server socket, maximum 5 pending connections
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 8089))
serversocket.listen(5)
print( "Server starts listening... ")
stopFlag=False

def split_service_exdate_date(service_exdate_date):#Split the argument(a string containing service, duration and date) into service, duration, date and return them
    service,exdate_date = service_exdate_date.split("[")
    service = service.replace("|","")
    exdate,date = exdate_date.split("]")
    date = date.replace("<","")
    date = date.replace(">","")
    date = date.replace("|","")
    return service,exdate,date

def checkifinserviceslist(service):#Check if service in services list
    with open(services_txt_path,"r") as services_list:
        for line in services_list:
            serviceinlist = (line.split(":")[0]).replace("|","")
            if service == serviceinlist:
                return True
        return False

def account_path(username):#Generate path for user account file
    account_data_path = "C:/PSEC/server/data/accounts/" + username + ".txt"
    return account_data_path

def simple_encryption(data):#Do simple encryption
    encrypteddata = data.encode()
    encrypteddata = encrypteddata.hex()[::-1]
    encrypteddata = encrypteddata[-2:] + encrypteddata[:-2]
    return encrypteddata

def simple_decryption(data):#Do simple decryption
    decrypteddata = data[2:] + data[:2]
    decrypteddata = decrypteddata[::-1]
    decrypteddata = bytes.fromhex(decrypteddata)
    return decrypteddata.decode()

def savelog(message,client_addr,logtype=""):#Save logs to log.txt and rawlogs.txt file
    datenow = datetime.datetime.now()
    logtime = str(datenow.strftime("%c"))
    logmessage = "\n["+logtime+"]"+" "+str(client_addr)+" "+str(message)
    i = 0
    while True:
        i += 1
        if i > 20:
            print("Log was unable to be saved")
        try:
            if logtype == "raw":
                with open(rawlog_txt_path,"a") as logsfile:
                    logsfile.write(logmessage)
            else:
                with open(log_txt_path,"a") as logsfile:
                    logsfile.write(logmessage)
                print(logmessage)
            break
        except:
            time.sleep(0.1)

def checkpass(username,passwd,client_addr):#Check if password is correct for user
    with open(account_path(username),"r") as account_data:
        accountinfolines = account_data.readlines()
    account_password = simple_decryption(accountinfolines[1][10:].rstrip())
    if account_password == simple_decryption(passwd):
        return True
    else:
        savelog(username+"'s password failed to authenticate",client_addr)
        return False
        

def test_if_file_exist(Filepath):#Check if a file exist
    try:
        f = open(Filepath)
        f.close()
        return True
    except FileNotFoundError:
        print(f"{Filepath} path has no existing file")
        return False

def rssl(message,client_addr):#Searching for service
    searchserviceslist = []
    usersearchinput = message
    with open(services_txt_path,"r") as servicesfile:
        for line in servicesfile:
            lowername = line.split(":")[0].lower().strip()
            lowername = lowername.replace("|","")
            if usersearchinput in lowername:
                searchedserviceline = line.strip()
                searchserviceslist += [searchedserviceline]
    reply = "\n".join(searchserviceslist)
    savelog("Searched for '"+usersearchinput+"' in services list",client_addr)
    return reply

def rsfl(client_addr):#Retrieve full service list
    with open(services_txt_path,"r") as serviceslistfile:
        reply = serviceslistfile.read()
    savelog("Retrieved full service list",client_addr)
    return reply

def logi(message,client_addr):#Login to a account
    clientusername,clientpassword = message.split("^")
    account_data_path = account_path(clientusername)
    if test_if_file_exist(account_data_path):
        with open(account_data_path,"r") as account_data:
            accountinfolines = account_data.readlines()
        account_password = simple_decryption(accountinfolines[1][10:].rstrip())
        clientpassword = simple_decryption(clientpassword)
        if account_password == clientpassword:
            clientfullname = simple_decryption(accountinfolines[2][11:].strip())
            reply = f"\nWelcome {clientfullname}, you have successfully logged in."
            reply += expired_service(clientusername,client_addr)
            reply += check_cart_for_removed_services(clientusername,client_addr)
            savelog("successfully logged into "+clientusername,client_addr)
        else:
            savelog("Failed to log into "+clientusername+" as password is wrong",client_addr)
            reply = "failed"
    else:
        savelog("Failed to log into "+clientusername+" as there is no such user registered",client_addr)
        reply = "failed"
    return reply

def expired_service(clientusername,client_addr): #Remove expired services from subscribed services
    account_data_path = account_path(clientusername)
    with open(account_data_path,"r") as account_data:
        old_account_data_string = account_data.read()
    accountinfolines = old_account_data_string.split("\n")
    subscribedservices = accountinfolines[6][18:]
    if subscribedservices == " ":
        return ""
    else:
        reply = ""
        subscribedservices = subscribedservices.strip()
        subscribedserviceslist = subscribedservices.split(",")
        datenow = datetime.datetime.now()
        daynow,monthnow,yearnow = int(datenow.strftime("%d")),int(datenow.strftime("%m")),int(datenow.strftime("%Y"))
        new_subscribed_services_list = []
        for service_exdate_date in subscribedserviceslist:
            service,exdate,datebought = split_service_exdate_date(service_exdate_date)
            exday,exmonth,exyear = exdate.split("/")
            exday,exmonth,exyear = int(exday),int(exmonth),int(exyear)
            if yearnow < exyear:
                new_subscribed_services_list += [service_exdate_date.strip()]
            elif (yearnow == exyear) and (monthnow<exmonth):
                new_subscribed_services_list += [service_exdate_date.strip()]
            elif (yearnow == exyear) and (monthnow==exmonth) and (daynow<exday):
                new_subscribed_services_list += [service_exdate_date.strip()]
            else:
                reply += f"\n{service} has expired and will be removed from subscribed services."
        old_subscribedservices_string = accountinfolines[6].strip()
        new_subscribedservices_string = "Existing services: " + ",".join(new_subscribed_services_list)
        if old_subscribedservices_string == new_subscribedservices_string:
            return ""
        old_subscribedservices_string = old_account_data_string.split("\n")[6]
        new_account_data_string = old_account_data_string.replace(old_subscribedservices_string,new_subscribedservices_string)
        with open(account_data_path,"w") as account_data:
            account_data.write(new_account_data_string)
        savelog("Expired services has been updated and removed from "+clientusername+" subscribed services",client_addr)
    return reply

def check_cart_for_removed_services(clientusername,client_addr):#Check user's cart for services not in services list anymore and remove them
    account_data_path = account_path(clientusername)
    reply = ""
    with open(account_data_path,"r") as account_data:
        account_data_string = account_data.read()
    fullcart = account_data_string.split("\n")[9]
    cart = fullcart[5:]
    if cart != " ":
        cart = cart.strip()
        cartlist = cart.split(",")
        newcartlist = []
        for service_and_years in cartlist:
            service = service_and_years.split("[")[0].replace("|","")
            if checkifinserviceslist(service):
                newcartlist = newcartlist + [service_and_years]
            else:
                reply += f"\n{service} is not avilable anymore and has been removed from cart."
        if newcartlist != cartlist:
            new_account_data_string = account_data_string.replace(fullcart,"Cart: "+",".join(newcartlist))
            with open(account_data_path,"w") as account_data:
                account_data.write(new_account_data_string)
            savelog("Services not in services list anymore has been removed from the cart of "+clientusername,client_addr)
    return reply

def ciue(message,client_addr): #check if user account already exist
    account_data_path = account_path(message.lower())
    if test_if_file_exist(account_data_path):
        savelog("checked that "+message+" account exist",client_addr)
        return "exist"
    else:
        savelog("checked that "+message+" account do not exist",client_addr)
        return "noexist"

def mnaf(message,client_addr): #Make new account file
    username, password, fullname, email, address1, address2 = message.split("^")
    username = username.lower()
    new_account_data_filename = account_path(username)
    if test_if_file_exist(new_account_data_filename):
        return "failed"
    else:
        try:
            with open(new_account_data_filename,"w") as new_account_data_file:
                new_account_data_file.write("Username: " + username + "\nPassword: " + password + "\nFull name: " + fullname + "\nEmail: " + email + "\nAddress line 1: " + address1 + "\nAddress line 2: " + address2 + "\nExisting services: \nTotal amount of money spent: 0\nMembership Tier: Bronze\nCart: ")
            savelog("New account file for "+username+" created",client_addr)
            return "succeed"
        except:
            savelog("New account file for "+username+"not able to be created",client_addr)
            return "failed"

def astc(message,client_addr): #Add service to cart
    servicetoadd,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_data_path = account_path(clientusername)
    with open(account_data_path,"r") as account_data:
        checkcart = account_data.readlines()[9].split(":")[1]
    if checkcart == " ":
        with open(account_data_path,"a") as account_data:
            account_data.write(f"|{servicetoadd}[1]|")
    else:
        service_cart_info_to_change = False
        checkcart = (checkcart.strip()).replace("|","")
        cartlist = checkcart.split(",")
        for serviceinfo_cart in cartlist:
            service = (serviceinfo_cart.strip()).split("[")[0]
            if service == servicetoadd:
                service_cart_info_to_change = serviceinfo_cart
        if service_cart_info_to_change == False:
            with open(account_data_path,"a") as account_data:
                account_data.write(f",|{servicetoadd}[1]|")
        else:
            numofyear = (service_cart_info_to_change.split("[")[1]).replace("]","")
            numofyear = int(numofyear) + 1
            new_service_in_cart = service_cart_info_to_change.split("[")[0] + f"[{numofyear}]"
            with open(account_data_path,"r") as account_data:
                account_data_string = account_data.read()
            new_account_data = account_data_string.replace(f"|{service_cart_info_to_change}|",f"|{new_service_in_cart}|")                          
            with open(account_data_path,"w") as account_data:
                account_data.write(new_account_data)
    savelog(servicetoadd+" was added to "+clientusername+"'s cart",client_addr)
    return "service added to cart"

def sdpc(message,client_addr): #Expected services, duration of subscription and price infomration part of invoice for services in cart
    payment,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_file_path = account_path(clientusername)
    cartchange = check_cart_for_removed_services(clientusername,client_addr)
    with open(account_file_path,"r") as account_data:
        account_data_lines = account_data.readlines()
        checkcart,membershiptier = account_data_lines[9].split(":")[1],account_data_lines[8][17:].strip()
    if checkcart == " ":
        return "No service"
    cart = (checkcart.strip()).replace("|","")
    with open(services_txt_path,"r") as servicesprice_file:
        services_and_price = servicesprice_file.readlines()
    cartlist = cart.split(",")
    paymentstring = "\n{:<5} {:<40} {:<10} {}".format("No.","Service:","Duration:","Amount:")
    i = 0
    subtotal = 0
    servicenamelist = []
    for service in cartlist:
        servicename,duration = service.split("[")
        servicenamelist += [servicename]
        duration = duration.replace("]","")
        for service_nameprice in services_and_price:
            if servicename == (service_nameprice.split(":")[0]).replace("|",""):
                price_of_service = float(service_nameprice.split(":")[1]) * int(duration)
                price_of_service = round((price_of_service/107)*100,2)
                subtotal += price_of_service
                price_of_service = "${:.2f}".format(price_of_service)
                break
        if duration == "1":
            duration = duration + " year"
        else:
            duration = duration + " years"
        i += 1  
        paymentstring += "\n{:<5} {:<40} {:<10} {}".format(i,servicename,duration,price_of_service)
    paymentstring += "\n\n{:>57} {}".format("Subtotal: ","${:.2f}".format(subtotal))
    if membershiptier == "Bronze":#Give discount according to membershiptier
        discount = 0
    elif membershiptier == "Sliver":
        discount = round((subtotal/100)*10,2)
    elif membershiptier == "Gold":
        discount = round((subtotal/100)*20,2)
    paymentstring += "\n{:>57} -${:.2f}".format(f"Member's discount({membershiptier})",discount)
    gst = ((subtotal-discount)/100*7) // 0.01 * 0.01
    paymentstring += "\n{:>57} ${:.2f}".format("GST 7%: ",gst)
    total = subtotal - discount + gst
    paymentstring += "\n{:>57} ${:.2f}".format("Total: ",total)
    savelog(clientusername+" got expected services, duration of subscription and price infomration part of invoice for services in cart",client_addr)
    if payment == "yes":
        return afterpayment(paymentstring,total,cartlist,clientusername,client_addr)
    else:
        return cartchange + "\n" + paymentstring + "^" + ",".join(servicenamelist)

def afterpayment(invoicestring,total,cartlist,clientusername,client_addr):#Finish payment, generate invoice and move services in cart into existing(subscribed) services, update total amount of money spent and membership tier of user account
    email = "defenber@gmail.com"
    date = datetime.datetime.now()
    account_file_path = account_path(clientusername)
    datenow = date.strftime("%d") + "/" + date.strftime("%m") + "/" + date.strftime("%Y")
    with open(account_file_path,"r") as account_data:
        account_data_string = account_data.read()
    account_data_lines = account_data_string.split("\n")
    existingservices = (account_data_lines[6])[18:]
    if existingservices == " ":
        servicelist = []
        for service_duration in cartlist:
            service, duration = service_duration.split("[")
            duration = int(duration.replace("]",""))
            exdate = date.strftime("%d") + "/" + date.strftime("%m") + "/" + str(int(date.strftime("%Y"))+duration)
            servicelist = servicelist + [f"|{service}[{exdate}]<{datenow}>|"]
        new_account_data_string = account_data_string.replace("Existing services: ","Existing services: "+",".join(servicelist))
    else:
        old_existingservices_string = account_data_lines[6].strip()
        new_existingservices_string = old_existingservices_string
        existingservices = existingservices.strip()
        nonexistingservices = ""
        if "," in existingservices:
            existingserviceslist = existingservices.split(",")
        else:
            existingserviceslist = [existingservices]
        for serviceduration_in_cart in cartlist:
            service_in_cart_existing = False
            service_in_cart, duration_for_service_cart = serviceduration_in_cart.split("[")
            duration_for_service_cart = int(duration_for_service_cart.replace("]",""))
            for service_subscribed_data in existingserviceslist:
                service_subscribed,oldexdate,subdate  = split_service_exdate_date(service_subscribed_data)
                service_subscribed = service_subscribed.replace("|","")
                if service_in_cart == service_subscribed:
                    service_in_cart_existing = True
                    exday,exmonth,exyear = oldexdate.split("/")
                    new_exyear = int(exyear) + duration_for_service_cart
                    list_to_join = [exday,exmonth,str(new_exyear)]
                    exdate =  "/".join(list_to_join)
                    new_service_subscribed_data = f"|{service_subscribed}[{exdate}]<{subdate}>|"
                    new_existingservices_string = new_existingservices_string.replace(service_subscribed_data,new_service_subscribed_data)
                    break
            if not(service_in_cart_existing):
                exdate = date.strftime("%d") + "/" + date.strftime("%m") + "/" + str(int(date.strftime("%Y"))+duration_for_service_cart)
                new_existingservices_string += f",|{service_in_cart}[{exdate}]<{datenow}>|"
        new_account_data_string = account_data_string.replace(old_existingservices_string,new_existingservices_string)
    existingcart = account_data_lines[9]
    new_account_data_string = new_account_data_string.replace(existingcart,"Cart: ")
    oldmoneyspentstring = account_data_lines[7].strip()
    moneyspent = float(oldmoneyspentstring[29:]) + float(total)
    newmoneyspentstring = "Total amount of money spent: {:.2f}".format(moneyspent)
    new_account_data_string = new_account_data_string.replace(oldmoneyspentstring,newmoneyspentstring)

    existingmembershiptier = account_data_lines[8].strip()
    if moneyspent >= 1000000:#Change membership tier of user's account according to total money spent
        newmembershiptier = "Membership Tier: Gold"
        new_account_data_string = new_account_data_string.replace(existingmembershiptier,newmembershiptier)
    elif moneyspent >= 100000:
        newmembershiptier = "Membership Tier: Sliver"
        new_account_data_string = new_account_data_string.replace(existingmembershiptier,newmembershiptier)

    with open(account_file_path,"w") as account_data:
        account_data.write(new_account_data_string)
                    
    with open(invoice_num_txt_path,"r") as invoicenumdata:
        invoicenumber = invoicenumdata.read()

    userfullname = simple_decryption(account_data_lines[2][11:].strip())
    useremail = simple_decryption(account_data_lines[3][7:].strip())
    useraddress1 = simple_decryption(account_data_lines[4][15:].strip())
    useraddress2 = simple_decryption(account_data_lines[5][15:].strip())
    invoicestart = "Invoice#{}\nInvoice date: {}\nDue date: {}".format(invoicenumber,datenow,datenow) 
    invoicestart += f"\n\nFrom:\nDEFENBER Inc.\n{email}\n69 Fake Street\nSingapore\n\nTo:\n" + userfullname
    invoicestart += "\n{}\n{}\n{}\n".format(useremail,useraddress1,useraddress2)
    finalinvoice = invoicestart + invoicestring  + "\n{:>57} ${:.2f}".format("Paid: ",total) + "\n{:>57} ${}".format("Due: ",0.00) + "\n\n\nThis invoice also acts as a recipe(proof of payment)"
    invoicefilename = "C:/PSEC/server/data/Invoices/Invoice#" + str(invoicenumber) + ".txt"
    with open(invoicefilename,"w") as newinvoicefile:
        newinvoicefile.write(finalinvoice)
    with open(invoice_tracking_txt_path,"r") as invoicetracking:
        invoice_tracking_string = invoicetracking.read()
    if invoice_tracking_string == "":
        invoice_tracking_string = "Invoice#{}:{}".format(invoicenumber,clientusername)
        with open(invoice_tracking_txt_path,"w") as invoicetrackingdata:
            invoicetrackingdata.write(invoice_tracking_string)
    else:
        invoice_tracking_string = "\nInvoice#{}:{}".format(invoicenumber,clientusername)
        with open(invoice_tracking_txt_path,"a") as invoicetrackingdata:
            invoicetrackingdata.write(invoice_tracking_string)
    newinvoicenumber = int(invoicenumber) + 1
    newinvoicenumber = str(newinvoicenumber)
    with open(invoice_num_txt_path,"w") as invoice_num_data:
        invoice_num_data.write(newinvoicenumber)
    try:
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "sendingemailpython@gmail.com"
        receiver_email = useremail
        password = "python123@"
        message = "Subject: Invoice for defenber services\n" + finalinvoice
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:#Send email invoice to user's email
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        savelog(clientusername+" finished payment and invoice was sent to his email",client_addr)
        return "emailsuccess" + "^" + finalinvoice + "^" + str(invoicenumber)
    except:
        savelog(clientusername+" finished payment and invoice was unable to be sent to his email",client_addr)
        return "success" + "^" + finalinvoice + "^" + str(invoicenumber)

def esic(message,client_addr): #Change duration to subscribe for a service in cart
    serviceduration_to_edit,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_data_path = account_path(clientusername)
    servicename,duration = serviceduration_to_edit.split("[")
    duration = duration[:-1]
    print(duration)
    with open(account_data_path,"r") as account_data:
        account_data_list = account_data.readlines()
        cartstring = account_data_list[9].split(":")[1]
    if cartstring == " ":
        return "update failed"
    cartstring = cartstring.strip()
    cartstring = cartstring.replace("|","")
    cartlist = cartstring.split(",")
    newcartlist = []
    servicefound = False
    for servicename_incart_duration in cartlist:
        servicename_incart = servicename_incart_duration.split("[")[0]
        if servicename_incart == servicename:
            if duration == "0":
                pass
            else:
                newcartlist += ["|"+servicename+"["+duration+"]"+"|"]
            servicefound = True
        else:
            newcartlist += ["|"+servicename_incart_duration+"|"]
    if servicefound == False:
        return "update failed"
    newcartstring = ",".join(newcartlist)
    account_data_list[9] = "Cart: " + newcartstring
    with open(account_data_path,"w") as account_data:
        account_data.write("".join(account_data_list))
    if duration == "0":
        savelog(clientusername+" removed "+servicename+" from cart"+duration,client_addr)
    else:
        savelog(clientusername+" changed duration to subscribe to of "+servicename+" in cart to "+duration,client_addr)
    return "update successful"

def ssde(message,client_addr):#Show subscribed services and their expiry date
    message = message[1:]
    clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_data_path = account_path(clientusername)
    with open(account_data_path,"r") as account_data:
        account_data_lines = account_data.readlines()
    subscribedservices = account_data_lines[6][18:]
    return subscribedservices

def rfai(message,client_addr):#Retrieve full account information
    message = message[1:]
    clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_data_path = account_path(clientusername)
    with open(account_data_path,"r") as account_data:
        account_data_lines = account_data.readlines()
    fullname = account_data_lines[2][11:].strip()
    email = account_data_lines[3][7:].strip()
    address1 = account_data_lines[4][15:].strip()
    address2 = account_data_lines[5][15:].strip()
    membershiptier = account_data_lines[8][17:].strip()
    savelog(clientusername + " retrieved his account information",client_addr)
    return fullname + "," + email + "," + address1 + "," + address2 + "," + membershiptier

def cuap(message,client_addr,adminstate=False):#Change a user account's password
    if adminstate:
        newpasswd,accountusername,clientusername,passwd = message.split("^")
        if not(checkadminpassword(clientusername,passwd,client_addr)):
            return "Passwrong"
        account_data_path = account_path(accountusername)
    else:
        newpasswd,clientusername,passwd = message.split("^")
        if not(checkpass(clientusername,passwd,client_addr)):
            return "Passwrong"
        account_data_path = account_path(clientusername)
    with open(account_data_path,"r") as account_data:
        account_data_string = account_data.read()
    accountinfolines = account_data_string.split("\n")
    new_account_data_string = account_data_string.replace(accountinfolines[1].rstrip(),f"Password: {newpasswd}")        
    with open(account_data_path,"w") as account_data:
        account_data.write(new_account_data_string)
    if adminstate:
        savelog("(admin) "+simple_decryption(clientusername) + " changed the account's password successfully",client_addr)
    else:
        savelog(clientusername + " changed the account's password successfully",client_addr)
    return "Password successfully changed"

def capc(message,client_addr):#check account password correct
    client_input_passwd,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    if not(checkpass(clientusername,client_input_passwd,client_addr)):
        savelog(clientusername + " got his password wrong",client_addr)
        return "Password wrong"
    else:
        savelog(clientusername + " got his password right",client_addr)
        return "Password right"

def cafn(message,client_addr):#change account full name
    newfullname,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_data_path = account_path(clientusername)
    with open(account_data_path,"r") as account_data:
        account_data_string = account_data.read()
    accountinfolines = account_data_string.split("\n")
    new_account_data_string = account_data_string.replace(accountinfolines[2].rstrip(),f"Full name: {newfullname}")
    with open(account_data_path,"w") as account_data:
        account_data.write(new_account_data_string)
    savelog(clientusername + " changed the account's full name successfully",client_addr)
    return "Full name successfully changed"

def caem(message,client_addr):#Change account email
    newemail,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_data_path = account_path(clientusername)
    with open(account_data_path,"r") as account_data:
        account_data_string = account_data.read()
    accountinfolines = account_data_string.split("\n")
    new_account_data_string = account_data_string.replace(accountinfolines[3].rstrip(),f"Email: {newemail}")
    with open(account_data_path,"w") as account_data:
        account_data.write(new_account_data_string)
    savelog(clientusername + " changed the account's email successfully",client_addr)
    return "Email successfully changed"

def caad(message,client_addr):#Change account address
    newaddress1,newaddress2,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_data_path = account_path(clientusername)
    with open(account_data_path,"r") as account_data:
        account_data_string = account_data.read()
    accountinfolines = account_data_string.split("\n")
    new_account_data_string = account_data_string.replace(accountinfolines[4].rstrip(),f"Address line 1: {newaddress1}")
    new_account_data_string = new_account_data_string.replace(accountinfolines[5].rstrip(),f"Address line 2: {newaddress2}")
    with open(account_data_path,"w") as account_data:
        account_data.write(new_account_data_string)
    savelog(clientusername + " changed the account's address successfully",client_addr)
    return "Address successfully changed"

def capi(message,client_addr):#Check avilable past invoices
    message = message[1:]
    clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    with open(invoice_tracking_txt_path,"r") as account_data:
        invoice_tracking_string = account_data.read()
    if invoice_tracking_string == "":
        savelog(clientusername + " has no past invoice number to retrieve",client_addr)
        return "No invoices"
    invoice_tracking_list = invoice_tracking_string.split("\n")
    userinvoicenums = []
    for invoicenum_user in invoice_tracking_list:
        invoicenum,user = invoicenum_user.split(":")
        if user == clientusername:
            userinvoicenums += [invoicenum]
    if len(userinvoicenums)==0:
        savelog(clientusername + " has no past invoice number to retrieve",client_addr)
        return "No invoices"
    else:
        savelog(clientusername + " retrieved his past invoice numbers",client_addr)
        return ",".join(userinvoicenums)

def rapi(message,client_addr):#Retrieve avilable past invoices
    invoicenum,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    invoice_path = "C:/PSEC/server/data/Invoices/" + invoicenum + ".txt"
    try:
        with open(invoice_path,"r") as invoicefile:
            invoice_string = invoicefile.read()
        savelog(clientusername + " retrieved "+invoicenum,client_addr)
        return invoice_string
    except:
        savelog(clientusername + " was unable to retrieve "+invoicenum,client_addr)
        return "failed"

def checkadminpassword(username,passwd,client_addr):#Check if admin password is correct for admin account
    with open(adminaccounts_txt_path,"r") as admin_account_data:
        adminuserandpass = admin_account_data.read()
    adminuserandpasslist = adminuserandpass.split("\n")
    username_password_correct = False
    for adminuserandpass in adminuserandpasslist:
        adminuser, adminpass = adminuserandpass.split(":")
        if adminuser == username and adminpass==passwd:
            username_password_correct = True
            break
    if username_password_correct:
        savelog("Succesfully logged into a admin account",client_addr)
    else:
        savelog("Failed to log into a admin account",client_addr)
    return username_password_correct
    
            
def ciem(message,client_addr):#Change if ESP in maintenance mode or not
    try:
        newmode,adminusername,adminpasswd = message.split("^")
        if not(checkadminpassword(adminusername,adminpasswd,client_addr)):
            return "Passwrong"
        with open(maintenance_txt_path,"w") as maintenance_file:
            maintenance_file.write(newmode)
        if newmode == "1":
            savelog("(admin) "+simple_decryption(adminusername)+" put the ESP server in maintenance mode",client_addr)
        else:
            savelog("(admin) "+simple_decryption(adminusername)+" taken the ESP server out of maintenance mode",client_addr)
        return "success"
    except:
        return "failed"

def anss(message,client_addr):#add new service to services list:
    try:
        serviceandprice,adminusername,adminpasswd = message.split("^")
        if not(checkadminpassword(adminusername,adminpasswd,client_addr)):
            return "Passwrong"
        with open(services_txt_path,"r") as serviceslistfile:
            services_string = serviceslistfile.read()
        if services_string == "":
            with open(services_txt_path,"w") as serviceslistfile:
                serviceslistfile.write(serviceandprice)
        else:
            with open(services_txt_path,"a") as serviceslistfile:
                serviceslistfile.write("\n"+serviceandprice)
        savelog("(admin) "+simple_decryption(adminusername)+" added "+serviceandprice+" into services list",client_addr)
        return "success"
    except:
        return "failed"

def wnsl(message,client_addr):#Write new service list into file
    try:
        newservicedatastring,adminusername,adminpasswd = message.split("^")
        if not(checkadminpassword(adminusername,adminpasswd,client_addr)):
            return "Passwrong"
        with open(services_txt_path,"w") as servicesdata:
            servicesdata.write(newservicedatastring)
        savelog("(admin) "+simple_decryption(adminusername)+" changed services list",client_addr)
        return "success"
    except:
        return "failed"  

def ciae(message,client_addr):#Check if admin acccount exist
    adminaccount_check_name,adminusername,adminpasswd =message.split("^")
    if not(checkadminpassword(adminusername,adminpasswd,client_addr)):
        return "Passwrong"
    repeat = False
    with open(adminaccounts_txt_path,"r") as usernamesandpass:
        for line in usernamesandpass:
            existingusername = line.split(":")[0]
            existingusername = existingusername
            if existingusername == adminaccount_check_name:
                repeat = True
                print(f"The username {adminaccount_check_name} is already in use. Please try to input a different unique username")
                break
    if repeat:
        savelog("(admin) "+simple_decryption(adminusername)+"checked that admin account "+simple_decryption(adminaccount_check_name)+" exist",client_addr)
        return "not unique"
    else:
        savelog("(admin) "+simple_decryption(adminusername)+"checked that admin account "+simple_decryption(adminaccount_check_name)+" do not exist",client_addr)
        return "unique"

def anaa(message,client_addr):#Add a new admin account
    newadminaccountname,newadminaccountpassword,adminusername,adminpasswd =message.split("^")
    if not(checkadminpassword(adminusername,adminpasswd,client_addr)):
        return "Passwrong"
    repeat = False
    with open(adminaccounts_txt_path,"r") as usernamesandpass:
        for line in usernamesandpass:
            existingusername = line.split(":")[0]
            existingusername = existingusername
            if existingusername == newadminaccountname:
                repeat = True
                print(f"The username {newadminaccountname} is already in use. Please try to input a different unique username")
                break
    if repeat:
        return "Failed"
    else:
        with open(adminaccounts_txt_path,"a") as adminaccountfile:
            adminaccountfile.write("\n"+newadminaccountname+":"+newadminaccountpassword)
        savelog("(admin) "+simple_decryption(adminusername)+" added a new admin account, "+simple_decryption(newadminaccountname),client_addr)
        return "success"

def tuss(message,client_addr):#Terminate users subscribed service
    service_to_terminate,clientusername,passwd = message.split("^")
    if not(checkpass(clientusername,passwd,client_addr)):
        return "Passwrong"
    account_file_path = account_path(clientusername)
    with open(account_file_path,"r") as account_data:
        account_data_string = account_data.read()
    account_data_lines = account_data_string.split("\n")
    subscribedservices = account_data_lines[6][19:]
    subscribedserviceslist = subscribedservices.split(",")
    try:
        subscribedserviceslist.remove(service_to_terminate)
        newsubscribedserviceslist = ",".join(subscribedserviceslist)
        newaccount_data_string = account_data_string.replace("Existing services: "+subscribedservices,"Existing services: "+newsubscribedserviceslist)
        with open(account_file_path,"w") as account_data:
            account_data.write(newaccount_data_string)
        savelog(clientusername+" succesfully removed "+service_to_terminate+" from existing services",client_addr) 
        return "success"
    except ValueError:
        savelog(clientusername+" could not remove "+service_to_terminate+" from existing services as it may not be there",client_addr) 
        return "failure"
    

def handler(con,client_addr):#handler for connection
    savelog("Started a new connection with server",client_addr)
    con.settimeout(5.0)#Timeout if idle for 5 seconds
    idle_count = 0
    with open(maintenance_txt_path,"r") as maintenance_file:
        maintenancemode = maintenance_file.read()
    while True:
        try:
            fullmessage = ""
            while True:#Receiving full message from client
                buf = con.recv(1024).decode()
                fullmessage += buf
                if buf[-1] == ";":
                    break
            fullmessage = fullmessage[0:-1]
            fullmessage = simple_decryption(fullmessage)
            savelog("(Received)"+fullmessage,client_addr,"raw")#Log full message that client send to server
            if fullmessage[0]=="~":
                fullmessage = fullmessage[1:]
                command = fullmessage[0:4]
                message = fullmessage[4:]
                if command == "caup":#Check admin user and password
                    message = message[1:]
                    inputusername, inputpassword = message.split("^")
                    if checkadminpassword(inputusername,inputpassword,client_addr):
                        reply = "Correct"
                    else:
                        reply = "Wrong"
                elif command == "ciem":#Change if ESP in maintenance mode or not
                    reply = ciem(message,client_addr)
                elif command == "rsfl":#Retrieve full service list
                    reply = rsfl(client_addr)
                elif command == "anss":#add new service to services list:
                    reply = anss(message,client_addr)
                elif command == "wnsl":#Write new service list into file
                    reply = wnsl(message,client_addr)
                elif command == "ciue":#check if user account already exist:
                    reply = ciue(message,client_addr)
                elif command == "cuap":#Change a user account's password
                    reply = cuap(message,client_addr,True)
                elif command == "ciae":#Check if admin acccount exist
                    reply = ciae(message,client_addr)
                elif command == "anaa":#Add a new admin account
                    reply = anaa(message,client_addr)
                elif command == "sdes":#Shut dopwn esp server
                    global stopFlag
                    stopFlag = True
                    reply = "Succesfully shut down ESP server"
                    savelog("shut down ESP server",client_addr)
                savelog("(Reply)"+reply,client_addr,"raw")
                reply = simple_encryption(reply) + ";"
                con.sendall(reply.encode())#Send reply to client
                break
            elif maintenancemode != "1":#Checked that server is in maintenance mode
                savelog("Checked that server is in maintenance mode",client_addr)
                reply = simple_encryption("~") + ";"
                savelog("(Reply)"+reply,client_addr,"raw")
                con.sendall(reply.encode())
                break
            elif 0 < len(fullmessage) <= 4:
                idle_count = 0
                if fullmessage == "ciim":#Checked that server is not in maintenance mode
                    savelog("Checked that server is not in maintenance mode",client_addr)
                    reply = "Not in maintenance mode"
                elif fullmessage == "rsfl":#Retrieve full service list
                    reply = rsfl(client_addr)
                savelog("(Reply)"+reply,client_addr,"raw")
                reply = simple_encryption(reply) + ";"
                con.sendall(reply.encode())#Send reply to client
                break
            elif len(fullmessage) > 4:
                command = fullmessage[0:4]
                message = fullmessage[4:]
                if command == "rssl":#Search searvice list
                    reply = rssl(message,client_addr)
                elif command == "logi":#Login to a account
                    reply = logi(message,client_addr)
                elif command == "ciue":#check if user account already exist
                    reply = ciue(message,client_addr)
                elif command == "mnaf":#Make new account file
                    reply = mnaf(message,client_addr)
                elif command == "astc":#Add service to cart
                    reply = astc(message,client_addr)
                elif command == "sdpc":#Expected services, duration of subscription and price infomration part of invoice for services in cart
                    reply = sdpc(message,client_addr)
                elif command == "esic":#Change duration to subscribe for a service in cart
                    reply = esic(message,client_addr)
                elif command == "ssde":#Show subscribed services and their expiry date
                    reply = ssde(message,client_addr)
                elif command == "rfai":#Retrieve full account information:
                    reply = rfai(message,client_addr)
                elif command == "cuap":#Change user account's password
                    reply = cuap(message,client_addr)
                elif command == "capc":#check account password correct
                    reply = capc(message,client_addr)
                elif command == "cafn":#change account full name
                    reply = cafn(message,client_addr)
                elif command == "caem":#Change account email
                    reply = caem(message,client_addr)
                elif command == "caad":#Change account address
                    reply = caad(message,client_addr)
                elif command == "capi":#Check avilable past invoices
                    reply = capi(message,client_addr)
                elif command == "rapi":#Retrieve avilable past invoices
                    reply = rapi(message,client_addr)
                elif command == "tuss":#Terminate users subscribed service
                    reply = tuss(message,client_addr)
                savelog("(Reply)"+reply,client_addr,"raw")#Log reply message that server send to client
                reply = simple_encryption(reply) + ";"
                con.sendall(reply.encode())#Send reply to client
                break
            else:
                return
        except Exception as inst:
            if str(inst) == "timed out":#Timeout counter
                idle_count = idle_count + 1
                print("handler {} time out: idle count is {}".format(str(client_addr),idle_count))
            if idle_count > 4 or (str(inst) != "timed out"):#Check for time out
                break
    con.close()
    savelog("handler terminated",client_addr)
    return


while True:
    if stopFlag:#Check if to shutdown ESP server
        time.sleep(6)#Let the last thread finish running or time out by itself
        break
    try:
        connection, address= serversocket.accept()#Accept connection for client
        #setup and start a new thread to run an instance of handler()
        t = threading.Thread(target=handler, args=(connection,address))
        t.start()
    except Exception:
        break

serversocket.close()#Close server socket
print("Server is halted.")
sys.exit(0)