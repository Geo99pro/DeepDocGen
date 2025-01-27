
def get_min_max_values(block_config):
    vmin = block_config.get("min", None)
    vmax = block_config.get("max", None)
    val = vmin if vmin is not None else vmax
    if vmin is None or vmax is None: 
        return [val, val]

    return [vmin, vmax]