from MontagePy.main import mDiffFitExec

def main(params):
    path = params['path']
    tblfile = params['tblfile']
    template = params['template']
    diffdir = params['diffdir']
    fitfile = params['fitfile']
    rtn = mDiffFitExec(path, tblfile, template, diffdir, fitfile)
    return {'rtn': str(rtn)}
