import configparser

def read_config(filename, section):
    cfg= configparser.ConfigParser()
    cfg.read(filename)
    return {option: cfg.get(section, option) for option in cfg.options(section)}