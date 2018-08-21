from app import app,db
from app.fg.utils import SaveTeams, PutLegaInfo, PathIDGenerator, DownloadPlayerList
from app.models import Leghe
from app.fg.requirements import GetFantagazzettaRequirements, GetFantagazzettaRecover
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Response,stream_with_context,render_template,redirect,url_for,request,session


@app.route('/fg/randombyrole/requirements', methods=['GET', 'POST'])
def FgRandombyRoleRequirements():
    form = GetFantagazzettaRequirements(request.form)
    if request.method == 'GET':
        return render_template('fg-requirements.html', form=form)
    else:
        if request.method == 'POST' and form.validate():
            lega_infos = LegaInfo(form)
            return LegaValidationStarting(lega_infos)

def LegaInfo(form):
    lega_infos = {}
    lega_infos['password_lega'] = form.password_lega.data
    lega_infos['url_teams'] = form.url_lega.data + '/squadre'
    lega_infos['millions'] = form.millions.data
    lega_infos['name'] = lega_infos['url_teams'].split('/')[-2]
    lega_infos['path_xls'] =  'app/static/list/'  + PathIDGenerator() + '-' + lega_infos['name']
    lega_infos['password_crypted'] = generate_password_hash(lega_infos['password_lega'])
    #Put Values into session
    session['lega_url_teams'] = lega_infos['url_teams']
    session['lega_millions'] = lega_infos['millions']
    session['lega_name'] = lega_infos['name']
    session['path_xls'] = lega_infos['path_xls']
    return lega_infos

def LegaValidationStarting(lega_infos):
    lega_already_used = Leghe.query.filter_by(url_teams=session['lega_url_teams'], status='opened' ).first()
    if lega_already_used is None:
        app.logger.info("Rendering FG-Preparation da metodo post")
        PutLegaInfo(lega_infos)
        return render_template('fg-preparation.html')
    else:
        app.logger.info("Lega already present and opened")
        return redirect(url_for('FgRandombyRoleRecover'))

@app.route('/fg/randombyrole/recover', methods=['GET', 'POST'])
def FgRandombyRoleRecover():
    app.logger.info("Starting Recover Asta")
    form = GetFantagazzettaRecover(request.form)
    if request.method == 'GET':
        return render_template('fg-lega-opened.html', form=form)
    else:
        if request.method == 'POST' and form.validate():
            lega = Leghe.query.filter_by(url_teams=session['lega_url_teams'], status='opened' ).first()
            password_lega = lega.password
            password_inserted = form.password_recupero.data
            password_ok = check_password_hash(password_lega, password_inserted)
            if password_ok:
                session['lega_url_teams'] = lega.url_teams
                session['lega_id'] = lega.id
                session['lega_name'] = lega.name
                session['lega_millions'] = lega.millions
                session['path_xls'] = lega.path_xls
                return redirect(url_for('play'))
            else:
                return redirect(url_for('FgRandombyRoleRecover', password_ok=password_ok))

@app.route('/fg/randombyrole/preparation')
def progress():
    def main():
        tasks = 2
        progress = 0
        todo = [SaveTeams,DownloadPlayerList]

        while progress < tasks:
            todo[progress]()
            progress +=1
            yield "data:" + str(((100/tasks)*progress)/100) + "\n\n"
            time.sleep(0.2)

    app.logger.info("Progress Lega team url is {}".format(session.get('lega_url_teams')))
    return Response(stream_with_context(main()), mimetype='text/event-stream')

