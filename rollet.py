from time import time
from random import choice, shuffle, randint
from math import ceil, floor

class Rollet:
	"""docstring for Rollet"""
	def __init__(self, howLong=0, ticket=0, percentOfWinners=0, json={}):
		super(Rollet, self).__init__()

		self.maxPercentOfWinning = 80

		self.startTime = time()
		self.howLong = howLong * 60 * 60 # second

		self.remainingSeconds = self.getRemainingSeconds()

		self.ticket = ticket
		self.percentOfWinners = percentOfWinners

		self.participants = []
		self.winners = []

		self.upNow = 1 ## valid to apply and this stuff
		self.closingTime = 7 * 60# min

		self.totalParticipants		= 0
		self.winnersNumber			= 0
		self.totalMoney				= 0
		self.everyWinnerTake		= 0
		self.winningRate			= 0
		self.tenPercent				= 0
		self.fivePercent			= 0
		self.websiteTake			= 0
		self.everyWinnerRealTake	= 0
		self.remainingMoney			= 0
		self.percentForWebsite		= 0
		self.websiteRealTake 		= 0

		self.db = None

		if self.percentOfWinners > self.maxPercentOfWinning:
			self.percentOfWinners = self.maxPercentOfWinning

		if json:
			self.__setJSON__(json)


		# self.__compute__()

	def __checkInputs__(self):
		pass

	def __compute__(self):
		self.totalParticipants		= len(self.participants)
		if self.totalParticipants:
			self.selectWinners()

			self.winnersNumber			= floor(self.percentOfWinners/100 * self.totalParticipants) or 1		
			self.totalMoney				= self.totalParticipants * self.ticket
			self.everyWinnerTake		= round(self.totalMoney/self.winnersNumber, 2)
			self.winningRate			= self.everyWinnerTake/self.ticket
			self.tenPercent				= self.totalMoney*10/100
			self.fivePercent			= self.totalMoney*5/100
			self.websiteTake			= sorted([self.fivePercent, self.everyWinnerTake, self.tenPercent])[1]
			self.everyWinnerRealTake	= round((self.totalMoney-self.websiteTake)/self.winnersNumber, 2)
			self.remainingMoney			= round(self.totalMoney - (self.everyWinnerRealTake * self.winnersNumber + self.websiteTake), 3)
			self.websiteRealTake		= self.websiteTake + self.remainingMoney
			self.percentForWebsite		= round(self.websiteRealTake/self.totalMoney * 100, 3)
			self.upNow					= 1 if self.startTime + self.howLong - time() > self.closingTime else 0

	def __setJSON__(self, json):
		self.startTime = json['startTime']
		self.howLong = json['howLong']
		self.ticket = json['ticket']
		self.percentOfWinners = json['percentOfWinners']
		self.participants = json['participants']
		self.winners = json['winners']

		self.db = json.get('db')

		self.__compute__()

	def addParticipant(self, userId):
		self.participants.append(userId)
		self.__compute__()

	def isTimeOver(self):
		return time() - self.startTime >= self.howLong

	def selectWinners(self):
		if self.isTimeOver():
			participants = self.participants.copy()
			for _ in range(randint(3,10+1)):
				shuffle(participants)

			while len(self.winners) < self.winnersNumber:
				winner = choice(participants)
				participants.remove(winner)
				self.winners.append(winner)

	def getRemainingSeconds(self):
		seconds = self.startTime + self.howLong - time()
		return seconds if seconds > 0 else 0

	def getJSON(self):
		return {
			'isTimeOver': self.isTimeOver(),
			'remainingSeconds': self.getRemainingSeconds(),
			'maxPercentOfWinning' : self.maxPercentOfWinning,
			'startTime' : self.startTime,
			'howLong' : self.howLong,
			'ticket' : self.ticket,
			'percentOfWinners' : self.percentOfWinners,
			'participants' : self.participants,
			'winners' : self.winners,
			'upNow' : self.upNow,
			'totalParticipants' : self.totalParticipants,
			'winnersNumber' : self.winnersNumber,
			'totalMoney' : self.totalMoney,
			'everyWinnerTake' : self.everyWinnerTake,
			'winningRate' : self.winningRate,
			'tenPercent' : self.tenPercent,
			'fivePercent' : self.fivePercent,
			'websiteTake' : self.websiteTake,
			'everyWinnerRealTake' : self.everyWinnerRealTake,
			'remainingMoney' : self.remainingMoney,
			'percentForWebsite' : self.percentForWebsite,
			'websiteRealTake' : self.websiteRealTake ,
			'db': self.db,
		}
