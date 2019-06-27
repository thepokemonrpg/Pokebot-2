import pokepy
from pokemon import BadArgumentError

client = pokepy.V2Client()

class Item:
    def __init__(self, **kwargs):
        if kwargs.get("item_id").isdigit():
            self.item = client.get_item(kwargs.get("item_id"))
            self.item_name = self.item.name
        else:
            raise BadArgumentError("Invalid arguments passed on")

        if kwargs.get("item_name") is str:
            self.item_name = kwargs.get("item_name")

        self.item_cost = self.item.cost

    def get_id(self):
        return self.item.id

    def get_name(self):
        return self.item.item_name

    def get_cost(self):
        return self.item.item_cost










