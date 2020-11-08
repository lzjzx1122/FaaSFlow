from MontagePy.main import mViewer

def main(params):
    cmdstr = params['cmdstr']
    rtn = mViewer(cmdstr, "", mode=2)
    return {'rtn': str(rtn)}