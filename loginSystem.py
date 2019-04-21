import os

from flask import session, redirect, url_for

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from random import choice
from string import printable
from hashlib import sha1

from validationSystem import Validate
from api import message, takeMeHome

# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

class LoginSystem(Validate):
	"""docstring for LoginSystem"""
	def __init__(self):
		super(LoginSystem, self).__init__()
		self.username = None
		self.password =None
		self.email = None

	def __saltPassword__(self, length= 300):
		space = printable.split(' ')[0]
		return ''.join( [choice(space) for i in range(length)] )

	def __encryptPassword__(self, password, givenSalt=None):
		salt = givenSalt or self.__saltPassword__()
		password += salt
		password = password.encode('utf-8')
		encrypt = sha1( password )
		if givenSalt:
			return encrypt.hexdigest()
		return encrypt.hexdigest(), salt

	def __getdata__(self, form):
		self.username = form.get('username')
		self.password = form.get('password')
		self.email = form.get('email')

	def login(self, form={}):
		self.__getdata__(form)
		u = self.username
		p = self.password

		if self.instaUsername(u) and self.numInRange(len(p), mn=7, mx=60): 
			salt = db.execute('SELECT salt FROM users \
				WHERE username=:u;', {'u': u}
			)

			if salt.rowcount == 1:
				salt = salt.fetchone()[0]

				encryptedPass = self.__encryptPassword__(p, salt)
			
				user = db.execute('SELECT * FROM users \
					WHERE username=:u AND password=:p;', {'u': u, 'p': encryptedPass}
				)

				if user.rowcount == 1:
					id,username,email,password,salt,rollets = user.fetchone()			
					session['user'] = {
						'id': id,
						'email': email,
						'username': username,
						'rollets': rollets,
						'active': 1,
					}

					session['wallet'] = db.execute(
						'SELECT * FROM wallets \
						WHERE username=:u ;', {'u': u}
					).fetchone()

					return takeMeHome()

		message('not valid data', 'danger')
		return takeMeHome()

	def register(self, form={}):
		self.__getdata__(form)
		
		u = self.username
		e = self.email
		p = self.password

		## validate inputs
		if self.instaUsername(u) and self.eMail(e) and self.numInRange(len(p), mn=7, mx=60) and self.numInRange(len(u), mn=2, mx=60):
			p, salt = self.__encryptPassword__(p)

			## check if username or email are taken
			chkUnique = db.execute(
				"SELECT * FROM users \
				WHERE username=:u OR email=:e;",
				{'u': u, 'e': e}
			).fetchall()

			if len(chkUnique) == 0:
				db.execute("INSERT INTO wallets \
					(username) VALUES \
					(:u);", {'u': u}
				)

				db.execute("INSERT INTO users \
					(username, email, password, salt) VALUES \
					(:u, :e, :p, :s);", { 'u': u, 'e': e, 'p': p, 's': salt }
				)
				
				db.commit()
				return self.login(form)
		message('invalid data', 'danger failed')
		return takeMeHome()

	def logout(self):
		if session.get('user'):
			session.pop('user')
		return self.login()

