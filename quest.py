import os
import json
import requests
from bs4 import BeautifulSoup as bsoup

# load login credentials
with open(os.getcwd() + "\config.json", "r") as f:
    config = json.load(f)


class Application:
    def __init__(self, username, password):
        self.s = requests.Session()
        self.s.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"})

        # program information
        self.programs = []

        # login
        payload = {
            "j_username": username,
            "j_password": password,
            "_eventId_proceed": "Login"
        }
        # login cookies
        r = self.s.get(
            "https://idp.uwaterloo.ca/idp/profile/SAML2/Unsolicited/SSO?providerId=quest.ss.apps.uwaterloo.ca")
        execution = r.url.split("execution=")[1]
        r = self.s.post(
            f"https://idp.uwaterloo.ca/idp/profile/SAML2/Unsolicited/SSO?execution={execution}", data=payload)

        # get SAMLResponse for verification
        soup = bsoup(r.content, "lxml")
        SAMLResponse = soup.find(
            "input", {"name": "SAMLResponse"}).get("value")
        payload = {
            "SAMLResponse": SAMLResponse
        }
        # authenticate
        r = self.s.post(
            "https://quest.pecs.uwaterloo.ca/psc/SS/ACADEMIC/SA/s/WEBLIB_PTBR.ISCRIPT1.FieldFormula.IScript_StartPage", data=payload)

        # get application page
        r = self.s.get(
            "https://quest.pecs.uwaterloo.ca/psc/SS/ACADEMIC/SA/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?&ICAGTarget=start")

        appsoup = bsoup(r.content, "lxml")

        # get programs
        programshtml = appsoup.find_all(
            "span", {"title": "Enrollment Appointments"})

        for program in programshtml:
            programhtml = program.find("a")
            # get program icaction and name
            self.programs.append({"Program": programhtml.get_text(),
                                  "ICAction": programhtml.get("id")})

        inputs = appsoup.find(
            "div", {"id": "win0divPSHIDDENFIELDS"}).find_all("input")

        form = {
            "ICAJAX": "1",
            "ICNAVTYPEDROPDOWN": "0",
        }
        for fieldinput in inputs:
            form[fieldinput.get("id")] = fieldinput.get("value")

        # get program application link
        for ind, program in enumerate(self.programs):
            form["ICAction"] = program["ICAction"]
            r = self.s.post(
                "https://quest.pecs.uwaterloo.ca/psc/SS/ACADEMIC/SA/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL", data=form)
            applinkpage = bsoup(r.content, "lxml-xml")
            # parses text to find link
            applink = applinkpage.find_all("GENSCRIPT", {
                "id": "onloadScript"})[-1].get_text().split("'")[1]

            # get iframe link
            applink = applink.replace(
                "https://quest.pecs.uwaterloo.ca/psp", "https://quest.pecs.uwaterloo.ca/psc")
            self.programs[ind]["Link"] = applink

    def get_appstatus(self):
        appstatus = {}
        for program in self.programs:
            r = self.s.get(program["Link"])
            appstatuspage = bsoup(r.content, "lxml")
            status = appstatuspage.find("a", {"name": "STATUS$0"}).get_text()
            appstatus[program["Program"]] = status

        return appstatus

    def reset_timeout(self):
        # resets Quest's timeout
        self.s.get(
            "https://quest.pecs.uwaterloo.ca/psc/SS/ACADEMIC/SA/?cmd=resettimeout")


if __name__ == '__main__':
    a = Application(config["username"], config["password"])
    appstatus = a.get_appstatus()
    print("-" * 25)
    for key, value in appstatus.items():
        print(key)
        print(value)
        print("-" * 25)
