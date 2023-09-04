# -*- coding:utf-8 -*-
from collections import defaultdict
import os, json, re
import couchdb


# couchdb_address = 'http://openwhisk:openwhisk@10.2.64.8:5984/'
# db = couchdb.Server(couchdb_address)

# def active_storage(avtive_type, user_object,document_id,filename,file_path=None,content_type=None, save_path=None):
#     if avtive_type == 'PUT':
#         content = open(file_path, 'rb')
#         user_object.put_attachment(user_object[document_id], content.read(), filename = filename, content_type = content_type)
#         content.close()
#     elif avtive_type == 'GET':
#         r = user_object.get_attachment(document_id,filename = filename)
#         with open(save_path,'wb') as f: f.write(r.read())


class DFAFilter():
    '''
    Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    '''

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode('utf-8')
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path) as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode('utf-8')
        message = message.lower()
        ret = []
        replaced = 0
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        replaced += 1
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1
        return ''.join(ret), replaced


gfw = DFAFilter()
gfw.parse("spooky_keywords")

# evt = json.loads(event)
# user_name = evt['user_name']
# document_id = evt['document_id']
# extracted_text_filename = evt['extracted_text_filename']

# user_object = db[user_name]

# input_path = os.path.join('..',user_name,document_id)
# input_filepath = os.path.join(input_path,extracted_text_filename)
# if os.path.exists(input_filepath):os.remove(input_filepath)
# else: os.makedirs(input_path)
# active_storage('GET', user_object,document_id,extracted_text_filename,save_path = input_filepath)

# with open(input_filepath,"r") as f:
#     text_content = f.read()
text_content = store.fetch(['text'])['text']

word_filter, filter_count = gfw.filter(text_content, "*")
print(word_filter, filter_count)
# document = user_object[document_id]
illegal = False
# output_result = {'filter_count': filter_count}
if filter_count >= 1:
    illegal = True
    # output_result['illegal_flag'] = True
    # output_result['illegal_reason'] = 'illegal: Spooky words detected in the image!'
illegal = True
# store.put(output_result, {})
store.post('illegal', illegal)
# main('{"user_name":"user_2","document_id":"object_id_1","extracted_text_filename":"extract_test.txt"}')
