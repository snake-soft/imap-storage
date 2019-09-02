"""Address class"""
from email.headerregistry import Address as Addr

__all__ = ['Address']


class Address(Addr):
    """Represents addresses mainly for the Email header"""
    def __init__(self,  display_name='', addr_spec=None):
        if isinstance(display_name, tuple):
            display_name, addr_spec = display_name
        super().__init__(
            display_name=display_name if display_name else addr_spec,
            addr_spec=addr_spec
            )
