from pymongo import MongoClient
import os


class InitializeDb:
    def __init__(self, dbname):
        self._dbname = dbname

        if os.environ.get('MONGODB_URI') is None:
            mongodb = 'mongodb://localhost:27017'
        else:
            mongodb = os.environ.get('MONGODB_URI')
            if os.environ.get('ENV') == 'HEROKU':
                self._dbname = mongodb.rsplit('/', 1)[1]

        self.client = MongoClient(mongodb)
        self.collections = self.client[self._dbname]
        self.group_collection = self.collections.groups
        self.command_collection = self.collections.commands
