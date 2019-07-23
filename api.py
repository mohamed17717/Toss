import os

from flask import session, jsonify, render_template, redirect, url_for

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from time import time
from json import dumps, loads

import math
from random import choice

from rollet import *

# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

## start helper functions ##
def getUserId():
	return session['user']['id']

def getUsernameById(userId):
	username = db.execute('SELECT username FROM users WHERE id=:id', {'id':userId}).fetchone()
	if username: return username[0]

def getWallet(username=None):

	username = username or session['user']['username']

	wallet = db.execute(
		'SELECT * FROM wallets WHERE username=:username;',
		{'username': username}
	).fetchone()

	if wallet:
		_id,username,balance,lose,win,charged,inuse,pulled = wallet
		wallet =  {
			'id': _id,
			'username': username,
			'balance': balance,
			'lose': lose,
			'win': win,
			'charged': charged,
			'inuse': inuse,
			'pulled': pulled,
		}
		if username == session['user']['username']:
			session['wallet'] = wallet
		return wallet

def setWallet(username=None, wallet=None):
	username = username or session['user']['username']
	clms = ('id','username','balance','lose','win','charged','inuse','pulled')
	values = wallet or session['wallet']
	if not values: return

	clms = [f'{clm}=:{clm}' for clm in clms]
	clms = ','.join(clms)

	db.execute(
		'UPDATE wallets SET {} \
		WHERE username=:username'.format(clms), 
		values)
	db.commit()

def insertRollet(values):
	clms = (
		'upNow',
		'creator',
		'howLong',
		'startTime',
		'percentOfWinners',
		'ticket',
		'participants',
		'winners'
	)
	clms   = ','.join(clms)

	command = '''
		INSERT INTO rollets ({clms})
		VALUES (
			:upNow,
			:creator,
			:howLong,
			:startTime,
			:percentOfWinners,
			:ticket,
			:participants,
			:winners
		);'''.format(clms=clms)

	db.execute(
		command, 
		values
	)
	db.commit()

def getRollet(rolletId):
	return db.execute(
					'SELECT * FROM rollets WHERE id=:rolletId;', 
					{'rolletId': rolletId}
				).fetchone()

def getRolletInstance(rolletRow):
	id, upNow, creator, howLong, startTime, percentOfWinners, ticket, participants, winners = rolletRow

	theRollet = Rollet(json={
		'db':{
			'id': id,
			'creator': creator,
			'upNow': upNow,
		},
		'howLong' : howLong, 
		'startTime' : startTime, 
		'percentOfWinners' : percentOfWinners, 
		'ticket' : ticket, 
		'participants' : loads(participants) or [], 
		'winners' : loads(winners) or [],
	})
	return theRollet

def getRolletInstanceByRolletId(rolletId):
	rollet = getRollet(rolletId)
	if rollet:
		return getRolletInstance(rollet)

def getUserRollets(userId):
	rollets = db.execute(
		'SELECT rollets FROM users WHERE id=:userId;',
		{'userId': userId}
	).fetchone()
	if rollets:
		return loads(rollets[0])

def setUserRollets(userId, rollets):
	db.execute(
		'UPDATE users SET rollets=:rollets WHERE id=:userId;',
		{'userId': userId, 'rollets': dumps(rollets)}
	)
	db.commit()

def updateRolletParticipants(rolletId, participants, winners=[], upNow= 1):
	db.execute(
		'UPDATE rollets SET participants=:participants, winners=:winners, upnow=:upnow WHERE id=:rolletId;',
		{
			'rolletId': rolletId, 
			'participants': dumps(participants), 
			'winners': dumps(winners),
			'upnow': upNow,
		}
	)
	db.commit()
## end helper functions ##


## start wallet ##
def charge_Wallet():
	getWallet()
	wallet = session['wallet']

	## youe code here

	setWallet()

def pull_Wallet():
	getWallet()
	wallet = session['wallet']

	## youe code here

	setWallet()

