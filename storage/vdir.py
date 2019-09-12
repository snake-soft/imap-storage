class Vdir:

    def __init__(self, subject):
        self.tag, self.subject = subject.split(' ', 1)

        splitted = self.subject.strip('/').split('/')
        self.app = splitted[0] if len(splitted) else '/'
        self.item = splitted[-1] if len(splitted) >= 2 else '/'
        self.path = '/'.join(splitted[1:-1]) if len(splitted) >= 3 else '/'

    @classmethod
    def set_class_tag(cls, tag):
        cls.TAG = tag

    def __hash__(self):
        return hash((self.tag, self.subject))

    def __lt__(self, other):
        return self.item < other.item

    def __eq__(self, other):
        #import pdb; pdb.set_trace()  # <---------
        # isinstance
        return self.subject == other.subject

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not self == other

    def __str__(self):
        return self.subject
