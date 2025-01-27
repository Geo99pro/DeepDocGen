from random import randint, choice, random
import math
from src.Synthetic_document_pipeline.content_generator.content_src.blocks.block import Block
from src.Synthetic_document_pipeline.content_generator.content_src.config.color import Color
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config, TextData
from src.Synthetic_document_pipeline.content_generator.content_src.config.enums import Subtypes
from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import TITLE_TYPES
from src.Synthetic_document_pipeline.content_generator.content_src.config.textconfig import TextConfig
from src.Synthetic_document_pipeline.content_generator.content_src.document import Document
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import random_number
from src.Synthetic_document_pipeline.content_generator.content_src.utils.text_utils import request_words, int2roman


class TextBlock(Block):
    def __init__(self, x0, x1, y0, y1, subtype, **kwargs):
        super().__init__(x0, x1, y0, y1, 'text', subtype)
        self.subtype_enum = Subtypes[subtype.upper()]
    
    def __str__(self):
        values = ""
        values += f"x0: {self.x0}\t"
        values += f"x1: {self.x1}\t"
        values += f"y0: {self.y0}\t"
        values += f"y1: {self.y1}\t"
        values += f"width: {self.width}\t"
        values += f"height: {self.height}\t"
        return values

    def draw(self, image: Document, text_data: TextData = None, font='arial', save_blocks=False,):
        # iniciando valores
        doc_coords = self * image.size
        self.text_dictionary = {}
        self.list_items = 1
        self.indentation = False
        if text_data is None:
            text_data = Config.text
        text_config = TextConfig(self.subtype, font=font, modifiers="regular", block_height=doc_coords.height)

        
        # seleciona um espaço entre linhas 
        spacing = random_number(Config.text.random_space, ndigits=2)
        # para não ter muito espaço entre linhas nos titulos
        if self.subtype in TITLE_TYPES:
            spacing /= 2
        
        # define alguns valores e marcadores quando é lista
        indentation_space, indentation_end_space, doc_coords.x0, doc_coords.x1, align = self.init_list_markers(image, text_config, doc_coords)
        
        # cria um diccionario com as linhas do texto
        text_dictionary = self.get_words_per_line(self.subtype, image.draw, text_config.font, text_config.line_height, doc_coords.width, 
                                            doc_coords.y1, doc_coords.y0, spacing, doc_coords)
        
        
        #print(type(text_dictionary))
        #print(text_dictionary)
        #for k, v in text_dictionary.items():
        #   print(k, v)
        # modifica a ultima linha para terminar em um lugar aleatorio e acrescentar um .
        if len(text_dictionary) > 0:

            key_last_line = list(text_dictionary)[-1]
            #print(f'The key_last_line is {key_last_line}')

            if len(text_dictionary) > 1:
                text_dictionary[key_last_line] = self.process_last_line(text_dictionary[key_last_line])
                if self.subtype == "list" and self.list_with_page_at_end:
                    text_dictionary[key_last_line] = self.fill_line_with_symbol_and_number(text_dictionary[key_last_line], image.draw, text_config.font, doc_coords.width)


            # ajusta a coordenada do Y0 para cada linha para não deixar espaços em branco no final 
            text_dictionary = self.fit_y0_line(doc_coords, text_dictionary, text_config, key_last_line, spacing)

        # adiciona o texto no documento
        for key, line_dictionary in text_dictionary.items():
            if self.subtype == 'title':
                line_dictionary["text"] = line_dictionary["text"].upper() # convert the text to uppercase
                #check if the text comes out of the box and then remove any characters that exceed the width of the box
                text_width = image.draw.textbbox((0,0), line_dictionary["text"], text_config.font)[2] - image.draw.textbbox((0,0), line_dictionary["text"], text_config.font)[0]

                while text_width > doc_coords.width:
                    if not line_dictionary["text"]:
                        break
                    line_dictionary["text"] = line_dictionary["text"][:-1]
                    text_width = image.draw.textbbox((0,0), line_dictionary["text"], text_config.font)[2] - image.draw.textbbox((0,0), line_dictionary["text"], text_config.font)[0]
                    
                self.text_dictionary[key] = self.draw_text(line_dictionary, doc_coords.x0, text_config, align, key, key_last_line, doc_coords.width, image.draw, indentation_space)
            self.text_dictionary[key] = self.draw_text(line_dictionary, doc_coords.x0, text_config, align, key, key_last_line, doc_coords.width, image.draw, indentation_space)
            image.draw.rectangle(self.text_dictionary[key]["box"],  width=1)
        if save_blocks:
            box = (doc_coords.x0-indentation_space, doc_coords.y0, doc_coords.x1, doc_coords.y1)
            color = Color.from_subtype(self.subtype)
            image.draw.rectangle(box, outline=color.outline, width=1)
        return self

    def fit_y0_line(self, doc_coords, text_dictionary, text_config, key_last_line, spacing):
        # adjust "y" lines positions
        block_height = doc_coords.y1 - doc_coords.y0
        total_lines = len(text_dictionary)
        line_height = text_config.line_height
        spacing = spacing*line_height
        excess_height = block_height - (total_lines*(spacing+line_height)) + spacing - 1
        excess_height_per_line = excess_height / (total_lines-1) if total_lines > 1 else 0

        
        
        if self.subtype == "list" and self.list_items > 1:
            excess_height_per_item = excess_height / (self.list_items-1) if self.list_items > 1 else 0
            items_counter = 0
            for key, line_dictionary in text_dictionary.items():
                if text_dictionary[key]["last_line"]:
                    items_counter += 1
                if key != key_last_line:
                    text_dictionary[key+1]["y0"] = text_dictionary[key+1]["y0"] + (items_counter*excess_height_per_item)

        else:
            for key, line_dictionary in text_dictionary.items():
                text_dictionary[key]["y0"] = text_dictionary[key]["y0"] + (int(key)*excess_height_per_line)

        
        ######################################################
        return text_dictionary

    def fill_line_with_symbol_and_number(self, line_dictionary, draw, font, max_width):
        """
        esse método prenche a linha final das listas com "_", "-", "." ou " " para colocar o númeor de pagina no final 
        """
        line = line_dictionary["text"]
        pag_number = str(randint(1,300))
        
        # se o tamanho da linha mais o número de pagina já é maior que o width do bb escolhe um número menor
        #if draw.textsize(line + self.separate_symbol + self.end_symbol + " " + pag_number, font)[0] > max_width:
        if (draw.textbbox((0,0), line + self.separate_symbol + self.end_symbol + " " + pag_number, font)[2] - draw.textbbox((0,0), line + self.separate_symbol + self.end_symbol + " " + pag_number, font)[0]) > max_width:
            pag_number = str(randint(1,9))
            # se o tamanho da linha mais o número de pagina já é maior que o width do bb tem que verificar de onde vem o erro,
            #if draw.textsize(line + self.separate_symbol + " " + pag_number, font)[0] > max_width:
            if (draw.textbbox((0,0), line + self.separate_symbol + " " + pag_number, font)[2] - draw.textbbox((0,0), line + self.separate_symbol + " " + pag_number, font)[0]) > max_width:
                raise Exception("erro colocando numero no final do item da lista\n")
        else:
            # se o número de pagina vai estar entre (), [] ou {}
            if len(self.end_symbol) == 2:
                end_line = " " + self.end_symbol[0] + pag_number + self.end_symbol[1]
                #while draw.textsize(line + self.separate_symbol + end_line, font)[0] < max_width:
                while (draw.textbbox((0,0), line + self.separate_symbol + end_line, font)[2] - draw.textbbox((0,0), line + self.separate_symbol + end_line, font)[0]) < max_width:
                    line += self.separate_symbol
                line_dictionary["text"] = line + end_line
            # se o número de pagina vai estar só
            else:
                end_line = " " + pag_number
                #while draw.textsize(line + self.separate_symbol + end_line, font)[0] < max_width:
                while (draw.textbbox((0,0), line + self.separate_symbol + end_line, font)[2] - draw.textbbox((0,0), line + self.separate_symbol + end_line, font)[0]) < max_width:
                    line += self.separate_symbol
                line_dictionary["text"] = line + end_line

        return line_dictionary
    



    def get_words_per_line(self, subtype, draw, font, line_height, max_width, max_y1, start_y0, spacing, doc_coords, max_chars=None):
        spacing = spacing*line_height
        block_height = max_y1-start_y0
        total_lines = round(((block_height-line_height) / (spacing+line_height))+1)
        line_y0 = start_y0
        words, i = request_words()
        #print(words)
        text_dictionary = {}
        item_list_lines, current_item_list_lines = self.set_item_list_lines()
        while len(text_dictionary) < total_lines and line_y0 < max_y1:
            if len(text_dictionary) < 1:
                isfixed, line = self.set_line_start()
            else:
                isfixed, line = False, ""
            if subtype == "list" and current_item_list_lines == item_list_lines:
                text_dictionary[len(text_dictionary)-1] = self.process_last_line(text_dictionary[len(text_dictionary)-1])
                if self.list_with_page_at_end:
                    text_dictionary[len(text_dictionary)-1] = self.fill_line_with_symbol_and_number(text_dictionary[len(text_dictionary)-1], draw, font, max_width)
                isfixed, line = self.set_line_start()
                item_list_lines, current_item_list_lines = self.set_item_list_lines()
                self.list_items += 1
                words, i = request_words()

            if isfixed:
                text_dictionary[len(text_dictionary)] = {"text": line,
                                                        "y0": line_y0,
                                                        "last_line": False, 
                                                        "bullet_out_of_line": ""}
                break
            line, i, words, bullet_out_of_line = self.get_words_for_line(draw, font, line, max_width, max_chars, i, words, line_y0, line_height, max_y1)

            text_dictionary[len(text_dictionary)] = {"text": line,
                                                    "y0": line_y0,
                                                    "last_line": False, 
                                                    "bullet_out_of_line": bullet_out_of_line}
            current_item_list_lines += 1
            line_y0 += line_height + spacing
        return text_dictionary

    """(this is the original code) def get_words_per_line(self, subtype, draw, font, line_height, max_width, max_y1, start_y0, spacing, max_chars=None):
        spacing = spacing*line_height
        block_height = max_y1-start_y0
        total_lines = round(((block_height-line_height) / (spacing+line_height))+1)
        line_y0 = start_y0
        words, i = request_words()
        print(words)
        text_dictionary = {}
        item_list_lines, current_item_list_lines = self.set_item_list_lines()
        while len(text_dictionary) < total_lines and line_y0 < max_y1:
            if len(text_dictionary) < 1:
                isfixed, line = self.set_line_start()
            else:
                isfixed, line = False, ""
            if subtype == "list" and current_item_list_lines == item_list_lines:
                text_dictionary[len(text_dictionary)-1] = self.process_last_line(text_dictionary[len(text_dictionary)-1])
                if self.list_with_page_at_end:
                    text_dictionary[len(text_dictionary)-1] = self.fill_line_with_symbol_and_number(text_dictionary[len(text_dictionary)-1], draw, font, max_width)
                isfixed, line = self.set_line_start()
                item_list_lines, current_item_list_lines = self.set_item_list_lines()
                self.list_items += 1
                words, i = request_words()

            if isfixed:
                text_dictionary[len(text_dictionary)] = {"text": line,
                                                         "y0": line_y0,
                                                         "last_line": False, 
                                                         "bullet_out_of_line": ""}
                break
            line, i, words, bullet_out_of_line = self.get_words_for_line(draw, font, line, max_width, max_chars, i, words, line_y0, line_height, max_y1)

            text_dictionary[len(text_dictionary)] = {"text": line,
                                                    "y0": line_y0,
                                                    "last_line": False, 
                                                    "bullet_out_of_line": bullet_out_of_line}
            current_item_list_lines += 1
            line_y0 += line_height + spacing
        return text_dictionary"""

    def get_words_for_line(self, draw, font, line, max_width, max_chars, i, words, line_y0, line_height, max_y1):
        ### for list
        bullet_out_of_line = ""
        if self.indentation:
            bullet_out_of_line = line
            line = ""

        while font.getlength(line) < max_width or (max_chars is not None and len(line) < max_chars):
            if i >= len(words):
                if line_y0 + line_height > max_y1: break
                words, i = request_words()
            word = words[i]
            if font.getlength(line + " " + word) > max_width:
                if self.subtype in ["title", "subtitle", "subsubtitle", "subsubsubtitle"]:
                    while font.getlength(line + " " + word) > max_width:
                        word = word[:-1]
                        if len(word) == 0: break
                else:
                    break
            i += 1
            line += word if line == "" else " " + word
        return line, i, words, bullet_out_of_line

    def set_item_list_lines(self):
        if random()<0.7:
            return randint(1,3), 0
        else:
            return randint(4,6), 0
    
    def set_line_start(self):
        subtype = Subtypes[self.subtype.upper()]
        fixed_text = False
        if subtype == Subtypes.PAGENUMBER:
            line_start = str(randint(1, 3001))
            fixed_text = True
        elif subtype == Subtypes.TITLE:
            line_start = f"{randint(1,16)}."
        elif subtype == Subtypes.SUBTITLE:
            line_start = f"{randint(1, 16)}.{randint(1, 16)}."
        elif subtype == Subtypes.SUBSUBTITLE:
            line_start = f"{randint(1, 16)}.{randint(1, 16)}.{randint(1, 16)}."
        elif subtype == Subtypes.LIST:
            if self.marker_type == "symbol":
                line_start = " " + self.bullet + " "
            else:
                line_start = " " + self.bullet[0] + str(self.index_list_counter) + self.bullet[1] + " "
                self.index_list_counter += 1
        else:
            line_start = ""
        return fixed_text, line_start
    
    def justify_line_with_spaces(self, draw, font, line, width, x0, y0):
        words = line.split()
        if len(words) > 1:
            line_list = [words[0]]
            for word in words[1:]:
                line_list.extend([" ", word])

            #original_space = draw.textsize(line, font)[0]
            original_space = draw.textbbox((0,0), line, font)[2] - draw.textbbox((0,0), line, font)[0]
            spare_space = width - original_space - 0
            #space_width = draw.textsize(" ", font)[0]
            space_width = draw.textbbox((0,0), " ", font)[2] - draw.textbbox((0,0), " ", font)[0]
            spaces_quantity = int(spare_space/space_width)
            index_to_append_space = 1
            for i in range(spaces_quantity):
                line_list[index_to_append_space] += " "
                index_to_append_space += 2
                if index_to_append_space >= len(line_list):
                    index_to_append_space = 1
            line = ''.join(line_list)

        return line

    def process_last_line(self, line_dictionary):
        """
        function to process the last line of the paragraph and cut it at a random place and end with a dot
        """
        line = line_dictionary["text"]
        if self.subtype == "list":
            words = line.split()
            if len(words)==1:
                line = ' '.join(words)+"."
            elif len(words) <= 4:
                line = ' '.join(words[:2])+"."
            elif len(words) >4:
                words_to_take = randint(2, len(words)-3)
                line = ' '.join(words[:words_to_take])+"."
        else:
            # cut the line at random word and put a "."
            words = line.split()
            #print(type(words))
            if len(words)>2:
                words_to_take = randint(2, len(words)-1)
                #dico = {"word_1": "hello", "word_2": "content generator", "word_3": "depois", "word_4": "durante", "word_5": "fim da semana", "word_6": "igreja"}
                #selected_words_from_dico=[]
                #for _ in range(min(words_to_take, len(dico))):
                  #  selected_words_from_dico.append(choice([v for v in dico.values()]))
                #for _, value in enumerate(selected_words_from_dico):
                   # words.append(value)
                line= ' '.join(words)+"."
                #print(str(line))  
                
                #print(font.getlength(line))
                #line= words+ ' '.join(selected_words_from_dico)+"."
                
                #line = ' '.join(words[:words_to_take])+"."
                #print(type(line))
                #print(line)

        while line[-2:-1] in [".", ",", ":", ";", "_"]:
            line = line[:-2] + "."
        line_dictionary["text"] = line
        line_dictionary["last_line"] = True
        return line_dictionary
        
    def set_x0_by_align(self, align, doc_x0, doc_width, draw, font, line):
        if align == "left":
            x0 = doc_x0

        elif align == "right":
            x0 = doc_x0 + doc_width - draw.textsize(line, font)[0]
            if x0<doc_x0:
                x0=doc_x0
        elif align == "center":
            x0 = doc_x0 + (doc_width - draw.textsize(line, font)[0])/2

            if x0<doc_x0:
                x0=doc_x0
        return int(x0)

    def draw_text(self, line_dictionary, x0, text_config, align, key, key_last_line, width_block, draw, indentation_space):
        y0 = line_dictionary["y0"]
        line = line_dictionary["text"]
        align= 'justify'

        if align == "justify":
            if key != key_last_line and line_dictionary["last_line"] == False:
                line = self.justify_line_with_spaces(draw, text_config.font, line, width_block, x0, y0)
        elif align in ["left", "right", "center"]:
            x0 = self.set_x0_by_align(align, x0, width_block, draw, text_config.font, line)
        
        draw.text((x0, y0), line, font=text_config.font, fill='black', align='center')

        if line_dictionary["bullet_out_of_line"] != "":
            x0 = x0 - indentation_space
            draw.text((x0, y0), line_dictionary["bullet_out_of_line"], font=text_config.font, fill='black', align='center')
        #line_width = draw.textsize(line, text_config.font)[0]
        line_width = draw.textbbox((0,0), line, font=text_config.font)
        line_width = line_width[2] - line_width[0]
        
        # fill line_dictionary
        line_dictionary["x0"] = int(x0)
        if line_dictionary["bullet_out_of_line"] != "":
            line_dictionary["x1"] = round(x0+line_width+indentation_space)
        else:
            line_dictionary["x1"] = round(x0+line_width)
        line_dictionary["y0"] = round(y0)
        line_dictionary["y1"] = round(y0+text_config.line_height)

        line_dictionary["box"] = (line_dictionary["x0"], line_dictionary["y0"], line_dictionary["x1"], line_dictionary["y1"])

        return line_dictionary

    def init_list_markers(self, image, text_config, doc_coords):
        indentation_space = 0
        indentation_end_space = 0
        self.indentation_end = False
        self.list_with_page_at_end = False
        self.indentation = False


        align = choice(["left", "right", "center", "justify"]) if self.subtype not in ["list", "title", "subtitle", "subsubtitle", "subsubsubtitle"] else choice(["left", "justify"])

        if self.subtype == "list":
            # iniciar marcador 
            self.marker_type = choice(["numeric", "symbol"])
            if self.marker_type == "symbol":
                bullets = ["+", "-", "*", "°", "•"]
                self.bullet = choice(bullets)
            else:
                bullets = ["[]", "()", "{}"]
                self.index_list_counter = 1
                self.bullet = choice(bullets)
            
            self.indentation = choice([False, True])

            if self.indentation:
                if self.marker_type == "symbol":
                    #indentation_space = image.draw.textsize("    " + self.bullet, text_config.font)[0]
                    indentation_space = image.draw.textbbox((0,0), "    " + self.bullet, text_config.font)[2] - image.draw.textbbox((0,0), "    " + self.bullet, text_config.font)[0]
                else:
                    #indentation_space = image.draw.textsize("  99  " + self.bullet, text_config.font)[0]
                    indentation_space = image.draw.textbbox((0,0), "  99  " + self.bullet, text_config.font)[2] - image.draw.textbbox((0,0), "  99  " + self.bullet, text_config.font)[0]

                doc_coords.x0 += indentation_space
            
            # iniciar final do item
            indentation_end_space = 0
            self.list_with_page_at_end = choice([False, True, False])
            if self.list_with_page_at_end:
                self.separate_symbol = choice([".", "_", "-", " ", " "])
                self.end_symbol = choice(["[]", "()", "{}"]) if random() > 0.5 else ""
                self.indentation_end = choice([False, True])
                self.indentation_end = False

                if self.indentation_end:
                    if self.end_symbol != "":
                        indentation_end_space = image.draw.textsize(" 999" + self.end_symbol, text_config.font)[0]
                    else:
                        indentation_end_space = image.draw.textsize(" 999", text_config.font)[0]

                    doc_coords.x1 -= indentation_end_space
        
        return indentation_space, indentation_end_space, doc_coords.x0, doc_coords.x1, align
