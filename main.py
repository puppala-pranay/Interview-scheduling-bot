import pyttsx3
import datetime
import json
import base64


class MyAssistant:
    def __init__(self):
        """
        Constructor to class MyAssistant .
        It setup the Speech Engine
        It loads the json data of time slots .
        It makes some variables which are used later
        """
        print('Loading your AI personal assistant - G One')

        self.engine = pyttsx3.init('sapi5')
        self.voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', 'self.voices[0].id')

        with open('time_slots.json') as f:
            self.slots_data = json.load(f)

        self.role = None
        self.user_name = None
        self.password = None

    def validate(self, role_, user_name, password):
        """
        When the Username and Password are entered,
        These are checked with the username, password from database(Here file) and
        validated
        :param role_: role of person - manager/interview applicant
        :param user_name: username entered
        :param password: password entered
        :return: True if details are matched , else false
        """
        with open('user_pass.json') as f:
            user_data = json.load(f)
        if user_name not in user_data:
            return False
        if user_data[user_name] != str(base64.b64encode(password.encode("utf-8"))):
            return False
        self.role = role_
        self.user_name = user_name
        self.password = password
        return True

    def speak(self, text):
        """
        Converts the text into speech
        :param text:  text to be converted
        :return: void
        """
        self.engine.say(text)
        self.engine.runAndWait()

    def wish_me(self):
        """
        Greet the user
        :return: void
        """
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            self.speak("Hello,Good Morning")
            print("Hello,Good Morning")
        elif 12 <= hour < 18:
            self.speak("Hello,Good Afternoon")
            print("Hello,Good Afternoon")
        else:
            self.speak("Hello,Good Evening")
            print("Hello,Good Evening")

    def speak_input(self, text):
        """
        Given a text , converts into speech and takes the input .
        :param text: text to be converted
        :return: void
        """
        print(text, end=" ")
        self.speak(text)
        return input()

    def login(self):
        """
        Login phase , which takes the username and password and validates
        :return: void
        """
        self.speak("Are you a manager or interview applicant")

        role_ = int(self.speak_input("Enter 1 for Manager , 2 for applicant : "))
        user_name = self.speak_input("Enter the username : ")
        self.speak("Hello " + user_name)
        password = self.speak_input("Please Enter your password: ")

        if self.validate(role_, user_name, password):
            self.speak("Congratulations your authorised")
        else:
            self.speak("you are not authorised to performed the task. Thank you")
            exit()

        return

    def signup(self):
        """
        Creates and stores new username ,password if user don't have account previously
        :return:
        """
        self.speak("Are you a manager or interview applicant")

        role_ = int(self.speak_input("Enter 1 for Manager , 2 for applicant : "))
        user_name = self.speak_input("Enter the username : ")
        self.speak("Hello " + user_name)
        password = self.speak_input("Please Enter your password: ")

        with open('user_pass.json') as f:
            user_data = json.load(f)
        user_data[user_name] = str(base64.b64encode(password.encode("utf-8")))

        with open('user_pass.json', 'w') as json_file:
            json.dump(user_data, json_file)
        self.speak("Account created .")
        print("Account Created")

        self.role = role_
        self.user_name = user_name
        self.password = password

        return

    def update_flexible_times(self):
        """
        If user is manager , This function updates the free slots according to input
        :return: -
        """
        self.speak("Select the day in this week you want to update . M is Monday, "
                   "T is tuesday ,W is wednesday, TH for Thursday , F for Friday ")
        day = input("Select the day in this week you want to update(M,T,W,TH,F) : ")
        timeslots = set()
        self.speak("Now , Enter the time slots in which you are free in that day ")
        print("These are the time slots 8-10am(1) , 10-12am(2) , 1pm-3pm(3) , 3pm-5pm(4) ")
        timeslot = input("Enter the timeslot number in brackets to add into Free slots . If done enter 0 : ")
        while timeslot != "0":
            timeslots.add(timeslot)
            timeslot = input("Enter the timeslot number in brackets to add into Free slots . If done enter 0 : ")
        if self.user_name in self.slots_data:
            self.slots_data[self.user_name][day] = list(timeslots)
        else:
            self.slots_data[self.user_name] = {}
            self.slots_data[self.user_name][day] = list(timeslots)

        return

    def select_time(self):
        """
        If user is applicant , the time slot is selected and updated to booked_slots.txt based on input
        :return:
        """

        available_slots = {
            "M": set(),
            "T": set(),
            "W": set(),
            "TH": set(),
            "F": set()
        }
        slots = ["8am-10am(1)", "10am-12am(2)", "1pm-3pm(3)", "3pm-5pm(4)"]

        if not self.slots_data:
            self.speak("Sorry "+self.user_name+" No slots available for this week. Try later ")
            print("Thank you")
            return

        for value in self.slots_data.values():
            for key1 in value.keys():
                for val in value[key1]:
                    available_slots[key1].add(val)

        self.speak("Select the time-slot in this week you want to attend . M is Monday, "
                   "T is tuesday ,W is wednesday, TH for Thursday , F for Friday ")

        for key in available_slots:
            if available_slots[key]:
                print(key + ":", end=" ")
                for val in available_slots[key]:
                    print(slots[int(val)-1], end=" ")
                print(end="\n")

        day = self.speak_input("Select the day from above available slots (M/T/W/TH/F) :  ")
        slot_time = self.speak_input("Select the time slot on the selected day (Enter number inside the brackets of "
                                     "time slot) : ")
        manager_allocated = None
        for manager_name in self.slots_data.keys():
            if day in self.slots_data[manager_name].keys():
                if slot_time in self.slots_data[manager_name][day]:
                    manager_allocated = manager_name
                    self.slots_data[manager_name][day].remove(slot_time)
                    if not self.slots_data[manager_name][day]:
                        self.slots_data[manager_name].remove(day)
                    if not self.slots_data[manager_name]:
                        self.slots_data.remove(manager_name)

        file1 = open("booked_slots.txt", "a")  # append mode
        file1.write(self.user_name + " " + day + " " + slots[int(slot_time)-1] + " " + manager_allocated + "\n")
        file1.close()
        return

    def end_program(self):
        """
        Re-enters the new time-slots data into time_slots.json and end the program by ending note.
        :return:
        """
        with open('time_slots.json', 'w') as json_file:
            json.dump(self.slots_data, json_file)
        self.speak("Thanks for your time. Details have been updated")
        exit(0)
        return


if __name__ == '__main__':

    assistant = MyAssistant()  # instance of MyAssistant class
    assistant.wish_me()        # Greet the user

    resp = assistant.speak_input("Do You Already Have Account(Y/N) : ")  # login / signup
    if resp == "Y":
        assistant.login()
    else:
        assistant.signup()

    if assistant.role == 1:                                         # Update the free time slots if manager
        res = input("Do you want to update time slots - Y/N : ")
        while res == "Y":
            assistant.update_flexible_times()
            res = input("Do you want to update time slots - Y/N : ")
        assistant.end_program()

    elif assistant.role == 2:                       # select the suitable time slots if applicant
        assistant.select_time()
        assistant.end_program()

    exit()
