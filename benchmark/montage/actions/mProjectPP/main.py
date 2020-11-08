from MontagePy.main import mProjectPP

def main(params):
    input_file = params['input_file']
    output_file = params['output_file']
    template_file = params['template_file']
    rtn = mProjectPP(input_file, output_file, template_file)
    return {'rtn': str(rtn)}