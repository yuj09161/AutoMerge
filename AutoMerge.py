import os
import re
import datetime


def natsort(sortable):
    return sorted(
        sortable,
        key=lambda item: [
            (int(part) if part.isdigit() else part)
            for part in re.split('([0-9]+)', item)
        ]
    )


# constants
NL = '\n'
PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__)) + os.sep

# variables
turtle_func = ''
console_func = ''
turtle_names = []
console_names = []
turtle_file = []
console_file = []
imports = set()


# parsing source
for name in natsort(os.listdir(PROGRAM_DIR)):
    if os.path.isfile(PROGRAM_DIR + name) and '_' in name:
        if name.split('_', 1)[0].isnumeric():
            is_turtle = False
        elif name.split('_', 1)[0].isalpha():
            is_turtle = True
        else:
            continue

        # determine function title
        title = os.path.splitext(os.path.basename(name))[0].split('_', 1)[1]

        # read source file
        with open(PROGRAM_DIR + name, 'r', encoding='utf-8') as file:
            raw_source = file.read()

        # remove unnecessary blank line(s)
        raw_source = re.sub('\n{3,}', '\n\n', raw_source)

        # remove import(s) from function part
        lines = raw_source.replace('turtle.done()', '').split('\n')
        linecnt = len(lines)
        k = 0
        while k < linecnt:
            if lines[k].startswith('import') or lines[k].startswith('from'):
                imports.add(lines.pop(k))
                linecnt -= 1
            else:
                k += 1

        # generate source
        source = '\n'.join((
            # function definition
            f'def {title}():',
            # remove blank(s) on sides and give indentation
            ' ' * 4 + '\n'.join(lines).strip('\n').replace('\n', '\n    '),
            # blank lines at end
            '\n' * 3
        ))

        if is_turtle:
            turtle_names.append(title)
            turtle_file.append(name)
            turtle_func += source
        else:
            console_names.append(title)
            console_file.append(name)
            console_func += source


# generate head part
head = f"""'''
{'#' * 10}
This file is merged by AutoMerge
(Generated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})

AutoMerge is made by Yunseong Ha,
undergraduate of Kyungpook National University.
(https://github.com/yuj09161/AutoMerge)
(License: MIT)

Original source names:
    Python file that contains "console_func":
    {(NL + ' ' * 4).join(console_file)}

    Python file that contains "turtle_func":
    {(NL + ' ' * 4).join(turtle_file)}
{'#' * 10}
'''

"""


# generate bottom part
bottom = f'''console_func = [\n    {(',' + NL + ' ' * 4).join(console_names)}\n]
turtle_func = [\n    {(',' + NL + ' ' * 4).join(turtle_names)}\n]''' + '''

if __name__ == '__main__':
    # pylint: disable = no-member
    print('#####CONSOLE OUTPUT#####')
    for index, func in enumerate(console_func, 1):
        print(f'{index}_{func.__name__}')
        func()
        print()

    print('#####TURTLE OUTPUT#####')
    for func in turtle_func:
        print(f'{func.__name__}')
        turtle.reset()
        func()
        print()

    turtle.done()
'''


# merge & write to file
merged = (
    head
    + '\n'.join(imports) + '\n' * 3
    + '#####Console Functions#####  # noqa: E265' + '\n' * 3
    + console_func
    + '#####Turtle Functions#####  # noqa: E265' + '\n' * 3
    + turtle_func
    + '#####Bottom Parts#####  # noqa: E265' + '\n' * 3
    + bottom
).replace('    \n', '\n')
merged = re.sub('\n{4,}', '\n\n\n', merged)
with open('merged.py', 'w', encoding='utf-8') as file:
    file.write(merged)
