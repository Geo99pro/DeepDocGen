import sys

from src.Synthetic_document_pipeline.content_generator.content_src.config.settings import FUNCTIONS, GRAPH_COLORS
from src.Synthetic_document_pipeline.content_generator.content_src.generators.TextFigure import TextFigure
sys.path.append('./')

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import LinearLocator

from PIL import Image
import random
import time
import glob

from src.Synthetic_document_pipeline.content_generator.content_src.generators.TextFigure import TextFigure
from src.Synthetic_document_pipeline.content_generator.content_src.generators.TextFigure import *
from src.Synthetic_document_pipeline.content_generator.content_src.utils.generator_utils import *

import os

class Plotgen():
    def __init__(self, config):
        self.config = config
        self.test = self.config["test"]
        self.output_path = self.config["output_path"]
        self.type_plot=self.config["type_plot"]
        if "file_name" in self.config:
            self.file_name = self.config["file_name"]
        else:
            self.file_name = ""
        self.size = self.config["size"]
        self.init_values()
        
    def init_values(self):
        # self.output_path
        os.makedirs(self.output_path,exist_ok=True)
        if self.test:
            self.png_path = "src/temp/document_test.png"
            self.xml_path = "src/temp/document_test.xml"

    def plot_line(self):
        # Data for plotting
        x = np.arange(0.0, 1.0, 0.01)
        
        lines = random.randint(1,4)
        y=np.zeros([lines, len(x)])
        
        for i in range(lines):
            number_of_functions = random.randint(0,10)
            # number_of_functions = 1
            y[i] = self.generate_function(x, random.choice(FUNCTIONS))*random.uniform(0.1,10)
            for n in range(number_of_functions):
                y[i] = y[i] + (self.generate_function(x, random.choice(FUNCTIONS)) * random.uniform(0.1,10)) + (random.uniform(0.1,10)) 
        
        if "ratio" in self.config:
            image_ratio_h = self.config["ratio"][0]
            image_ratio_v = self.config["ratio"][1]
        else:
            image_ratio_h = random.randint(3,9)
            image_ratio_v = random.randint(3,9)
        self.fig, self.ax = plt.subplots(figsize=(image_ratio_h,image_ratio_v))

        for y_ in y:
            self.ax.plot(x, y_)
        
        # borders
        self.set_borders(style="plot")
        
    def plot_pcolormesh(self):
        np.random.seed(random.randint(0,9999))
        x_len = random.randint(5,20)
        y_len = random.randint(5,20)
        Z = np.random.rand(y_len, x_len)

        x = np.arange(0.5, 1.5+x_len, 1)
        y = np.arange(0.5, 1.5+y_len, 1)


        if "ratio" in self.config:
            image_ratio_h = self.config["ratio"][0]
            image_ratio_v = self.config["ratio"][1]
        else:
            image_ratio_h = random.randint(3,9)
            image_ratio_v = random.randint(3,9)
        self.fig, self.ax = plt.subplots(figsize=(image_ratio_h,image_ratio_v))

        color_map = random.choice(GRAPH_COLORS)

        im = self.ax.pcolormesh(x, y, Z, cmap=color_map)
        if random.choice([True,False]):
            self.fig.colorbar(im, ax=self.ax)
            cbar = self.ax.collections[0].colorbar
            cbar.set_ticks([])
        self.set_borders(style="plot")

    def plot_pcolormesh2(self):
        # make these smaller to increase the resolution
        dx, dy = random.randint(1,50)/100, random.randint(1,50)/100

        # generate 2 2d grids for the x & y bounds
        y_lim = random.randint(2,20)
        x_lim = random.randint(2,20)
        y, x = np.mgrid[slice(1, y_lim + dy, dy),
                        slice(1, x_lim + dx, dx)]
        
        if random.random() < 0.5:
            z = np.sin(x)**random.randint(1,10)
        else:
            z = np.cos(x)**random.randint(1,10)

        
        if random.random() < 0.5:
            z = z + np.cos(1 + y*x) * np.cos(2 * np.pi * random.uniform(0.1, 5))
        else:
            z = z + np.sin(1 + y*x) * np.sin(2 * np.pi * random.uniform(0.1, 5))

        if random.choice([True, False]):
            for _ in range(random.randint(1,5)):
                if random.random() < 0.5:
                    z = z + np.sin(x*random.uniform(0.1,10))**random.randint(1,10)
                else:
                    z = z + np.cos(x*random.uniform(0.1,10))**random.randint(1,10)

                if random.random() < 0.5:
                    z = z + np.cos(1 + y*x*random.uniform(0.1,10)) * np.cos(2 * np.pi * random.uniform(0.1, 5))
                else:
                    z = z + np.sin(1 + y*x*random.uniform(0.1,10)) * np.sin(2 * np.pi * random.uniform(0.1, 5))


        # x and y are bounds, so z should be the value *inside* those bounds.
        # Therefore, remove the last value from the z array.
        z = z[:-1, :-1]
        levels = MaxNLocator(nbins=15).tick_values(z.min(), z.max())


        # pick the desired colormap, sensible levels, and define a normalization
        # instance which takes data values and translates those into levels.
        cmap = plt.get_cmap('PiYG')
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

        if "ratio" in self.config:
            image_ratio_h = self.config["ratio"][0]
            image_ratio_v = self.config["ratio"][1]
        else:
            image_ratio_h = random.randint(3,9)
            image_ratio_v = random.randint(3,9)
        self.fig, self.ax = plt.subplots(figsize=(image_ratio_h,image_ratio_v))
        

        color_map = random.choice(GRAPH_COLORS)
        if random.random() < 0.5:
            im = self.ax.pcolormesh(x, y, z, cmap=color_map, norm=norm)
            self.fig.colorbar(im, ax=self.ax)
            
            cbar = self.ax.collections[0].colorbar
            cbar.set_ticklabels([])

            self.set_borders(style="plot")

            cbar = self.ax.collections[0].colorbar


        else:
            # contours are *point* based plots, so convert our bound into point
            # centers
            cf = self.ax.contourf(x[:-1, :-1] + dx/2.,
                            y[:-1, :-1] + dy/2., z, levels=levels,
                            cmap=color_map)
            
            if random.choice([True, False]):
                self.fig.colorbar(cf, ax=self.ax)
            self.set_borders(style="plot")

    def plot_map(self, image_files):
        images_path = "/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/maps/"
        image_file = random.choice(return_images_files(images_path))

        img = Image.open(image_file)
        width, height = img.size
        # crop the image
        scale_factor = random.randint(20,95)/100
        cropped_width = int(width*scale_factor)
        cropped_height = int(height*scale_factor)
        cropped_x0 = random.randint(0, width-cropped_width-1)
        cropped_y0 = random.randint(0, height-cropped_height-1)
        cropped_x1 = cropped_x0 + cropped_width
        cropped_y1 = cropped_y0 + cropped_height
        img = img.crop((cropped_x0, cropped_y0, cropped_x1, cropped_y1))

        # plot the image
        max_wh = max(width, height)
        prop_w = (width*8/max_wh)
        prop_h = (height*8/max_wh)
        if random.random() < 0.3:
            border = 0
        else:
            border = random.uniform(0,0.1)
        self.fig, self.ax = plt.subplots(figsize=(prop_w,prop_h))


        
        self.set_borders(style="image")

        self.ax.imshow(img)
        # self.fig.tight_layout()

    def plot_texture(self):
        images_path = "/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/textures/"
        image_file = random.choice(return_images_files(images_path))

        img = Image.open(image_file)
        width, height = img.size
        
        # crop the image
        scale_factor = random.randint(20,95)/100
        cropped_width = int(width*scale_factor)
        cropped_height = int(height*scale_factor)
        cropped_x0 = random.randint(0, width-cropped_width-1)
        cropped_y0 = random.randint(0, height-cropped_height-1)
        cropped_x1 = cropped_x0 + cropped_width
        cropped_y1 = cropped_y0 + cropped_height
        img = img.crop((cropped_x0, cropped_y0, cropped_x1, cropped_y1))

        # plot the image
        max_wh = max(width, height)
        prop_w = (width*8/max_wh)
        prop_h = (height*8/max_wh)
        self.fig, self.ax = plt.subplots(figsize=(prop_w,prop_h))
        self.ax.imshow(img)
        self.set_borders(style="image")

    def plot_bars(self):
        if "ratio" in self.config:
            image_ratio_h = self.config["ratio"][0]
            image_ratio_v = self.config["ratio"][1]
        else:
            image_ratio_h = random.randint(3,9)
            image_ratio_v = random.randint(3,9)
        self.fig, self.ax = plt.subplots(figsize=(image_ratio_h,image_ratio_v))

        
        # random parameters for histogram
        bins_h = random.randint(10, 50) if random.random() < 0.5 else random.randint(2, 10)
        bar_color = random_color_hex("color")
        edge_color = random_color_hex("dark")
        alpha_ = random.uniform(0.3, 0.9) if random.random() < 0.7 else 1
        orientation_ = random.choice(['vertical', 'horizontal'])
        bar_width = random.uniform(0.3, 0.9) if random.random() < 0.7 else 1
        cumulative_ = False if random.random() < 0.8 else True

        # bins_h, orientation_, bar_width, cumulative_ = 10, "vertical", 0.8, False

        

        
        x_option = random.choice(['normal', 'random', 'random'])
        x_option = 'normal'
        if x_option == "normal":
            mu = random.randint(50,200)
            sigma = random.randint(5,20)
            x = mu + sigma * np.random.randn(random.randint(1000, 10000))
        else:
            x = list()
            for i in range(bins_h):
                x.extend([i+1]*random.randint(1,10))

        

        
        


        

        # the histogram of the data
        n, bins, patches = self.ax.hist(x, bins=bins_h,
                            facecolor= bar_color , alpha=alpha_, orientation=orientation_,
                            ec=edge_color, rwidth=bar_width, cumulative=cumulative_)
        


        # borders
        self.set_borders(style="plot")

    def plot_3dsurface(self):
        self.create_fig_ax(style="3d")

        # Make data.
        range_ = random.randint(2,20)
        step = random.randint(1,100)/100
        X = np.arange(-range_, range_, step)
        Y = np.arange(-range_, range_, step)
        X, Y = np.meshgrid(X, Y)
        R = np.sqrt(X**2 + Y**2)

        number_of_functions = random.randint(0,3)

        function = random.choice(FUNCTIONS)
        Z = self.generate_function_2d(R, function)
        for n in range(number_of_functions):
            function = random.choice(FUNCTIONS)
            Z = Z + (self.generate_function(R, function) * random.uniform(0.1,10))

        color_map = random.choice(GRAPH_COLORS)

        # Plot the surface.
        surf = self.ax.plot_surface(X, Y, Z, cmap=color_map,
                            linewidth=0, antialiased=False)

        # Customize the z axis.
        self.ax.zaxis.set_major_locator(LinearLocator(10))
        # A StrMethodFormatter is used automatically
        self.ax.zaxis.set_major_formatter('{x:.02f}')

        # Add a color bar which maps values to colors.
        if random.choice([True,False]):
            self.fig.colorbar(surf, shrink=0.5, aspect=5)
            cbar = self.ax.collections[0].colorbar
            cbar.set_ticks([])
            
        # borders
        self.set_borders(style="plot")

    def create_fig_ax(self, style="3d"):
        image_ratio_h = random.randint(3,9)
        image_ratio_v = random.randint(3,9)
        dpi_ = random.randint(75,300) if random.random() < 0.8 else random.randint(40,80)
        if style == "3d":
            image_ratio_h = random.randint(5,8)
            image_ratio_v = image_ratio_h + random.randint(-2,2)
            self.fig, self.ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(image_ratio_h,image_ratio_v), dpi=dpi_)
        else:
            self.fig, self.ax = plt.subplots(figsize=(image_ratio_h,image_ratio_v), dpi=dpi_)
    
    def modifications(self):
        # grid
        if random.choice([True,False]):
            self.ax.grid()

        # scale
        if self.type_plot == "map" or self.type_plot == "texture":
            if random.random() < -0.1:
                self.ax.set_yscale("symlog")
                self.ax.set_xscale("symlog")
        else:
            # self.ax.set_yscale(random.choice(["linear", "log", "symlog"]))
            self.ax.set_yscale(random.choice(["linear", "symlog"]))
            self.ax.set_xscale(random.choice(["linear", "symlog"]))

        # remove labels
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])
        try:
            self.ax.set_zticklabels([])
        except:
            pass
        # self.fig.tight_layout()
        
    def save_fig(self):
        self.fig.savefig(self.png_path)

    def generate_function(self, x, function):
        if function == "random": return np.random.rand(len(x))
        if function == "sin": return np.sin(2 * np.pi * x * random.uniform(0.1, 5))
        if function == "cos": return np.cos(2 * np.pi * x * random.uniform(0.1, 5))
        if function == "tan": return np.tan(2 * np.pi * x * random.uniform(0.1, 5))
        if function == "exp": return np.exp(x * random.uniform(0.1, 2))
        if function == "expm1": return np.expm1(x * random.uniform(0.1, 2))
        if function == "exp2": return np.exp2(x * random.uniform(0.1, 2))
        if function == "log": return np.log((x+0.1) * random.uniform(0.1, 2))
        if function == "log10": return np.log10((x+0.1) * random.uniform(0.1, 2))

    def generate_function_2d(self, x, function):
        if function == "sin": return np.sin(x)
        if function == "cos": return np.cos(x)
        if function == "tan": return np.tan(x)
        if function == "exp": return np.exp(x * random.uniform(0.1, 2))
        if function == "expm1": return np.expm1(x * random.uniform(0.1, 2))
        if function == "exp2": return np.exp2(x * random.uniform(0.1, 2))
        if function == "log": return np.log((x+0.1) * random.uniform(0.1, 2))
        if function == "log10": return np.log10((x+0.1) * random.uniform(0.1, 2))

    def set_borders(self, style="plot"):
        if style == "plot":
            # borders
            bt = random.uniform(0.01,0.15)
            bb = random.uniform(0.01,0.15)
            bl = random.uniform(0.01,0.15)
            br = random.uniform(0.01,0.15)
            
            self.fig.subplots_adjust(top=1-bt, bottom=0+bb, left=0+bl, right=1-br)
        elif style == "image":
            if random.random() < 0.3:
                bt, bb, bl, br = 0, 0, 0, 0
            else:
                # borders
                bt = random.uniform(0.00,0.15)
                bb = random.uniform(0.00,0.15)
                bl = random.uniform(0.00,0.15)
                br = random.uniform(0.00,0.15)
                
            self.fig.subplots_adjust(top=1-bt, bottom=0+bb, left=0+bl, right=1-br)
        else:
            # borders
            bt = random.uniform(0.01,0.15)
            bb = random.uniform(0.01,0.15)
            bl = random.uniform(0.01,0.15)
            br = random.uniform(0.01,0.15)
            
            self.fig.subplots_adjust(top=1-bt, bottom=0+bb, left=0+bl, right=1-br)
            

