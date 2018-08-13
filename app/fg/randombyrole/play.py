from app import app,db
from flask import render_template,session
from app.models import Teams

@app.route('/fg/randombyrole/play')
def play():
    print(session['lega_id'])
    teams = Teams.query.filter_by(leghe_id=session['lega_id'])
    for team in teams:
        print(team.name)
    return render_template('fg-randombyrole.html')

