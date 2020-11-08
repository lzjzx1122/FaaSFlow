from MontagePy.main import mImgtbl

def main(params):
    pathname = params['pathname']
    tblname = params['tblname']
    rtn = mImgtbl(pathname, tblname)
    return {'rtn': str(rtn)}