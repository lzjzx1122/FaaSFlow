from MontagePy.main import mOverlaps

def main(params):
    tblfile = params['tblfile']
    difftbl = params['difftbl']
    rtn = mOverlaps(tblfile, difftbl)
    return {'rtn': str(rtn)}