import markdown
from Store import Store

store = Store(workflow_name, function_name, request_id, input, output, to, keys)

def main():
    content = store.fetch(['file'])['file']
    html = markdown.markdown(content)
    store.put({'html': html}, {})