import sys
sys.path.append('./')

# include classes
from src.Synthetic_document_pipeline.content_generator.content_src.generators.Tablegen import Tablegen
import random
import math
# include utils and configurations

"""
page_table_pag_01:  Tabela com fundos cinzas e linhas espessas
page_table_pag_02:  Tabela com linhas e colunas aleatorias
                    pode juntar celulas da primeira e da última linha
                    pode juntar as duas primeiras linhas por colunas
                    pode colocar colores nos fundos das células
page_table_pag_03:  Tabelas com fundos aleatoreos com ou sem bordas
page_table_pag_04:  Tabela com imagens na celulas
page_table_pag_05:  Tabelas com fundos brancos e cinzas na borda
"""

def generate_table_config(config):
    if type(config["size"][0]) is list:
        size = [random.randint(config["size"][0][0],config["size"][0][1]), random.randint(config["size"][1][0],config["size"][1][1])]
    elif type(config["size"][0]) is int:
        size = config["size"]

    if type(config["font_size"]) is list:
        font_size = random.randint(config["font_size"][0],config["font_size"][1])
    elif type(config["font_size"]) is int:
        font_size = config["font_size"]

    table_config = {
        "size": size,
        "ts_text": [random.choice(config["font_name"]), config["font_style"], font_size],
        "margins": [[0,0]],
        "bg_color": random.choice(config["bg_color"]),
        }

    return table_config

