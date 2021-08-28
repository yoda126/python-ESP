#p2025845
#Chian ZhengHang
#DISM 1B/01

import sys#Library to exit code anytime
import getpass #Library for password input without being displayed to user
import socket#Library for socket

#admin username:admin
#admin password:admin
host = "localhost"
admininfo = {}
maintenancemodenow = ""
def send_to_server(msgtosend):#Sending data to server and receive corresponding reply data
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
    return fullmessage

def admin_send_to_server(msgtosend):#Sending data including admin username and password to server and receive corresponding reply data
    try:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((host, 8089))
        clientsocket.send((simple_encryption("~"+msgtosend+"^"+admininfo["Username"]+"^"+admininfo["Password"]) +";").encode())
        fullmessage = ""
        while True:
            buf = clientsocket.recv(1024).decode()
            fullmessage += buf
            if buf[-1] == ";":
                break
        clientsocket.close()
    except:
        print("Could not connect to server, server may be down.")
        print("Exiting Admin ESP now")
        sys.exit(0)
    if fullmessage == "Passwrong":
        print("Password may have been changed, please log in again.")       
        print("Exiting admin ESP programme")
        sys.exit(0)
    fullmessage = fullmessage[0:-1]
    fullmessage = simple_decryption(fullmessage)
    return fullmessage

def checkmaintenancestat():#Check if ESP is in maintenancemode
    server_reply = send_to_server("ciim")
    if server_reply == "~":
        return True
    elif server_reply == "Not in maintenance mode":
        return False
    else:
        print("Server may be down.")
        print("Exiting Admin ESP now")
        sys.exit(0)

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


def printsort(servicesdic,servicesdatastring): #print the sorted services and their corresponding prices and then continue editing service
    print('{:<5}{:<40}{:>5}'.format("No.","Service:","Price of service(GST included):"))
    i = 0
    for service in list(servicesdic):
        i += 1
        printservice(i,service,servicesdic[service])
    editservice(i,servicesdic,servicesdatastring)


def is_float(checkfloat):#check if argument is a float or not
    try:
        float(checkfloat)
        return True
    except ValueError:
        return False


def printservice(index,name,price):#Print out the index, name and price of a service
    price = "$" + price + "/year"
    print('{:<5}{:<40}{:>5}'.format(index,name,price))

def adminlogin():#Login into a admin account to access admin features
    startingline = "=" * 60
    print(startingline)
    print("Welcome to Electronic Services & Protection Admin System:")
    print(startingline)
    print("Please login to your admin account\n")
    global admininfo
    while True:
        admininfo["Username"] = simple_encryption(input("Username: ").lower())
        admininfo["Password"] = simple_encryption(getpass.getpass(prompt="Password: "))
        server_reply = admin_send_to_server("caup")
        if server_reply == "Correct":
            print("Logging in.\nLogged in.")
            adminmainmenu()
            break
        else:
            print("Username and password incorrect please try again.")


def adminmainmenu():#main menu of ESP admin system
    global maintenancemodenow
    if checkmaintenancestat():
        maintenancemodenow = True
        print("\n\t1. Take ESP out of maintenance mode\n\t2. Edit services list\n\t3. Change a user's password\n\t4. Add a admin account\n\t5. Shut down ESP server\n\t6. Exit admin ESP")
    else:
        maintenancemodenow = False
        print("\n\t1. Put ESP into maintenance mode\n\t2. Edit services list\n\t3. Change a user's password\n\t4. Add a admin account\n\t5. Shut down ESP server\n\t6. Exit admin ESP")
    while True:
        choice = input("\nPlease choose your choice of action, please input a integer number from 1 to 5: ").strip()
        if choice == "1":
            maintenancemode()
            break
        elif choice == "2":
            editserviceschoices()
            break
        elif choice == "3":
            changeuserpass()
            break
        elif choice == "4":
            addadminaccount()
            break
        elif choice == "5":
            print("\nShutting down ESP server")
            server_reply = admin_send_to_server("sdes")
            admin_send_to_server("sdes")
            print(server_reply)
            break
        elif choice == "6":
            print("\nExiting ESP admin system")
            sys.exit(0)
            break
        else:
            print("Invalid input. Please input a integer number between 1 to 5.")
    
    
def maintenancemode():#Put ESP into maintenance mode or take it out of maintenance mode
    global maintenancemodenow
    if maintenancemodenow:
        newmode = "1"
    else:
        newmode = "0"
    server_reply = admin_send_to_server("ciem"+newmode)
    if server_reply == "success":
        if newmode == "1":
            print("ESP server succesfully taken out of maintenance mode")
        else:
            print("ESP server succesfully put into maintenance mode")
    else:
        print("Maintenance mode change unsuccesful")

    adminmainmenu()

