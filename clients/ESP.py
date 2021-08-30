#p2025845
#Chian ZhengHang
#DISM 1B/01
import sys#Library to exit code anytime
import re #Library for regular expression
import socket#Library for socket
from getpass import getpass #Library for password input without being displayed to user
from datetime import datetime #for dates and times
import os

loggedin = False
accountinfo = {}

#Pathing
dirname = os.path.dirname(__file__)
invoice_file_path = os.path.join(dirname, "invoice/")

host = "localhost"
def send_to_server1(msgtosend):#Sending data to server and receive corresponding reply data
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((host, 8089))
        clientsocket.send((simple_encryption(msgtosend)+";").encode())
        fullmessage = ""
        while True:
            buf = clientsocket.recv(1024).decode()
            fullmessage += buf
            if buf[-1] == ";":
                break
        clientsocket.close()
    except:
        print("Could not connect to server, server may be down for maintenance")
        print("Exiting ESP now")
        sys.exit(0)
    fullmessage = fullmessage[0:-1]
    fullmessage = simple_decryption(fullmessage)
    if fullmessage == "~":
        print("Server is under maintenance right now, please come back later.")
        print("Exiting ESP now")
        sys.exit(0)
    return fullmessage

def send_to_server2(msgtosend):#Sending data including username and password to server and receive corresponding reply data
    global accountinfo
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((host, 8089))
        clientsocket.send((simple_encryption(msgtosend+"^"+accountinfo["Username"]+"^"+accountinfo["Password"])+";").encode())
        fullmessage = ""
        while True:
            buf = clientsocket.recv(1024).decode()
            fullmessage += buf
            if buf[-1] == ";":
                break
        clientsocket.close()
    except:
        print("Could not connect to server, server may be down for maintenance")
        print("Exiting ESP now")
        sys.exit(0)
    fullmessage = fullmessage[0:-1]
    fullmessage = simple_decryption(fullmessage)
    if fullmessage == "~":
        print("Server is in maintenance mode right now.")
        print("Exiting ESP now")
        sys.exit(0)
    if fullmessage == "Passwrong":
        print("Password may have been changed, please log in again.")
        print("Logging out.")       
        accountinfo = {}
        global loggedin
        loggedin = False
        print("Logged out.")
        loginorcreate()
        sys.exit(0)
    clientsocket.close()
    return fullmessage


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

def is_int(checkint):#check if argument is a integer or not
    try:
        int(checkint)
        return True
    except ValueError:
        return False


def printsort(servicesdic):#print the sorted services and their corresponding prices and then continue choosing services to add into cart
    i = 0
    for service in list(servicesdic):
        i += 1
        printservice(i,service,servicesdic[service])
    choosingservices(i,servicesdic)

def printservice(index,name,price): #Print out the index, name and price of a service
    price = "$" + price + "/year"
    print('{:<5}{:<40}{:>5}'.format(index,name,price))

def split_servicename_price(serviceandprice):
    name, price = serviceandprice.split(":")
    name = name.replace("|","")
    name, price = name.strip(), price.strip()
    return name,price

def split_service_exdate_date(service_exdate_date):#Split the argument(a string containing service, duration and date) into service, duration, date and return them
    service,exdate_date = service_exdate_date.split("[")
    service = service.replace("|","")
    exdate,date = exdate_date.split("]")
    date = date.replace("<","")
    date = date.replace(">","")
    date = date.replace("|","")
    return service,exdate,date


