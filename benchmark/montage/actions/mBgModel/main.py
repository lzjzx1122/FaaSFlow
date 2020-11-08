from MontagePy.main import mBgModel

def main(params):
    input_file = params['input_file']
    fit_file = params['fit_file']
    corr_file = params['corr_file']
    rtn = mBgModel(input_file, fit_file, corr_file)

    # Extract parameters which will be used by mBackground
    A, B, C = [], [], []
    with open(corr_file, 'r') as f:
        s = f.readlines()
    for i in range(1, len(s)):
        tmp = s[i].split()
        A.append(eval(tmp[1]))
        B.append(eval(tmp[2]))
        C.append(eval(tmp[3]))

    return {'rtn': str(rtn), 'a': A, 'b': B, 'c': C}