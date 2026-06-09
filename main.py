
# Create Bank Account
# Deposit money
# Withdrow money
# Verify details
# Update details
# Delete Account



import json
import random
import string
from pathlib import Path



class Bank:
          database='bankData.json'
          data=[]

          try:
                  if Path(database).exists():
                          with open(database) as f:
                                  data=json.loads(f.read())

                  else:
                    print("\nNo such file exist:") 
          
          except Exception as err:
                 print(f"\n An exception occured as {err}")






          '''@staticmethod
          def update():
                 with open(Bank.database, "w") as f:
                        f.write(json.dumps(Bank.data))'''
          


          @classmethod
          def __update(cls):
                 with open(cls.database, "w") as f:
                        f.write(json.dumps(cls.data))

          
          
          @classmethod
          def __accountgenerate(cls):
                 alpha = random.choices(string.ascii_letters, k = 4)
                 num = random.choices(string.digits, k = 5)
                 spchar = random.choices("!@#$%^&*", k = 1)
                 id = alpha + num + spchar
                 random.shuffle(id)
                 return "".join(id)
                        

          




          def createaccount(self):
                  info = {
                         "Name" : input("\nPlease tell your Name :- "),
                         "Age" : int(input("Please tell your Age :- ")),
                         "Mobile No" : int(input("Please tell your Mobile Number :- ")),
                         "Email" : input("Please tell your Email :- "),
                         "Aadhaar No" : int(input("Please tell your Aadhaar Number :- ")),
                         "Pen No" : input("Please tell your Pen Number :- "),
                         "Father Name" : input("Please tell your Father Name :- "),
                         "Mother Name" : input("Please tell your Mother Name :- "),
                         "Address" : input("Please tell your Address :- "),
                         "Pin" : int(input("Please tell your 4 Number Pin :- ")),
                         "Account No" : Bank.__accountgenerate(),
                         "Balance" : 0

                  }

                  if info["Age"] < 18:
                         print("\nSorry you cannot create your Account.")
                         print("You are under 18 years of Age.")

                  elif len(str(info["Mobile No"])) != 10:
                         print("\nSorry you cannot create your Account.")
                         print("Your Moblile Number is incorrect.")

                  elif len(str(info["Aadhaar No"])) != 12:
                         print("\nSorry you cannot create your Account.")
                         print("Your Aadhaar Number is incorrect.")

                  elif len(info["Pen No"]) != 10:
                         print("\nSorry you cannot create your Account.")
                         print("Your Pen Number is incorrect.")

                  elif len(str(info["Pin"])) != 4:
                         print("\nSorry you cannot create your Account.")
                         print("Your Pin Number is incorrect.")

                  else:
                         print("\n\n******  YOUR ACCOUNT HAS BEEN CREATED SUCCESSFULLY  *****\n\n")
                         for i in info:
                                print(f"{i} : {info[i]}")
                         print ("\nPlease note down your Account Number and Pin.\n")
                         Bank.data.append(info)
                         Bank.__update()





          
          def depositemoney(self):
                 name = input("\nPlease tell your Name :- ")
                 accnumber = input("Please tell your Account Number :- ")
                 pin = int(input("Please tell your Pin aswell :- "))


                 userdata = [i for i in Bank.data if (i["Account No"] == accnumber and i["Pin"] == pin)]
                 
                 userdata=userdata[0]

                 if userdata == False:
                        print("\nSoory no data found.")
                        print("You do not have an Account with Bank.")
                        print("Please Created your Account.")


                 else:
                        amount = int(input("\nHow much Amount you want to Depoit :- "))
                        if amount < 0:
                               print("Sorry the Amount very low you can Deposit above 0.")
                    
                        
                        else:
                               userdata["Balance"] += amount
                               Bank.__update()
                               print(f"\n\n*****  {name.upper()} YOUR AMOUNT DEPOSITED SUCCESSFULLY  *****\n\n")
                               print(f'\nName : {userdata["Name"]}')
                               print(f'Account Number : {userdata["Account No"]}')
                               print(f'Totle Balance : {userdata["Balance"]}\n')







                            
          def withdrowmoney(self):
                 name = input("\nPlease tell your Name :- ")
                 accnumber = input("Please tell your Account Number :- ")
                 pin = int(input("Please tell your Pin aswell :- "))
                 

                 userdata = [i for i in Bank.data if (i["Account No"] == accnumber and i["Pin"] == pin)]
                 
                 # userdata=userdata[0]

                 if userdata == False:
                        print("\nSoory no data found.")
                        print("You do not have an Account with Bank.")
                        print("Please Created your Account.")


                 else:
                        amount = int(input("\nHow much Amount you want to Withdrow :- "))
                        if amount < 0:
                               print("Sorry the Amount very low you can Withdrow above 0.")

                     
                        elif amount > userdata[0]["Balance"]:
                               print("Soory you dont have that much Money.")
                    
                        
                        else:
                               userdata[0]["Balance"] -= amount
                               Bank.__update()
                               print(f"\n\n*****  {name.upper()} YOUR AMOUNT WITHDREW SUCCESSFULLY  *****\n\n")
                               print(f"\nName : {userdata[0]['Name']}")
                               print(f"Account Number : {userdata[0]['Account No']}")
                               print(f"Totle Balance : {userdata[0]['Balance']}\n")

                 
                 

                    

          def detailshow(self):
                 accnumber = input("Please tell your Account Number :- ")
                 pin = int(input("Please tell your Pin aswell :- "))
                 

                 userdata = [i for i in Bank.data if (i["Account No"] == accnumber and i["Pin"] == pin)]
                 

                 if userdata == False:
                        print("\nSoory no data found.")
                        print("You do not have an Account with Bank.")
                        print("Please Created your Account.")


                 else:
                        print("\n\n*****  BANKA DETAILS SHOW SUCCESSFULLY *****\n\n")
                        print("\nYour Information are: ")
                        for i in userdata[0]:
                               print(f"{i} : {userdata[0][i]}")
                               
                        

  

          def updatdetails(self):
                 accnumber = input("Please tell your Account Number :- ")
                 pin = int(input("Please tell your Pin aswell :- "))
                 

                 userdata = [i for i in Bank.data if (i["Account No"] == accnumber and i["Pin"] == pin)]
       

                 if userdata == False:
                        print("\nSoory no data found.")
                        print("You do not have an Account with Bank.")
                        print("Please Created your Account.")


                 else:
                        print("\nYou cannot change the Age, Aadhaar Number, Pen Number, Father Name, Mother Name, Address, Account Number, Balance :")
                        print("Fill the details for change or leave it empty if NO change.")
                        newdata={
                               "Name" : input("\nPlease tell Your New Name or press Enter to skip :- "),
                               "Mobile No" : input("Please tell your New Mobile Number or press Enter to skip :- "),
                               "Email" : input("Please tell your New Email or press Enter to skip :- "),
                               "Pin" : input("Please tell your New 4 Number Pin or press Enter to skip :- ")
                        }
                        

                        if newdata["Name"] == "":
                               newdata["Name"] = userdata[0]["Name"]

                        if newdata["Mobile No"] == "":
                               newdata["Mobile No"] = userdata[0]["Mobile No"]

                        if newdata["Email"] == "":
                               newdata["Email"] = userdata[0]["Email"]
                     
                        if newdata["Pin"] == "":
                               newdata["Pin"] = userdata[0]["Pin"]

                        newdata["Age"] = userdata[0]["Age"]
                        newdata["Aadhaar No"] = userdata[0]["Aadhaar No"]
                        newdata["Pen No"] = userdata[0]["Pen No"]
                        newdata["Father Name"] = userdata[0]["Father Name"]
                        newdata["Mother Name"] = userdata[0]["Mother Name"]
                        newdata["Address"] = userdata[0]["Address"]
                        newdata["Account No"] = userdata[0]["Account No"]
                        newdata["Balance"] = userdata[0]["Balance"]


                        if type(newdata["Mobile No"]) == str:
                               newdata["Mobile No"] = int(newdata["Mobile No"])

                        
                        if type(newdata["Pin"]) == str:
                               newdata["Pin"] = int(newdata["Pin"])
                               
                               
                        for i in newdata:
                               if newdata[i] == userdata[0][i]:
                                      continue
                               
                               else:
                                      userdata[0][i] = newdata[i]

                            
                        Bank.__update()
                        print("\n\n*****  BANKA DETAILS UPDATE SUCCESSFULLY *****\n\n")
                        print("\nYour Information are: ")
                        for i in userdata[0]:
                               print(f"{i} : {userdata[0][i]}")






          def delete(self):
                 accnumber = input("Please tell your Account Number :- ")
                 pin = int(input("Please tell your Pin aswell :- "))
                 

                 userdata = [i for i in Bank.data if (i["Account No"] == accnumber and i["Pin"] == pin)]
       

                 if userdata == False:
                        print("\nSoory no data found.")
                        print("You do not have an Account with Bank.")
                        print("Please Created your Account.")


                 else:
                        check = input("\nPress Y if you actually want to Delete the Account or Press N.")
                        if check == 'n' or check == 'N':
                               print("\n\n*****  BY PASSED  *****\n\n")
                     
                        else:
                               index = Bank.data.index(userdata[0])
                               Bank.data.pop(index)
                               Bank.__update()
                               print("\n\n*****  YOUR ACCOUNT DELETE SUCCESSFULLY  *****")
                        
                 
                 
              
                 



user=Bank()



print("\n\n=====  WELCOME TO BANKA  =====\n")
print("Press 1 for Creating an Account.")
print("Press 2 for Depositing the money in the bank.")
print("Press 3 for Withdrowing the money.")
print("Press 4 for check your details.")
print("Press 5 for Updating the details.")
print("Press 6 for Deleting your Account.")

check = int(input("\nPlease tell your response :- "))

if check == 1:
        user.createaccount()

elif check == 2:
       user.depositemoney()

elif check == 3:
       user.withdrowmoney()

elif check == 4:
       user.detailshow()

elif check == 5:
       user.updatdetails()

elif check == 6:
       user.delete()

else:
       print("Please Enter A Vaild Number:")