def create_plot_text(parameters):
    if "size" in parameters:
        prop = min(parameters["size"])/4
        parameters["ratio"] = [4,max(parameters["size"])/prop]
    else:
        parameters["ratio"] = [4,4]
    # output_path, test_document, type_plot, file_name = parameters
    graph = Plotgen(parameters)
    type_plot = parameters["type_plot"]
    if type_plot == "line":
        graph.plot_line()
    elif type_plot == "pcolormesh":
        graph.plot_pcolormesh()
    elif type_plot == "pcolormesh2":
        graph.plot_pcolormesh2()
    elif type_plot == "map":
        graph.plot_map()
    elif type_plot == "texture":
        graph.plot_texture()
    elif type_plot == "bars":
        graph.plot_bars()
    elif type_plot == "3dsurface":
        graph.plot_3dsurface()
    else:
        graph.plot_line()
    
    graph.modifications()
    
    # plot text
    #################################################

    image = TextFigure(parameters)
    
    image.load_img_plot(graph)
    
    # graph.fig.cla()
    graph.ax.cla()
    plt.close(graph.fig)

    
    
    if image.height < 400:
        image.font_size = int(image.height*(random.uniform(4,6))/100)
    else:
        image.font_size = int(image.height*(random.uniform(3,5))/100)

    if image.document.mode == "L":
        image.document = image.document.convert('RGB')

    # plot random lines
    if random.random() < 0.1:
        image.plot_random_lines()

    
    image.init_csv()
    
    if random.random() < 0.6:
        universal_angle = 0
    else:
        universal_angle = random.uniform(-100,100)
    
    if random.random() < 0.5:
        angle_variability = 0
    else:
        angle_variability = random.randint(0,30)
    for i in range(random.randint(5,25)):
        angle = universal_angle + random.uniform(-angle_variability,angle_variability)
        image.print_text(angle)

    # image.check_csv()
    image.save_image()
    return image
    

