import io
import sys
from src.Synthetic_document_pipeline.content_generator.content_src.config.config import Config
from src.Synthetic_document_pipeline.content_generator.content_src.utils.random_utils import random_color

from src.Synthetic_document_pipeline.content_generator.content_src.utils.text_utils import generate_font, request_words
sys.path.append('./')

import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import PIL

import time, datetime, os, tqdm, math
#from numpy.lib.npyio import _save_dispatcher
import xml.etree.ElementTree as ET
from cv2 import *
from datetime import datetime
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from src.Synthetic_document_pipeline.content_generator.content_src.utils.generator_utils import rotate_around_point_highperf
from src.Synthetic_document_pipeline.content_generator.content_src.utils.generator_utils import *


from multiprocessing import Pool, cpu_count
from tqdm.contrib.concurrent import process_map  # or thread_map






class TextFigure():
    def __init__(self, text_config):
        self.config = text_config

        self.init_values()

    def init_values(self):
        self.set_name()

        # font
        self.fonts_names = ["arial", "courier", "opensans", "raleway", "roboto", "times"]
        self.font_name = random.choice(self.fonts_names)
        
        self.font_size = 30

        self.font_styles = ["regular", "bold", "italic", "bolditalic"]
        self.font_style = random.choice(self.font_styles)

        self.font = generate_font(Config.fonts_folder, font_name=self.font_name, font_style="regular", font_size=self.font_size)
        self.font_color = "red"
        self.font_color = "black"
        #self.line_height = self.font.getsize('gh')[1]
        self.line_height = self.font.getbbox('hg')[3]-self.font.getbbox('hg')[1]

    def set_name(self):
        self.file_basename_ = "src/temp/document_test.png"
        self.file_basename = "src/temp/document_test"
        self.png_path = "src/temp/document_test.png"
        self.xml_path = "src/temp/document_test.xml"
        self.csv_path = "src/temp/document_test.csv"
    
    def load_img(self):
        self.document = Image.open(self.image)
        if "size" in self.config:
            self.size = tuple(self.config["size"])
            self.document = self.document.resize(self.size)

        self.draw = ImageDraw.Draw(self.document)
        self.width = self.document.size[0]
        self.height = self.document.size[1]
    
    def load_img_plot(self, graph):
        """Convert a Matplotlib figure to a PIL Image and return it"""
        buf = io.BytesIO()
        graph.fig.savefig(buf)
        buf.seek(0)
        img = Image.open(buf)
        self.document = img.resize(tuple(graph.size))
        self.draw = ImageDraw.Draw(self.document)
        self.width = self.document.size[0]
        self.height = self.document.size[1]
        self.png_path = graph.png_path
        self.csv_path = os.path.splitext(self.png_path)[0] + ".csv"

        
    def init_csv(self):
        self.csv_df_document = pd.DataFrame(columns=["xmin", "ymin", "xmax", "ymax", "label", "text_line", "top_left_x", "top_left_y", "top_right_x", "top_right_y", "bottom_right_x", "bottom_right_y", "bottom_left_x", "bottom_left_y"])

        row = {
            "xmin": int(0),
            "ymin": int(0),
            "xmax": self.width,
            "ymax": self.height,
            "label": "image",
            "text_line": self.file_basename_,
            "top_left_x": "",
            "top_left_y": "",
            "top_right_x": "",
            "top_right_y": "",
            "bottom_right_x": "",
            "bottom_right_y": "",
            "bottom_left_x": "",
            "bottom_left_y": ""
        }
        pd.concat([self.csv_df_document, pd.Series(row)], ignore_index=True)

    def print_text(self, angle):
        skip_print_text = False
        if angle < -90: angle = -90
        if angle > 90: angle = 90
        # self.font_size = 30
        # angle = 30

        
        self.font = generate_font(Config.fonts_folder, font_name=self.font_name, font_style="regular", font_size=self.font_size)
        #self.line_height = self.font.getsize('gh')[1]
        self.line_height = self.font.getbbox('hg')[3]-self.font.getbbox('hg')[1]

        line = self.return_text()

        if random.random() < 0.1:
            color_text = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        else:
            color_text = (0, 0, 0)

        x0_, y0_ = int(self.width/2), int(self.height/2)

        #x1_ = x0_ + self.font.getsize(line)[0]
        x1_ = x0_ + self.font.getbbox(line)[2] - self.font.getbbox(line)[0]
        #y1_ = y0_ + self.font.getsize(line)[1]
        y1_ = y0_ + self.font.getbbox(line)[3] - self.font.getbbox(line)[1]

        while x1_ - x0_ >= self.width-20:
            line = self.return_text()
            x0_, y0_ = int(self.width/2), int(self.height/2)
            #x1_ = x0_ + self.font.getsize(line)[0]
            x1_ = x0_ + self.font.getbbox(line)[2] - self.font.getbbox(line)[0]
            #y1_ = y0_ + self.font.getsize(line)[1]
            y1_ = y0_ + self.font.getbbox(line)[3] - self.font.getbbox(line)[1]

        # rotate text
        p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, bbx0, bby0, bbx1, bby1 = self.rotate_coordinates(angle, x0_, y0_, x1_, y1_)
            
        
        
        # add text
        self.img_txt=Image.new('L', (self.width, self.height))
        self.txt_draw = ImageDraw.Draw(self.img_txt)
        self.txt_draw.text( (x0_, y0_), line,  font=self.font, fill=255)
        w=self.img_txt.rotate(angle,  expand=0)
        
        self.check_coordinates(bbx0, bby0, bbx1, bby1)
        x0_def = random.randint(5, self.width-(bbx1-bbx0)-5) if self.width - (bbx1 - bbx0) - 5 > 5 else 5
        y0_def = random.randint(5, self.height-(bby1-bby0)-5) if self.height - (bby1 - bby0) - 5 > 5 else 5

        if len(self.csv_df_document.index) > 1:
            counter = 0
            while (self.check_overlapping_text(x0_def, y0_def, angle) and not skip_print_text):
                #####################################

                line = self.return_text()
                if counter > 100:
                    # print("mais de 100 tentativas de colocar texto")
                    line = "1"

                if counter > 200:
                    # print("mais de 200 tentativas de colocar texto")
                    line = "1"
                    skip_print_text = True

                x0_, y0_ = int(self.width/2), int(self.height/2)

                #x1_ = x0_ + self.font.getsize(line)[0]
                x1_ = x0_ + self.font.getbbox(line)[2] - self.font.getbbox(line)[0]
                #y1_ = y0_ + self.font.getsize(line)[1]
                y1_ = y0_ + self.font.getbbox(line)[3] - self.font.getbbox(line)[1]

                while x1_ - x0_ >= self.width-20:
                    line = self.return_text()
                    x0_, y0_ = int(self.width/2), int(self.height/2)
                    #x1_ = x0_ + self.font.getsize(line)[0]
                    x1_ = x0_ + self.font.getbbox(line)[2] - self.font.getbbox(line)[0]
                    #y1_ = y0_ + self.font.getsize(line)[1]
                    y1_ = y0_ + self.font.getbbox(line)[3] - self.font.getbbox(line)[1]
            
            

                # rotate text
                p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, bbx0, bby0, bbx1, bby1 = self.rotate_coordinates(angle, x0_, y0_, x1_, y1_)
                    
                
                
                # add text
                self.img_txt=Image.new('L', (self.width, self.height))
                self.txt_draw = ImageDraw.Draw(self.img_txt)
                self.txt_draw.text( (x0_, y0_), line,  font=self.font, fill=255)
                w=self.img_txt.rotate(angle,  expand=0)
                
                self.check_coordinates(bbx0, bby0, bbx1, bby1)
                x0_def = random.randint(5, self.width-(bbx1-bbx0)-5)
                y0_def = random.randint(5, self.height-(bby1-bby0)-5)
                




                #####################################
                # x0_def = random.randint(5, self.width-(bbx1-bbx0)-5)
                # y0_def = random.randint(5, self.height-(bby1-bby0)-5)
                counter += 1

        if not skip_print_text:
            # self.document.paste( ImageOps.colorize(w, (0,0,0), (color_text,color_text,color_text)), (-bbx0+x0_def, -bby0+y0_def),  w)
            self.document.paste( ImageOps.colorize(w, (0,0,0), color_text), (-bbx0+x0_def, -bby0+y0_def),  w)
            
            self.draw = ImageDraw.Draw(self.document)

            x_offset = bbx0-x0_def
            y_offset = bby0-y0_def
            p0x, p0y = p0x-x_offset, p0y-y_offset
            p1x, p1y = p1x-x_offset, p1y-y_offset
            p2x, p2y = p2x-x_offset, p2y-y_offset
            p3x, p3y = p3x-x_offset, p3y-y_offset
            if angle < 0:
                bbx0, bby0, bbx1, bby1 = p3x, p0y, p1x, p2y
            else:
                bbx0, bby0, bbx1, bby1 = p0x, p1y, p2x, p3y

            row = {
                "xmin": bbx0,
                "ymin": bby0,
                "xmax": bbx1,
                "ymax": bby1,
                "label": "text",
                "text_line": line,
                "top_left_x": p0x,
                "top_left_y": p0y,
                "top_right_x": p1x,
                "top_right_y": p1y,
                "bottom_right_x": p2x,
                "bottom_right_y": p2y,
                "bottom_left_x": p3x,
                "bottom_left_y": p3y
            }
            
            pd.concat([self.csv_df_document, pd.Series(row)], ignore_index=True)

    def rotate_coordinates(self, angle, x0_, y0_, x1_, y1_):
        angle_rad = math.radians(angle)
        more_pixe = 0
        p0x, p0y = rotate_around_point_highperf((x0_-more_pixe, y0_-more_pixe), angle_rad, origin=(int(self.width/2), int(self.height/2)))
        p1x, p1y = rotate_around_point_highperf((x1_+more_pixe, y0_-more_pixe), angle_rad, origin=(int(self.width/2), int(self.height/2)))
        p2x, p2y = rotate_around_point_highperf((x1_+more_pixe, y1_+more_pixe), angle_rad, origin=(int(self.width/2), int(self.height/2)))
        p3x, p3y = rotate_around_point_highperf((x0_-more_pixe, y1_+more_pixe), angle_rad, origin=(int(self.width/2), int(self.height/2)))


        p0x, p0y, p1x, p3x = math.floor(p0x), math.floor(p0y), math.floor(p1x), math.floor(p3x)
        p1y, p2x, p2y, p3y = math.floor(p1y), math.floor(p2x), math.floor(p2y), math.floor(p3y)
        if angle < 0:
            bbx0, bby0, bbx1, bby1 = p3x, p0y, p1x, p2y
        else:
            bbx0, bby0, bbx1, bby1 = p0x, p1y, p2x, p3y
        self.points = [p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, bbx0, bby0, bbx1, bby1]
        return p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, bbx0, bby0, bbx1, bby1

    def return_text(self):
        type_content = random.choice(["number", "string"])
        if type_content == "string":
            words, _ = request_words()
            line = " ".join(words)
            # random.choice(["[u.a]", "text", "speed", "test text ()", "test (m/s)", "rua test"])
        elif type_content == "number":
            option = random.choice(["ent", "d1", "d2", "d3", "por_ent", "por_d1", "por_d2"])
            if option == "ent":
                line = str(random.randint(-10000,1000))
            elif option == "d1":
                line = str(random.randint(-10000,1000))+"."+str(random.randint(0,9))
            elif option == "d2":
                line = str(random.randint(-10000,1000))+"."+str(random.randint(0,99))
            elif option == "d3":
                line = str(random.randint(-10000,1000))+"."+str(random.randint(0,999))
            elif option == "por_ent":
                line = str(random.randint(-10000,1000))+"%"
            elif option == "por_d1":
                line = str(random.randint(-10000,1000))+"."+str(random.randint(0,9))+"%"
            elif option == "por_d2":
                line = str(random.randint(-10000,1000))+"."+str(random.randint(0,99))+"%"

        return line

    def check_overlapping_text(self, x0_def, y0_def, angle):
        overlapping_text = False
        p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, bbx0, bby0, bbx1, bby1 = self.points
        offset_bb = 2
        # print(angle)
        # print(self.csv_df_document)
        # print(p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y)
        # print("-----------")

        x_offset = bbx0-x0_def
        y_offset = bby0-y0_def
        p0x, p0y = p0x-x_offset, p0y-y_offset
        p1x, p1y = p1x-x_offset, p1y-y_offset
        p2x, p2y = p2x-x_offset, p2y-y_offset
        p3x, p3y = p3x-x_offset, p3y-y_offset
        if angle < 0:
            bbx0, bby0, bbx1, bby1 = p3x, p0y, p1x, p2y
        else:
            bbx0, bby0, bbx1, bby1 = p0x, p1y, p2x, p3y

        i=0
        for index, row in self.csv_df_document.iterrows():
            if i < 1:
                pass
            else:
                rectangle1 = [bbx0-offset_bb, bby0-offset_bb, bbx1+offset_bb, bby1+offset_bb]
                rectangle2 = [row["xmin"], row["ymin"], row["xmax"], row["ymax"]]
                if isRectangleOverlap(rectangle1, rectangle2):
                    overlapping_text = True
            i += 1
       
        


        return overlapping_text

    def check_coordinates(self, bbx0, bby0, bbx1, bby1):
        x2 = self.width-(bbx1-bbx0)-5
        if 5 >= x2:
            print("self.width-(bbx1-bbx0)-5 ", self.width-(bbx1-bbx0)-5)
            print("self.width", self.width)
            print("bbx1", bbx1)
            print("bbx0", bbx0)
            print("bbx1-bbx0", bbx1-bbx0)
            return False
        else:
            return True

    def calculate_text_size(self):
        self.text_width = 0
        for line in self.lines:
            #if self.font.getsize(line)[0] > self.text_width:
            if self.font.getbbox(line)[2] - self.font.getbbox(line)[0] > self.text_width:
                #self.text_width = self.font.getsize(line)[0]
                self.text_width = self.font.getbbox(line)[2] - self.font.getbbox(line)[0]

    def plot_random_lines(self):
        w = self.width
        h = self.height
        for i in range(random.randint(1,50)):
            x0 = random.randint(-w*2,w*2)
            y0 = random.randint(-h*2,h*2)
            x1 = random.randint(-w*2,w*2)
            y1 = random.randint(-h*2,h*2)
            if random.random() < 0.8:
                color_line = "black"
            else:
                color_line = random_color("RGB")
            # print(color)
            try:
                self.draw.line((x0,y0,x1,y1), fill=color_line, width=random.randint(1,2))
            except:
                pass

    def save_image(self):
        self.document = self.document.convert('RGB')
        path = os.path.split(self.png_path)[0]
        os.makedirs(path, exist_ok=True)
        self.document.save(self.png_path)

    def check_csv(self):
        prints = False
        i = 0
        for index, row in self.csv_df_document.iterrows():
            if i<1:
                pass
            else:
                if prints: print(int(row[0]), int(row[1]), int(row[2]), int(row[3]))
                line_width_bb = 1
                self.draw.rectangle((int(row[0]), int(row[1]), int(row[2]), int(row[3])), fill=None, outline="red", width=line_width_bb)

                line_width = 1
                self.draw.line((int(row[6]), int(row[7]), int(row[8]), int(row[9])), fill="blue", width=line_width)
                self.draw.line((int(row[8]), int(row[9]), int(row[10]), int(row[11])), fill="blue", width=line_width)
                self.draw.line((int(row[10]), int(row[11]), int(row[12]), int(row[13])), fill="blue", width=line_width)
                self.draw.line((int(row[12]), int(row[13]), int(row[6]), int(row[7])), fill="blue", width=line_width)
            i += 1

