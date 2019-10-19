from yaml import safe_load as yaml_safe_load

with open('content.yml', 'r') as content_file:
    content = yaml_safe_load(content_file.read())