def table_format_1(table_config, test=False, save=False):
    
    table_config = generate_table_config(table_config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    
    if random.random() < 0.3:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,7)
    rows = 100

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(1.5)
        else:
            row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    # coloca todas as linhas
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    
    # parametros para mudar tabela
    merge_row_0 = False
    merge_row_1e2 = False
    merge_last_line = False
    set_color = False
    
    if random.random() < 0.4: merge_row_0 = True
    if random.random() < 0.4: merge_row_1e2 = True
    if random.random() < 0.4: merge_last_line = True
    if random.random() < 0.4: set_color = True

    colums_to_merge = random.randint(1, table_img.columns-1)


    # borda da tabela com linha mais espessa
    if random.random() < 0.3:
        table_img.change_line(row = 0, t_line=1, t_line_width=3)
        table_img.change_line(row = table_img.rows-1, b_line=1, b_line_width=3)
        table_img.change_line(column = 0, l_line=1, l_line_width=3)
        table_img.change_line(column = table_img.columns-1, r_line=1, r_line_width=3)


    # juntar duas primeiras linhas até colums_to_merge
    if table_img.columns > 2:
        if merge_row_1e2:
            for i in range(colums_to_merge):
                table_img.merge_cells(c1=[i,0], c2=[i,1])
            if random.random() < 0.5:
                table_img.change_line(row = 2, t_line=1, t_line_width=3)


    # juntar primeira linha até colums_to_merge
    if table_img.columns > 2 and table_img.rows > 2 :
        if merge_row_0:
            for i in range(colums_to_merge-1):
                table_img.merge_cells(c1=[0,0], c2=[1+i,0])
        if random.random() < 0.5:
            table_img.change_line(column=0, row=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
        if random.random() < 0.5:
            table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)


    # juntar final última linha até colums_to_merge ou desde colums_to_merge
    if table_img.columns > 2 and table_img.rows > 3:
        if merge_last_line:
            if random.random() < 0.5:
                for i in range(colums_to_merge-1):
                    c1_ = [0,table_img.rows-1]
                    c2_ = [1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column=0, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
            else:
                # juntar final última linha desde colums_to_merge
                for i in range(colums_to_merge-1):
                    c1_ = [table_img.columns-colums_to_merge,table_img.rows-1]
                    c2_ = [table_img.columns-colums_to_merge+1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
                    
    


    if set_color:
        table_img.set_color_pred()

    
    table_img.fill_table()

    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    return table_img

def table_format_2(table_config, test=False, save=False):
    table_config = generate_table_config(table_config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.3:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,7)
    
    cols = 5
    rows = 10
    rows = 100

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        row_list.append(round(random.uniform(1,4),1))
        # if random.random() < 0.7:
        #     row_list.append(1)
        # elif random.random() < 0.5:
        #     row_list.append(2)
        # elif random.random() < 0.5:
        #     row_list.append(1.5)
        # else:
        #     row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    
    
    
    
    # parametros para mudar tabela
    merge_row_0 = random.choice([True, False])
    merge_row_1e2 = random.choice([True, False])
    merge_last_line = random.choice([True, False])
    set_color = random.choice([True, False])
    
    colums_to_merge = random.randint(1, table_img.columns-1)


    # borda da tabela com linha mais espessa
    if random.random() < 0.3:
        table_img.change_line(row = 0, t_line=1, t_line_width=3)
        table_img.change_line(row = table_img.rows-1, b_line=1, b_line_width=3)
        table_img.change_line(column = 0, l_line=1, l_line_width=3)
        table_img.change_line(column = table_img.columns-1, r_line=1, r_line_width=3)


    # juntar duas primeiras linhas até colums_to_merge
    if table_img.columns > 2:
        if merge_row_1e2:
            for i in range(colums_to_merge):
                table_img.merge_cells(c1=[i,0], c2=[i,1])
            if random.random() < 0.5:
                table_img.change_line(row = 2, t_line=1, t_line_width=3)


    # juntar primeira linha até colums_to_merge
    if table_img.columns > 2 and table_img.rows > 2 :
        if merge_row_0:
            for i in range(colums_to_merge-1):
                table_img.merge_cells(c1=[0,0], c2=[1+i,0])
        if random.random() < 0.5:
            table_img.change_line(column=0, row=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
        if random.random() < 0.5:
            table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)


    # juntar final última linha até colums_to_merge ou desde colums_to_merge
    if table_img.columns > 2 and table_img.rows > 3:
        if merge_last_line:
            if random.random() < 0.5:
                for i in range(colums_to_merge-1):
                    c1_ = [0,table_img.rows-1]
                    c2_ = [1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column=0, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
            else:
                # juntar final última linha desde colums_to_merge
                for i in range(colums_to_merge-1):
                    c1_ = [table_img.columns-colums_to_merge,table_img.rows-1]
                    c2_ = [table_img.columns-colums_to_merge+1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
                    
    
    # parametros para colocar as linhas
    all_lines = random.choice([True, False])
    first_line_t = random.choice([True, False])
    first_line_b = random.choice([True, False])
    last_line_t = random.choice([True, False])
    last_line_b = random.choice([True, False])
    all_lines_h = random.choice([True, False])
    
    if all_lines:
        table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    if first_line_t:
        table_img.change_line(row=0, t_line=1)
    if first_line_b:
        table_img.change_line(row=0, b_line=1)
    if last_line_t:
        table_img.change_line(row=-1, t_line=1)
    if last_line_b:
        table_img.change_line(row=-1, b_line=1)
    if all_lines_h:
        for col_ in range(table_img.columns-1):
            table_img.change_line(column=col_, r_line=1)

    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)

    fill_multi_line = random.choice([True, False])
    if fill_multi_line:
        center_col_0 = random.choice([True, False])
        for s, size in enumerate(table_img.rows_sizes):
            # print(s, table_img.character_height, size, math.floor(size/(table_img.character_height*1.1)))
            lines = math.floor(size/(table_img.character_height*1.1))
            if lines > 1:
                for c in range(table_img.columns):
                    if random.choice([True, False]):
                        if c == 0:
                            table_img.fill_cell(row=s, column=c, row_column=True, text_prop = [1]*lines, text_align = ["left"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
                        else:
                            table_img.fill_cell(row=s, column=c, row_column=True, text_prop = [1]*lines, text_align = ["center"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
            if center_col_0:
                table_img.fill_cell(row=s, column=0, row_column=True, text_prop = [1]*lines, text_align = ["center"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
            else:
                table_img.fill_cell(row=s, column=0, row_column=True, text_prop = [1]*lines, text_align = ["left"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
    
    table_img.set_color_pred_gray()
    
    table_img.fill_table()

    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    return table_img


#region UNUSED

def init_table(config):
    test = config["test"]
    
    if type(config["size"][0]) is list:
        size = [random.randint(config["size"][0][0],config["size"][0][1]), random.randint(config["size"][1][0],config["size"][1][1])]
    elif type(config["size"][0]) is int:
        size = config["size"]

    if type(config["font_size"]) is list:
        font_size = random.randint(config["font_size"][0],config["font_size"][1])
    elif type(config["font_size"]) is int:
        font_size = config["font_size"]

    table_config = {
        "size": size,
        "ts_text": [random.choice(config["font_name"]), config["font_style"], font_size],
        # "margins": [[0.5,2],[0.5,2],[0.5,2],[0.5,2]],
        "margins": [[0,0]],
        "bg_color": random.choice(config["bg_color"]),
        }

    save = config["save"]

    return test, table_config, save


def header_table_01(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    cols = 5
    rows = 4

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,6),1))
    if col_list[1]<3: col_list[1] = round(random.uniform(2.5,4),1)
    if col_list[2]<3: col_list[2] = round(random.uniform(2.5,4),1)
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1.5)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(2.5)
        else:
            row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    # self.draw_total_table()
    
    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    table_img.change_font(row="all", horizontal_align="center")
    
    table_img.delete_lines()

    table_img.merge_cells(c1=[0,0], c2=[0,1])
    table_img.merge_cells(c1=[0,0], c2=[0,2])
    table_img.merge_cells(c1=[0,0], c2=[0,3])

    table_img.merge_cells(c1=[2,0], c2=[3,0])

    table_img.merge_cells(c1=[1,1], c2=[2,1])

    table_img.merge_cells(c1=[1,2], c2=[1,3])
    table_img.merge_cells(c1=[2,2], c2=[2,3])
    
    table_img.merge_cells(c1=[1,2], c2=[2,2])

    table_img.merge_cells(c1=[3,1], c2=[4,1])
    table_img.merge_cells(c1=[3,2], c2=[4,2])
    table_img.merge_cells(c1=[3,3], c2=[4,3])



    table_img.fill_table()
    table_img.change_content(column = 0, row = 0, row_column = True, type_value="img", value="_logo")
    
    table_img.fill_cell(row=0, column=1, row_column=True, text_prop = [1.3], text_align = ["center"])
    
    table_img.fill_cell(row=2, column=1, row_column=True, text_prop = [0.5, 1, 1], text_align = ["left", "center", "center"], f_style=["regular", "bold", "bold"], len_text=["word", "text", "word"])
    table_img.fill_cell(row=0, column=4, row_column=True, text_prop = [0.5, 1], text_align = ["left", "center"])
    table_img.fill_cell(row=0, column=2, row_column=True, text_prop = [0.5, 1], text_align = ["left", "center"], f_style=["bold", "regular"])

    table_img.fill_cell(row=1, column=3, row_column=True, text_prop = [0.5, 1], text_align = ["left", "center"])
    
    table_img.fill_cell(row=2, column=3, row_column=True, text_prop = [])
    
    
    table_img.print_cells()
    # table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1, r_line_color="red", l_line_color="red", b_line_color="red", t_line_color="red" )
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    table_img.draw_lines()
    table_img.cut_table()

    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def header_table_pag_01(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    cols = 3
    rows = 4

    col_list=[]
    col_list.append(round(random.uniform(8,14),1))
    col_list.append(round(random.uniform(1,2.5),1))
    col_list.append(round(random.uniform(2,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1.5)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(2.5)
        else:
            row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    # table_img.init_table(cols=[11,1,2], rows=[1.6,1.2,1,1,1.7])
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()
    
    
    
    # self.draw_total_table()
    
    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    table_img.change_font(row="all", horizontal_align="center")
    
    table_img.delete_lines()

    table_img.merge_cells(c1=[0,2], c2=[0,3])
    table_img.merge_cells(c1=[1,0], c2=[2,0])

    table_img.fill_table()
    
    
    
    table_img.change_font(column=1, horizontal_align="left")
    table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.5], text_align = ["center"], f_style=["bold"], len_text=["text"])
    table_img.fill_cell(row=0, column=1, row_column=True, text_prop = [1.2], text_align = ["center"], f_style=["bold"], len_text=["word"])

    table_img.fill_cell(row=1, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])
    table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [0.8, 0.8], text_align = ["center", "center"], len_text=["text", "text"])

    table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    table_img.fill_cell(row=1, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    table_img.fill_cell(row=2, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    table_img.fill_cell(row=3, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    table_img.fill_cell(row=4, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    
    
    
    table_img.print_cells()
    # table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1, r_line_color="red", l_line_color="red", b_line_color="red", t_line_color="red" )
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def footer_table_pag_01(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    cols = random.randint(1,3)
    rows = random.randint(2,4)

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(round(random.uniform(0.8,1.2),1))
        elif random.random() < 0.5:
            col_list.append(round(random.uniform(1.8,2.2),1))
        elif random.random() < 0.5:
            col_list.append(round(random.uniform(1.3,1.7),1))
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.5:
            row_list.append(1.0)
        elif random.random() < 0.4:
            row_list.append(1.5)
        elif random.random() < 0.4:
            row_list.append(2.0)
        elif random.random() < 0.5:
            row_list.append(2.5)
        else:
            row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()
    
    # self.draw_total_table()
    
    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "str"
    table_img.create_cells()

    table_img.change_font(row=0, font_style="bold", font_size=0, font_color=None, row_column=False)
    
    table_img.change_font(row="all", horizontal_align="center")
    
    table_img.delete_lines()

    table_img.fill_table()
    
    
    
    table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1], text_align = ["center"], f_style=["bold"], len_text=["text"])
    table_img.fill_cell(row=0, column=1, row_column=True, text_prop = [1], text_align = ["center"], f_style=["bold"], len_text=["text"])
    table_img.fill_cell(row=0, column=2, row_column=True, text_prop = [1], text_align = ["center"], f_style=["bold"], len_text=["text"])

    table_img.fill_cell(row=1, column=0, row_column=True, text_prop = [1], text_align = ["center"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=1, column=1, row_column=True, text_prop = [1], text_align = ["center"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=1, column=2, row_column=True, text_prop = [1], text_align = ["center"], f_style=["regular"], len_text=["text"])
    
    
    
    table_img.print_cells()
    # table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1, r_line_color="red", l_line_color="red", b_line_color="red", t_line_color="red" )
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_01(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    cols = 8
    rows = 12
    
    # table_img.init_table(cols=[3,1,1,1,1,1,1,1], rows=[1,1,1,2,2,2,1,1,1,1,1,1])

    col_list=[]
    for i in range(cols):
        if random.random() < 0.8:
            col_list.append(round(random.uniform(0.8,1.2),1))
        elif random.random() < 0.5:
            col_list.append(round(random.uniform(1.8,2.2),1))
        else:
            col_list.append(round(random.uniform(1.3,1.7),1))
    if col_list[0]<3: col_list[0] = round(random.uniform(2.5,5),1)
    
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1.5)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(2.5)
        else:
            row_list.append(round(random.uniform(1,4),1))
    if col_list[3]<2: col_list[3] = round(random.uniform(2,3),1)
    if col_list[4]<2: col_list[4] = round(random.uniform(2,3),1)
    if col_list[5]<2: col_list[5] = round(random.uniform(2,3),1)


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()
    


    # self.draw_total_table()
    
    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    table_img.change_font(row="all", horizontal_align="center")
    
    table_img.delete_lines()

    table_img.merge_cells(c1=[0,0], c2=[0,1])

    table_img.merge_cells(c1=[1,0], c2=[2,0])
    table_img.merge_cells(c1=[1,0], c2=[3,0])
    table_img.merge_cells(c1=[1,0], c2=[4,0])

    table_img.merge_cells(c1=[5,0], c2=[6,0])
    table_img.merge_cells(c1=[5,0], c2=[7,0])

    for i in range(5):
        table_img.merge_cells(c1=[2,11], c2=[3+i,11])
    
    table_img.fill_table()

    table_img.fill_cell(row=11, column=2, row_column=True, text_prop = [])
    table_img.fill_cell(row=11, column=2, row_column=True, text_prop = [])

    
    
        
    
    
    
    # table_img.change_font(column=1, horizontal_align="left")
    
    
    table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.2], text_align = ["left"], f_style=["bold"], len_text=["word"])

    table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=6, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=7, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=8, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=9, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=10, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=11, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    
    # table_img.fill_cell(row=3, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])
    # table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])
    # table_img.fill_cell(row=5, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])

    table_img.fill_cell(row=3, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=5, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])

    
    
    
    


    for i in range(7):
        table_img.fill_cell(row=1, column=1+i, row_column=True, text_prop = [1], text_align = ["center"], f_style=["regular"], len_text=["word"])

    # for i in range(3):
    #     table_img.fill_cell(row=2, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=4, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=5, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=9, column=5+i, row_column=True, text_prop = [])
    
    # for i in range(7):
    #     table_img.fill_cell(row=7, column=1+i, row_column=True, text_prop = [])

    for _ in range(4):
        j = random.randint(2,10)
        for i in range(3):
            table_img.specific_content(column=5+i, row=j, row_column = True, type_value="text", value="-")
            table_img.change_cell_background(column=5+i, row=j, color=(180,180,180), row_column = True)
    
    
    for _ in range(2):
        r = random.randint(2,10)
        for i in range(7):
            table_img.specific_content(column=1+i, row=r, row_column = True, type_value="text", value="-")

    # # table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.5], text_align = ["center"], f_style=["bold"], len_text=["text"])
    # table_img.fill_cell(row=0, column=1, row_column=True, text_prop = [1.2], text_align = ["center"], f_style=["bold"], len_text=["word"])

    # table_img.fill_cell(row=1, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])
    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    # table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [0.8, 0.8], text_align = ["center", "center"], len_text=["text", "text"])

    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    # table_img.fill_cell(row=1, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=2, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=3, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=4, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    
    
    
    table_img.print_cells()
    
    
    # table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1, r_line_color="red", l_line_color="red", b_line_color="red", t_line_color="red" )
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)

    table_img.change_line(row=11, column=2, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
    table_img.change_line(row=0, column=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
    
    table_img.change_line(column=1, l_line=1, l_line_width=4)
    table_img.change_line(column=5, l_line=1, l_line_width=4)
    table_img.change_line(column=7, r_line=1, r_line_width=4)
    table_img.change_line(row=0, r_line=1, r_line_width=4, t_line_width=4)

    table_img.change_line(column=0, l_line_width=4)
    table_img.change_line(row=2, column=0, row_column=True, t_line_width=4)
    
    table_img.change_line(row=11, column=0, row_column=True, t_line_width=4, b_line_width=4)
    table_img.change_line(row=11, column=1, row_column=True, t_line_width=4, b_line_width=4, r_line_width=4)
    table_img.change_line(row=10, b_line_width=4)
    





    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_03(config):
    test, table_config, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.5:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,8)


    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(1.5)
        else:
            row_list.append(round(random.uniform(1,4),1))



    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    # coloca todas as linhas
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    
    if random.random() < 0.5:
        table_img.set_color_pred()
    
    table_img.fill_table()
    
    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    return table_img

def page_table_pag_04(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    cols = random.randint(2,3)
    # rows = random.randint(1,4)
    rows = random.randint(2,4)

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        else:
            col_list.append(round(random.uniform(0.8,1.2),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(8)
        else:
            row_list.append(round(random.uniform(8,12),1))



    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    # coloca todas as linhas
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    
    
    table_img.fill_table()

    for r in range(table_img.rows):
        for c in range(table_img.columns):
            if random.random() < 0.3:
                table_img.change_content(column = c, row = r, row_column = True, type_value="img", value="_figure")


    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_05(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.3:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,7)

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(1.5)
        else:
            row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    
    
    
    
    # parametros para mudar tabela
    merge_row_0 = random.choice([True, False])
    merge_row_1e2 = random.choice([True, False])
    merge_last_line = random.choice([True, False])
    set_color = random.choice([True, False])
    
    colums_to_merge = random.randint(1, table_img.columns-1)


    # borda da tabela com linha mais espessa
    if random.random() < 0.3:
        table_img.change_line(row = 0, t_line=1, t_line_width=3)
        table_img.change_line(row = table_img.rows-1, b_line=1, b_line_width=3)
        table_img.change_line(column = 0, l_line=1, l_line_width=3)
        table_img.change_line(column = table_img.columns-1, r_line=1, r_line_width=3)


    # juntar duas primeiras linhas até colums_to_merge
    if table_img.columns > 2:
        if merge_row_1e2:
            for i in range(colums_to_merge):
                table_img.merge_cells(c1=[i,0], c2=[i,1])
            if random.random() < 0.5:
                table_img.change_line(row = 2, t_line=1, t_line_width=3)


    # juntar primeira linha até colums_to_merge
    if table_img.columns > 2 and table_img.rows > 2 :
        if merge_row_0:
            for i in range(colums_to_merge-1):
                table_img.merge_cells(c1=[0,0], c2=[1+i,0])
        if random.random() < 0.5:
            table_img.change_line(column=0, row=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
        if random.random() < 0.5:
            table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)


    # juntar final última linha até colums_to_merge ou desde colums_to_merge
    if table_img.columns > 2 and table_img.rows > 3:
        if merge_last_line:
            if random.random() < 0.5:
                for i in range(colums_to_merge-1):
                    c1_ = [0,table_img.rows-1]
                    c2_ = [1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column=0, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
            else:
                # juntar final última linha desde colums_to_merge
                for i in range(colums_to_merge-1):
                    c1_ = [table_img.columns-colums_to_merge,table_img.rows-1]
                    c2_ = [table_img.columns-colums_to_merge+1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
                    
    
    # parametros para colocar as linhas
    all_lines = random.choice([True, False])
    first_line_t = random.choice([True, False])
    first_line_b = random.choice([True, False])
    last_line_t = random.choice([True, False])
    last_line_b = random.choice([True, False])
    all_lines_h = random.choice([True, False])
    
    if all_lines:
        table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    if first_line_t:
        table_img.change_line(row=0, t_line=1)
    if first_line_b:
        table_img.change_line(row=0, b_line=1)
    if last_line_t:
        table_img.change_line(row=-1, t_line=1)
    if last_line_b:
        table_img.change_line(row=-1, b_line=1)
    if all_lines_h:
        for col_ in range(table_img.columns-1):
            table_img.change_line(column=col_, r_line=1)

            
    table_img.set_color_pred_gray()
    
    table_img.fill_table()

    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def test_table(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)
    
    table_img.run_table()

    # coloca todas as linhas
    
    table_img.draw_lines()
    table_img.cut_table()


    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img




def page_table_pag_01_sem(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    cols = 8
    rows = 12
    
    # table_img.init_table(cols=[3,1,1,1,1,1,1,1], rows=[1,1,1,2,2,2,1,1,1,1,1,1])

    col_list=[]
    for i in range(cols):
        if random.random() < 0.8:
            col_list.append(round(random.uniform(0.8,1.2),1))
        elif random.random() < 0.5:
            col_list.append(round(random.uniform(1.8,2.2),1))
        else:
            col_list.append(round(random.uniform(1.3,1.7),1))
    if col_list[0]<3: col_list[0] = round(random.uniform(2.5,5),1)
    
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1.5)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(2.5)
        else:
            row_list.append(round(random.uniform(1,4),1))
    if col_list[3]<2: col_list[3] = round(random.uniform(2,3),1)
    if col_list[4]<2: col_list[4] = round(random.uniform(2,3),1)
    if col_list[5]<2: col_list[5] = round(random.uniform(2,3),1)


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()
    


    # self.draw_total_table()
    
    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    table_img.change_font(row="all", horizontal_align="center")
    
    table_img.delete_lines()

    table_img.merge_cells(c1=[0,0], c2=[0,1])

    table_img.merge_cells(c1=[1,0], c2=[2,0])
    table_img.merge_cells(c1=[1,0], c2=[3,0])
    table_img.merge_cells(c1=[1,0], c2=[4,0])

    table_img.merge_cells(c1=[5,0], c2=[6,0])
    table_img.merge_cells(c1=[5,0], c2=[7,0])

    for i in range(5):
        table_img.merge_cells(c1=[2,11], c2=[3+i,11])
    
    table_img.fill_table()

    table_img.fill_cell(row=11, column=2, row_column=True, text_prop = [])
    table_img.fill_cell(row=11, column=2, row_column=True, text_prop = [])

    
    
        
    
    
    
    # table_img.change_font(column=1, horizontal_align="left")
    
    
    table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.2], text_align = ["left"], f_style=["bold"], len_text=["word"])

    table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=6, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=7, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=8, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=9, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=10, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=11, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    
    table_img.fill_cell(row=3, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])
    table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])
    table_img.fill_cell(row=5, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])

    table_img.fill_cell(row=3, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=5, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])

    
    
    
    


    for i in range(7):
        table_img.fill_cell(row=1, column=1+i, row_column=True, text_prop = [1], text_align = ["center"], f_style=["regular"], len_text=["word"])

    # for i in range(3):
    #     table_img.fill_cell(row=2, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=4, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=5, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=9, column=5+i, row_column=True, text_prop = [])
    
    # for i in range(7):
    #     table_img.fill_cell(row=7, column=1+i, row_column=True, text_prop = [])

    for _ in range(4):
        j = random.randint(2,10)
        for i in range(3):
            table_img.specific_content(column=5+i, row=j, row_column = True, type_value="text", value="-")
            table_img.change_cell_background(column=5+i, row=j, color=(180,180,180), row_column = True)
    
    
    for _ in range(2):
        r = random.randint(2,10)
        for i in range(7):
            table_img.specific_content(column=1+i, row=r, row_column = True, type_value="text", value="-")

    # # table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.5], text_align = ["center"], f_style=["bold"], len_text=["text"])
    # table_img.fill_cell(row=0, column=1, row_column=True, text_prop = [1.2], text_align = ["center"], f_style=["bold"], len_text=["word"])

    # table_img.fill_cell(row=1, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])
    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    # table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [0.8, 0.8], text_align = ["center", "center"], len_text=["text", "text"])

    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    # table_img.fill_cell(row=1, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=2, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=3, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=4, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    
    
    
    table_img.print_cells()
    
    
    table_img.delete_lines()

    table_img.change_line(row=11, column=2, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
    table_img.change_line(row=0, column=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
    
    table_img.change_line(column=1, l_line=1, l_line_width=4)
    table_img.change_line(column=5, l_line=1, l_line_width=4)
    table_img.change_line(column=7, r_line=1, r_line_width=4)
    table_img.change_line(row=0, r_line=1, r_line_width=4, t_line_width=4)

    table_img.change_line(column=0, l_line_width=4)
    table_img.change_line(row=2, column=0, row_column=True, t_line_width=4)
    
    table_img.change_line(row=11, column=0, row_column=True, t_line_width=4, b_line_width=4)
    table_img.change_line(row=11, column=1, row_column=True, t_line_width=4, b_line_width=4, r_line_width=4)
    table_img.change_line(row=10, b_line_width=4)
    





    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_03_sem(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.5:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,8)


    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(1.5)
        else:
            row_list.append(round(random.uniform(1,4),1))



    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    # coloca todas as linhas
    # table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    
    if random.random() < 0.5:
        table_img.set_color_pred()
    
    table_img.fill_table()
    
    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_05_sem(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.3:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,7)

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(1.5)
        else:
            row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    
    
    
    
    # parametros para mudar tabela
    merge_row_0 = random.choice([True, False])
    merge_row_1e2 = random.choice([True, False])
    merge_last_line = random.choice([True, False])
    set_color = random.choice([True, False])
    
    colums_to_merge = random.randint(1, table_img.columns-1)


    # borda da tabela com linha mais espessa
    if random.random() < 0.3:
        table_img.change_line(row = 0, t_line=1, t_line_width=3)
        table_img.change_line(row = table_img.rows-1, b_line=1, b_line_width=3)
        table_img.change_line(column = 0, l_line=1, l_line_width=3)
        table_img.change_line(column = table_img.columns-1, r_line=1, r_line_width=3)


    # juntar duas primeiras linhas até colums_to_merge
    if table_img.columns > 2:
        if merge_row_1e2:
            for i in range(colums_to_merge):
                table_img.merge_cells(c1=[i,0], c2=[i,1])
            if random.random() < 0.5:
                table_img.change_line(row = 2, t_line=1, t_line_width=3)


    # juntar primeira linha até colums_to_merge
    if table_img.columns > 2 and table_img.rows > 2 :
        if merge_row_0:
            for i in range(colums_to_merge-1):
                table_img.merge_cells(c1=[0,0], c2=[1+i,0])
        if random.random() < 0.5:
            table_img.change_line(column=0, row=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
        if random.random() < 0.5:
            table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)


    # juntar final última linha até colums_to_merge ou desde colums_to_merge
    if table_img.columns > 2 and table_img.rows > 3:
        if merge_last_line:
            if random.random() < 0.5:
                for i in range(colums_to_merge-1):
                    c1_ = [0,table_img.rows-1]
                    c2_ = [1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column=0, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
            else:
                # juntar final última linha desde colums_to_merge
                for i in range(colums_to_merge-1):
                    c1_ = [table_img.columns-colums_to_merge,table_img.rows-1]
                    c2_ = [table_img.columns-colums_to_merge+1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
                    
    
    # parametros para colocar as linhas
    all_lines = random.choice([True, False])
    first_line_t = random.choice([True, False])
    first_line_b = random.choice([True, False])
    last_line_t = random.choice([True, False])
    last_line_b = random.choice([True, False])
    all_lines_h = random.choice([True, False])
    
    if all_lines:
        table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    if first_line_t:
        table_img.change_line(row=0, t_line=1)
    if first_line_b:
        table_img.change_line(row=0, b_line=1)
    if last_line_t:
        table_img.change_line(row=-1, t_line=1)
    if last_line_b:
        table_img.change_line(row=-1, b_line=1)
    if all_lines_h:
        for col_ in range(table_img.columns-1):
            table_img.change_line(column=col_, r_line=1)

    table_img.delete_lines()            
    table_img.set_color_pred_gray()
    
    table_img.fill_table()

    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_06_sem(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.3:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,7)
    
    cols = 5
    rows = 10

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        row_list.append(round(random.uniform(1,4),1))
        # if random.random() < 0.7:
        #     row_list.append(1)
        # elif random.random() < 0.5:
        #     row_list.append(2)
        # elif random.random() < 0.5:
        #     row_list.append(1.5)
        # else:
        #     row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    
    
    
    
    # parametros para mudar tabela
    merge_row_0 = random.choice([True, False])
    merge_row_1e2 = random.choice([True, False])
    merge_last_line = random.choice([True, False])
    set_color = random.choice([True, False])
    
    colums_to_merge = random.randint(1, table_img.columns-1)


    # borda da tabela com linha mais espessa
    if random.random() < 0.3:
        table_img.change_line(row = 0, t_line=1, t_line_width=3)
        table_img.change_line(row = table_img.rows-1, b_line=1, b_line_width=3)
        table_img.change_line(column = 0, l_line=1, l_line_width=3)
        table_img.change_line(column = table_img.columns-1, r_line=1, r_line_width=3)


    # juntar duas primeiras linhas até colums_to_merge
    if table_img.columns > 2:
        if merge_row_1e2:
            for i in range(colums_to_merge):
                table_img.merge_cells(c1=[i,0], c2=[i,1])
            if random.random() < 0.5:
                table_img.change_line(row = 2, t_line=1, t_line_width=3)


    # juntar primeira linha até colums_to_merge
    if table_img.columns > 2 and table_img.rows > 2 :
        if merge_row_0:
            for i in range(colums_to_merge-1):
                table_img.merge_cells(c1=[0,0], c2=[1+i,0])
        if random.random() < 0.5:
            table_img.change_line(column=0, row=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
        if random.random() < 0.5:
            table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)


    # juntar final última linha até colums_to_merge ou desde colums_to_merge
    if table_img.columns > 2 and table_img.rows > 3:
        if merge_last_line:
            if random.random() < 0.5:
                for i in range(colums_to_merge-1):
                    c1_ = [0,table_img.rows-1]
                    c2_ = [1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column=0, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
            else:
                # juntar final última linha desde colums_to_merge
                for i in range(colums_to_merge-1):
                    c1_ = [table_img.columns-colums_to_merge,table_img.rows-1]
                    c2_ = [table_img.columns-colums_to_merge+1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
                    
    
    # parametros para colocar as linhas
    all_lines = random.choice([True, False])
    first_line_t = random.choice([True, False])
    first_line_b = random.choice([True, False])
    last_line_t = random.choice([True, False])
    last_line_b = random.choice([True, False])
    all_lines_h = random.choice([True, False])
    
    if all_lines:
        table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    if first_line_t:
        table_img.change_line(row=0, t_line=1)
    if first_line_b:
        table_img.change_line(row=0, b_line=1)
    if last_line_t:
        table_img.change_line(row=-1, t_line=1)
    if last_line_b:
        table_img.change_line(row=-1, b_line=1)
    if all_lines_h:
        for col_ in range(table_img.columns-1):
            table_img.change_line(column=col_, r_line=1)

    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)

    fill_multi_line = random.choice([True, False])
    if fill_multi_line:
        center_col_0 = random.choice([True, False])
        for s, size in enumerate(table_img.rows_sizes):
            # print(s, table_img.character_height, size, math.floor(size/(table_img.character_height*1.1)))
            lines = math.floor(size/(table_img.character_height*1.1))
            if lines > 1:
                for c in range(table_img.columns):
                    if random.choice([True, False]):
                        if c == 0:
                            table_img.fill_cell(row=s, column=c, row_column=True, text_prop = [1]*lines, text_align = ["left"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
                        else:
                            table_img.fill_cell(row=s, column=c, row_column=True, text_prop = [1]*lines, text_align = ["center"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
            if center_col_0:
                table_img.fill_cell(row=s, column=0, row_column=True, text_prop = [1]*lines, text_align = ["center"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
            else:
                table_img.fill_cell(row=s, column=0, row_column=True, text_prop = [1]*lines, text_align = ["left"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
    
    table_img.set_color_pred_gray()
    table_img.delete_lines()
    table_img.fill_table()

    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img


def page_table_pag_01_com(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    cols = 8
    rows = 12
    
    # table_img.init_table(cols=[3,1,1,1,1,1,1,1], rows=[1,1,1,2,2,2,1,1,1,1,1,1])

    col_list=[]
    for i in range(cols):
        if random.random() < 0.8:
            col_list.append(round(random.uniform(0.8,1.2),1))
        elif random.random() < 0.5:
            col_list.append(round(random.uniform(1.8,2.2),1))
        else:
            col_list.append(round(random.uniform(1.3,1.7),1))
    if col_list[0]<3: col_list[0] = round(random.uniform(2.5,5),1)


    
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1.5)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(2.5)
        else:
            row_list.append(round(random.uniform(1,4),1))
    if col_list[3]<2: col_list[3] = round(random.uniform(2,3),1)
    if col_list[4]<2: col_list[4] = round(random.uniform(2,3),1)
    if col_list[5]<2: col_list[5] = round(random.uniform(2,3),1)


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()
    


    # self.draw_total_table()
    
    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    table_img.change_font(row="all", horizontal_align="center")
    
    table_img.delete_lines()

    table_img.merge_cells(c1=[0,0], c2=[0,1])

    table_img.merge_cells(c1=[1,0], c2=[2,0])
    table_img.merge_cells(c1=[1,0], c2=[3,0])
    table_img.merge_cells(c1=[1,0], c2=[4,0])

    table_img.merge_cells(c1=[5,0], c2=[6,0])
    table_img.merge_cells(c1=[5,0], c2=[7,0])

    for i in range(5):
        table_img.merge_cells(c1=[2,11], c2=[3+i,11])
    
    table_img.fill_table()

    
    

    table_img.fill_cell(row=11, column=2, row_column=True, text_prop = [])


    
    
        
    
    
    
    # table_img.change_font(column=1, horizontal_align="left")
    
    
    table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.2], text_align = ["left"], f_style=["bold"], len_text=["word"])

    table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=6, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=7, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=8, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=9, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=10, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=11, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    
    table_img.fill_cell(row=3, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])
    table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])
    table_img.fill_cell(row=5, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])

    table_img.fill_cell(row=3, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    table_img.fill_cell(row=5, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])


    # for cell in table_img.cells:
    #     if cell[0][0] == 0:
    #         if len(cell[2]) > 1:
    #             print(cell[0], cell[2])

    
    
    
    


    for i in range(7):
        table_img.fill_cell(row=1, column=1+i, row_column=True, text_prop = [1], text_align = ["center"], f_style=["regular"], len_text=["word"])

    # for i in range(3):
    #     table_img.fill_cell(row=2, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=4, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=5, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=9, column=5+i, row_column=True, text_prop = [])
    
    # for i in range(7):
    #     table_img.fill_cell(row=7, column=1+i, row_column=True, text_prop = [])

    for _ in range(4):
        j = random.randint(2,10)
        for i in range(3):
            table_img.specific_content(column=5+i, row=j, row_column = True, type_value="text", value="-")
            table_img.change_cell_background(column=5+i, row=j, color=(180,180,180), row_column = True)
    
    
    for _ in range(2):
        r = random.randint(2,10)
        for i in range(7):
            table_img.specific_content(column=1+i, row=r, row_column = True, type_value="text", value="-")

    # # table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.5], text_align = ["center"], f_style=["bold"], len_text=["text"])
    # table_img.fill_cell(row=0, column=1, row_column=True, text_prop = [1.2], text_align = ["center"], f_style=["bold"], len_text=["word"])

    # table_img.fill_cell(row=1, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])
    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    # table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [0.8, 0.8], text_align = ["center", "center"], len_text=["text", "text"])

    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    # table_img.fill_cell(row=1, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=2, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=3, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=4, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    

    
    table_img.print_cells()
    
    
    
    # table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1, r_line_color="red", l_line_color="red", b_line_color="red", t_line_color="red" )
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)

    table_img.change_line(row=11, column=2, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
    table_img.change_line(row=0, column=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
    
    table_img.change_line(column=1, l_line=1, l_line_width=4)
    table_img.change_line(column=5, l_line=1, l_line_width=4)
    table_img.change_line(column=7, r_line=1, r_line_width=4)
    table_img.change_line(row=0, r_line=1, r_line_width=4, t_line_width=4)

    table_img.change_line(column=0, l_line_width=4)
    table_img.change_line(row=2, column=0, row_column=True, t_line_width=4)
    
    table_img.change_line(row=11, column=0, row_column=True, t_line_width=4, b_line_width=4)
    table_img.change_line(row=11, column=1, row_column=True, t_line_width=4, b_line_width=4, r_line_width=4)
    table_img.change_line(row=10, b_line_width=4)
    





    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_03_com(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.5:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,8)


    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(1.5)
        else:
            row_list.append(round(random.uniform(1,4),1))



    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    table_img.delete_lines()

    # coloca todas as linhas
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    
    if random.random() < 0.5:
        table_img.set_color_pred()
    
    table_img.fill_table()
    
    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_05_com(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.3:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,7)

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(1.5)
        else:
            row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    # table_img.delete_lines()

    
    
    
    
    # parametros para mudar tabela
    merge_row_0 = random.choice([True, False])
    merge_row_1e2 = random.choice([True, False])
    merge_last_line = random.choice([True, False])
    set_color = random.choice([True, False])
    
    colums_to_merge = random.randint(1, table_img.columns-1)


    # borda da tabela com linha mais espessa
    if random.random() < 0.3:
        table_img.change_line(row = 0, t_line=1, t_line_width=3)
        table_img.change_line(row = table_img.rows-1, b_line=1, b_line_width=3)
        table_img.change_line(column = 0, l_line=1, l_line_width=3)
        table_img.change_line(column = table_img.columns-1, r_line=1, r_line_width=3)


    # juntar duas primeiras linhas até colums_to_merge
    if table_img.columns > 2:
        if merge_row_1e2:
            for i in range(colums_to_merge):
                table_img.merge_cells(c1=[i,0], c2=[i,1])
            if random.random() < 0.5:
                table_img.change_line(row = 2, t_line=1, t_line_width=3)


    # juntar primeira linha até colums_to_merge
    if table_img.columns > 2 and table_img.rows > 2 :
        if merge_row_0:
            for i in range(colums_to_merge-1):
                table_img.merge_cells(c1=[0,0], c2=[1+i,0])
        if random.random() < 0.5:
            table_img.change_line(column=0, row=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
        if random.random() < 0.5:
            table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)


    # juntar final última linha até colums_to_merge ou desde colums_to_merge
    if table_img.columns > 2 and table_img.rows > 3:
        if merge_last_line:
            if random.random() < 0.5:
                for i in range(colums_to_merge-1):
                    c1_ = [0,table_img.rows-1]
                    c2_ = [1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column=0, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
            else:
                # juntar final última linha desde colums_to_merge
                for i in range(colums_to_merge-1):
                    c1_ = [table_img.columns-colums_to_merge,table_img.rows-1]
                    c2_ = [table_img.columns-colums_to_merge+1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
                    
    
    # parametros para colocar as linhas
    all_lines = random.choice([True, False])
    first_line_t = random.choice([True, False])
    first_line_b = random.choice([True, False])
    last_line_t = random.choice([True, False])
    last_line_b = random.choice([True, False])
    all_lines_h = random.choice([True, False])
    
    if all_lines:
        table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    if first_line_t:
        table_img.change_line(row=0, t_line=1)
    if first_line_b:
        table_img.change_line(row=0, b_line=1)
    if last_line_t:
        table_img.change_line(row=-1, t_line=1)
    if last_line_b:
        table_img.change_line(row=-1, b_line=1)
    if all_lines_h:
        for col_ in range(table_img.columns-1):
            table_img.change_line(column=col_, r_line=1)

            
    table_img.set_color_pred_gray()
    
    table_img.fill_table()

    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img

def page_table_pag_06_com(config):
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(2,max_columns)
    if random.random() < 0.3:
        rows = random.randint(2,30)
    else:
        rows = random.randint(2,7)
    
    cols = 5
    rows = 10

    col_list=[]
    for i in range(cols):
        if random.random() < 0.7:
            col_list.append(1)
        elif random.random() < 0.5:
            col_list.append(2)
        elif random.random() < 0.5:
            col_list.append(1.5)
        else:
            col_list.append(round(random.uniform(1,4),1))
    row_list=[]
    for i in range(rows):
        row_list.append(round(random.uniform(1,4),1))
        # if random.random() < 0.7:
        #     row_list.append(1)
        # elif random.random() < 0.5:
        #     row_list.append(2)
        # elif random.random() < 0.5:
        #     row_list.append(1.5)
        # else:
        #     row_list.append(round(random.uniform(1,4),1))


    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()

    table_img.set_column_value_type()
    table_img.column_type[0] = "str"
    table_img.create_cells()

    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    # centra todas as celulas
    table_img.change_font(row="all", horizontal_align="center")
    
    # apaga todas as linhas
    # table_img.delete_lines()

    
    
    
    
    # parametros para mudar tabela
    merge_row_0 = random.choice([True, False])
    merge_row_1e2 = random.choice([True, False])
    merge_last_line = random.choice([True, False])
    set_color = random.choice([True, False])
    
    colums_to_merge = random.randint(1, table_img.columns-1)


    # borda da tabela com linha mais espessa
    if random.random() < 0.3:
        table_img.change_line(row = 0, t_line=1, t_line_width=3)
        table_img.change_line(row = table_img.rows-1, b_line=1, b_line_width=3)
        table_img.change_line(column = 0, l_line=1, l_line_width=3)
        table_img.change_line(column = table_img.columns-1, r_line=1, r_line_width=3)


    # juntar duas primeiras linhas até colums_to_merge
    if table_img.columns > 2:
        if merge_row_1e2:
            for i in range(colums_to_merge):
                table_img.merge_cells(c1=[i,0], c2=[i,1])
            if random.random() < 0.5:
                table_img.change_line(row = 2, t_line=1, t_line_width=3)


    # juntar primeira linha até colums_to_merge
    if table_img.columns > 2 and table_img.rows > 2 :
        if merge_row_0:
            for i in range(colums_to_merge-1):
                table_img.merge_cells(c1=[0,0], c2=[1+i,0])
        if random.random() < 0.5:
            table_img.change_line(column=0, row=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
        if random.random() < 0.5:
            table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)


    # juntar final última linha até colums_to_merge ou desde colums_to_merge
    if table_img.columns > 2 and table_img.rows > 3:
        if merge_last_line:
            if random.random() < 0.5:
                for i in range(colums_to_merge-1):
                    c1_ = [0,table_img.rows-1]
                    c2_ = [1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column=0, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
            else:
                # juntar final última linha desde colums_to_merge
                for i in range(colums_to_merge-1):
                    c1_ = [table_img.columns-colums_to_merge,table_img.rows-1]
                    c2_ = [table_img.columns-colums_to_merge+1+i,table_img.rows-1]
                    table_img.merge_cells(c1=c1_, c2=c2_)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, row=table_img.rows-1, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
                if random.random() < 0.5:
                    table_img.change_line(column = table_img.columns-colums_to_merge, l_line=1, l_line_width=3)
                if random.random() < 0.5:
                    table_img.change_line(row = table_img.rows-1, t_line=1, t_line_width=3)
                    
    
    # parametros para colocar as linhas
    all_lines = random.choice([True, False])
    first_line_t = random.choice([True, False])
    first_line_b = random.choice([True, False])
    last_line_t = random.choice([True, False])
    last_line_b = random.choice([True, False])
    all_lines_h = random.choice([True, False])
    
    if all_lines:
        table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)
    if first_line_t:
        table_img.change_line(row=0, t_line=1)
    if first_line_b:
        table_img.change_line(row=0, b_line=1)
    if last_line_t:
        table_img.change_line(row=-1, t_line=1)
    if last_line_b:
        table_img.change_line(row=-1, b_line=1)
    if all_lines_h:
        for col_ in range(table_img.columns-1):
            table_img.change_line(column=col_, r_line=1)

    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)

    fill_multi_line = random.choice([True, False])
    if fill_multi_line:
        center_col_0 = random.choice([True, False])
        for s, size in enumerate(table_img.rows_sizes):
            # print(s, table_img.character_height, size, math.floor(size/(table_img.character_height*1.1)))
            lines = math.floor(size/(table_img.character_height*1.1))
            if lines > 1:
                for c in range(table_img.columns):
                    if random.choice([True, False]):
                        if c == 0:
                            table_img.fill_cell(row=s, column=c, row_column=True, text_prop = [1]*lines, text_align = ["left"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
                        else:
                            table_img.fill_cell(row=s, column=c, row_column=True, text_prop = [1]*lines, text_align = ["center"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
            if center_col_0:
                table_img.fill_cell(row=s, column=0, row_column=True, text_prop = [1]*lines, text_align = ["center"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
            else:
                table_img.fill_cell(row=s, column=0, row_column=True, text_prop = [1]*lines, text_align = ["left"]*lines, f_style=["regular"]*lines, len_text=["text"]*lines)
    
    table_img.set_color_pred_gray()
    
    table_img.fill_table()

    table_img.print_cells()
    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img



###################################################################
# novas


def page_table_pag_07(config):
    
    test, table_config, return_, save = init_table(config)

    table_img = Tablegen(table_config)

    # criar lista de tamanhos de colunas e linhas
    max_columns = math.floor(table_config["size"][0]/(table_config["ts_text"][2]*4))
    cols = random.randint(max_columns-4,max_columns)
    # cols = random.randint(15,30)
    rows = random.randint(15,30)
        
    
    
    # table_img.init_table(cols=[3,1,1,1,1,1,1,1], rows=[1,1,1,2,2,2,1,1,1,1,1,1])

    col_list=[]
    for i in range(cols):
        if random.random() < 0.8:
            col_list.append(round(random.uniform(0.8,1.2),1))
        elif random.random() < 0.5:
            col_list.append(round(random.uniform(1.8,2.2),1))
        else:
            col_list.append(round(random.uniform(1.3,1.7),1))
    if random.random() < 0.7:
        col_list[0] = round(random.uniform(1.0,3.0),1)
    else:
        col_list[0] = round(random.uniform(2.5,5),1)
    
    
    row_list=[]
    for i in range(rows):
        if random.random() < 0.7:
            row_list.append(1.5)
        elif random.random() < 0.5:
            row_list.append(2)
        elif random.random() < 0.5:
            row_list.append(round(random.uniform(2,9),1))
        else:
            row_list.append(round(random.uniform(3,6),1))
        # row_list.append(5)

    # inicia a tabela 
    table_img.init_values()
    table_img.init_table(cols=col_list, rows=row_list)
    table_img.create_img()
    


    # self.draw_total_table()
    
    table_img.set_column_value_type()
    for i in range(len(table_img.column_type)):
        table_img.column_type[i] = "num"
    # table_img.column_type[0] = "str"
    table_img.create_cells()

    
    # header content
    style_font = random.choice(["regular", "italic", "bold"])
    table_img.change_font(row=0, font_style=style_font, font_size=0, font_color=None, row_column=False)
    
    table_img.change_font(row="all", horizontal_align="center")
    
    table_img.delete_lines()

    
    
    if random.random() < 10.5:
        for c in range(1,cols):
            r = 0
            while r < rows:
                if random.random() < 0.3:
                    table_img.merge_cells(c1=[c,r], c2=[c,r+1])
                    r += 1
                    if random.random() < 0.3:
                        table_img.merge_cells(c1=[c,r-1], c2=[c,r+1])
                        r += 1
                r += 1






    # table_img.merge_cells(c1=[0,0], c2=[0,1])

    # table_img.merge_cells(c1=[1,0], c2=[2,0])
    # table_img.merge_cells(c1=[1,0], c2=[3,0])
    # table_img.merge_cells(c1=[1,0], c2=[4,0])

    # table_img.merge_cells(c1=[5,0], c2=[6,0])
    # table_img.merge_cells(c1=[5,0], c2=[7,0])

    # for i in range(5):
    #     table_img.merge_cells(c1=[2,11], c2=[3+i,11])
    
    table_img.fill_table()

    c=0
    for r in range(rows):
        for c in range(cols):
            max_lines = math.floor(row_list[r])
            if max_lines > 1:
                lines_in_cell = random.randint(1,max_lines)
                # lines_in_cell = max_lines
                if random.random() < 0.8:
                    text_prop = [1]*lines_in_cell
                else:
                    text_prop = [round(random.uniform(0.7,1),1)]*lines_in_cell
                
                text_align = ["center"]*lines_in_cell
                
                if random.random() < 0.7:
                    len_text = ["num"]*lines_in_cell
                elif random.random() < 0.7:
                    len_text = ["str"]*lines_in_cell
                else:
                    len_text = ["text"]*lines_in_cell

                table_img.fill_cell(row=r, column=c, row_column=True, text_prop = text_prop, text_align = text_align, len_text=len_text)
            else:
                if random.random() < 0.9:
                    text_prop = [1]
                else:
                    text_prop = [round(random.uniform(0.7,1),1)]
                
                text_align = ["center"]
                
                if random.random() < 0.7:
                    len_text = ["num"]
                elif random.random() < 0.7:
                    len_text = ["str"]
                else:
                    len_text = ["text"]

                table_img.fill_cell(row=r, column=c, row_column=True, text_prop = text_prop, text_align = text_align, len_text=len_text)


                table_img.fill_cell(row=r, column=c, row_column=True, text_prop = text_prop, text_align = text_align, len_text=len_text)
            # table_img.fill_cell(row=r, column=c, row_column=True, text_prop = [1], text_align = ["center"], len_text=[])
    


    # table_img.fill_cell(row=11, column=2, row_column=True, text_prop = [])
    # table_img.fill_cell(row=11, column=2, row_column=True, text_prop = [])

    
    
        
    
    
    
    # table_img.change_font(column=1, horizontal_align="left")
    
    
    # table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.2], text_align = ["left"], f_style=["bold"], len_text=["word"])

    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    # table_img.fill_cell(row=6, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    # table_img.fill_cell(row=7, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    # table_img.fill_cell(row=8, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    # table_img.fill_cell(row=9, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    # table_img.fill_cell(row=10, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    # table_img.fill_cell(row=11, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    
    # table_img.fill_cell(row=3, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])
    # table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])
    # table_img.fill_cell(row=5, column=0, row_column=True, text_prop = [1, 1], text_align = ["left", "left"], f_style=["regular", "regular"], len_text=["text", "text"])

    # table_img.fill_cell(row=3, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    # table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])
    # table_img.fill_cell(row=5, column=0, row_column=True, text_prop = [1], text_align = ["left"], f_style=["regular"], len_text=["text"])

    
    
    
    


    # for i in range(7):
    #     table_img.fill_cell(row=1, column=1+i, row_column=True, text_prop = [1], text_align = ["center"], f_style=["regular"], len_text=["word"])

    # for i in range(3):
    #     table_img.fill_cell(row=2, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=4, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=5, column=5+i, row_column=True, text_prop = [])
    #     table_img.fill_cell(row=9, column=5+i, row_column=True, text_prop = [])
    
    # for i in range(7):
    #     table_img.fill_cell(row=7, column=1+i, row_column=True, text_prop = [])

    # for _ in range(4):
    #     j = random.randint(2,10)
    #     for i in range(3):
    #         table_img.specific_content(column=5+i, row=j, row_column = True, type_value="text", value="-")
    #         table_img.change_cell_background(column=5+i, row=j, color=(180,180,180), row_column = True)
    
    
    # for _ in range(2):
    #     r = random.randint(2,10)
    #     for i in range(7):
    #         table_img.specific_content(column=1+i, row=r, row_column = True, type_value="text", value="-")

    # # table_img.fill_cell(row=0, column=0, row_column=True, text_prop = [1.5], text_align = ["center"], f_style=["bold"], len_text=["text"])
    # table_img.fill_cell(row=0, column=1, row_column=True, text_prop = [1.2], text_align = ["center"], f_style=["bold"], len_text=["word"])

    # table_img.fill_cell(row=1, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])
    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    # table_img.fill_cell(row=4, column=0, row_column=True, text_prop = [0.8, 0.8], text_align = ["center", "center"], len_text=["text", "text"])

    # table_img.fill_cell(row=2, column=0, row_column=True, text_prop = [1.3], text_align = ["center"], f_style=["bolditalic"], len_text=["text"])

    # table_img.fill_cell(row=1, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=2, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=3, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    # table_img.fill_cell(row=4, column=1, row_column=True, text_prop = [0.7], text_align = ["left"], f_style=["regular"], len_text=["word"])
    
    
    
    table_img.print_cells()
    
    
    # table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1, r_line_color="red", l_line_color="red", b_line_color="red", t_line_color="red" )
    table_img.change_line(row="all", b_line = 1, l_line=1, r_line=1, t_line=1)

    table_img.change_line(row=11, column=2, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
    table_img.change_line(row=0, column=0, row_column=True, b_line = 0, l_line=0, r_line=0, t_line=0)
    
    # table_img.change_line(column=1, l_line=1, l_line_width=4)
    # table_img.change_line(column=5, l_line=1, l_line_width=4)
    # table_img.change_line(column=7, r_line=1, r_line_width=4)
    # table_img.change_line(row=0, r_line=1, r_line_width=4, t_line_width=4)

    # table_img.change_line(column=0, l_line_width=4)
    # table_img.change_line(row=2, column=0, row_column=True, t_line_width=4)
    
    # table_img.change_line(row=11, column=0, row_column=True, t_line_width=4, b_line_width=4)
    # table_img.change_line(row=11, column=1, row_column=True, t_line_width=4, b_line_width=4, r_line_width=4)
    # table_img.change_line(row=10, b_line_width=4)
    





    
    table_img.draw_lines()
    table_img.cut_table()

    
    
    if save:
        if test:
            table_img.document.save("src/temp/document_test.png")
            table_img.xml_path = "src/temp/document_test.xml"
            table_img.create_xml_file()
        else:
            table_img.save_image()
            table_img.create_xml_file()
    
    if return_:
        return table_img




import xml.etree.ElementTree as ET
def check_table_xml(table_img = "output/document_test.png"):
    table_xml = table_img[:-4] + ".xml"
    # print(table_img)
    # print(table_xml)

    tree = ET.parse(table_xml)
    root = tree.getroot()

    img = Image.open(table_img)
    width, height = img.size
    document = Image.new("RGB", (width, height), color="white")
    document.paste(img, (0,0))
    draw = ImageDraw.Draw(document)

    font = set_font("arial", "regular", int(height/75))

    for table in range(len(root)):
        # color = random_color("RGB")
        
        for child in root[table]:

            # print(child.tag, child.attrib)
            if child.tag == "cell":
                for child_cell in child:
                    if child_cell.tag == "value":
                        for child_value in child_cell:
                            coor = child_value.attrib["bounding_box"].split(" ")
                            x0, y0 = int(coor[0].split(",")[0]) , int(coor[0].split(",")[1])
                            x1, y1 = int(coor[1].split(",")[0]) , int(coor[1].split(",")[1])
                            draw.rectangle((x0, y0, x1, y1), fill=None, outline="red", width=1)
                # print(child.attrib)
                # print(child[1])
                # coord = child[0].attrib["points"].split(" ")
                # draw.line(((0,0),(100,200)), fill="red", width=1)

                # for i in range(len(coord)):
                #     if i != len(coord)-1:
                #         points0 = coord[i].split(",")
                #         points1 = coord[i+1].split(",")
                #         x0 = int(points0[0])
                #         y0 = int(points0[1])
                #         x1 = int(points1[0])
                #         y1 = int(points1[1])
                #         draw.line(((x0,y0),(x1,y1)), fill=color, width=width_line)
                #     else:
                #         points0 = coord[i].split(",")
                #         points1 = coord[0].split(",")
                #         x0 = int(points0[0])
                #         y0 = int(points0[1])
                #         x1 = int(points1[0])
                #         y1 = int(points1[1])
                #         draw.line(((x0,y0),(x1,y1)), fill=color, width=width_line)
                # row = int(child.attrib["end-row"])-int(child.attrib["start-row"])+1
                # col = int(child.attrib["end-col"])-int(child.attrib["start-col"])+1
                
                
                # points0 = coord[0].split(",")
                # x0 = int(points0[0])
                # y0 = int(points0[1])
                # text_to_print = str(row) + "-" + str(col)
                # draw.text((x0, y0), text_to_print , fill="Blue", font=font)
                # # printi(row, col)
            
        # for child in root[table]:
        #     if child.tag == "Coords":
        #         # printi(child.attrib)
        #         # printi(child.attrib["points"])
        #         coord = child.attrib["points"].split(" ")
        #         for i in range(len(coord)):
        #             if i != len(coord)-1:
        #                 points0 = coord[i].split(",")
        #                 points1 = coord[i+1].split(",")
        #                 x0 = int(points0[0])
        #                 y0 = int(points0[1])
        #                 x1 = int(points1[0])
        #                 y1 = int(points1[1])
        #                 draw.line(((x0,y0),(x1,y1)), fill=color_table, width=width_line_table)
        #             else:
        #                 points0 = coord[i].split(",")
        #                 points1 = coord[0].split(",")
        #                 x0 = int(points0[0])
        #                 y0 = int(points0[1])
        #                 x1 = int(points1[0])
        #                 y1 = int(points1[1])
        #                 draw.line(((x0,y0),(x1,y1)), fill=color_table, width=width_line_table)
            

    # printi("saving img...")
    document.save("output/document_test_boxes.png")


config={
    # "size":[[400,1500], [300,1500]],
    "size":[800,1200],
    # "size":[400,1500],
    "font_name":["arial", "courier", "opensans", "raleway", "roboto", "times"],
    "font_style":"regular",
    "font_size":[10,30],
    "bg_color":["white"],
    "test":True, 
    "return":False, 
    "save":True, 
    }

#endregion