def lose_Wallet(participantId, ticket):
	username = getUsernameById(participantId)
	wallet = getWallet(username)

	wallet['lose'] += ticket
	wallet['inuse'] -= ticket
	# wallet['balance'] -= ticket

	setWallet(username, wallet)

def win_Wallet(participantId, ticket, everyWinnerRealTake):
	username = getUsernameById(participantId)
	wallet = getWallet(username)

	earnedMoney = everyWinnerRealTake - ticket

	wallet['win'] += earnedMoney
	wallet['inuse'] -= ticket
	wallet['balance'] += everyWinnerRealTake

	setWallet(username, wallet)

def changeInUse_Wallet(ticket):
	getWallet()
	wallet = session['wallet']
	wallet['inuse'] += ticket
	wallet['balance'] += -ticket
	setWallet()

def getBalance_Wallet():
	getWallet()
	wallet = session['wallet']
	return wallet['balance']
## end Wallet ##

## start Rollet ##
def allowedToCreateGame(userId):
	return db.execute(
		'SELECT * FROM rollets WHERE creator=:userId AND upnow=1;',
		{'userId': userId}
	).rowcount < 90

def create_Rollet(howLong, ticket, percentOfWinners):
	creatorId = getUserId()

	theRollet = Rollet(howLong=howLong, ticket=ticket, percentOfWinners=percentOfWinners)
	if  theRollet.ticket <= getBalance_Wallet() and allowedToCreateGame(creatorId):
		rolletJSON = theRollet.getJSON()
		rolletJSON.update({'creator': creatorId})

		insertRollet(rolletJSON)
		
		rolletId = db.execute('''
			SELECT id FROM rollets WHERE startTime=:startTime ORDER BY id DESC LIMIT 1;
			''', {
				'startTime': theRollet.startTime
			}).fetchone()[0]
		participate_Rollet(rolletId)
		return rolletId
	else:
		message('you dont have enough money or you not allowed to create games', ' danger failed')

def participate_Rollet(rolletId):
	userId = getUserId()
	theRollet = getRolletInstanceByRolletId(rolletId)
	if theRollet.upNow and theRollet.ticket <= getBalance_Wallet():
		changeInUse_Wallet(theRollet.ticket)
		theRollet.participants.append(userId)
		
		rollets = getUserRollets(userId)
		if rollets.get(str(rolletId)):
			rollets[str(rolletId)]['joinTime'].append(time())
		else:
			rollets[str(rolletId)] = { 'joinTime': [time()] }

		setUserRollets(userId, rollets)
		updateRolletParticipants(rolletId, theRollet.participants)

		return True

def delete_Rollet(rolletId):
	userId = getUserId()
	theRollet = getRolletInstanceByRolletId(rolletId)
	if theRollet and theRollet.upNow:

		if theRollet.participants:
			uniqueParticipants = list(set(theRollet.participants))
			if len(uniqueParticipants) != 1 or uniqueParticipants[0] != userId: return

		db.execute('''
			DELETE FROM rollets WHERE id=:rolletId;
			''', {'rolletId': rolletId})
		db.commit()

		rollets = getUserRollets(userId)
		rollets.pop(str(rolletId))
		setUserRollets(userId, rollets)
		changeInUse_Wallet(-theRollet.ticket * theRollet.totalParticipants)
		return True

def dare_Rollet(rolletId):
	userId = getUserId()
	rollets = getUserRollets(userId)
	rollet = rollets.get(str(rolletId))
	
	if not rollet: return

	lastJoinTime = rollet['joinTime'][-1]
	howLongJoined = time() - lastJoinTime

	maxTimeToDar = 15 # min
	if howLongJoined < maxTimeToDar*60:

		theRollet = getRolletInstanceByRolletId(rolletId)
		if theRollet.upNow and userId in theRollet.participants:
			
			rollet['joinTime'].pop()
			setUserRollets(userId, rollets)

			theRollet.participants.remove(userId)
			if theRollet.participants:
				## this function also called when remove a game
				changeInUse_Wallet(-theRollet.ticket) 
				updateRolletParticipants(rolletId, theRollet.participants)
			else:
				delete_Rollet(rolletId)
			return True

