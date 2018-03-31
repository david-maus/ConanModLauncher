from lxml import html
import json
import requests
import re


class getSteamModsFromCollection(object):
    def __init__(self, CollectionID):
        self.CollectionID = CollectionID

    def getCollectionInfo(self):

        data = [
          ('collectioncount', '1'),
          ('publishedfileids[0]', self.CollectionID)
        ]

        response = requests.post('https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/', data=data)
        data = response.json()

        self.modItemsArray = []
        self.modListMatrix = []

        i = 0
        try:
            while data["response"]["collectiondetails"][0]["children"][i]:
                self.modItemNr = data["response"]["collectiondetails"][0]["children"][i]["publishedfileid"]

                # self.modItemsArray.append(self.modItemNr)
                # self.modItemsArray.append(self.getModName(self.modItemNr))

                self.modListMatrix.append([self.modItemNr, self.getModName(self.modItemNr)])

                i = i + 1
        except:
            pass

        return self.modListMatrix

    def getModName(self, modItemNr):

        page = requests.get('http://steamcommunity.com/sharedfiles/filedetails/?id=' + self.modItemNr)
        tree = html.fromstring(page.content)
        self.workShopItemName = tree.xpath('//div[@class="workshopItemTitle"]/text()')
        self.workShopItemName = ''.join(self.workShopItemName)

        return self.workShopItemName

    def getConnectionInfo(self):

        page = requests.get('http://steamcommunity.com/sharedfiles/filedetails/?id=' + self.CollectionID)
        tree = html.fromstring(page.content)
        self.ServerAdress = tree.xpath('//*[contains(text(), "CMLCONNECT:")]/text()')
        self.ServerAdress = ''.join(self.ServerAdress)
        self.ServerAdress = self.ServerAdress.replace('CMLCONNECT: ', '')
        self.ServerAdress = self.ServerAdress.strip()
        return self.ServerAdress
