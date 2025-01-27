SUBTYPECOLOR = {'image': '#A2005C',
                'equation': '#6A00FF',
                'paragraph': '#008A00',
                'title': '#0050EF',
                'subtitle': '#1BA1E2',
                'subsubtitle': '#0E8088',
                'list': '#60A917',
                'pagenumber': '#B0E3E6',
                'table': '#B09500'}

TYPESDICT = {
    'image': 'image',
    'paragraph': 'text',
    'title': 'text',
    'subtitle': 'text',
    'subsubtitle': 'text',
    'list': 'text',
    'pagenumber': 'text',
    'table': 'table',
    'equation': 'image'
}
TITLE_TYPES = ["title", "subtitle", "subsubtitle", "subsubsubtitle"]

TEXTSIZEMODIFIERS = {
    'paragraph': {
        'size': ["regular", 0],
        'modifier': ["regular", "italic", "bold", "bolditalic"] 
    },
    'title': {
        'size': ["increase", 3],
        'modifier': ["regular", "italic", "bold", "bolditalic"] 
    },
    'subtitle': {
        'size': ["increase", 2],
        'modifier': ["regular", "italic", "bold", "bolditalic"] 
    },
    'subsubtitle': {
        'size': ["increase", 1],
        'modifier': ["regular", "italic", "bold", "bolditalic"] 
    },
    'list': {
        'size': ["regular", 0],
        'modifier': ["regular", "italic", "bold", "bolditalic"] 
    },
    'note': {
        'size': ["reduce", 1],
        'modifier': ["regular", "italic", "bold", "bolditalic"] 
    },
    'pagenumber': {
        'size': ["reduce", 1],
        'modifier': ["regular", "bold"] 
    },
}

DEFAULTFONT = 'arial'
TESTINPUT = "./temp/input_test/"
TESTOUTPUT = "./temp/"

GRAPH_COLORS = ['viridis', 'plasma', 'cividis', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 
                'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 
                'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 
                'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdBu', 'RdYlBu', 'RdYlGn', 
                'Spectral', 'coolwarm', 'bwr', 'seismic', 'twilight', 'twilight_shifted', 
                'hsv', 'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 
                'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c', 
                'flag', 'prism', 'ocean', 'terrain', 'gist_stern', 'brg', 'gist_rainbow', 'rainbow', 'jet', 'turbo', 'gist_ncar']


FUNCTIONS = ["sin", "random", "cos", "tan", "exp", "expm1", "exp2", "log", "log10",
             "sin", "random", "cos", "exp", "expm1", "exp2", "log", "log10",
             "sin", "random", "cos", "exp", "expm1", "exp2", "log", "log10"]
        