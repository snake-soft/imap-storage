class Vdir:
    TAG = None

    def __init__(self, subject):
        self.subject = subject

    @classmethod
    def set_class_tag(cls, tag):
        cls.TAG = tag

    def __hash__(self):
        return hash(self.subject)

    def __eq__(self, other):
        import pdb; pdb.set_trace()  # <---------
        # isinstance
        return self.subject == other.subject

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not self == other
