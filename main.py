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

    def get_appstatus(self):
        # get application page
        r = self.s.get(
            "https://quest.pecs.uwaterloo.ca/psc/SS/ACADEMIC/SA/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?&ICAGTarget=start")

        appsoup = bsoup(r.content, "lxml")

        # get programs
        programshtml = appsoup.find_all(
            "span", {"title": "Enrollment Appointments"})

        programs = []
        for program in programshtml:
            programhtml = program.find("a")
            # get program icaction and name
            programs.append([programhtml.get("id"), programhtml.get_text()])

        inputs = appsoup.find(
            "div", {"id": "win0divPSHIDDENFIELDS"}).find_all("input")

        form = {
            "ICAJAX": "1",
            "ICNAVTYPEDROPDOWN": "0",
        }
        for fieldinput in inputs:
            form[fieldinput.get("id")] = fieldinput.get("value")

        appstatus = {}

        for program in programs:
            form["ICAction"] = program[0]
            r = self.s.post(
                "https://quest.pecs.uwaterloo.ca/psc/SS/ACADEMIC/SA/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL", data=form)
            applinkpage = bsoup(r.content, "lxml-xml")
            # parses text to find link
            applink = applinkpage.find_all("GENSCRIPT", {
                "id": "onloadScript"})[-1].get_text().split("'")[1]

            # get iframe link
            applink = applink.replace(
                "https://quest.pecs.uwaterloo.ca/psp", "https://quest.pecs.uwaterloo.ca/psc")

            r = self.s.get(applink)
            appstatuspage = bsoup(r.content, "lxml")
            status = appstatuspage.find("a", {"name": "STATUS$0"}).get_text()
            appstatus[program[1]] = status

        return appstatus


if __name__ == '__main__':
    a = Application(config["username"], config["password"])
    appstatus = a.get_appstatus()
    print("-" * 25)
    for key, value in appstatus.items():
        print(key)
        print(value)
        print("-" * 25)
