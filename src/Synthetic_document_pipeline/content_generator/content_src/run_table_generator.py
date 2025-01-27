import sys
sys.path.append('./')

# include classes
from src.Synthetic_document_pipeline.content_generator.content_src.generators.Tablegen import Tablegen
from src.Synthetic_document_pipeline.content_generator.content_src.generators.tables_samples import *

# include utils and configurations
#from generators.utils_old import rand_list

# include external libraries
import PIL, random, datetime


images_folder = "/petrobr/parceirosbr/buscaict/share/document_generator/files_images_document_generator/"



if __name__ == "__main__":
    print("Pillow version:", PIL.__version__)
     
    run_option = 1

    # 4 - rodar paralelo no SD

    if run_option == 1:
        config={
            "size":[[400,1500], [100,1500]],
            "font_name":["arial", "courier", "opensans", "raleway", "roboto", "times"],
            "font_style":"regular",
            "font_size":[10,30],
            "bg_color":["white"],
            "test":True, 
            "return":False, 
            "save":True, 
            }
        


        for i in range(1):
            # header_table_01(config)
            # header_table_pag_01(config)
            # footer_table_pag_01(config)
            # page_table_pag_01(config)
            # page_table_pag_02(config)
            page_table_pag_03(config)
            # test_table(config)

                        

    elif run_option == 4:
        config={
            "size":[[600,1000], [1400,2400]],
            "font_name":["arial", "courier", "opensans", "raleway", "roboto", "times"],
            "font_style":"regular",
            "font_size":[10,30],
            "bg_color":["white"],
            "test":False, 
            "return":False, 
            "save":True, 
            }
        



        # header_table_01([config])
        # header_table_pag_01([config])
        # footer_table_pag_01([config])
        # page_table_pag_01([config])
        # page_table_pag_02([config])
        # page_table_pag_03([config])
        # test_table([config])

        cores = cpu_count()
        list_generator = [
            # (header_table_01, (config), 100),
            # (header_table_pag_01, (config), 100),
            # (footer_table_pag_01, (config), 100),
            # (page_table_pag_01, (config), 100),
            # (page_table_pag_02, (config), 5000),
            # (page_table_pag_03, (config), 5000),
            (page_table_pag_07, (config), 5000),
        ]

        list_generator_sem = [
            # (page_table_pag_01_sem, (config), 4000),
            # (page_table_pag_03_sem, (config), 4000),
            # (page_table_pag_05_sem, (config), 4000),
            (page_table_pag_06_sem, (config), 100)
        ]

        list_generator_com = [
            (page_table_pag_01_com, (config), 4000),
            (page_table_pag_03_com, (config), 4000),
            (page_table_pag_05_com, (config), 4000),
            (page_table_pag_06_com, (config), 4000)
        ]

        


        for element in list_generator:
            runs = element[2]
            print("")
            with Pool(processes=cores) as p:
                with tqdm.tqdm(total=runs) as pbar:
                    for i, _ in enumerate(p.imap_unordered(element[0], [element[1]] * runs)):
                        pbar.update()
                        
                        