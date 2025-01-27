import xml.etree.ElementTree as ET
from src.Synthetic_document_pipeline.content_generator.content_src.blocks.block import Block
from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import TYPESDICT

class XMLParser():
    def __init__(self, document) -> None:
        """
        document is the file.xml
        """
        self.root = ET.parse(document)
    
    def get_blocks(self):
        for page in self.root:
            for item in page:
                yield Block.from_content(item)
    
    def generate_blocks_xml(modules: list, xml_fullpath:str):
        doc = ET.Element("doc")
        for module in modules:
            name = module.__class__.__name__.lower()
            mod = ET.SubElement(doc, "module", name=name, 
                                x0=str(module.coords.x0), x1=str(module.coords.x1), 
                                y0=str(module.coords.y0), y1=str(module.coords.y1))
            for [x0, x1, y0, y1], bsubtype in module.blocks:
                btype = TYPESDICT.get(bsubtype, '')
                ET.SubElement(mod, "block", type=btype, subtype=bsubtype, 
                            x0=str(x0), x1=str(x1), y0=str(y0), y1=str(y1))
        tree = ET.ElementTree(doc)
        tree.write(xml_fullpath)
        return xml_fullpath