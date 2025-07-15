def main():
    data = loadFile('escolas.txt')

    with open('escolas.csv', 'w', newline='') as fp:
        a = csv.writer(fp,)
        a.writerows([(r, ) for r in data])