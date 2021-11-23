import markdown

def main():
    content = store.fetch(['file'])['file']
    html = markdown.markdown(content)
    store.put({'html': html}, {})