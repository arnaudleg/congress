#Copyright 2014 Plexxi, Inc.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import logging


class dataObject(object):
    def __init__(self, data={}, version=0):
        self.data = data
        if version:
            self.version = version
        else:
            self.version = int(bool(data))


class subData(object):
    def __init__(self, key, dataindex, corrId, callback):
        self.key = key
        self.dataindex = dataindex
        self.corrId = corrId
        self.callback = callback
        self.dataObjects = {}
        logging.info(
            "*****New subdata: %s, %s, %s"
            % (key, dataindex, str(id(self.dataObjects))))

    def getSources(self):
        return self.dataObjects.keys()

    def update(self, sender, newdata):
        self.dataObjects[sender] = newdata

    def version(self, sender):
        version = 0

        if sender in self.dataObjects:
            version = self.dataObjects[sender].version

        return version

    def getData(self, sender):
        result = dataObject()

        if sender in self.dataObjects:
            logging.info("subdata object: %s", self.dataObjects[sender])
            result = self.dataObjects[sender]

        return result

    def getAllData(self):
        result = {}
        for sender in self.dataObjects:
            result[sender] = self.dataObjects[sender]

        return result


class pubData(object):
    def __init__(self, dataindex, args={}):
        self.dataindex = dataindex
        self.dataObject = dataObject()
        self.subscribers = {}
        self.requesters = {}
        self.args = args

    def update(self, newdata):
        version = self.dataObject.version + 1
        self.dataObject = dataObject(newdata, version)

    def get(self):
        return self.dataObject

    def version(self):
        return self.dataObject.version

    def addsubscriber(self, sender, type, corrId):
        if sender not in self.subscribers:
            self.subscribers[sender] = {}
            self.subscribers[sender]['type'] = type
            self.subscribers[sender]['correlationId'] = corrId

    def removesubscriber(self, sender):
        if sender in self.subscribers:
            del self.subscribers[sender]

    def getsubscribers(self, sender=""):
        if sender:
            if sender in self.subscribers:
                return self.subscribers[sender]
        else:
            return self.subscribers
