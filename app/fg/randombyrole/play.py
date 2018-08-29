from app import app,db
from flask import render_template,session,redirect,url_for,request
from openpyxl import load_workbook, Workbook
import os
import requests
import random
from app.models import Teams


class Estrazione():
    def __init__(self, tipo):
        self.tipo = tipo
        if 'path_xls' in session:
            self.path_lista_xls = session['path_xls'] + "/lista.xlsx"
            self.path_lega = session['path_xls']
        else:
            app.logger.error("Error, path_xls non e' in sessione")
            raise "PathXLSEmpty"

    def _error(which):
        print(which)

    def _createPlayersList(self):
        players_source_list = self.path_lista_xls
        wb = load_workbook(players_source_list)
        ws_role = wb[self.players]
        offset = 2
        players_list = []
        for row in ws_role.rows:
            if row[0].row <= offset:
                continue
            if len(row) == 8:
                if row[7].value == "aggiudicato":
                    continue
            player_info = {}
            player_info['name'] = row[2].value
            player_info['player_row'] = row[0].row
            player_info['club'] = row[3].value
            player_info['quotazione'] = row[4].value
            app.logger.info("added {} to player list".format(player_info['name']))
            players_list.append(player_info)

        return players_list

    def getPlayerList(self):
        if self.players_list_name not in session:
            app.logger.info("Metto in sessione la lista")
            session[self.players_list_name] = self._createPlayersList()

        return session[self.players_list_name]

    def _removePlayerFromList(self, list_name, index):
        del session[list_name][index]

    def incorso(self, *positional_parameters, **keyword_parameters):
        if ('quale' in keyword_parameters):
            quale = keyword_parameters['quale']
            session['estrazione_in_corso'] = url_for('estrai', players=quale)
        else:
            try:
                return session['estrazione_in_corso']
            except:
                return self._error(which="Missing parameter in function 'incorso'")

    def getRandomPlayer(self, players):
        self.players = players
        self.players_list_name = "lista_" + players
        players_list = self.getPlayerList()
        randomnumber = random.randint(0, len(players_list) -1 )
        if 'img_url' not in players_list[randomnumber]:
            self._addPlayerImage(randomnumber)
        return players_list[randomnumber], randomnumber

    def getPlayerbyIndex(self, players, index):
        self.players = players
        self.players_list_name = "lista_" + players
        players_list = self.getPlayerList()
        return players_list[index]

    def _campioncinoImageChecker(self, nameurl):
        campioncino_url = "https://content.fantagazzetta.com/web/campioncini/card/"
        complete_url = campioncino_url + nameurl + '.jpg'
        session = requests.Session()
        richiesta = session.get(complete_url, verify=True, headers=app.config['HTTP_HEADERS'])
        if (richiesta.status_code == 200):
            return complete_url
        else:
            return False

    def _getPlayerImage(self, name):
        app.logger.info("Download Url Campioncino")
        nameurls = []
        list_exception = ["ROSSI F"]
        if name not in list_exception:
            # Primo: al posto degli spazi metto dash
            nameurls.append(name.replace(" ", "-"))
            # Secondo: prendo solo la prima parola
            nameurls.append(name.split()[0])
            # Default image
            nameurls.append('NO-CAMPIONCINO')
        else:
            nameurls.append('NO-CAMPIONCINO')
        for nameurl in nameurls:
            imageurl = self._campioncinoImageChecker(nameurl)
            if imageurl is not False:
                app.logger.info("{} immagine {}".format(name, imageurl))
                return imageurl

    def _addPlayerImage(self, index):
        session[self.players_list_name][index]['img_url'] = self._getPlayerImage(session[self.players_list_name][index]['name'])

    def assignToTeam(self, team, player, index, players):
        team_xls = self.path_lega + "/" + team.replace("  ", "_") + ".xlsx"
        if not os.path.exists(team_xls):
            app.logger.info("File {} non esistente, lo creo".format(team_xls))
            wb = Workbook()
            wb.save(team_xls)

        wb = load_workbook(team_xls)
        sheet = 'rosa'
        if sheet not in wb.sheetnames:
            app.logger.info("Sheet {} non esistente, lo creo".format(sheet))
            wb.create_sheet(sheet)
            wb.save(team_xls)

        # Salva su file di team
        wb = load_workbook(team_xls)
        ws_role = wb[sheet]

        ws_rows = list(ws_role.rows)
        ws_last_row = len(ws_rows) -1

        if ws_rows[ws_last_row] is None:
            position = ws_last_row
        else:
            position = ws_last_row + 1

        ws_role.cell(column=1, row=position, value=player['name'])
        wb.save(team_xls)

        # Salvo su file di lega
        players_source_list = self.path_lista_xls
        wb = load_workbook(players_source_list)
        ws_role = wb[players]
        position = player['player_row']
        ws_role.cell(column=7, row=position, value = "aggiudicato")
        wb.save(players_source_list)
        # Remove from list
        lista_in_estrazione = "lista_" + players
        self._removePlayerFromList(lista_in_estrazione, index)


@app.route('/fg/randombyrole/play')
def play():
    return render_template('fg-randombyrole.html')

@app.route('/fg/randombyrole/estrai')
def estrai():
    try:
        players = request.args['players']
    except:
        return redirect(url_for('error', missing_role=True))

    session.modified = True

    Estrazione(tipo='randombyrole').incorso(quale=players)
    app.logger.info("Estrazione {}".format(players))

    player, index = Estrazione(tipo='randombyrole').getRandomPlayer(players)
    app.logger.info("Estratto {}".format(player['name']))

    return render_template('fg-randombyrole-play.html', player = player, num=index, action = "estrai")

@app.route('/fg/randombyrole/assegna')
def assegna():
    try:
        players = request.args['players']
    except:
        return redirect(url_for('error', missing_param="players"))
    try:
        index = int(request.args['index'])
    except:
        return redirect(url_for('error', missing_param="player_id"))

    teams = Teams.query.filter_by(leghe_id=session['lega_id'])

    player = Estrazione(tipo='randombyrole').getPlayerbyIndex(players, index)

    return render_template('fg-randombyrole-play.html', player = player, num=index, teams = teams, action = "assegna")

@app.route('/fg/randombyrole/confermato', methods=["POST"])
def confermato():
    session.modified = True

    try:
        players = request.form['players']
    except:
        return redirect(url_for('error', missing_param="role"))

    try:
        index = int(request.form['index'])
    except:
        return redirect(url_for('error', missing_param="player_id"))

    player = Estrazione(tipo='randombyrole').getPlayerbyIndex(players, index)

    if request.form['action'] == "assegna":
        team = request.form['team[1][]']
        Estrazione(tipo='randombyrole').assignToTeam(team, player, index, players)

    return redirect(Estrazione(tipo='randombyrole').incorso())