def mainmenu():#main menu to choose what to do
    global loggedin
    #print("Do not put * or [ or ^ in any inputs!")
    if loggedin:
        print("\n\n\t1. Display Our List of Services\n\t2. Search for service\n\t3. Display and edit services added to cart and payment\n\t4. Subscribed services\n\t5. View past invoices\n\t6. Log out of account\n\t7. Display and editing account information\n\t8. Exit ESP\n\n")
        inputprompt = "Please choose your choice of action, please input a integer number between 1 and 8: "
        invalid_mainmenu_input_msg = "Invalid input! Please input a whole number between 1 to 8"
    else:
        print("\n\n\t1. Display Our List of Services\n\t2. Search for service\n\t3. Log in to or create a account\n\t4. Exit ESP\n\n")
        inputprompt = "Please choose your choice of action, please input a integer number between 1 and 4: "
        invalid_mainmenu_input_msg = "Invalid input! Please input a whole number between 1 to 4"
    while True:
        choice = input(inputprompt).strip()
        if choice == "1": 
            listservices()
            break
        elif choice == "2":
            searchservice()
            break
        elif choice == "3" and loggedin:
            cart_and_payment()
            break
        elif choice == "4" and loggedin:
            show_subscribedservices()
            break
        elif choice == "3" and not(loggedin):
            loginorcreate()
            break
        elif choice == "5" and loggedin:
            pastinvoice()
            break
        elif choice == "6" and loggedin: 
            print("Logging out.")       
            global accountinfo
            accountinfo = {}
            loggedin = False
            print("Logged out.")
            mainmenu()
            break
        elif (choice == "4" and not(loggedin)) or (choice == "8" and loggedin):
            print("Thank you for using ESP")
            sys.exit(0)
            break
        elif choice == "7" and loggedin:
            changeaccoountinfo()
            break
        else:
            print(invalid_mainmenu_input_msg)



def listservices(): #list(print) all services avilable and its price, make a dictionary with services as its key and price as its value and pass
    servicesdic = {}
    services = send_to_server1("rsfl")
    if services == "":
        print("\nNo service avilable")
        print("Going back to main menu")
        mainmenu()
    else:
        serviceslist = services.split("\n")
        print('\n{:<5}{:<40}{:>5}'.format("No.","Service:","Price of service:"))
        i = 0
        for line in serviceslist:
            i += 1
            name,price = split_servicename_price(line)
            printservice(i,name,price)
            servicesdic[name] = price
        choosingservices(i,servicesdic)


def choosingservices(i,servicesdic):#Choose the services to add into cart from the services dictionary containing service(key) and price(value) passed in
    global loggedin
    if loggedin:
        while True:
            serviceselection = input(f"\nEnter the service No. 1-{i} you would like to add 1 year of into cart, 0 to go back to main menu, a to go into advanced menu, p to display and edit cart or payment: ").strip()
            if is_int(serviceselection):
                serviceselection = int(serviceselection)
                if 1 <= serviceselection <= int(i):
                    serviceselection = int(serviceselection) - 1
                    addservice = list(servicesdic)[serviceselection]
                    server_reply = send_to_server2("astc"+addservice)
                    if server_reply == "service added to cart":
                        print(f"{addservice} added to cart")
                    else:
                        print(f"{addservice} was not able to be added to cart")
                elif serviceselection == 0:
                    mainmenu()
                    break
                else:
                    print("Invalid input. Please enter a valid input.")
            elif serviceselection == "a":
                choosingservicesadvancedmenu(i,servicesdic)
                break
            elif serviceselection == "p":
                cart_and_payment()
                break
            else:
                print("Invalid input. Please enter a valid input.")
    else:
        print("\nPlease log into an account to be able to acquire our services. ")
        while True:
            loginormain = input("Enter 1 to go to log in or creating account menu and 0 to go back to main menu: ").strip()
            if loginormain == "0":
                mainmenu()
                break
            elif loginormain == "1":
                loginorcreate()
                break
            else:
                print("Input invalid. Please enter either 0 or 1")



def searchservice(): #search and list(print) out services avilable and its price, make a dictionary with services as its key and price as its value and pass
    servicesdic = {}
    usersearchinput = input("\nPlease input service to search(GST included in service's price): ").lower()
    while True:
        if usersearchinput == "":
            print("Search is blank")
        else:
            break
        usersearchinput = input("\nPlease input service to search(GST included in service's price): ").lower()
    print('\n{:<5}{:<40}{:>5}'.format("No.","Service:","Price of service:"))
    serviceslist = send_to_server1("rssl"+usersearchinput)
    i = 0
    if serviceslist != "":
        serviceslist = serviceslist.split("\n")
        for line in serviceslist:
            i += 1
            name, price = split_servicename_price(line)
            servicesdic[name] = price
            printservice(i,name,price)
        choosingservices(i,servicesdic)
    else:
        print("No result")
        while True:
            continue_searching = input("Do you still want to continue searching? Y for yes and N for no: ").strip().lower()
            if continue_searching == "y":
                searchservice()
                break
            elif continue_searching == "n":
                mainmenu()
                break
            else:
                print("Input invalid. Please try again.")


