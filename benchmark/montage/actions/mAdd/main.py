from MontagePy.main import mAdd

def main(params):
    path = params['path']
    tblfile = params['tblfile']
    template_file = params['template_file']
    outfile = params['outfile']
    rtn = mAdd(path, tblfile, template_file, outfile)
    return {'rtn': str(rtn)}