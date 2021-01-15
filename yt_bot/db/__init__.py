from yt_bot.db.initialize import Initializer
from yt_bot.db.tables import ProcessedTable

# Register tables to create on bot start up

initializer = Initializer()
initializer.register(ProcessedTable)