def choosingservicesadvancedmenu(i,servicesdic):#Advance menu so as to be able to choose to go to search for service or sort service
    print("\n\t1. Search for service\n\t2. Sort the services\n\t3. Go back to choosing services menu\n\t4. Go back to main menu\n")
    advance_menu_input = input("Please choose your choice of action, please input a integer number between 1 and 4: ").strip()
    while True:
        if advance_menu_input == "1":
            searchservice()
            break
        elif advance_menu_input == "2":
            sortingservices(i,servicesdic)
            break
        elif advance_menu_input == "3":
            choosingservices(i,servicesdic)
            break
        elif advance_menu_input == "4":
            mainmenu()
            break
        else:
            print("Invalid input")



def sortingservices(i,servicesdic):#Sorting the services dictionary and passing it into printsort()
    print("\nWays to sort:\n\t1. Alphabetical order (ascending)\n\t2. Alphabetical order (descending)\n\t3. Price (ascending)\n\t4. Price (descending)\n")
    while True:
        choose_sorting = input("How would you like to sort, please input a integer number between 1 and 4: ").strip()
        if choose_sorting == "1":
            servicesdic = dict(sorted(servicesdic.items()))#Sort the dictionary using keys(services) by alphabetical order in ascending order
            printsort(servicesdic)
            break
        elif choose_sorting == "2":
            servicesdic = dict(sorted(servicesdic.items(),reverse=True))#Sort the dictionary using keys(services) by alphabetical order in descending order
            printsort(servicesdic)
            break
        elif choose_sorting == "3":
           servicesdic = dict(sorted(servicesdic.items(), key=lambda x: x[1]))#Sort the dictionary using values(price) by numerical order in ascending order
           printsort(servicesdic)
           break 
        elif choose_sorting == "4":
           servicesdic = dict(sorted(servicesdic.items(), key=lambda x: x[1],reverse=True))#Sort the dictionary using values(price) by numerical order in descending order
           printsort(servicesdic)
           break
        else:
            print("Invalid input. Please try again.")



def editcart(cartservicelist):#Edit the services added into cart, change the years of subscription or remove from cart.
    cartlist_length = len(cartservicelist)
    while True:
        service_to_edit = input(f"Enter the service No. 1-{cartlist_length} you would like to edit, p for payment, 0 go back to mainmenu: ").lower().strip()
        if is_int(service_to_edit):
            service_to_edit = int(service_to_edit)
            if 1 <= service_to_edit <= cartlist_length:
                service_edit = cartservicelist[service_to_edit-1]
                while True:
                    years_to_change_to = input(f"How many years do you want to change the {cartlist_length} in cart to(positive integer only), 0 to remove from cart: ").strip()
                    if is_int(years_to_change_to):
                        years_to_change_to = int(years_to_change_to)
                        if years_to_change_to >= 0:
                            reply_server = send_to_server2("esic"+service_edit+"["+str(years_to_change_to)+"]")
                            if reply_server == "update successful":
                                cart_and_payment("edit")
                            else:
                                print("Cart was unable to be updated")
                                print("Going back to main menu")
                                mainmenu()
                            break 
                    print("Invalid input. Please input a positive integer or 0.")
                break
            elif service_to_edit == 0:
                mainmenu()
                break
            else:
                print("Invalid input")
        elif service_to_edit == "p":
            cart_and_payment()
            break
        else:
            print("Invalid input. Please enter a valid input.")



def cart_and_payment(state=""):#Show cart, ask for confirmation for payment
    if loggedin:
        print("Cart: ")
        server_reply = send_to_server2("sdpcno")
        if server_reply == "No service":
            print("No services in cart.")
            print("\nGoing back to main menu.")
            mainmenu()
            sys.exit(0)
        cartinvoicestring,cartservicelist = server_reply.split("^")
        cartservicelist = cartservicelist.split(",")
        print(cartinvoicestring)
        while True:
            if state == "edit":
                editcart(cartservicelist)
                break
            else:
                editorpay = input("Input e to edit your cart, p to proceed to payment, 0 to go back to mainmenu: ").lower().strip()
            if editorpay == "e":
                editcart(cartservicelist)
                break
            elif editorpay == "p":
                print("Please check the services in cart again.")
                print(cartinvoicestring)
                while True:
                    proceedtopay = input("Input the word 'c' to confirm payment, e to go back to edit your cart, 0 to go back to mainmenu: ").lower().strip()
                    if proceedtopay == "c":
                        print("Payment processing...")
                        afterpayment()
                        break
                    elif proceedtopay == "e":
                        cart_and_payment()
                        break
                    elif proceedtopay == "0":
                        mainmenu()
                        break
                    else:
                        print("Invalid input. Please input either 'confirm', e or 0")
                break
            elif editorpay == "0":
                mainmenu()
                break
            else:
                print("Input invalid. Please input either e or p.")
    else:
        print("\nPlease log into an account to be able to display,edit cart and pay.")
        while True:
            loginormain = input("Enter 1 to go to log in or creating account menu and 0 to go back to main menu: ").strip()
            if loginormain == "0":
                mainmenu()
                break
            elif loginormain == "1":
                loginorcreate()
                break
            else:
                print("Input invalid. Please enter either 0 or 1")



