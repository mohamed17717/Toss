from flask import session, redirect, url_for, abort

from api import *
from loginSystem import *

def index(pageNumber = 1):
	context = {}

	if logined():
		rollets, pagesCount = rolletSlider(pageNumber)

		context['rollets']    = rollets
		context['hotRollets'] = getHotRollets(rollets)
		context['pagesCount'] = range(1, pagesCount+1)

		return renderTemplate('home.html', context=context)
	return renderTemplate('login.html', context=context)

def getRollet(rolletId):
	# theRollet = getRolletInstanceByRolletId(rolletId)
	theRollet = end_Rollet(rolletId) ## anyway it execute the above function
	if theRollet:
		context = {'theRollet': theRollet.getJSON()}
		return renderTemplate('rollet.html', context=context)
	return abort(404)

def getProfile(userId):
	context = {}

	user = db.execute(
		'SELECT username, rollets FROM users \
		WHERE id=:userId;', 
		{'userId': userId}
	)
	if user.rowcount == 1:
		username, rollets = user.fetchone()

		userWallet = db.execute(
			'SELECT win, lose FROM wallets \
			WHERE username=:u;', 
			{'u': username}
		)

		if userWallet.rowcount == 1:
			wallet = userWallet.fetchone()
			userRolletsJoined = {}

			[userRolletsJoined.update({
				rolletId: getRolletInstanceByRolletId(int(rolletId)).getJSON()
			}) for rolletId in loads(rollets).keys()]

			context.update({
				'profile':{
					'ownProfile': userId == getUserId(),
					'username': username,
					'userWalletWin': wallet[0],
					'userWalletLose': wallet[1],
					'userRolletsJoined': userRolletsJoined,
				}
			})

			return renderTemplate('profile.html', context=context)
	return abort(404)


