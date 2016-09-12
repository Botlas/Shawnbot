import csv

class Quotes:
    _instance = None
    quote_list = {}
    
    def load_config(self, quote_path):
        with open(quote_path, 'rb') as csvfile:
            quotes = csv.reader(csvfile)
            for row in quotes:
                if row[0] not in self.quote_list:
                    self.quote_list[row[0]] = []
                self.quote_list[row[0]].append(row[1])
                
        Quotes._instance = self
        
    @staticmethod
    def get():
        return Quotes._instance