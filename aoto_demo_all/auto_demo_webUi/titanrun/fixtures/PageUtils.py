import requests


def jq_format(code):
    code = code.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n')
    code = code.replace('\"', '\\\"').replace('\'', '\\\'')
    code = code.replace('\v', '\\v').replace('\a', '\\a').replace('\f', '\\f')
    code = code.replace('\b', '\\b').replace(r'\u', '\\u').replace('\r', '\\r')
    return code


def get_domain_url(url):
    url_header = url.split('://')[0]
    simple_url = url.split('://')[1]
    base_url = simple_url.split('/')[0]
    domain_url = url_header + '://' + base_url
    return domain_url


def is_xpath_selector(selector):
    if (selector.startswith('/') or
            selector.startswith('./') or
            selector.startswith('(')):
        return True
    return False


def _download_file_to(file_url, destination_folder, new_file_name=None):
    if new_file_name:
        file_name = new_file_name
    else:
        file_name = file_url.split('/')[-1]
    r = requests.get(file_url)
    with open(destination_folder + '/' + file_name, "wb") as code:
        code.write(r.content)