def create_plot(output_path="src/temp", test_document=True, type_plot="line"):
    graph = Plotgen({'test':test_document, 'output_path':output_path, 'type_plot':type_plot, 'size':[400, 400]})
    if type_plot == "line":
        graph.plot_line()
    elif type_plot == "pcolormesh":
        graph.plot_pcolormesh()
    elif type_plot == "pcolormesh2":
        graph.plot_pcolormesh2()
    elif type_plot == "map":
        graph.plot_map()
    elif type_plot == "texture":
        graph.plot_texture()
    elif type_plot == "bars":
        graph.plot_bars()
    elif type_plot == "3dsurface":
        graph.plot_3dsurface()
    else:
        graph.plot_line()

    graph.modifications()
    
    # plot text
    #################################################
    image = TextFigure({'test': True})
    
    image.image = "src/temp/graph_test.png"

    image.load_img_plot(graph)
    
    # graph.fig.cla()
    graph.ax.cla()
    plt.close(graph.fig)

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
        # image.print_text(angle)

    image.save_image()
    


if __name__ == "__main__":
    now = datetime.datetime.now()
    dataset_name = "plots_{:04d}_{:02d}_{:02d}".format(now.year, now.month, now.day)
    output_path_sub = "/petrobr/parceirosbr/buscaict/share/document_generator/datasets/"
    output_path = output_path_sub + dataset_name + "/"

    run_option = 1

    # 1 - rodar um documento e salvar no output/document_test.png
    # 2 - rodar um documento como se fosse no SD
    # 4 - rodar paralelo no SD
    # 6 - crop screenshot maps images
    # 7 - test random image and csv
    # 20 - join original and inferenced images

    if run_option == 1:
        test_document = True
        type_plots = ["line", "pcolormesh", "pcolormesh2", "map", "texture", "bars", "3dsurface"]
        type_plot = random.choice(type_plots)
        # type_plot = "line"
        file_name = "test_02"

        plot_config={
				"size": [400, 400],
				"test":test_document,
                "output_path": output_path,
                "type_plot": type_plot,
                "file_name": file_name,
			}
        create_plot_text(plot_config)
        # create_plot(parameters)
    elif run_option == 2:
        print("option 2")
        print("dataset_name: ", dataset_name)
        print("output_path_sub: ", output_path_sub)
        print("output_path: ", output_path)
        print()

        test_document = False
        type_plot = "line"
        type_plots = ["line", "pcolormesh", "pcolormesh2", "map", "texture"]
        type_plot = random.choice(type_plots)
        plot_config={
				"size": [200, 200],
				"test":test_document,
                "output_path": output_path,
                "type_plot": type_plot,
			}
        create_plot_text(plot_config)

        # for type_plot in ["line", "pcolormesh", "pcolormesh2", "map"]:
        #     parameters = [output_path, test_document, type_plot]
        #     create_plot_text(parameters)
    elif run_option == 4:
        test_document = False

        cores = cpu_count()
        factor = 1 * 100

        list_generator = [
            ["line", 3 * factor],
            ["pcolormesh", 1 * factor],
            ["pcolormesh2", 1 * factor],
            ["map", 2 * factor],
            ["texture", 3 * factor],
            ["bars", 3 * factor],
            ["3dsurface", 3 * factor],
        ]

        total_set_images = len(list_generator)
        total_plots = 0
        for element in list_generator: total_plots += element[1]


        set_image = 1
        total_start_time_mp = time.time()
        partial_images_ready = 0
        print()
        print("############################################################################")
        print("#                 -- image plots generator - ICA - 2021 --                 #")
        print("############################################################################")
        print()
        print("starting dataset with", total_set_images, "sets of plots and", total_plots, "images")
        for element in list_generator:
            start_time_mp = time.time()
            runs = element[1]
            parameters = [output_path, test_document, element[0]]
            plot_config={
				"size": [200, 200],
				"test":test_document,
                "output_path": output_path,
                "type_plot": element[0],
			}
            with Pool(processes=cores) as p:
                with tqdm.tqdm(total=runs) as pbar:
                    for i, _ in enumerate(p.imap_unordered(create_plot_text, [plot_config] * runs)):
                        pbar.update()
            end_time_mp = time.time()
            partial_images_ready += runs
            print(set_image, "set image of", total_set_images, " -> ", element[0], " -> Cores: ", cores, " | Docs: ", runs, " | Time: ",
                round(end_time_mp - start_time_mp, 4), " s | Avg: ",
                round((end_time_mp - start_time_mp) / runs, 4),
                " | images ready: ", partial_images_ready, "of: ", total_plots)
            set_image += 1
        total_end_time_mp = time.time()

        print("\n-----------------------------------------------------------------")
        print("total time for the entire dataset with ", total_plots, " images: ",
              round(total_end_time_mp - total_start_time_mp, 2), " seconds")
        print("average time: ", round((total_end_time_mp - total_start_time_mp) / total_plots, 4),
              "seconds")
    elif run_option == 6:
        images_path = "/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/maps/999"
        image_files = return_images_files(images_path)

        for t, test_image in enumerate(image_files):
            print(t, " of ", len(image_files))
            
            original = Image.open(test_image)

            dirname = os.path.dirname(test_image)
            basename = os.path.basename(test_image)
            path_new = os.path.join(dirname, "ready", basename)

            width, height = original.size   # Get dimensions
            # cropped_example = original.crop((105, 0, 1750, 1060))
            cropped_example = original.crop((0, 0, width, 980))

            # cropped_example.savefig(self.png_path)
            cropped_example.save(path_new)
    elif run_option == 7:
        output_path_sub
        dataset_folders = output_path_sub + "plots*/"
        last_dataset_path= glob.glob(dataset_folders)[-1]
        image_files = return_images_files(last_dataset_path)
        
        image_path = random.choice(image_files)
        csv_path = os.path.splitext(image_path)[0] + ".csv"
        # print(image_path)
        # print(csv_path)

        if True:
            png_path_out="output/boxes_from_csv.png"
            png_path_out="output/document_test.png"
            thickness_line=3
            thickness_bb=5
            text_label=True
            prints=False
            img = Image.open(image_path)
            width, height = img.size
            document = Image.new("RGB", (width, height), color="white")
            document.paste(img, (0,0))
            draw = ImageDraw.Draw(document)
            
            fontsize=int(height/100)
            
            csv_df = pd.read_csv(csv_path) 
            i=0
            for index, row in csv_df.iterrows():
                if prints: print(i, int(row[0]), int(row[1]), int(row[2]), int(row[3]), row[5])
                if i<0:
                    pass
                else:
                    if prints: print(int(row[0]), int(row[1]), int(row[2]), int(row[3]))
                    line_width_bb = 1
                    draw.rectangle((int(row[0]), int(row[1]), int(row[2]), int(row[3])), fill=None, outline="red", width=line_width_bb)

                    line_width = 1
                    draw.line((int(row[6]), int(row[7]), int(row[8]), int(row[9])), fill="blue", width=line_width)
                    draw.line((int(row[8]), int(row[9]), int(row[10]), int(row[11])), fill="blue", width=line_width)
                    draw.line((int(row[10]), int(row[11]), int(row[12]), int(row[13])), fill="blue", width=line_width)
                    draw.line((int(row[12]), int(row[13]), int(row[6]), int(row[7])), fill="blue", width=line_width)
                i += 1

        document.save(png_path_out)
    elif run_option == 10:
        folder_path = "/petrobr/parceirosbr/buscaict/share/document_generator/temporary_files/"
        file_images = return_images_files(folder_path)
        print("*************")
        for file_im in file_images:
            print(file_im)
        file_images.sort()
        print("*************")
        print(file_images)
        print("*************")
        for file_im in file_images:
            print(file_im)
        if len(file_images)>0:
            file_image = file_images[-1]
        else:
            file_image = "output/document_test.png"
        print(file_image)
    elif run_option == 20:
        base_path = "/petrobr/parceirosbr/buscaict/share/document_generator/results/plots_generator/2021_09_23/"
        original_path = base_path + "original/"
        result_path = base_path + "result/"
        join_path = base_path + "join/"

        original_images = glob.glob(original_path+"*")
        original_image = original_images[:2]


        for original_image in original_images[:5]:
            img = Image.open(original_image)
            img_size = img.size
            
            basename = os.path.basename(original_image)
            result_image = os.path.join(result_path, basename)
            join_image = os.path.join(join_path, basename)

            result = Image.open(result_image)
            result = result.resize(img_size)

            
            document = Image.new("RGB", (img_size[0]*2, img_size[1]), color="white")
            document_draw = ImageDraw.Draw(document)
            
            

            
            document.paste(img, (0,0))
            document.paste(result, (img_size[0],0))
            # document.save("output/document_test.png")
            document_draw.line((img_size[0], 0, img_size[0], img_size[1]), fill="black", width=2)
            document.save(join_image)

    elif run_option == 100:
        print("teste de codigo")
        width = 800
        height = 600
        min_hw = min(width, height)
        prop = min_hw/4
        prop2 = max(width, height)/prop
        print(4, prop2)


