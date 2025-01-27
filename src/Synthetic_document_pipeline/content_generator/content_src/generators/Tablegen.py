import sys
import os
import pandas as pd
import random, datetime, math

from xml.dom import minidom
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config
from src.Synthetic_document_pipeline.content_generator.content_src.utils.text_utils import generate_font, request_words, set_margins
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import rand_gauss, random_color
from PIL import Image, ImageDraw
sys.path.append('./')

"""
p0-------------p1
|               |
|               |
p3-------------p2


col_start, row_start = 0,0
col_end, row_end = 0,0
x0, y0, x1, y1, x2, y2, x3, y3 = 0,0,0,0,0,0,0,0

value_type = "str"
value_content = "129.45"
font_name = "arial"
font_style = "bold"
font_size = "20"

lines = [[1, "solid", "black", 2],[1, "solid", "black", 2],[1, "solid", "black", 2],[1, "solid", "black", 2]]


cell = [\
        ["col_start", "row_start", "col_end", "row_end"],\
        [["x0", "y0"], ["x1","y1"], ["x2","y2"], ["x3","y3"]],\
        [["value_type", "value_content", ["font_name", "font_style", "font_size", "font_color", "vertical_align", "horizontal_align"]]],\
        [[0, "solid", "black", 0],[0, "solid", "black", 0],[0, "solid", "black", 0],[0, "solid", "black", 0]]
        background_cell_color
    ]
"""


