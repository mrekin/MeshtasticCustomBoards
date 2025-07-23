import configparser
import os
import json
import argparse
import re

my_args = []
files =[]
filledSections = []

def init():
    parser = argparse.ArgumentParser(description='Args parser')
    parser.add_argument('-d','--dir', type=str, default='.', help='Path to directory')
    parser.add_argument('-r','--recurcive',  action=argparse.BooleanOptionalAction, help='Recurcieve search')
    parser.add_argument('-m','--mask', type=str, default='.*\\.ini', help='PyRegex for file filtering by name. Can be used with `-e` option')
    parser.add_argument('-e','--extention', type=str, default='.ini', help='List of file extentions for file filtering. Comma separated. Can be used with `-m` option')
    parser.add_argument('-k','--keymask', type=str, default=r'.*', help='PyRegex for config key filtering')
    parser.add_argument('-s','--resolve', action=argparse.BooleanOptionalAction, help='Resolve variables in values')
    parser.add_argument('-a','--arguments',action=argparse.BooleanOptionalAction, help='Try parse param value as arguments, will try to represent string value as groups list or args')
    parser.add_argument('-p','--parammask',type=str, default=r'.*', help='PyRegex for config value filtering')
    parser.add_argument('-g','--groups',type=str, default=None, help='List of args groups for filtering, comma separated. Use with `-a`. Example: `D,I,W`')
    parser.add_argument('-j','--json',action=argparse.BooleanOptionalAction, help='Format Json output')
    
    global my_args
    my_args = parser.parse_args()
    #print(my_args)
    #Some args validation here (?)

def searchIni():
    # TBD need to parse first `extra_configs` in main ini file and then search ini files only here.
    # Currently loads all ini files.
    flist = []
    pattern = re.compile(my_args.mask)
    for address, _dirs, files in os.walk(my_args.dir, topdown=True if my_args.recurcive else False, onerror=None, followlinks=False):
        for file in files:
            if pattern.match(file):
                #print(f'{address}/{file}')
                flist.append(f'{address}/{file}')
    return flist

# TBD Need to solve recurcive loops if it happens
# TBD No need to resolve multiple times the same var, maybe need keep resolved dict
def resolveVars(value:str, config):
    resolved = True
    value = value.replace("\n"," ")
    var_pattern = re.compile(r'\${([^{}]+)}')
    #matches= re.search(var_pattern, value)
    for var in re.finditer(var_pattern, value):
        parts = var.group(1).split('.')
        t = config
        for p in parts:
            if p in t:
                t = t[p]
            else:
                #Can't resolve var (pio has default value, or `this.` - env variable or missconfig), so leaving as is
                resolved = False
                break
                
        if resolved: 
            t = resolveVars(t,config)
            t = t.strip()
            t = t.replace("\n"," ")
            value = value.replace(var.group(0),t.strip())
    #value = resolveVars(value,config)
    return value

   
# TBD move comment prefixes to args
def parseIni(files):
    config = configparser.ConfigParser(inline_comment_prefixes=';')
    for file in files:
        config.read(file)

    #fill sections by extends/parents
    sections = config.sections()# Get all sections
    for section in sections:
        config =infill(config,section)
    
    return config

def infill(config,section): # Fill recurceivly every section by parent section params, defined in `extends` param
    if config.has_option(section,'extends') and section not in filledSections:
        parent = config[section]['extends']
        if parent in config:
            if config.has_option(parent,'extends') and parent not in filledSections:
                infill(config,parent)                    
            for key in config[parent]:
                if not config.has_option(section,key):
                    config[section][key] = config[parent][key]
            filledSections.append(section)# Add section to filled sections list
    return config
    
       
def filterData(config:configparser.ConfigParser):
    cfg = {}
    key_pattern = re.compile(my_args.keymask)
    value_pattern = re.compile(my_args.parammask)
    #group_pattern = re.compile(my_args.groupmmask)
    sections = config.sections()
    for section in sections:
        cfg[section]={}
        for key in config[section]:
            if re.match(key_pattern,key):
                if my_args.resolve:
                    val=resolveVars(config[section][key],config)
                else:    
                    val=config[section][key]
                # Try parse val as args (-a)
                if my_args.arguments:
                    cmd = argparse.ArgumentParser()
                    if my_args.groups:
                        for g in my_args.groups.strip().split(','):
                            cmd.add_argument(f"-{g.strip()}", action=argparse._AppendAction, default=[])                    
                    args, unknown = cmd.parse_known_args(val.split())
                    val = vars(args)
                    val['unknown'] = unknown


                # Filter values (-p)
                if my_args.arguments:
                    #val is dict
                    keys = set(val.keys())
                    for k in keys:
                        kval = set(val[k]) #set of values
                        for v in val[k]:
                            if not re.match(value_pattern,v):
                                kval.discard(v)
                        if len(kval) ==0:
                            val.pop(k)
                        else:
                            val[k]=list(kval)
                    if val != {}:
                        cfg[section][key] = val
                else:
                    #val is str
                    if re.match(value_pattern,val):
                        cfg[section][key] = val
    
    sections = list(cfg.keys())
    for section in sections:
        if cfg[section] == {}:
            cfg.pop(section)

    

    
    #test = config['env:tbeam']['build_flags'].strip()
    #test = resolveVars(test,config)
    #cmd = argparse.ArgumentParser()
    #cmd.add_argument('-I', action=argparse._AppendAction, default=[])
    #cmd.add_argument('-W', action=argparse._AppendAction, default=[])
    #args, unknown = cmd.parse_known_args(test.split())
    return cfg

def configToJson(config):
    jdict={}
    sections= config.sections()
    for section in sections:
        items=config.items(section)
        jdict[section]=dict(items)
    return json.dumps(jdict)

if __name__ == "__main__":
    init()
    files = searchIni()  # array of files paths
    config = parseIni(files) # load ini files to mem
    cfg = filterData(config) # Also makes dict from config
    if my_args.json:
        res = json.dumps(cfg,indent=4, sort_keys=True)
    else:
        res = json.dumps(cfg)
    print(res)
