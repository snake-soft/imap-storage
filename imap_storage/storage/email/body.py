"""Body class"""
from lxml import etree as ET


class Body:
    """This class represents the Email body without physical attachments"""
    def __init__(self, xml_str):
        # self.email = email
        parser = ET.XMLParser(remove_blank_text=True)
        self.xml = ET.fromstring(xml_str, parser) if xml_str else None

    def new(self, tag='container'):
        """Create new Email body
        :param tag: Tag of the main node
        :returns: self
        """
        self.xml = ET.Element(tag)
        self.xml.attrib['id'] = self.new_id()
        return self

    def get_by_tag(self, tag):
        """Get xml item by tag
        :param tag: Tag to return
        :returns: List of tag items
        """
        return self.xml.xpath('//{}'.format(tag))

    def add_item(self, tag, text=None, attribs=None, parent=None):
        """Add new Child to body or some other parent
        :param tag: Tag name of the new item
        :param text: Text content of the new item
        :param attribs: Dictionary!!! {'attribname': 'attribvalue'}
        :returns: reference to new item
        """
        attribs = {str(k): str(v) for k, v in attribs.items()
                   } if attribs else {}
        attribs['id'] = self.new_id()
        if parent is not None:
            child = ET.SubElement(parent, tag, attribs)
        else:
            child = ET.SubElement(self.xml, tag, attribs)
        if text:
            child.text = text
        return child

    def remove_item(self, id_):
        """remove item from body
        :param id_: Id of the item to remove
        """
        for bad in self.xml.xpath("//*[@id=\'{}\']".format(id_)):
            bad.getparent().remove(bad)

    @staticmethod
    def new_id(count=8):
        """Creates Unique ID
        :param count: Number of letters the id should have
        :returns: new uid
        """
        from random import randint
        from string import ascii_letters, digits
        pcs = ascii_letters + digits
        randint(0, len(pcs))
        return ''.join([pcs[randint(0, len(pcs) - 1)] for _ in range(count)])

    def __str__(self):
        return ET.tostring(self.xml, pretty_print=True).decode()
