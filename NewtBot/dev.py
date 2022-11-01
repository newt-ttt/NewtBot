import discord


class statuses:
    
    def __init__(self, user, is_dev, is_cursed):
        self.user = user
        self.is_dev = is_dev
        self.is_cursed = is_cursed
        
    def get_statuses(self, devlist):
     
        
        

dev = statuses(222466490216087552, True, True)
file = "data\status_list.txt"
dev.get_statuses(file)

print