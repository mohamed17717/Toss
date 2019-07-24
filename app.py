import os

from view import *

from flask import Flask, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__, template_folder='templates', static_folder='static')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

loginSystem = LoginSystem()
valid = LoginSystem()

@app.route("/", methods=['GET'])
@app.route('/<int:pageNumber>/', methods=['GET'])
def home(pageNumber=1):
	clearFilterGames()
	return index(pageNumber)

@app.route('/login/', methods=['POST'])
def login():
	if logined(): return takeMeHome()

	return loginSystem.login(request.form)

@app.route('/register/', methods=['POST'])
def register():
	if logined(): return takeMeHome()

	return loginSystem.register(request.form)

@app.route('/logout/', methods=['GET'])
def logout():
	if not logined(): return takeMeHome()

	return loginSystem.logout()

@app.route('/profile/<int:userId>/', methods=['GET'])
def profile(userId):
	if not logined(): return takeMeHome()

	return getProfile(userId)

@app.route('/game/<int:rolletId>/', methods=['GET'])
def rollet(rolletId):
	if not logined(): return takeMeHome()

	return getRollet(rolletId)

@app.route('/createGame/', methods=['POST'])
def createGame():
	if not logined(): return takeMeHome()

	try:
		howLong = int(request.form.get('howLong'))
		ticket = int(request.form.get('ticket'))
		percentOfWinners = int(request.form.get('percentOfWinners'))
	except:
		message('Can\'t convert int ', 'danger fail')
		return takeMeHome()
	
	## check inputs
	if valid.numInRange(howLong, 1, 24) and ticket > 0 and valid.integer(percentOfWinners):
		rolletId = create_Rollet(howLong, ticket, percentOfWinners)

		if rolletId:
			message('Congrtulation You Now a Founder For This Game', 'success')	
			return  redirect( url_for('rollet', rolletId=rolletId) )

	message('Sorry Ther Is Something Wrong We Can\'t Create A Game Right Now', 'danger')
	return takeMeHome()

@app.route('/dareGame/<int:rolletId>/', methods=['POST'])
def dareGame(rolletId):
	if not logined(): return takeMeHome()

	if dare_Rollet(rolletId):
		message('Shame.. You Dare Well', 'success')
		return takeMeHome()
	message('Sorry You Can\'t Dare The Game', 'danger')	
	return takeMeHome()

@app.route('/removeGame/<int:rolletId>/', methods=['POST'])
def removeGame(rolletId):
	if not logined(): return takeMeHome()

	if delete_Rollet(rolletId):
		message('Game Deleted', 'success')
		return takeMeHome()
	message('Game Can\'t Deleted', 'danger')	
	return redirect(url_for('rollet', rolletId = rolletId))
	
@app.route('/joinGame/<int:rolletId>/', methods=['POST'])
def joinGame(rolletId):
	if not logined(): return takeMeHome()

	try:
		times = int(request.form.get('times'))
	except:
		message('failed to join the game', 'danger')
		return takeMeHome()

	for i in range(times):
		status = participate_Rollet(rolletId)
		if not status: break

	return redirect(url_for('rollet', rolletId = rolletId))

@app.route('/endGame/<int:rolletId>/', methods=['POST'])
def endGame(rolletId):
	if not logined(): return takeMeHome()

	end_Rollet(rolletId)
	return redirect( url_for('rollet', rolletId=rolletId))

@app.route('/filterGames/', methods=['POST'])
@app.route('/filterGames/<int:pageNumber>/', methods=['GET'])
def filterGames(pageNumber=1):
	if not logined(): return takeMeHome()

	if request.method == 'POST':
		upNow = request.form.get('upNow') or 1
		percentOfWinnersStart = request.form.get('percentOfWinnersStart') or 0
		percentOfWinnersEnd = request.form.get('percentOfWinnersEnd') or 100
		ticketStart = request.form.get('ticketStart') or 0
		ticketEnd = request.form.get('ticketEnd') or 10**6

		filterRollets( 
			upNow=upNow, 
			percentOfWinnersBetween=(percentOfWinnersStart, percentOfWinnersEnd), 
			ticketBetween= (ticketStart, ticketEnd),
		)

	return index(pageNumber)

@app.route('/clearFilter/', methods=['GET','POST'])
def clearFilterGames():
	if session.get('filteredRollets'): session.pop('filteredRollets')
	return takeMeHome()

@app.errorhandler(404)
def page_not_found(e):
	return renderTemplate('404.html'), 404