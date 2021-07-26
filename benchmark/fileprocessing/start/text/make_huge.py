new_text_line = ['Introduction\n', 'This is a report that captures important information regarding an interview.\n']
for _ in range(200000):
    new_text_line.append('Interview 1\n')
    new_text_line.append('The person I spoke with was elated.  They used words like \'fantastic\', \'impressive\', and \'ground breaking\' to describe the new thing.\n')
with open('sample.md', 'w') as f:
    for t in new_text_line:
        f.write(t)
