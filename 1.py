import os
import re
file1 = open('input.txt', 'r')
file2 = open("output.txt", "w") 
Lines = file1.readlines()

list_all_words = [] #保留entry的顺序
# 一个词头允许同时出现于d1 d2
d1 = {}
d2 = {}
# 目前的链接源词头
k1 = ''
# 展开过的节点
list_done_words = []
# 树形图仅参考，已完成的树不会再嫁接上另一个树
tree = ''
print_tree = False
# 写词头与内容，d can be d1 or d2
def write_to_d(k,v,d):
    if k not in d:
        d[k] = [v]
    elif v not in d[k]:
        d[k].append(v)
# 展开一个有链接的词头
def dig(k,l=0):
    global tree
    global print_tree
    if l>1:
        print_tree = True
    list_done_words.append(k)
    for item in d2[k]:
        is_in_d1 = False
        if item in list_done_words:
            tree = tree + ' '*4*l+'+---'+item+': ✗'+'\n'
            continue
        if item in d1:
            is_in_d1 = True
            tree = tree + ' '*4*l+'+---'+item+': ✓'+'\n'
            for v in d1[item]:
                write_to_d(k1, v, d1)
        if item in d2:
            if not is_in_d1:
                tree = tree + ' '*4*l+'+---'+item+'\n'
            dig(item,l+1)
# Split file to d1,d2
current_word = ''
con = ''
is_head = True
no_non_link_line = True
has_link_line = False
linked_word = ''
word_count = 0
warnings = ''
for line in Lines:
    # head
    if is_head:
        current_word = line.rstrip("\n")
        word_count += 1
        if word_count%10000 == 0:
            print('read: '+str(word_count))
        if current_word not in list_all_words:
            list_all_words.append(current_word)
        con = ''
        is_head = False
        no_non_link_line = True
        has_link_line = False
        linked_word = ''
        continue
    # link
    matchObj = re.match('^@@@LINK=(.+)', line)
    if matchObj:
        if has_link_line:
            warnings += 'warning: more than one LINK line in entry: '
            warnings += current_word
            warnings += '\n'
        linked_word = matchObj.group(1) 
        write_to_d(current_word, linked_word, d2)
        has_link_line = True
        continue
    # end of an entry
    matchObj = re.match('^</>', line)
    if matchObj:
        if has_link_line and not no_non_link_line:
            warnings += 'warning: both LINK line and non-LINK line found in entry: '
            warnings += current_word
            warnings += '\n'
        if con != '':
            write_to_d(current_word, con, d1)
        is_head = True
        continue
    # content line
    no_non_link_line = False
    con += line

# 处理d2
d2_processed_count = 0
while bool(d2):
    k1 = list(d2.keys())[0]
    list_done_words=[]
    tree = k1 + '\n'
    print_tree = False
    dig(k1,0)
    if print_tree:
        print(tree)
    del d2[k1]
    d2_processed_count += 1
    if d2_processed_count%10000 == 0:
        print('processed: '+str(d2_processed_count))

# now d2 is empty, and all entry is in d1, let’s write d1 to a new file
f2_entrys_count = 0
for entry in list_all_words:
    if entry in d1:
        for content in d1[entry]:
            file2.write(entry)
            file2.write('\n')
            file2.write(content)
            file2.write('</>\n')
            f2_entrys_count += 1
            if f2_entrys_count%10000 == 0:
                print('wrote: '+str(f2_entrys_count))

file2.close()

print(warnings)
print('words:'+str(word_count)+' (in input file)')
print('words:'+str(f2_entrys_count)+' (in output file)')
print('words:'+str(len(list_all_words))+' (separate entrys, maybe with empty entrys)')

# remove the last empty line
with open('output.txt') as f_input:
    data = f_input.read().rstrip('\n')
with open('output.txt', 'w') as f_output:    
    f_output.write(data)
