# -*- coding: utf-8 -*-

from app import app,db
import crypt,string,random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display
from flask import session
from app.models import Leghe, Teams


def GetTeamsbyUrl(url_teams):
    teams = []
    # Chrome Options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors.

    display = Display(visible=0, size=(1280, 2048))
    display.start()
    app.logger.info("Opened Display for downloading teams by {}".format(url_teams))

    browser = webdriver.Chrome('/af/bin/chromedriver', chrome_options=chrome_options,  service_args=['--verbose', '--log-path=/af/bin/bin_logs/chromedriver.log'])
    browser.get(url_teams)
    wait = WebDriverWait(browser, 10)
    app.logger.info("Page downloaded")
    team_class="team-description"
    div_teams = browser.find_elements_by_class_name(team_class)
    for team in div_teams:
        team_name = team.find_element_by_css_selector('h5')
        app.logger.info("Found team {}".format(team_name.text))
        teams.append(team_name.text)

    browser.quit()
    display.stop()

    return teams

def SaveTeams():
    app.logger.info("Beggined teams crowler")
    app.logger.info("Application context {}".format(app.app_context()))
    app.logger.info("Lega team url is {}".format(session.get('lega_url_teams')))
    if 'lega_url_teams' not in session:
        app.logger.error("No url found in session")
        error = 1
        return error
    teams = GetTeamsbyUrl(session['lega_url_teams'])
    for team in teams:
        team_insert = Teams(name=team,leghe_id=session['lega_id'],millions=session['lega_millions'])
        db.session.add(team_insert)
        db.session.commit()
        db.session.flush()
        app.logger.info("Added team {} to db".format(team))
    app.logger.info("Team downloaded")


def PathIDGenerator(size=24, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def PutLegaInfo(lega_infos):
    print(lega_infos['name'])
    lega=Leghe(name=lega_infos['name'], path_xls=lega_infos['path_xls'], password=lega_infos['password_crypted'], millions=lega_infos['millions'], url_teams=lega_infos['url_teams'], status='opened')
    db.session.add(lega)
    db.session.commit()
    db.session.flush()
    session['lega_id'] = lega.id
    app.logger.info("Added lega {} with id {}".format(lega_infos['name'], lega.id))

