from dataclasses import dataclass

@dataclass
class Margin:
    top:float
    right:float
    bottom:float
    left:float

    @classmethod
    def from_list(cls, margin_list, is_percentage=False):
        if len(margin_list) != 4: return
        factor = 100 if is_percentage else 1
        return cls(top=margin_list[0]/factor, right=margin_list[1]/factor, 
                bottom=margin_list[2]/factor, left=margin_list[3]/factor)

