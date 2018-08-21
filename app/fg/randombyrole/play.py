from app import app,db
from flask import render_template,session,redirect,url_for,request
from openpyxl import load_workbook
import requests
import random
from app.models import Teams

@app.route('/fg/randombyrole/play')
def play():
    teams = Teams.query.filter_by(leghe_id=session['lega_id'])
    return render_template('fg-randombyrole.html', teams=teams)

@app.route('/fg/randombyrole/estrai')
def estrai():
    try:
        players = request.args['players']
    except:
        return redirect(url_for('play', missing_role=True))

    app.logger.info("Estrazione {}".format(players))

    if 'path_xls' in session:
        lista = session['path_xls'] + "/lista.xlsx"
    else:
        app.logger.error("Error, sessione vuota")
        return redirect(url_for('error', msg = 'sessionevuota'))

    lista_da_estrarre = "lista_" + players
    if lista_da_estrarre not in session:
        session[lista_da_estrarre] = CreaListaGiocatoridaEstrarre(lista, players)
    randomnumber = random.randint(0, len(session[lista_da_estrarre]) -1 )
    player_img_url = GetImgUrl(name=session[lista_da_estrarre][randomnumber]['player'])
    return render_template('fg-estrai.html', player = session[lista_da_estrarre][randomnumber], player_img_url = player_img_url)

def CreaListaGiocatoridaEstrarre(lista, players, con_scartati=False):
    wb = load_workbook(lista)
    ws_role = wb[players]
    offset = 2
    players_list = []
    for row in ws_role.rows:
        if row[0].row <= offset:
            continue
        if len(row) == 8:
            if row[7].value == "aggiudicato":
                continue
            else:
                if con_scartati == False:
                    if row[7].value == "scartato":
                        continue
        player_info = {}
        player_info['player'] = row[2].value
        player_info['player_row'] = row[7].row
        player_info['club'] = row[3].value
        player_info['quotazione'] = row[4].value
        app.logger.info("added {} to player list".format(player_info['player']))
        players_list.append(player_info)

    return players_list

def CampioncinoImageChecker(nameurl):
    campioncino_url = "https://content.fantagazzetta.com/web/campioncini/card/"
    complete_url = campioncino_url + nameurl + '.jpg'
    session = requests.Session()
    richiesta = session.get(complete_url, verify=True, headers=app.config['HTTP_HEADERS'])
    if (richiesta.status_code == 200):
        return complete_url
    else:
        return False

def GetImgUrl(name):
    app.logger.info("Download Url Campioncino")
    nameurls = []
    # Primo: al posto degli spazi metto dash
    nameurls.append(name.replace(" ", "-"))
    # Secondo: prendo solo la prima parola
    nameurls.append(name.split()[0])
    # Default image
    nameurls.append('NO-CAMPIONCINO')
    for nameurl in nameurls:
        imageurl = CampioncinoImageChecker(nameurl)
        if imageurl is not False:
            app.logger.info("{} immagine {}".format(name, imageurl))
            return imageurl