def afterpayment():#Finish payment, generate invoice and move services in cart into existing(subscribed) services, update total amount of money spent and membership tier of user account
    server_reply = send_to_server2("sdpcyes")
    message,fullinvoice,invoicenum = server_reply.split("^")
    if message == "emailsuccess":
        print("Payment succesful")
        print("Invoice generated")
        print("\nInvoice:")
        print(fullinvoice)
        invoicenum_path = invoice_file_path+"invoice#"+invoicenum+".txt"
        print("Invoice was sent to your email")
        saveinvoice(invoicenum_path,fullinvoice)
    elif message == "success":
        print("Payment succesful")
        print("Invoice generated")
        print("\nInvoice:")
        print(fullinvoice)
        invoicenum_path = invoice_file_path+"invoice#"+invoicenum+".txt"
        print("Invoice was unable to be sent to your email")
        saveinvoice(invoicenum_path,fullinvoice)
    else:
        print("Payment failed")
    mainmenu() 


def show_subscribedservices():#Show user account's subscribed services
    if loggedin:
        subscribedservices = send_to_server2("ssde")
        if subscribedservices == " \n":
            print("\nYou are not subscribed to any services right now.")
            print("Redirecting you back to main menu.")
            mainmenu()
        else:
            subscribedservices = subscribedservices.strip()
            subscribedserviceslist = subscribedservices.split(",")
            print("{:<40} {:<30} {}".format("\nSubscribed service(s):","Subscription expiration date:","Subscription start date:"))
            for service_exdate_date in subscribedserviceslist:
                service,exdate,datebought = split_service_exdate_date(service_exdate_date)
                print("{:<40} {:<30} {}".format(service,exdate,datebought))
            while True:
                choice = input("Input m to go back to main menu or t to request early termination of a service: ")
                if choice == "m":
                    mainmenu()
                    break
                elif choice == "t":
                    print("\n{:<5}{:<40} {:<30} {}".format("No.","Subscribed service(s):","Subscription expiration date:","Subscription start date:"))
                    i = 0
                    for service_exdate_date in subscribedserviceslist:
                        i += 1
                        service,exdate,datebought = split_service_exdate_date(service_exdate_date)
                        print("{:<5}{:<40} {:<30} {}".format(i,service,exdate,datebought))
                    while True:
                        service_to_terminate = input(f"Enter the subscribed service No. 1-{i} you would like terminate early 0 go back to mainmenu: ").strip()
                        if is_int(service_to_terminate):
                            service_to_terminate = int(service_to_terminate)
                            if 1 <= service_to_terminate <= i:
                                service_terminating = subscribedserviceslist[service_to_terminate-1]
                                service,exdate,datebought = split_service_exdate_date(service_terminating)
                                confirmation = input(f"Are you really sure you want to terminate {service} early, input c to confirm and anything else to deny: ")
                                if confirmation == "c":
                                    server_reply = send_to_server2("tuss"+service_terminating)
                                    if server_reply == "success":
                                        print(f"{service} succesfully terminated")
                                    else:
                                        print(f"{service} was not able to be terminated")
                                    show_subscribedservices()
                                    sys.exit(0)
                            elif service_to_terminate == 0:
                                mainmenu()
                                break
                            else:
                                print("Invalid input. Please enter a valid input.")
                        else:
                            print("Invalid input. Please enter a valid input.")
                    break
                else:
                    print("Input invalid. Please enter either m or t")
    else:
        print("\nPlease log into an account to be able to view your subscribed services. ")
        while True:
            loginormain = input("Enter 1 to go to log in or creating account menu and 0 to go back to main menu: ").strip()
            if loginormain == "0":
                mainmenu()
                break
            elif loginormain == "1":
                loginorcreate()
                break
            else:
                print("Input invalid. Please enter either 0 or 1")