def create_image(parameters):
    test = parameters["test"]
    size = parameters["size"]

    text_config = {
        "test": test,
        }
    image = TextFigure(parameters)
    
    imgs_path = "/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/textures/"
    image.image = random.choice(return_images_files(imgs_path))
    # image.image = "/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/textures/textura_0_13997_13767361.jpeg"
    # image.image = "output/document_test.png"

    image.load_img()

    image.font_size = 30
    image.font_size = int(image.height*(random.uniform(2,5))/100)

    if image.document.mode == "L":
        image.document = image.document.convert('RGB')

    image.init_csv()
    
    if random.random() < 0.6:
        universal_angle = 0
    else:
        universal_angle = random.uniform(-100,100)
    
    if random.random() < 0.5:
        angle_variability = 0
    else:
        angle_variability = random.randint(0,30)
    for i in range(random.randint(5,30)):
        angle = universal_angle + random.uniform(-angle_variability,angle_variability)
        # angle=30
        image.print_text(angle)

    if test:
        image.check_csv()

    image.save_image()

def isRectangleOverlap(R1, R2):
    if (R1[0]>=R2[2]) or (R1[2]<=R2[0]) or (R1[3]<=R2[1]) or (R1[1]>=R2[3]):
        return False
    else:
        return True


if __name__ == "__main__":
    print("Pillow version:", PIL.__version__)

    # todo: fuentes negras y un poco grises
    # todo: girar imagenes
    # todo: girar textos y boundingbox

    
    run_option = 10000

    # 1 - rodar 1 local serial
    # 4 - rodar paralelo
    # 10 - tables

    if run_option == 1:
        test = True
        let = "aaa"
        parameters = [test, let]
        plot_config={
				"size": [400, 400],
				"test":test,
				"return":True,
			}
        for i in range(1):
            create_image(plot_config)
        

    elif run_option == 4:
        test = False
        parameters = [test, "aaa"]

        cores = cpu_count()
        cores = 12
        factor = 5000
        
        
        with Pool(processes=cores) as p:
            with tqdm.tqdm(total=factor) as pbar:
                for i, _ in enumerate(p.imap_unordered(create_image, [parameters]*factor)):
                    pbar.update()
    
    elif run_option == 6:
        
        path_image = "/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/textures/textura_0_13997_13767361.jpeg"
        document = Image.open(path_image)
        print(document.mode)
        document = document.convert('RGB')
        print(document.mode)
        draw = ImageDraw.Draw(document)
        draw.rectangle((150,150, 300, 350), fill="red", outline="blue", width=5)
        png_path = "output/document_test.png"
        document.save(png_path)

    elif run_option == 30:
        w, h = 500, 500
       
        # creating new Image object
        img = Image.new("RGB", (w, h))

        rects = []
        for i in range(2):
            x0 = random.randint(0,400)
            y0 = random.randint(0,400)
            x1 = random.randint(x0,499)
            y1 = random.randint(y0,499)
            rects.append([x0,y0,x1,y1])

        
        # create rectangle image
        img1 = ImageDraw.Draw(img)  
        for rect in rects:
            img1.rectangle((rect[0], rect[1], rect[2], rect[3]), fill=None, outline ="red")
        img.save("output/document_test.png")

        # check_rectangles(rects[0], rects[1])
        print(isRectangleOverlap(rects[0], rects[1]))


