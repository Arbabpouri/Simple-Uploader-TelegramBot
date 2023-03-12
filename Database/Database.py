from json import dumps
from os import path

if not path.exists('Database/Config.json'):
    Dt = {
    "Admins": [],"ChannelsID": [],"ChannelsLink": [],"Users": [],"Post": [],"PostChannel": -1001820187992
    }
    open('Database/Config.json','a+').write(dumps(Dt,indent=4))
    Dt = None

class Database(object): 
    def __init__(self,UserID = '',PostID = '',ChannelID = '',ChannelLink = '',Select = '',Data = ''):
        self.UserID = UserID
        self.PostID = PostID
        self.ChannelID = ChannelID
        self.ChannelLink = ChannelLink
        self.Select = Select
        self.Data = Data

    def RefreshUser(self):
        if self.UserID not in self.Data['Users']:
            self.Data['Users'].append(self.UserID)
            File = open('Database/Config.json','w')
            File.write(dumps(self.Data,indent=4))
            File.close()

    def RefreshAdmin(self):
        if (self.Select).lower() == 'add':
            self.Data['Admins'].append(int(self.UserID))
            File = open('Database/Config.json','w')
            File.write(dumps(self.Data,indent=4))
            File.close()
        elif (self.Select).lower() == 'remove':
            self.Data['Admins'].remove(self.UserID)
            File = open('Database/Config.json','w')
            File.write(dumps(self.Data,indent=4))
            File.close()

    def RefreshChannel(self):
        if (self.Select).lower() == 'add':
            self.Data['ChannelsID'].append(self.ChannelID)
            self.Data['ChannelsLink'].append(self.ChannelLink)
            File = open('Database/Config.json','w')
            File.write(dumps(self.Data,indent=4))
            File.close()
        elif (self.Select).lower() == 'remove':
            self.Data['ChannelsID'].remove(self.ChannelID)
            self.Data['ChannelsLink'].remove(self.ChannelLink)
            File = open('Database/Config.json', 'w')
            File.write(dumps(self.Data, indent=4))
            File.close()

    def RefreshPost(self):
        if (self.Select).lower() == 'add':
            self.Data['Post'].append(self.PostID)
            File = open('Database/Config.json','w')
            File.write(dumps(self.Data,indent=4))
            File.close()
        elif (self.Select).lower() == 'remove':
            self.Data['Post'].remove(self.PostID)
            File = open('Database/Config.json', 'w')
            File.write(dumps(self.Data, indent=4))
            File.close()