def loginorcreate():#Choose to log in, create new account or go back too main menu
    print("\n\t1. Log in\n\t2. Create new account\n\t3. Go back to main menu")
    while True:
        logorcreate = input("\nPlease choose your choice of action, please enter a integer number between 1 and 3: ").strip()
        if logorcreate == "1":
            login()
            break
        elif logorcreate == "2":
            createaccount()
            break
        elif logorcreate == "3":
            mainmenu()
            break
        else:
            print("Please enter either 1, 2 or 3")

def fullnamecreate(inputstring):#ask for fullname input, validate for fullname and return it
    while True:
        fullname = input(f"\n{inputstring} name: ").strip()
        if not(fullname.isspace()) and fullname != "":
            break
        else:
            print("Input is blank. Please enter a valid name.")
    fullname = simple_encryption(fullname)
    return fullname

def emailcreate(inputstring):#ask for email input, validate for email and return it
    emailregex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$"
    email = input(f"{inputstring}mail: ").strip()
    while not(re.search(emailregex,email)):
        print("Invalid email")
        email = input(f"{inputstring}mail: ")
    email = simple_encryption(email)
    return email

def addresscreate(inputstring):#ask for address line 1 and address line 2 input, validate both and return both
    while True:
        address1 = input(f"{inputstring}ddress line 1(do not add ':'): ").strip()
        if ":" in address1:
            print("Please do not have : in address. Please input a valid address.")
        else:
            break
    address1 = simple_encryption(address1)
    while True:
        address2 = input(f"{inputstring}ddress line 2: ").strip()
        if ":" in address1:
            print("Please do not have : in address. Please input a valid address.")
        else:
            break
    address2 = simple_encryption(address2)
    return address1,address2

def passwordcreate():#Ask for new password, confirm new password, validate both, check if they are the same and return the new password
    while True:
        while True:
            newpassword = input("New password(do not add space): ")
            if " " in newpassword or "\t"  in newpassword:
                print("Password invalid. Password contains space")            
            else:
                break
        confpassword = input("Confirm new password: ")
        if newpassword == confpassword:
            print("Passwords matches.")
            break
        else:
            print("Passwords did not match, please try again.")
    newpassword = simple_encryption(newpassword)
    return newpassword

def createaccount():#Create user account
    fullname = fullnamecreate("Full")
    email = emailcreate("E")
    address1,address2 = addresscreate("A")
    while True:
        repeat = False
        while True:
            username = input("Username (Used to login. Only alphanumeric characters are allowed in the username. Do not add space(s) or tab in the username. Uppercase,lowercase does not matter): ")
            if username.isalnum():
                username = username.lower()
                break
            else:
                print("Username invalid. Please input a valid username.")
        server_reply = send_to_server1("ciue"+username)
        if server_reply != "exist":
            print("Username is unique and valid")
            break
        else:
            print(f"The username {username} is already in use. Please try to input a different unique username.")
    password = passwordcreate()
    print("Creating account now.")
    send_to_server1("mnaf"+username+"^"+password+"^"+fullname+"^"+email+"^"+address1+"^"+address2)
    print("\nAccount succesfully created. ")
    print("You can login to your new account now.")
    loginorcreate()

def login():#Login to a account
    found = False
    while True:
        username = input("\nUsername(.main to go back to main menu): ")
        if username.isalnum():
            username = username.lower()    
            user_inputted_password = getpass(prompt="Password: ")
            server_reply = send_to_server1("logi"+username+"^"+simple_encryption(user_inputted_password))
            if server_reply != "failed":
                break
            else:
                print("Username or password is incorrect.")
        elif username == ".main":
            mainmenu()
            sys.exit(0)
        else:
            print("Username not valid")
    print("Password correct. Logging in")
    global loggedin
    global accountinfo
    loggedin = True
    print(server_reply)
    accountinfo = {}
    accountinfo["Username"] = username
    accountinfo["Password"] = simple_encryption(user_inputted_password)
    mainmenu()