def editserviceschoices():#Choose how to edit the services in services list(txt file)
    servicesdatastring = admin_send_to_server("rsfl")
    print("\n\t1. Add service to service list\n\t2. List services and choose to edit\n\t3. Search for service to edit\n\t4. Go back to admin main menu\n")
    servicechoice = input("Please choose your choice of action, please input a integer number between 1 to 4: ")
    if servicechoice == "1":
        addservice(servicesdatastring)
    elif servicechoice == "2":
        listservice_edit(servicesdatastring)
    elif servicechoice == "3":
        searchservice_edit(servicesdatastring)
    elif servicechoice == "4":
        adminmainmenu()
    else:
        print("Invalid input. Please input a integer number between 1 to 4")
        editserviceschoices()

def addservice(servicesdatastring):#add service and its respective price into the services list(txt file)
    havecannot = False
    cannothavelist = [',','[',']',':','<','>','/',"^","~"]
    servicesdatalist = servicesdatastring.split("\n")
    while True:
        print("Do not have ',', '[', ']', ':', '<', '>', '^', '~' or '/' in service name")
        servicename = input("Service name to add(input /back to go back to edit services list menu): ").strip()
        if servicename == "/back":
            editserviceschoices()
            break
        for cannothave in cannothavelist:
            if cannothave in servicename:
                havecannot = True
                break
        if not(havecannot):
            alreadyexisting = False
            for service_and_price in servicesdatalist:
                service = ((service_and_price.split(":")[0]).replace("|","")).lower()
                if service == servicename.lower():
                    print(f"{servicename} already exists in the services list.")
                    alreadyexisting = True
                    break
            if not(alreadyexisting):
               break 
    
    while True:
        serviceprice = input("Service's price per year(no need $, will be rounded off to 2dp, GST should be included in the price): ")
        if is_float(serviceprice):
            serviceprice = float(serviceprice)
            break
        else:
            print("Input invalid. Please input a valid price.")
    if servicesdatastring == "":
        new_service_and_price_string = "{}:{:.2f}".format(servicename,serviceprice)
    else:
        new_service_and_price_string = "|{}|:{:.2f}".format(servicename,serviceprice)
    server_reply = admin_send_to_server("anss"+new_service_and_price_string)
    if server_reply == "success":
        print("{} priced at {:.2f}/year succefuly added to service list.".format(servicename,serviceprice))
    else:
        print("{} priced at {:.2f}/year could not be added to service list.".format(servicename,serviceprice))
    addservice(new_service_and_price_string)


def listservice_edit(servicesdatastring):#List(print) existing services in service list and its price and make a dictionary with service(key) and price(value) use it in editservice()
    if servicesdatastring == "":
        print("There is no services in services list")
        editserviceschoices()
        sys.exit(0)
    servicesdic = {}
    servicesdatalist = servicesdatastring.split("\n")
    i = 0
    print('{:<5}{:<40}{:>5}'.format("No.","Service:","Price of service(GST included):"))
    for line in servicesdatalist:
        i += 1
        name, price = line.split(":")
        name = name.replace("|","")
        name, price = name.strip(), price.strip()
        printservice(i,name,price)
        servicesdic[name] = price
    editservice(i,servicesdic,servicesdatastring)

def searchservice_edit(servicesdatastring):#search and list(print) out services avilable and its price and make a dictionary with service(key) and price(value) use it in editservice()
    if servicesdatastring == "":
        print("There is no services in services list")
        editserviceschoices()
        sys.exit(0)
    servicesdic = {}
    usersearchinput = input("Please input service to search(GST included in service's price): ").lower()
    i = 0
    servicesdatalist = servicesdatastring.split("\n")
    print('{:<5}{:<40}{:>5}'.format("No.","Service:","Price of service(GST included):"))
    for line in servicesdatalist:
        lowername = line.split(":")[0].lower().strip()
        lowername = lowername.replace("|","")
        if usersearchinput in lowername:
            i += 1
            name, price = line.split(":")
            name = name.replace("|","")
            name, price = name.strip(), price.strip()
            servicesdic[name] = price
            printservice(i,name,price)
    if i == 0:
        print("No result")
        while True:
            continue_searching = input("Do you still want to continue searching? Y for yes and N for no: ").strip().lower()
            if continue_searching == "y":
                searchservice_edit(servicesdatastring)
                break
            elif continue_searching == "n":
                adminmainmenu()
                break
            else:
                print("Input invalid. Please try again.")
    else:
        editservice(i,servicesdic,servicesdatastring)