def end_Rollet(rolletId):
	theRollet = getRolletInstanceByRolletId(rolletId)
	if theRollet and theRollet.isTimeOver() and not theRollet.winners and theRollet.db.get('upNow'):
		participants = theRollet.participants

		## there is only one compitetor, give him his money back
		if len(set(participants)) == 1:
			changeInUse_Wallet(-theRollet.ticket * theRollet.totalParticipants)
		else:
			theRollet.selectWinners()
	
		winners = theRollet.winners or None
		updateRolletParticipants(rolletId, participants , winners, theRollet.upNow)

		if winners:
			ticket = theRollet.ticket
			everyWinnerRealTake = theRollet.everyWinnerRealTake
			
			for participantId in participants:
				if participantId in winners:
					winners.remove(participantId)
					win_Wallet(participantId, ticket, everyWinnerRealTake)
				else:
					lose_Wallet(participantId, ticket)
	return theRollet
## end Rollet ##


## Start View Functions ##
def getAliveRollets(limit=500):
	return db.execute(
		'SELECT * FROM rollets \
		WHERE upNow=1 \
		ORDER BY startTime DESC \
		LIMIT {};'.format(limit)
	).fetchall()

def getHotRollets(rollets):
	r = rollets.copy()
	
	r = list(r.items())
	r.sort(key= lambda x: x[1]['totalParticipants'])
	r = r[:-7]
	r = dict(r)

	session['hotRollets'] = r
	return r


def rolletSlider(pageNumber, total=200, everyPage=20):
	if session.get('filteredRollets') != None:
		rollets = session.get('filteredRollets')
	else: 
		rollets = getAliveRollets(total)
		session['rollets'] = rollets

	pageNumber -= 1
	start = pageNumber * everyPage
	end = start + everyPage
	rolletsInstances = {}
	[rolletsInstances.update({rollet[0]: getRolletInstance(rollet).getJSON()}) for rollet in rollets[start: end]]
	return rolletsInstances, math.ceil(len(rollets)/everyPage)

def filterRollets( 
		upNow=1, 
		percentOfWinnersBetween=(0, 100), 
		ticketBetween= (0, 1000000),
	):
	percentOfWinnersStart, percentOfWinnersEnd = percentOfWinnersBetween
	ticketStart, ticketEnd = ticketBetween


	session['filteredRollets'] = db.execute(
		'SELECT * FROM rollets WHERE \
		(upNow=:upNow) AND \
		(percentOfWinners BETWEEN :p1 AND :p2) AND \
		(ticket BETWEEN :t1 AND :t2);'
		,{
			'upNow': upNow, 
			'p1': percentOfWinnersStart,
			'p2': percentOfWinnersEnd,
			't1': ticketStart, 
			't2': ticketEnd
		}
	).fetchall()

def message(msg, classes):
	if session.get('messages'):
		if type(classes) in (tuple, list): 
			classes = ' '.join(classes)
		session['messages'].append({'msg': msg, 'class': classes})
	else:
		session['messages'] = [ {'msg': msg, 'class': classes} ]

def getMessages():
	if session.get('messages'):
		return session.pop('messages')

def logined():
	if session.get('user') != None:
		if activated():
			return True
		return False
	return None

def activated():
	if session.get('user'):
		return session['user'].get('active') == 1

def renderTemplate(html, context={}):
	''' you can add here default rendered data '''
	if logined():
		getWallet()

		userRolletsJoined = {}
		userRollets = getUserRollets(getUserId())
		if userRollets:
			[userRolletsJoined.update({
				rolletId: getRolletInstanceByRolletId(int(rolletId)).getJSON()
			}) for rolletId in userRollets.keys()]


		context.update({
			'logined': True,
			'header': True,
			'wallet': session['wallet'],
			'user': session['user'],
			'rolletsIn': userRolletsJoined
		})


	context['messages'] = getMessages()
	return render_template(html, **context) # jsonify(context)#


def takeMeHome():
	return redirect(url_for('home'))
## End View Functions ##



