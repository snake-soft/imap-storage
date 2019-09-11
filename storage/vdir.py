class Vdir:

    def __init__(self, tag, name):
        self.tag = tag
        self.name = name

    @classmethod
    def set_class_tag(cls, tag):
        cls.TAG = tag

    def __hash__(self):
        return hash((self.tag, self.name))

    def __eq__(self, other):
        #import pdb; pdb.set_trace()  # <---------
        # isinstance
        return self.name == other.name

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not self == other

    def __str__(self):
        return self.name
