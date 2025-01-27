from src.Synthetic_document_pipeline.content_generator.content_src.blocks.coords import Coords
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Size
from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import SUBTYPECOLOR, TYPESDICT

class Block(Coords):
    x0: float
    x1: float
    y0: float
    y1: float

    def __init__(self, x0, x1, y0, y1, type, subtype):
        super().__init__(x0, x1, y0, y1)
        self.subtype = subtype
        self._type = type
    
    def __mul__(self, other):
        """This function returns a new object of type block by applying the {*} operator after checking whether the specified object is a coordinate or a size.
        Args : 
        other : must be a new instantiation of the object block
        """
        if isinstance(other, Coords):
            return self.__class__(other.x0*self.x0, other.x1*self.x1, other.y0*self.y0, other.y1*self.y1, type=self.type, subtype=self.subtype)
        if isinstance(other, Size):
            return self.__class__(other.width*self.x0, 
                                other.width*self.x1, 
                                other.height*self.y0, 
                                other.height*self.y1, type=self.type, subtype=self.subtype)
        
    @classmethod
    def from_coords(cls, coords:Coords, type=None, subtype=None):
        if type is None:
            type = TYPESDICT.get(subtype)

        return cls(coords.x0, coords.x1, coords.y0, coords.y1, type=type, subtype=subtype)
    
    @classmethod
    def from_content(cls, item):
        return cls(item.attrib['x0'], item.attrib['x1'], 
                    item.attrib['y0'], item.attrib['y1'], 
                    item.attrib['type'], item.attrib['subtype'])

    @property 
    def type(self):
        return self._type if self._type is not None else TYPESDICT.get(self.subtype, '')
    
    @property
    def color(self):
        return SUBTYPECOLOR.get(self.subtype)

    def __round__(self, ndigits=None):
        return self.__class__(round(self.x0, ndigits), 
                            round(self.x1, ndigits), 
                            round(self.y0, ndigits), 
                            round(self.y1, ndigits), type=self.type, subtype=self.subtype)
    
    def to_list(self):
        return [self.x0, self.y0, self.x1, self.y1, self.subtype]

        

