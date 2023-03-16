class Container:
    def __init__(self, number, weight, origin, storage, merchandise):
        self.number = number
        self.place_stored = storage
        self.weight = weight
        self.origin = origin
        self.merchandise = merchandise
        # self.destination = random.choice(["China", "USA", "Germany", "France", "Italy", "Spain", "UK", "Japan", "India"])

    def explode(self):
        self.number = self.number
        print("Nothing will happen...")

    
