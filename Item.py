import pokepy
from pokemon import BadArgumentError

client = pokepy.V2Client()


class Item:
    def __init__(self, **kwargs):
        self.cost = 0
        self.desc = ""
        self.name = ""
        self.amount = 1

        if kwargs.get("amount"):
            self.amount = kwargs.get("amount")

        if kwargs.get("description"):
            self.desc = kwargs.get("description")

        if kwargs.get("cost") and kwargs.get("cost").isdigit():
            self.cost = int(kwargs.get("cost"))

        if kwargs.get("name"):
            self.name = kwargs.get("name")

    def get_name(self):
        return self.name

    def get_cost(self):
        return self.cost

    def get_description(self):
        return self.desc

    def get_amount(self):
        return self.amount
