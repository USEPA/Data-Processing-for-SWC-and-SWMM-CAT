import os

def read_tables():
    """
    Reads all temporal distributions in directory

    Temporal distributions were created by running WinTR-20
    and saving each separately as a text file in a directory
    nrcs_tables. Headers produced by WinTR-20 were kept.

    Returns a dict with the key as the distribution name
    (which is also the filename corresponding to the distribution)
    and the value a list of the 241 corresponding percentages
    of rainfall as strings.
    """

    table_dict = {}
    for item in os.listdir('nrcs_tables'):
        table_id = item.split('.')[0]
        with open(os.path.join('nrcs_tables', item), 'r') as file:
            data = file.readlines()

        header = data.pop(0)

        flat_data = []
        for x in data:
            for a in x.split():
                flat_data.append(str(round(float(a)*100, 3)))

        table_dict[table_id] = flat_data

    return table_dict

def write_file(table_dict):
    """
    Writes file in format SWC expects.

    Header is the word Time followed by each distribution name.
    Each line is a six-minute interval followed by each
    temporal distribution's value at that time.
    File is tab-separated.
    """

    times = [x/10 for x in range(0, 241)]
    table_ids = list(table_dict.keys())

    lines = []
    for i in range(0, 241):
        line = [str(times[i])]

        for table_id in table_ids:
            line.append(table_dict[table_id][i])

        lines.append(line)

    table_ids.insert(0, 'Time')

    with open('SCS24Hour.txt', 'w') as file:
        file.write('\t'.join(table_ids))
        file.write('\n')
        for each_line in lines:
            file.write('\t'.join(each_line))
            file.write('\n')


if __name__ == '__main__':
    nrcs_tables = read_tables()
    write_file(nrcs_tables)
