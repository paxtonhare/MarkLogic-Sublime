class mlErrorGlobalStore:
	errors = []

	@classmethod
	def reset(self):
		mlErrorGlobalStore.errors = []