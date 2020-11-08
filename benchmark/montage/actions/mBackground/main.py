from MontagePy.main import mBgModel

def main(params):
    input_file = params['input_file']
    output_file = params['output_file']
    A = params['A']
    B = params['B']
    C = params['C']
    rtn = mBgModel(input_file, output_file, A, B, C)
    return {'rtn': str(rtn)}