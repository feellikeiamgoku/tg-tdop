class ValidationError(Exception):
	pass


class LimiterError(Exception):
	pass


class RunningContextError(Exception):
	pass


class UnknownType(Exception):
	def __init__(self, instance):
		msg = f'Got unknown type {type(instance)}.'
		super().__init__(msg)
