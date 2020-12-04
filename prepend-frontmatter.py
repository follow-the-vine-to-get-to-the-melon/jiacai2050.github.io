#!/usr/bin/env python

from os import listdir
from os.path import isfile, join

post_dir = "./content/post"
for f in listdir(post_dir):
    fname = join(post_dir, f)
    if isfile(fname):
        new_content = []
        with open(fname) as post:
            first_line = True
            for line in post:
                if first_line and '--' not in line:
                    new_content.append('---\n')
                first_line = False

                new_content.append(line)

        with open(fname, 'w') as post:
            post.write(''.join(new_content))