def editservice(i,servicesdic,servicesdatastring):
    while True:
        #Choose which service to edit, sort the services or go back to main menu
        editserviceselection = input(f"\nEnter the service No. 1-{i} you would like to edit, e for edit service menu, s to sort the services,0 go back to mainmenu: ").strip()
        if is_int(editserviceselection):
            editserviceselection = int(editserviceselection)
            if 1 <= editserviceselection <= i:
                servicetoedit = (list(servicesdic))[editserviceselection-1]
                if servicesdic[servicetoedit] == "removed":
                    print("{} already removed from service list.".format(servicetoedit))
                else:
                    while True:#Choose to edit, change the price or remove the service from services list
                        part_of_service_to_edit = input(f"What do you want to change about {servicetoedit}, input r to remove the service from services list, p to change the price, g to go back to choosing the service to edit: ")
                        if part_of_service_to_edit == "r":
                            service_string_to_edit = "|{}|:{}\n".format(servicetoedit,servicesdic[servicetoedit])
                            newservicedatastring = servicesdatastring + "\n"
                            newservicedatastring = (newservicedatastring.replace(service_string_to_edit,"")).rstrip()
                            admin_send_to_server("wnsl"+newservicedatastring)
                            newservicesdic = servicesdic
                            newservicesdic[servicetoedit] = "removed"
                            print(f"{servicetoedit} removed from services list.")
                            editservice(i,newservicesdic,newservicedatastring)
                            break
                        elif part_of_service_to_edit == "p":
                            service_string_to_edit = "|{}|:{}".format(servicetoedit,servicesdic[servicetoedit])
                            print("Price of {} now is ${}/year".format(servicetoedit,servicesdic[servicetoedit]))
                            while True:
                                new_service_price = input("New service's price per year(no need $, will be rounded off to 2dp, GST should be included in the price): ")
                                if is_float(new_service_price):
                                    new_service_price = float(new_service_price)
                                    break
                                else:
                                    print("Input invalid. Please input a valid price.")
                            new_service_price = "{:.2f}".format(new_service_price)
                            newservicedatastring = servicesdatastring.replace(service_string_to_edit,"|{}|:{}".format(servicetoedit,new_service_price))
                            admin_send_to_server("wnsl"+newservicedatastring)
                            print("Price of {} now is ${}/year".format(servicetoedit,new_service_price))
                            newservicesdic = servicesdic
                            newservicesdic[servicetoedit] = new_service_price
                            editservice(i,newservicesdic,newservicedatastring)
                            break
                        elif part_of_service_to_edit == "g":
                            editservice(i,servicesdic,servicesdatastring)
                            break
                        else:
                            print("Invalid input. Please enter either r,p or g")
                    break
            elif editserviceselection == 0:
                adminmainmenu()
                break
            else:
                print("Invalid input. Please enter a valid input.")
        elif editserviceselection == "e":
            editserviceschoices()
            break
        elif editserviceselection == "s":
            print("\nWays to sort:\n1. Alphabetical order (ascending)\n2. Alphabetical order (descending)\n3. Price (ascending)\n4. Price (descending)\n")
            while True:
                choose_sorting = input("How would you like to sort, please input a integer number from 1 to 4: ").strip()
                if choose_sorting == "1":
                    servicesdic = dict(sorted(servicesdic.items()))#Sort the dictionary using keys(services) by alphabetical order in ascending order
                    printsort(servicesdic,servicesdatastring)
                    break
                elif choose_sorting == "2":
                    servicesdic = dict(sorted(servicesdic.items(),reverse=True))#Sort the dictionary using keys(services) by alphabetical order in descending order
                    printsort(servicesdic,servicesdatastring)
                    break
                elif choose_sorting == "3":
                   servicesdic = dict(sorted(servicesdic.items(), key=lambda x: x[1]))#Sort the dictionary using values(price) by numerical order in ascending order
                   printsort(servicesdic,servicesdatastring)
                   break 
                elif choose_sorting == "4":
                   servicesdic = dict(sorted(servicesdic.items(), key=lambda x: x[1],reverse=True))#Sort the dictionary using values(price) by numerical order in descending order
                   printsort(servicesdic,servicesdatastring)
                   break
                else:
                    print("Invalid input. Please enter a valid input.")
            break
        else:
            print("Invalid input. Please enter a valid input.")

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

def changeuserpass():#Change password of a user's account
    while True:
        username = input("Username of account password u want to change(input .main to go back to main menu): ").strip().lower()
        if username == ".main":
            adminmainmenu()
            break
        elif username.isalnum():
            found = send_to_server("~ciue"+username)
            if found=="exist":
                print(f"{username} account found.")
                newpassword = passwordcreate()
                server_reply = admin_send_to_server("cuap"+newpassword+"^"+username)
                if server_reply == "Password successfully changed":
                    print(f"Password of {username} account successfully changed")
                else:
                    print(f"Password of {username} account was not able to be changed")
            else:
                print(f"{username} account not found.")
        else:
            print("Input invalid. Username will only include alphanumeric characters.")

def addadminaccount():#Add a admin account for admins to log into ESP admin system with
    while True:
        while True:
            username = input("Username (Used to login. Only alphanumeric characters are allowed in the username. Do not add space(s) or tab in the username. Uppercase,lowercase does not matter): ")
            if username.isalnum():
                username = username.lower()
                break
            else:
                print("Username invalid. Please input a valid username.")
        username = simple_encryption(username)
        server_reply = admin_send_to_server("ciae"+username)
        if server_reply == "unique":
            print("Admin account username unique")
            break
    password = passwordcreate()
    server_reply = admin_send_to_server("anaa"+username+"^"+password)
    if server_reply == "success":
        print("New admin account created.")
    else:
        print("New admin account was unable to be created")
    
    adminmainmenu()


adminlogin()