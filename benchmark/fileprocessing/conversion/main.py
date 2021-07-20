import markdown
from Store import Store
def main(function_name, request_id, runtime, input, output, to, keys):
    store = Store(function_name, request_id, input, output, to, keys)
    content = store.fetch(['file'])['file']
    html = markdown.markdown(content)
    store.put({'html': html}, {'html': 'text/html'})