from re import match

class Validate:
	def __init__(self):
		super(Validate, self).__init__()

	def __x(self, pattern, string):
		if string:
			return True if match(pattern, string) else False
	
	def eMail(self, string):
		pattern = r'(^[\w\.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
		return self.__x(pattern, string)

	def instaUsername(self, string):
		pattern = r'(^[\w\.]+$)'
		return self.__x(pattern, string)

	def integer(self, num):
		try:
			num = float(num)
			return num.is_integer()
		except: return False

	def numInRange(self, num, mn, mx):
		return mn <= num <= mx
