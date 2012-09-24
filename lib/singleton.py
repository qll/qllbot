
# http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/
class Singleton:
	""" A python singleton """

	class __impl:
		""" Implementation of the singleton interface """

		def spam(self):
			""" Test method, return singleton id """
			return id(self)

	# storage for the instance reference
	__instance = None

	def __init__(self):
		""" Create singleton instance """
		if Singleton.__instance is None:
			Singleton.__instance = Singleton.__impl()

		self.__dict__['_Singleton__instance'] = Singleton.__instance

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)
