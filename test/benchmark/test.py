import yaml

yaml_data2 = {"functions": ['A', 'B']}
f = open('test.yaml', 'w', encoding = 'utf-8')
yaml.dump(yaml_data2, f, sort_keys=False)