class Tablegen():
    def __init__(self, config):
        self.config = config
    
    def run_table(self):
        self.init_values()
        self.init_table()
        self.create_img()

        # self.draw_total_table()
        
        self.set_column_value_type()
        self.create_cells()

        # header content
        style_font = random.choice(["regular", "italic", "bold"])
        self.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
        if random.random() < 0.4:
            if random.random() < 0.25:
                self.merge_row(0)
            else:
                self.merge_cells_header()
        if random.random() < 0.1:
            self.change_font(row=0, font_color=random_color("RBG"))

        # footer content
        style_font = random.choice(["regular", "regular", "regular", "italic", "bold"])
        self.change_font(row=-1, font_style=style_font, font_size=0, font_color=None, row_column=False)
        if random.random() < 0.1:
            self.merge_row(-1)
        if random.random() < 0.1:
            self.change_font(row=-1, font_color=random_color("RBG"))


        for i in range(self.columns):
            if self.column_type[i] == "str":
                self.change_font(column=i, horizontal_align = "center")
            elif self.column_type[i] == "num":
                self.change_font(column=i, horizontal_align = "right")

        # self.change_font(row=0, horizontal_align = random.choice(["left", "center", "right"]))

        self.delete_lines()


        # color
        header_c = None
        footer_c = None
        color1 = (random.randint(100,200), random.randint(100,200), random.randint(100,200))
        color2 = (color1[0]+50+random.randint(0,75), color1[1]+50+random.randint(0,75), color1[2]+50+random.randint(0,75))

        option_color = random.random()
        if option_color <= 0.2:
            # printi("tudo branco")
            color1=None
            color2=None
            header_c = None
            footer_c = None
        elif option_color > 0.2 and option_color <= 0.3:
            # printi("intercalado tudo")
            if random.random() < 0.5:
                color2 = None
        elif option_color > 0.3 and option_color <= 0.48:
            # printi("intercalado sem header e sem footer")
            header_c = random_color("RGB")
            footer_c = header_c
            if random.random() < 0.5:
                header_c = "white"
                if random.random() < 0.8:
                    footer_c = "white"
            if random.random() < 0.5:
                color2 = None
        elif option_color > 0.48 and option_color <= 0.64:
            # printi("intercalado sem header")
            header_c = random_color("RGB")
            if random.random() < 0.5:
                header_c = "white"
            if random.random() < 0.5:
                color2 = None
        elif option_color > 0.64 and option_color <= 0.80:
            # printi("intercalado sem footer")
            footer_c = random_color("RGB")
            if random.random() < 0.5:
                footer_c = "white"
            if random.random() < 0.5:
                color2 = None
        elif option_color > 0.80 and option_color <= 0.90:
            # printi("cor só no header")
            color1=None
            color2=None
            header_c = random_color("RGB")
            footer_c = None
        elif option_color > 0.90:
            # printi("cor só no footer")
            color1=None
            color2=None
            header_c = None
            footer_c = random_color("RGB")

        if random.random() <= 0.2:
            color1=None
            color2=None
            header_c = None
            footer_c = None
        
        self.intercalate_background_cell(option="row", header = header_c, footer=footer_c, first_color=color1, second_color=color2)


        # lines row
        option_line = random.random()
        if option_line <= 0.1:
            # printi("nenhuma linha")
            self.delete_lines()
        elif option_line > 0.1 and option_line <= 0.4:
            # printi("todas as linhas")
            self.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
        elif option_line > 0.4 and option_line <= 0.6:
            if random.random() <= 0.5:
                # printi("só linhas inferiores")
                self.change_line(row="all", b_line = 1)
            else:
                # printi("só horizontais")
                self.change_line(column="all",  l_line = 1)
                self.change_line(column=0,  l_line = 0)
        elif option_line > 0.6 and option_line <= 0.8:
            # printi("só primeira linha inferior")
            self.change_line(row=0, b_line = 1)
            if random.random() <= 0.4:
                if random.random() <= 0.5:
                    # printi("só primeira vertical")
                    self.change_line(column=0,  r_line = 1)
                else:
                    # printi("só ultima vertical")
                    self.change_line(column=-1,  l_line = 1)
        elif option_line > 0.8:
            # printi("só antes da ultima linha inferior")
            self.change_line(row=-2, b_line = 1)
            if random.random() <= 0.4:
                if random.random() <= 0.5:
                    # printi("só primeira vertical")
                    self.change_line(column=0,  r_line = 1)
                else:
                    # printi("só ultima vertical")
                    self.change_line(column=-1,  l_line = 1)
        
        if random.random() <= 0.5:
            if random.random() <= 0.5:
                self.change_line(row="all", b_line_width=3, t_line_width=3)
            else:
                self.change_line(row="all", b_line_width=2, t_line_width=2)
        
        
        # merge last row
        if random.random() <= 0.5:
            self.merge_row(-1)

        self.fill_table()
        self.print_cells()

        self.draw_lines()
        
        # self.save_image()

        # self.create_xml_file()
        pass

    def init_values(self):
        now = datetime.datetime.now()
        self.width = self.config["size"][0]
        self.height = self.config["size"][1]
        self.bg_color = self.config["bg_color"]
        # self.bg_color = random_color("RGB")
        self.margin = set_margins(self.config["margins"], self.width, self.height)
        self.workable_area = {"position":(self.margin[3], self.margin[0]),"size":(self.width-self.margin[1]-self.margin[3], self.height-self.margin[2]-self.margin[0])}

        # table lines
        min_lenght = min(self.width, self.height)
        if min_lenght < 200:
            line_width = 1
        else:
            line_width = math.floor(min_lenght/400)
        if line_width < 1:
            line_width = 1

        # line_width = line_width+1
        self.line_width_1 = [line_width]
        self.line_width_2 = [round(line_width*2)]
        self.line_width_3 = [round(line_width*2.5)]
        
        # fonts
        self.global_font_name = self.config["ts_text"][0]
        self.global_font_style = self.config["ts_text"][1]
        self.global_font_size = self.config["ts_text"][2]
        self.global_font_color = "black"
        
        self.font = generate_font(Config.fonts_folder, font_size=self.config["ts_text"][2], font_name=self.config["ts_text"][0], font_style=self.config["ts_text"][1])
        self.font_bold = generate_font(Config.fonts_folder, font_size=self.config["ts_text"][2], font_name=self.config["ts_text"][0], font_style="bold")
        
        #self.character_width = self.font.getsize('X')[0]
        self.character_width = self.font.getbbox('X')[2]-self.font.getbbox('X')[0]
        #self.character_height = self.font.getsize('hg')[1]
        self.character_height = self.font.getbbox('hg')[3]-self.font.getbbox('hg')[1]
        self.total_characters_horizontal = math.floor(self.workable_area["size"][0]/self.character_width)

    def init_table(self, cols=[], rows=[]):
        if cols != []:
            self.columns_sizes = []
            col_size = math.floor(self.workable_area["size"][0]/sum(cols))
            for col in cols:
                self.columns_sizes.append(round(col*col_size))
            self.columns_sizes[-1] = self.workable_area["size"][0]-(sum(self.columns_sizes[:-1]))-self.line_width_1[0]
            self.columns = len(self.columns_sizes)
        else:
            self.columns_sizes = []
            while sum(self.columns_sizes) < self.workable_area["size"][0]:
                self.columns_sizes.append(round(rand_gauss((2*self.character_width,20*self.character_width))))
                # self.columns_sizes.append(round(10*self.character_width))
                if len(self.columns_sizes) == 1:
                    if self.columns_sizes[0] > self.workable_area["size"][0]:
                        self.columns_sizes[0] = self.workable_area["size"][0]
                if sum(self.columns_sizes)>self.workable_area["size"][0]:
                    self.columns_sizes.pop(-1)
                    self.columns_sizes[-1] += 1
            self.columns = len(self.columns_sizes)

        if rows != []:
            self.rows_sizes = []
            for row in rows:
                self.rows_sizes.append(math.ceil((self.character_height*(1)+3)*row))
                
            # apaga as ultimas colunas se o tamanho a suma é maior que a workable_area vertical
            while sum(self.rows_sizes) > self.workable_area["size"][1]:
                self.rows_sizes.pop()

            self.rows = len(self.rows_sizes)
        else:
            self.rows_sizes = []
            if random.random()<0.4:
                self.rows_sizes.append(math.ceil(self.character_height*(1+random.random()+random.random()))+3)
                # self.rows_sizes.append(math.ceil(self.character_height*3))
            else:
                self.rows_sizes.append(math.ceil(self.character_height)+3)
            while sum(self.rows_sizes) < self.workable_area["size"][1]:
                self.rows_sizes.append(math.ceil(self.character_height*(1))+3)
            if sum(self.rows_sizes)>self.workable_area["size"][1]:
                self.rows_sizes.pop(-1)
            self.rows = len(self.rows_sizes)

        self.max_columns_characters = [math.floor(x/self.character_width) for x in self.columns_sizes]
        self.columns_characters = []
        for max_characters in self.max_columns_characters:
            self.columns_characters.append(self.set_characters_quantity(max_characters))
        # printi(self.columns_characters)
        pass

    def set_characters_quantity(self, max_characters):
        # return [digits, more, less, decimals]
        characters = random.randint(1, max_characters)
        if max_characters < 2:
            return [1, 0, 0, 0]
        elif max_characters == 2:
            return [1, 1, 0, 0]
        elif max_characters == 3:
            if random.random()>0.5:
                return [2, 1, 1, 0]
            else:
                return [1, 1, 0, 1]
        elif max_characters >= 4 and max_characters < 7:
            if random.random()>0.5:
                return [3, 1, 1, 0]
            else:
                return [2, 1, 0, 1]
        elif max_characters >=7:
            decimals = random.randint(0,4)
            numbers = random.randint(1, max_characters-decimals)
            leftover_digits = max_characters-decimals-numbers
            if leftover_digits > 1:
                more = random.randint(1, math.floor(leftover_digits/2))
                less = random.randint(1, math.floor(leftover_digits/2))
            else:
                more = 0
                less = 0
            if more >= numbers:
                more = numbers-1
            if less >= numbers:
                less = numbers-1
            return [numbers, more, less, decimals]
        return [1, 0, 0, 0]

    def create_img (self):
        self.document = Image.new("RGB", (self.width, self.height), color=self.bg_color)
        self.draw = ImageDraw.Draw(self.document)

    def show_workable_area (self, color="green", color_line="black", width=1):
        xmin=self.workable_area["position"][0]
        xmax=self.workable_area["position"][0]+self.workable_area["size"][0]
        ymin=self.workable_area["position"][1]
        ymax=self.workable_area["position"][1]+self.workable_area["size"][1]
        self.draw.rectangle((xmin,ymin,xmax,ymax), fill=color, outline=color_line, width=width)

    def plot_characters(self):
        x0=self.workable_area["position"][0]
        y0=self.workable_area["position"][1]
        count=0
        for i in range(self.total_characters_horizontal):
            if count<4:
                self.draw.text((x0, y0), "X", fill="black", font=self.font)
                x0 += self.character_width
                count += 1
            else:
                self.draw.text((x0, y0), "X", fill="red", font=self.font)
                x0 += self.character_width
                count = 0

    def draw_total_table(self):
        # to plot horizontal lines
        x0=self.workable_area["position"][0]
        y0=self.workable_area["position"][1]
        x1=self.workable_area["position"][0]+self.workable_area["size"][0]
        y1=self.workable_area["position"][1]
        color_lines = (175,175,175)

        for size in self.rows_sizes:
            # self.draw.line(((x0,y1),(x1,y1)), fill="black", width=self.line_width_1[0])
            self.draw.line(((x0,y1),(x1,y1)), fill=color_lines, width=1)
            y1 += size
        self.draw.line(((x0,y1),(x1,y1)), fill=color_lines, width=1)


        # to plot vertical lines
        x0=self.workable_area["position"][0]
        y0=self.workable_area["position"][1]
        # y1 -= self.character_height
        for size in self.columns_sizes:
            self.draw.line(((x0,y0),(x0,y1)), fill=color_lines, width=1)
            x0 += size
        self.draw.line(((x0,y0),(x0,y1)), fill=color_lines, width=1)

    def create_cells(self):
        self.cells=[]
        self.columns_sizes
        x0=self.workable_area["position"][0]
        y0=self.workable_area["position"][1]
        horizontal_align, vertical_align = "left", "top"
        for c, column in enumerate(self.columns_sizes):
            y0=self.workable_area["position"][1]
            x1=x0 + column
            for r, row in enumerate(self.rows_sizes):
                y1=y0 + row
                corner0 = (x0+self.line_width_1[0] , y0+self.line_width_1[0])
                corner1 = (x1-round(self.line_width_1[0]/2) , y1-round(self.line_width_1[0]/2))
                corner0 = (x0 , y0)
                corner1 = (x1 , y1)
                x0cell = corner0[0]
                y0cell = corner0[1]
                x1cell = corner1[0]
                y1cell = corner1[1]
                cell = [[c, r, c, r],\
                        [[x0cell, y0cell], [x1cell,y0cell], [x1cell,y1cell], [x0cell,y1cell]],\
                        [["value_type", "value_content", [self.global_font_name, self.global_font_style, self.global_font_size, self.global_font_color, horizontal_align, vertical_align]]],\
                        [[1, "solid", "black", 1],[1, "solid", "black", 1],[1, "solid", "black", 1],[1, "solid", "black", 1]],\
                        None
                    ]
                # self.cells.append([[c, r], [corner0[0], corner0[1], corner1[0], corner1[1]]])
                self.cells.append(cell)
                y0=y1
            x0=x1
        # print(*self.cells, sep="\n")
        pass

    def merge_cells_header(self):
        if self.columns > 2:
            rand_column = random.randint(0, self.columns-2)
            to_expand = -1
            to_delete = -1
            for c, cell in enumerate(self.cells):
                if cell[0][0] == rand_column and cell[0][1] == 0:
                    p0 = cell[1][0]
                    p3 = cell[1][3]
                    to_expand = c
                if cell[0][0] == rand_column+1 and cell[0][1] == 0:
                    p1 = cell[1][1]
                    p2 = cell[1][2]
                    end_column = cell[0][2]
                    to_delete = c
            if to_delete > 0 and to_expand > 0:
                self.cells.pop(to_delete)
                self.cells[to_expand][1] = [p0,p1,p2,p3]
                self.cells[to_expand][0][2] = end_column

    def merge_row(self, row_to_merge):
        if row_to_merge < 0:
            row_to_merge = self.rows + row_to_merge

        # to count the number of cells in the specific row
        count_row = 0
        for c, cell in enumerate(self.cells):
            if cell[0][1] == row_to_merge:
                count_row += 1
        
        # only can merge the row if there is more than 1 cell in the row
        if count_row > 1:
            for i, column in enumerate(range(count_row-1)):
                # to choose the cells to merge
                cells_to_merge=[]
                for c, cell in enumerate(self.cells):
                    if cells_to_merge == []:
                        if cell[0][1] == row_to_merge:
                            cells_to_merge.append(c)
                    elif len(cells_to_merge) == 1:
                        if cell[0][1] == row_to_merge:
                            cells_to_merge.append(c)
                
                # to merge the cells
                for c, cell in enumerate(cells_to_merge):
                    if 'minx' not in locals():
                        minx = self.cells[cell][1][0][0]
                    else:
                        if self.cells[cell][1][0][0] < minx:
                            minx = self.cells[cell][1][0][0]
                    
                    if 'miny' not in locals():
                        miny = self.cells[cell][1][0][1]
                    else:
                        if self.cells[cell][1][0][1] < miny:
                            miny = self.cells[cell][1][0][1]

                    if 'maxx' not in locals():
                        maxx = self.cells[cell][1][2][0]
                    else:
                        if self.cells[cell][1][2][0] > maxx:
                            maxx = self.cells[cell][1][2][0]
                    
                    if 'maxy' not in locals():
                        maxy = self.cells[cell][1][2][1]
                    else:
                        if self.cells[cell][1][2][1] > maxy:
                            maxy = self.cells[cell][1][2][1]

                    
                    
                    
                    if 'minc' not in locals():
                        minc = self.cells[cell][0][0]
                    else:
                        if self.cells[cell][0][0] < minc:
                            minc = self.cells[cell][0][0]
                    
                    if 'maxc' not in locals():
                        maxc = self.cells[cell][0][2]
                    else:
                        if self.cells[cell][0][2] > maxc:
                            maxc = self.cells[cell][0][2]

                self.cells[cells_to_merge[0]][0][0] = minc
                self.cells[cells_to_merge[0]][0][2] = maxc
                self.cells[cells_to_merge[0]][1] = [[minx, miny], [maxx,miny], [maxx,maxy], [minx,maxy]]
                self.cells.pop(cells_to_merge[1])
                del minc, maxc, minx, miny, maxx, maxy

    def merge_cells(self, c1=[], c2=[]):
        exist_c1 = False
        exist_c2 = False
        for c, cell in enumerate(self.cells):
            if cell[0][0] == c1[0] and cell[0][1] == c1[1]:
                exist_c1 = True
            if cell[0][0] == c2[0] and cell[0][1] == c2[1]:
                exist_c2 = True

        # only can merge the row if there is more than 1 cell in the row
        if exist_c1 and exist_c2:
            # to choose the cells to merge
            cells_to_merge=[]
            for c, cell in enumerate(self.cells):
                if cells_to_merge == []:
                    if cell[0][0] == c1[0] and cell[0][1] == c1[1]:
                        cells_to_merge.append(c)
                elif len(cells_to_merge) == 1:
                    if cell[0][0] == c1[0] and cell[0][1] == c1[1]:
                        cells_to_merge.append(c)
            for c, cell in enumerate(self.cells):
                if cells_to_merge == []:
                    if cell[0][0] == c2[0] and cell[0][1] == c2[1]:
                        cells_to_merge.append(c)
                elif len(cells_to_merge) == 1:
                    if cell[0][0] == c2[0] and cell[0][1] == c2[1]:
                        cells_to_merge.append(c)
            
            # to merge the cells
            for c, cell in enumerate(cells_to_merge):
                if 'minx' not in locals():
                    minx = self.cells[cell][1][0][0]
                else:
                    if self.cells[cell][1][0][0] < minx:
                        minx = self.cells[cell][1][0][0]
                
                if 'miny' not in locals():
                    miny = self.cells[cell][1][0][1]
                else:
                    if self.cells[cell][1][0][1] < miny:
                        miny = self.cells[cell][1][0][1]

                if 'maxx' not in locals():
                    maxx = self.cells[cell][1][2][0]
                else:
                    if self.cells[cell][1][2][0] > maxx:
                        maxx = self.cells[cell][1][2][0]
                
                if 'maxy' not in locals():
                    maxy = self.cells[cell][1][2][1]
                else:
                    if self.cells[cell][1][2][1] > maxy:
                        maxy = self.cells[cell][1][2][1]

                
                
                
                if 'minc' not in locals():
                    minc = self.cells[cell][0][0]
                else:
                    if self.cells[cell][0][0] < minc:
                        minc = self.cells[cell][0][0]
                
                if 'maxc' not in locals():
                    maxc = self.cells[cell][0][2]
                else:
                    if self.cells[cell][0][2] > maxc:
                        maxc = self.cells[cell][0][2]

            self.cells[cells_to_merge[0]][0][0] = minc
            self.cells[cells_to_merge[0]][0][2] = maxc
            self.cells[cells_to_merge[0]][1] = [[minx, miny], [maxx,miny], [maxx,maxy], [minx,maxy]]
            self.cells.pop(cells_to_merge[1])
            del minc, maxc, minx, miny, maxx, maxy

    def set_column_value_type(self):
        self.column_type = []
        for column in self.columns_sizes:
            if random.random() < 0.7:
                self.column_type.append("num")
            else:
                self.column_type.append("str")

    def fill_table(self):
        for cell in self.cells:
            self.font = generate_font(Config.fonts_folder, font_name=cell[2][0][2][0], font_style=cell[2][0][2][1], font_size=cell[2][0][2][2])

            column, row, x0c, y0c, x1c, y1c, width, height = self.cell_size(cell)
            text_to_print = []
            if row == 0:
                #if height > 2*self.font.getsize("hg")[1]:
                if height > 2*self.font.getbbox("hg")[3]-self.font.getbbox("hg")[1]:
                    self.global_font_name, self.global_font_style, self.global_font_size, self.global_font_color, horizontal_align, vertical_align = cell[2][0][2]
                    cell[2].append(["value_type", "value_content", [self.global_font_name, self.global_font_style, self.global_font_size, self.global_font_color, horizontal_align, vertical_align]])
                    text_to_print.append(self.generate_text(width, height, "str", self.font, column, row, cell))
                    text_to_print.append(self.generate_text(width, height, "str", self.font, column, row, cell))
                else:
                    text_to_print.append(self.generate_text(width, height, "str", self.font, column, row, cell))
            else:
                text_to_print.append(self.generate_text(width, height, self.column_type[column], self.font, column, row, cell))

            for i in range(len(text_to_print)):
                cell[2][i][0] = "text"
                cell[2][i][1] = text_to_print[i]

    def fill_cell(self, column = None, row = None, row_column = False, text_prop = [1], text_align = ["center"], f_style=[], len_text=[]):
        """
        column = None
        row = None
        row_column = False
        text_prop = [1] - size proportion difference, 1: same, 2: twice, 0.5: half
        text_align = ["center"]
        f_style=[]
        len_text=[]
        """
        for cell in self.cells:
            if column == cell[0][0] and row == cell[0][1]:
                cell[2] = []
                for p, prop in enumerate(text_prop):
                    font_name = self.config["ts_text"][0]
                    if f_style == []:
                        font_style = self.config["ts_text"][1]
                    else:
                        font_style = f_style[p]
                    font_size = int(self.config["ts_text"][2]*prop)
                    font = generate_font(Config.fonts_folder, font_name=font_name, font_style=font_style, font_size=font_size)
                    column, row, x0c, y0c, x1c, y1c, width, height = self.cell_size(cell)
                    if len_text != []:
                        if len_text[p] == "text":
                            text_ = self.generate_full_text(width, height, "str", font, column, row)
                        elif len_text[p] == "str":
                            text_ = self.generate_text(width, height, "str", font, column, row, cell)
                        elif len_text[p] == "num":
                            text_ = self.generate_text(width, height, "num", font, column, row, cell)
                        else:
                            text_ = self.generate_text(width, height, "num", font, column, row, cell)
                    else:
                        text_ = self.generate_text(width, height, "num", font, column, row, cell)
                    
                    cell[2].append(['text', text_, [font_name, font_style, font_size, 'black', text_align[p], 'top']])

    def print_cells(self):
        for cell in self.cells:
            text_to_print = []
            for i in range(len(cell[2])):
                text_to_print.append(cell[2][i][1])
            column, row, x0c, y0c, x1c, y1c, width, height = self.cell_size(cell)
            line_height=0
            for i in range(len(cell[2])):
                if cell[2][i][0] == "text":
                    font_name = cell[2][i][2][0]
                    font_style = cell[2][i][2][1]
                    font_size = cell[2][i][2][2]
                    font_color = cell[2][i][2][3]
                    font = generate_font(Config.fonts_folder, font_name=font_name, font_style=font_style, font_size=font_size)


                    ### to align the text to print
                    if cell[2][i][2][4] == "center":
                        #x0 = round(x0c + (width - font.getsize(text_to_print[i])[0])/2)
                        x0 = round(x0c + (width - font.getbbox(text_to_print[i])[2]-font.getbbox(text_to_print[i])[0])/2)
                    elif cell[2][i][2][4] == "left":
                        x0 = x0c + 0
                    else:
                        #x0 = round(x0c + width - font.getsize(text_to_print[i])[0])
                        x0 = round(x0c + width - font.getbbox(text_to_print[i])[2]-font.getbbox(text_to_print[i])[0])

                    cell[2][i][0] = "text"
                    cell[2][i][1] = text_to_print[i]

                    # self.draw.rectangle(((x0cell, y0cell),(x1cell, y1cell)), fill=color_fill, outline=None, width=10)
                    x0cell, y0cell, x1cell, y1cell = cell[1][0][0], cell[1][0][1], cell[1][2][0], cell[1][2][1]
                    color_fill = random_color("RGB")
                    color_fill = cell[4]
                    if color_fill and i == 0:
                        self.draw.rectangle(((x0cell, y0cell),(x1cell, y1cell)), fill=color_fill, outline=None, width=10)
                    self.draw.text((x0, y0c), text_to_print[i], fill=cell[2][0][2][3], font=font)
                    #cell[2][i][2].append([x0,y0c,   x0+font.getsize(text_to_print[i])[0]    ,y0c+font.getsize("hg")[1]])
                    cell[2][i][2].append([x0,y0c,   x0+font.getbbox(text_to_print[i])[2]-font.getbbox(text_to_print[i])[0]    ,y0c+font.getbbox("hg")[3]-font.getbbox("hg")[1]])
                    #y0c += int(font.getsize("hg")[1]*1.1)
                    y0c += int(font.getbbox("hg")[3]-font.getbbox("hg")[1]*1.1)
                    #line_height = font.getsize("hg")[1]
                    line_height = font.getbbox("hg")[3]-font.getbbox("hg")[1]

                if cell[2][i][0] == "img":
                    logo_img = Image.open(cell[2][i][1])
                    org_size = logo_img.size
                    if org_size[0] > org_size[1]:
                        # print("hor")
                        pass
                    else:
                        # print("ver")
                        pass
                    width_img = int(width*0.8)
                    height_img = int(height*0.8)
                    x0img = int(x0c+(((x1c-x0c)-width_img)/2))
                    y0img = int(y0c+(((y1c-y0c)-height_img)/2))
                    logo_img = logo_img.resize((width_img, height_img))
                    self.document.paste(logo_img, (x0img,y0img))
                    cell[2][i][2].append([x0img,y0img,   x0img+width_img,y0img+height_img])

    def draw_lines(self):
        for cell in self.cells:
            for line, cell_in_line in enumerate(cell[3]):
                if cell[3][line][0] != 1: continue
                j = line + 1 if line < len(cell_in_line) - 1 else 0
                x0 = cell[1][line][0]
                y0 = cell[1][line][1]
                x1 = cell[1][j][0]
                y1 = cell[1][j][1]
                self.draw.line(((x0,y0),(x1,y1)), fill=cell[3][line][2], width=cell[3][line][3])

    def cell_size(self, cell):
        # top, right, bottom, left
        column = cell[0][0]
        row = cell[0][1]
        x0c = cell[1][0][0] + cell[3][3][3] + 1
        y0c = cell[1][0][1] + cell[3][0][3] + 1
        x1c = cell[1][2][0] - cell[3][1][3] - 1
        y1c = cell[1][2][1] - cell[3][2][3] - 1
        width = x1c-x0c
        height = y1c-y0c

        return column, row, x0c, y0c, x1c, y1c, width, height

    def generate_text(self, width, height, type, font, column, row, cell):
        #characters = math.floor(width/font.getsize(str(0))[0])
        characters = math.floor(width/font.getbbox(str(0))[2]-font.getbbox(str(0))[0])
        if type == "num":
            dim_font = 1
            count_try_text = 0
            count_try_text1 = 0
            digits, more, less, decimals = self.columns_characters[column]
            text_width = width +10
            while text_width > width:
                ### to define the numbers quantity for the entire part
                option = random.choice(["same", "more", "less"])
                if option == "more":
                    if more >0:
                        numbers = digits + random.randint(1, more)
                    else:
                        numbers = digits
                elif option == "less":
                    if less >0:
                        numbers = digits - random.randint(1, less)
                    else:
                        numbers = digits
                else:
                    numbers = digits
                
                # printi(digits, more, less, decimals, " - ", numbers)
                
                ### to define the whole part of number
                min_ = int("1" + "0"*(numbers-1))
                max_ = int("9"*numbers)
                num = str(random.randint(min_,max_))

                ### to define the fractional part of number
                if decimals > 0:
                    decimal = random.randint(0, int("9"*decimals))
                    decimal_str = str(decimal)
                    while len(decimal_str) < decimals:
                        decimal_str = "0"+decimal_str
                    ### join the whole with the fractional part
                    num = num + "." + decimal_str
                #text_width =font.getsize(str(num))[0]
                text_width = font.getbbox(str(num))[2]-font.getbbox(str(num))[0]
                count_try_text += 1
                count_try_text1 += 1
                if count_try_text > 50:
                    if more == 0 and less == 0:
                        if decimals > 1:
                            decimals -= 1
                        elif digits > 1:
                            digits -= 1

                    # printi("-----", text_width, str(num), width)
                    # printi(digits, more, less, decimals)
                    count_try_text = 0
                if count_try_text1 > 100:
                    if decimals > 1:
                        decimals -= 1
                    elif digits > 1:
                        digits -= 1
                if count_try_text1 > 200:
                    decimals = 0
                if count_try_text1 > 300:
                    # printi(count_try_text1)
                    # printi("-----", text_width, str(num), width)
                    # printi(digits, more, less, decimals)
                    # printi()
                    digits, more, less, decimals = 1, 0, 0, 0
                if count_try_text1 == 400:
                    # font = generate_font(Config.fonts_folder, font_name=cell[2][0][2][0], font_style=cell[2][0][2][1], font_size=cell[2][0][2][2]-dim_font)
                    # if cell[2][0][2][2] > dim_font + 1:
                        # dim_font += 1
                        # count_try_text1 = 300
                    num = "."
                    # printi(count_try_text1)
                    # printi("400 -----", text_width, str(num), width)
                    # printi(digits, more, less, decimals)
                    # printi()
                    text_width = width - 1
                if count_try_text1 > 500:
                    num = ""

            return str(num)
        elif type == "str":
            text_size = width+1
            counter = 0
            while text_size > width*0.9:
                text = self.request_text()
                #text_size = font.getsize(text)[0]
                text_size = font.getbbox(text)[2]-font.getbbox(text)[0]
                counter += 1
                if counter > 100:
                    text = "."
                    #text_size = font.getsize(text)[0]
                    text_size = font.getbbox(text)[2]-font.getbbox(text)[0]
                if counter > 205:
                    text_size = width * 0.80
                    text_size = width * 0.70
                if counter == 350:
                    text_size = width * 0.7
            return text
        else:
            return ""

    def generate_full_text(self, width, height, type, font, column, row):
        if type == "str":
            words, _ = request_words()
            i = 0
            line = ""
            #width_line = font.getsize(line)[0]
            width_line = font.getbbox(line)[2]-font.getbbox(line)[0]
            #while i < len(words) and width_line + font.getsize(words[i])[0] < width*0.9:
            while i < len(words) and width_line + font.getbbox(words[i])[2]-font.getbbox(words[i])[0] < width*0.9:
                line = line + words[i] + " "
                #width_line = font.getsize(line)[0]
                width_line = font.getbbox(line)[2]-font.getbbox(line)[0]
                i += 1

            return line
        else:
            return ""

    def request_text(self):
        return random.choice(["absorvância", "adiamento", "afetando", "alocação", "alternativos", "amostras", "análise", "anteriormente", "ao", "apelo", "apesar", "apresentam", "aprisionado", "aquecimento", "ar", "áreas", "as", "às", "atual", "balão", "base", "berço", "bico", "biodiesel", "calculadas", "cálculo", "características", "caso", "catalisador", "catalisadores", "cinéticade", "com", "combustão", "combustíveis", "combustível", "comentado", "comercial", "Como", "competirão", "completa", "complexidade", "componentes", "comportamento", "comportamentos", "comum", "concede", "concentração", "concorrência", "condutas", "consequentemente", "consumidores", "consumo", "contribuir", "controle", "custo", "custos", "da", "das", "data", "de", "decisão", "decisões", "decorrência", "demais", "derivado", "descrito", "desempenho", "deslocando", "dessas", "destacado", "devido", "diferentes", "dificultando", "diminuição", "direção", "discutido", "distinto", "distintos", "dito", "diversas", "do", "dos", "durante", "e", "é", "eficiência", "elevada", "elevado", "em", "emissões", "empresas", "energética", "então", "entre", "envolverem", "épela", "escoamento", "estaria", "este", "estreita", "estrutura", "etanol", "explicação", "exploração", "fase", "fatode", "fenômenocompleto", "ficar", "físico", "floculação", "floculadas", "forma", "formação", "formando", "fundo", "garantir", "gasolina", "geram", "global", "grande", "grandes", "grau", "hidratos", "ideal", "inadequação", "incentivos", "incertezas", "indefinição", "indicando", "ineficiente", "influenciando", "infraestrutura", "injetor", "integradas", "intervenção", "investidores", "investimento", "investimentos", "irreversibilidade", "já", "julho", "limitadoras", "logística", "mais", "máxima", "medida", "medidas", "mercado", "métodos", "mistura", "modelo", "monitoramento", "muitas", "na", "não", "nesse", "neste", "níquel", "no", "norte-americana", "nos", "o", "oleifera", "óleo", "os", "ou", "outubro", "óxido", "país", "para", "parte", "partículas", "partirde", "pelasalturas", "pelo", "picos", "pode", "podem", "pois", "política", "por", "possibilidade", "possui", "prática", "preços", "previamente", "principais", "problemas", "produto", "projeto", "provocando", "publicações", "quantitativa", "quanto", "que", "queima", "reação", "realização", "realizado", "realizando", "recursos", "reduzindo", "refino", "reforma", "relação", "relativamente", "resultou", "retirado", "reunião", "são", "sem", "semiquantitativa", "sentido", "ser", "servir", "setor", "sobre", "spray", "sugeriu", "sujeito", "superior", "tamanhos", "também", "tanto", "tem", "tendo", "termos", "testes", "tipo", "tomada", "trabalho", "tratam", "um", "uma", "uso", "utilizados", "vantagens", "vem", "vezes", "virtude", "viscosidade", "vista"])

    def save_image (self):
        path = os.path.split(self.png_path)[0]
        os.makedirs(path,exist_ok=True)

        self.document.save(self.png_path)

    def draw_pixels(self):
        count = 0
        for i in range(self.width):
            if count < 4:
                self.draw.line(((i,0),(i,0)), fill=(150,150,150), width=1)
                self.draw.line(((i,0),(i,0)), fill=random_color("RGB"), width=1)
                count += 1
            else:
                self.draw.line(((i,0),(i,1)), fill=(50,50,50), width=1)
                count = 0

    def change_font(self, column = None, row = None, font_name = None, font_style = None, font_size= None, font_color= None, row_column = False, horizontal_align = None, vertical_align = None):
        if column != None and isinstance(column, (int, float)) and column < 0:
            column = self.columns + column
        if row != None and isinstance(row, (int, float)) and row < 0:
            row = self.rows + row
        if row_column:
            for cell in self.cells:
                if column == cell[0][0] and row == cell[0][1]:
                    if font_name != None:
                        cell[2][0][2][0] = font_name
                    if font_style != None:
                        cell[2][0][2][1] = font_style
                    if font_size != None:
                        cell[2][0][2][2] = round(cell[2][0][2][2] * (1 + (font_size/100)))
                    if font_color != None:
                        cell[2][0][2][3] = font_color
                    if horizontal_align != None:
                        cell[2][0][2][4] = horizontal_align
                    if vertical_align != None:
                        cell[2][0][2][5] = vertical_align

        else:
            for cell in self.cells:
                if column == cell[0][0] or column == cell[0][2] or column == "all":
                    if font_name != None:
                        cell[2][0][2][0] = font_name
                    if font_style != None:
                        cell[2][0][2][1] = font_style
                    if font_size != None:
                        cell[2][0][2][2] = round(cell[2][0][2][2] * (1 + (font_size/100)))
                    if font_color != None:
                        cell[2][0][2][3] = font_color
                    if horizontal_align != None:
                        cell[2][0][2][4] = horizontal_align
                    if vertical_align != None:
                        cell[2][0][2][5] = vertical_align
                if row == cell[0][1] or row == cell[0][3] or row == "all":
                    if font_name != None:
                        cell[2][0][2][0] = font_name
                    if font_style != None:
                        cell[2][0][2][1] = font_style
                    if font_size != None:
                        cell[2][0][2][2] = round(cell[2][0][2][2] * (1 + (font_size/100)))
                    if font_color != None:
                        cell[2][0][2][3] = font_color
                    if horizontal_align != None:
                        cell[2][0][2][4] = horizontal_align
                    if vertical_align != None:
                        cell[2][0][2][5] = vertical_align
    
    def change_cell_background(self, column = None, row = None, color = None, row_column = False):
        if column != None and isinstance(column, (int, float)) and column < 0:
            column = self.columns + column
        if row != None and isinstance(row, (int, float)) and row < 0:
            row = self.rows + row
        if row_column:
            for cell in self.cells:
                if column == cell[0][0] and row == cell[0][1]:
                    if color != None:
                        cell[4] = color

        else:
            for cell in self.cells:
                if column == cell[0][0] or column == cell[0][2]:
                    if color != None:
                        cell[4] = color
                if row == cell[0][1] or row == cell[0][3]:
                    if color != None:
                        cell[4] = color
    
    def intercalate_background_cell(self, option="row", first_color=None, second_color=None, header=None, footer=None):
        if option == "row":
            set_color = 1
            for row in range(self.rows):
                if header != None and row == 0:
                    self.change_cell_background(row=row, color=header)
                elif set_color == 1:
                    if first_color != None:
                        self.change_cell_background(row=row, color=first_color)
                    set_color = 2
                else:
                    if second_color != None:
                        self.change_cell_background(row=row, color=second_color)
                    set_color = 1
                if footer != None and row == self.rows-1:
                    self.change_cell_background(row=row, color=footer)
        if option == "column":
            set_color = 1
            for column in range(self.columns):
                if header != None and column == 0:
                    self.change_cell_background(column=column, color=header)
                elif set_color == 1:
                    if first_color != None:
                        self.change_cell_background(column=column, color=first_color)
                    set_color = 2
                else:
                    if second_color != None:
                        self.change_cell_background(column=column, color=second_color)
                    set_color = 1
                if footer != None and column == self.columns-1:
                    self.change_cell_background(column=column, color=footer)

    def set_color_pred(self):
        # color
        header_c = None
        footer_c = None
        color1 = (random.randint(100,200), random.randint(100,200), random.randint(100,200))
        color2 = (color1[0]+50+random.randint(0,75), color1[1]+50+random.randint(0,75), color1[2]+50+random.randint(0,75))

        option_color = random.random()
        if option_color <= 0.2:
            # printi("tudo branco")
            color1=None
            color2=None
            header_c = None
            footer_c = None
        elif option_color > 0.2 and option_color <= 0.3:
            # printi("intercalado tudo")
            if random.random() < 0.5:
                color2 = None
        elif option_color > 0.3 and option_color <= 0.48:
            # printi("intercalado sem header e sem footer")
            header_c = random_color("RGB")
            footer_c = header_c
            if random.random() < 0.5:
                header_c = "white"
                if random.random() < 0.8:
                    footer_c = "white"
            if random.random() < 0.5:
                color2 = None
        elif option_color > 0.48 and option_color <= 0.64:
            # printi("intercalado sem header")
            header_c = random_color("RGB")
            if random.random() < 0.5:
                header_c = "white"
            if random.random() < 0.5:
                color2 = None
        elif option_color > 0.64 and option_color <= 0.80:
            # printi("intercalado sem footer")
            footer_c = random_color("RGB")
            if random.random() < 0.5:
                footer_c = "white"
            if random.random() < 0.5:
                color2 = None
        elif option_color > 0.80 and option_color <= 0.90:
            # printi("cor só no header")
            color1=None
            color2=None
            header_c = random_color("RGB")
            footer_c = None
        elif option_color > 0.90:
            # printi("cor só no footer")
            color1=None
            color2=None
            header_c = None
            footer_c = random_color("RGB")

        if random.random() <= 0.2:
            color1=None
            color2=None
            header_c = None
            footer_c = None
        
        self.intercalate_background_cell(option="row", header = header_c, footer=footer_c, first_color=color1, second_color=color2)

    def set_color_pred_gray(self):
        # color
        header_c = None
        footer_c = None
        color1=None
        color2=None

        header_color = False
        footer_color = False
        column_color = False
        
        if random.random() < 0.5: header_color = True
        if random.random() < 0.5: footer_color = True
        if random.random() < 0.5: column_color = True

        random_gray = random.randint(100,220)
        gray_color = (random_gray, random_gray, random_gray)

        if header_color:
            self.change_cell_background(row=0, color=gray_color)
        if footer_color:
            self.change_cell_background(row=-1, color=gray_color)
        if column_color:
            self.change_cell_background(column=0, color=gray_color)
        
    def change_content(self, column = None, row = None, row_column = False, type_value="text", value="texto"):
        if column != None and isinstance(column, (int, float)) and column < 0:
            column = self.columns + column
        if row != None and isinstance(row, (int, float)) and row < 0:
            row = self.rows + row
        if row_column:
            for c, cell in enumerate(self.cells):
                if column == cell[0][0] and row == cell[0][1]:
                    if type_value == "img":
                        if value == "_logo":
                            cell[2] = [cell[2][0]]
                            cell[2][0][0] = "img"
                            cell[2][0][1] = random.choice(return_images_files("/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/logos/"))
                        if value == "_figure":
                            cell[2] = [cell[2][0]]
                            cell[2][0][0] = "img"
                            cell[2][0][1] = random.choice(return_images_files("/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/figures/"))

    def specific_content(self, column = None, row = None, row_column = False, type_value="text", value="-"):
        if column != None and isinstance(column, (int, float)) and column < 0:
            column = self.columns + column
        if row != None and isinstance(row, (int, float)) and row < 0:
            row = self.rows + row
        if row_column:
            for c, cell in enumerate(self.cells):
                if column == cell[0][0] and row == cell[0][1]:
                    if type_value == "text":
                        cell[2] = [cell[2][0]]
                        cell[2][0][0] = "text"
                        cell[2][0][1] = value
                


        else:
            for cell in self.cells:
                if column == cell[0][0] or column == cell[0][2] or column == "all":
                    pass
                    # print("-", cell)
                if row == cell[0][1] or row == cell[0][3] or row == "all":
                    pass
                    # print("---", cell)
        pass

    def delete_lines(self):
        for cell in self.cells:
            for line in cell[3]:
                line[0] = 0

    def set_line(self, cell_line, line = None, line_style = None, line_color= None, line_width = None):
        if line != None: cell_line[0] = line
        if line_style != None: cell_line[1] = line_style
        if line_color != None: cell_line[2] = line_color
        if line_width != None: cell_line[3] = line_width
        return cell_line

    def change_line(self, column = None, row = None, \
            t_line = None, t_line_style = None, t_line_color= None, t_line_width = None,\
            r_line = None, r_line_style = None, r_line_color= None, r_line_width = None,\
            b_line = None, b_line_style = None, b_line_color= None, b_line_width = None,\
            l_line = None, l_line_style = None, l_line_color= None, l_line_width = None,\
            row_column = False):
        if column != None and isinstance(column, (int, float)) and column < 0:
            column = self.columns + column
        if row != None and isinstance(row, (int, float)) and row < 0:
            row = self.rows + row
        # if is to format a specific cell
        if row_column:
            for cell in self.cells:
                if column == cell[0][0] and row == cell[0][1]:
                    # for top line
                    cell[3][0] = self.set_line(cell[3][0], t_line, t_line_style, t_line_color, t_line_width)
                    # for right line
                    cell[3][1] = self.set_line(cell[3][1], r_line, r_line_style, r_line_color, r_line_width)
                    # for bottom line
                    cell[3][2] = self.set_line(cell[3][2], b_line, b_line_style, b_line_color, b_line_width)
                    # for left line
                    cell[3][3] = self.set_line(cell[3][3], l_line, l_line_style, l_line_color, l_line_width)
        
        # if is to format a entire row or column
        else:
            for cell in self.cells:
                if column == cell[0][0]:
                    # for top line
                    cell[3][0] = self.set_line(cell[3][0], t_line, t_line_style, t_line_color, t_line_width)
                    # for right line
                    cell[3][1] = self.set_line(cell[3][1], r_line, r_line_style, r_line_color, r_line_width)
                    # for bottom line
                    cell[3][2] = self.set_line(cell[3][2], b_line, b_line_style, b_line_color, b_line_width)
                    # for left line
                    cell[3][3] = self.set_line(cell[3][3], l_line, l_line_style, l_line_color, l_line_width)

                if row == cell[0][1]:
                    # for top line
                    cell[3][0] = self.set_line(cell[3][0], t_line, t_line_style, t_line_color, t_line_width)
                    # for right line
                    cell[3][1] = self.set_line(cell[3][1], r_line, r_line_style, r_line_color, r_line_width)
                    # for bottom line
                    cell[3][2] = self.set_line(cell[3][2], b_line, b_line_style, b_line_color, b_line_width)
                    # for left line
                    cell[3][3] = self.set_line(cell[3][3], l_line, l_line_style, l_line_color, l_line_width)

        # if is to apply to all rows or/and columns
        if row == "all" or column == "all":
            for cell in self.cells:
                # for top line
                cell[3][0] = self.set_line(cell[3][0], t_line, t_line_style, t_line_color, t_line_width)
                # for right line
                cell[3][1] = self.set_line(cell[3][1], r_line, r_line_style, r_line_color, r_line_width)
                # for bottom line
                cell[3][2] = self.set_line(cell[3][2], b_line, b_line_style, b_line_color, b_line_width)
                # for left line
                cell[3][3] = self.set_line(cell[3][3], l_line, l_line_style, l_line_color, l_line_width)

    def cut_table(self):
        max_height = 0
        for cell in self.cells:
            if cell[1][2][1] > max_height:
                max_height = cell[1][2][1]
        max_height = max_height + self.margin[2] + self.line_width_1[0]
        self.max_height_cutted = max_height
        self.document = self.document.crop((0,0,self.width,max_height))

    def create_xml_file(self):
        document = minidom.Document()
  
        xml = document.createElement('document') 
        document.appendChild(xml)
        
        table = document.createElement('table')
        xml.appendChild(table)

        min_table = self.cells[0][1][0]
        max_table = self.cells[-1][1][2]

        x0 = str(min_table[0])
        y0 = str(min_table[1])
        x1 = str(max_table[0])
        y1 = str(max_table[1])
        
        points = ('%s,%s %s,%s %s,%s %s,%s' % (x0,y0, x1,y0, x1,y1, x0,y1))

        coords = document.createElement('coords')
        coords.setAttribute('points', points)
        table.appendChild(coords)

        for cell in self.cells:
            # to create cell
            cell_ = document.createElement('cell')
            
            # to add attributes in cell
            cell_.setAttribute('col_start', str(cell[0][0]))
            cell_.setAttribute('row_start', str(cell[0][1]))
            cell_.setAttribute('col_end', str(cell[0][2]))
            cell_.setAttribute('row_end', str(cell[0][3]))
            # add cell to Table
            table.appendChild(cell_)

            # add coordinates points of cell
            points = ""
            for coor in cell[1]:
                points = points + str(coor[0]) + "," + str(coor[1]) + " "
            while points[-1]==" ":
                points = points[:-1]
            coords_cell = document.createElement('coords')
            coords_cell.setAttribute('points', points)
            coords_cell.setAttribute('background', str(cell[4]))
            cell_.appendChild(coords_cell)

            # add values of cell
            for values in cell[2]:
                
                value_ = document.createElement('value')
                value_.setAttribute('type', values[0])
                value_.setAttribute('content', values[1])
                cell_.appendChild(value_)

                font_ = document.createElement('font')
                font_.setAttribute('name', values[2][0])
                font_.setAttribute('style', values[2][1])
                font_.setAttribute('size', str(values[2][2]))
                font_.setAttribute('color', str(values[2][3]))
                font_.setAttribute('horizontal_align', values[2][4])
                font_.setAttribute('vertical_align', values[2][5])
                
                if len (values[2])<7:
                    pass
                    # print("va a dar error")
                    # print(values)
                    # print(cell[2])
                    # print("dio error")
                else:
                    bbx0 = values[2][6][0]
                    bby0 = values[2][6][1]
                    bbx1 = values[2][6][2]
                    bby1 = values[2][6][3]
                    bb = str(bbx0) + "," + str(bby0) + " " + str(bbx1) + "," + str(bby1)
                    font_.setAttribute('bounding_box', bb)
                    value_.appendChild(font_)

            # add lines of cell
            lines_ = document.createElement('lines')
            cell_.appendChild(lines_)

            name_lines=['top', 'right', 'bottom', 'left']
            for i in range(4):
                line = document.createElement(name_lines[i])
                line.setAttribute('line', str(cell[3][i][0]))
                line.setAttribute('style', cell[3][i][1])
                line.setAttribute('color', cell[3][i][2])
                line.setAttribute('width', str(cell[3][i][3]))
                lines_.appendChild(line)



        xml_str = document.toprettyxml(indent ="\t") 
        
        
        with open(self.xml_path, "w", encoding="UTF-8") as f:
            f.write(xml_str)

    def create_csv_file(self):
        df = pd.DataFrame(columns=["xmin", "ymin", "xmax", "ymax", "label", "text_line", "top_left_x", "top_left_y", "top_right_x", "top_right_y", "bottom_right_x", "bottom_right_y", "bottom_left_x", "bottom_left_y", "text_font", "text_style", "size_font", "color", "horizontal_align", "vertical_align"])

        # min_table = self.cells[0][1][0]
        # max_table = self.cells[-1][1][2]
        min_table = [0, 0]
        max_table = [self.width, self.height]

        row = {
            "xmin": int(min_table[0]),
            "ymin": int(min_table[1]),
            "xmax": int(max_table[0]),
            "ymax": int(max_table[1]),
            "label": "table",
            "text_line": "",
            "top_left_x": int(min_table[0]),
            "top_left_y": int(min_table[1]),
            "top_right_x": int(max_table[0]),
            "top_right_y": int(min_table[1]),
            "bottom_right_x": int(max_table[0]),
            "bottom_right_y": int(max_table[1]),
            "bottom_left_x": int(min_table[0]),
            "bottom_left_y": int(max_table[1]),
        }
        df.append(row)

        for cell in self.cells:
            for value in cell[2]:
                if len(value) < 3 or len(value[2]) < 7:
                    # is not a text
                    continue
                else:
                    bbx0 = value[2][6][0]
                    bby0 = value[2][6][1]
                    bbx1 = value[2][6][2]
                    bby1 = value[2][6][3]

                    if int(bbx0) == int(bbx1) or value[1] == None or (type(value[1]) == str and len(value[1]) < 1):
                        continue

                    row = {
                        "xmin": int(bbx0),
                        "ymin": int(bby0),
                        "xmax": int(bbx1),
                        "ymax": int(bby1),
                        "label": "text",
                        "text_line": value[1],
                        "top_left_x": int(bbx0),
                        "top_left_y": int(bby0),
                        "top_right_x": int(bbx1),
                        "top_right_y": int(bby0),
                        "bottom_right_x": int(bbx1),
                        "bottom_right_y": int(bby1),
                        "bottom_left_x": int(bbx0),
                        "bottom_left_y": int(bby1),
                        "text_font": value[2][0],
                        "text_style": value[2][1],
                        "size_font": int(value[2][2]),
                        "color": value[2][3],
                        "horizontal_align": value[2][4],
                        "vertical_align": value[2][5]
                    }
                    df.append(row)

        df.to_csv(self.csv_path, index=False, header=True, line_terminator='\n')
