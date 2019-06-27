import pokepy
from pokemon import BadArgumentError

client = pokepy.V2Client()


class Item:
    def __init__(self, **kwargs):
        if kwargs.get("id").isdigit():
            self.item = client.get_item(kwargs.get("item_id"))
            self.name = self.item.name
        else:
            raise BadArgumentError("Invalid arguments passed on")

        if kwargs.get("name") is str:
            self.name = kwargs.get("item_name")

        self.item_cost = self.item.cost
        self.uses = False
        self.desc = ""

        if kwargs.get("cost"):
            self.cost = kwargs.get("cost")

        if kwargs.get("uses"):
            self.uses = kwargs.get("uses")

        if kwargs.get("description"):
            self.desc = kwargs.get("description")

    def get_id(self):
        return self.item.id

    def get_name(self):
        return self.name

    def get_cost(self):
        return self.cost

    def get_use(self):
        return self.uses

    def get_description(self):
        return self.desc