def changeaccoountinfo():#Choose to change the user's account information like Fullname, email and address or password.
    server_reply = send_to_server2("rfai")
    fullname,email,address1,address2,membershiptier = server_reply.split(",")
    #Print account information
    print("\nAccount information:")
    print("Fullname: {}".format(simple_decryption(fullname)))
    print("Email: {}".format(simple_decryption(email)))
    print("Address line 1: {}".format(simple_decryption(address1)))
    print("Address line 2: {}".format(simple_decryption(address2)))
    print("Membership tier: {}".format(membershiptier))
    input("\nPress enter to continue")
    print("\n\t1. Change this account's password\n\t2. Change this account user's full name\n\t3. Change this account's email info\n\t4. Change this account's address info\n\t5. Go back to main menu\n")
    while True:
        changingchoice = input("Please choose your choice of action, please input a integer number between 1 and 5: ").strip()
        if changingchoice == "1":
            while True:
                old_password = getpass(prompt="Password: ")
                server_reply = send_to_server2("capc"+simple_encryption(old_password))
                if server_reply == "Password right":
                    new_password = passwordcreate()
                    print("Changing password now.")
                    print(send_to_server2("cuap"+new_password))     
                    global accountinfo
                    accountinfo = {}
                    loggedin = False
                    print("Password has been changed, please log in again")
                    loginorcreate()
                    sys.exit(0)
                    break
                else:
                    print("Password incorrect. Please try again.")
            break
        elif changingchoice == "2":
            newfullname = fullnamecreate("New full")
            server_reply = send_to_server2("cafn"+newfullname)
            print(server_reply)
            changeaccoountinfo()
            break
        elif changingchoice == "3":
            newemail = emailcreate("New e")
            server_reply = send_to_server2("caem"+newemail)
            changeaccoountinfo()
            break
        elif changingchoice == "4":
            newaddress1,newaddress2 = addresscreate("New a")
            server_reply = send_to_server2("caad"+newaddress1+"^"+newaddress2)
            changeaccoountinfo()
            break
        elif changingchoice == "5":
            mainmenu()
            break
        else:
            print("Invalid input. Please input a integer number between 1 and 5.")

def saveinvoice(invoicepath,fullinvoice):#Choose to save invoice or not
    while True:
        download = input("\nDo you want to download this invoice(y for yes, n for no): ").lower().strip()
        if download == "y":
            try:
                with open(invoicepath,"w") as invoicesave:
                    invoicesave.write(fullinvoice)
                print(invoicepath +  " downloaded")
                break
            except:
                print("Invoice was unable to be downloaded")
                break
        elif download == "n":
            print("Invoice not downloaded")
            break
        else:
            print("Invalid input. Please enter a valid input.")

def pastinvoice():#View past invoices
    server_reply = send_to_server2("capi")
    if server_reply == "No invoices":
        print("\nNo past invoices available")
    else:
        print("\n{:<5} {}".format("No.","Invoice no."))
        invoicenums = server_reply.split(",")
        i = 0
        for invoicenum in invoicenums:
            i += 1
            print("{:<5} {}".format(i,invoicenum))
        while True:
            invoice_to_view = input(f"\nEnter the invoice No. 1-{i} you would like to view, 0 go back to mainmenu: ").strip()
            if is_int(invoice_to_view):
                invoice_to_view = int(invoice_to_view)
                if 0 < invoice_to_view <= i:
                    server_reply = send_to_server2("rapi"+invoicenums[i-1])
                    if server_reply == "failed":
                        print("Invoice was unable to be retrieved")
                    else:
                        printinvoice = "\n" + server_reply
                        print(printinvoice)
                        invoicenumpath = invoice_file_path+invoicenums[i-1]+".txt"
                        saveinvoice(invoicenumpath,server_reply)
                    pastinvoice()
                    break
                elif invoice_to_view == 0:
                    mainmenu()
                    break
                else:
                    print("Invalid input. Please enter a valid input.")
            else:
                print("Invalid input. Please enter a valid input.")

if send_to_server1("ciim") == "Not in maintenance mode":#Check if server is in maintenance mode
    startingline = "=" * 45#Start ESP
    print(startingline)
    print("Welcome to Electronic Services & Protection:")
    print(startingline)
    mainmenu()
else:
    print("Server is under maintenance right now, please come back later.")
    print("Exiting ESP now")


    
