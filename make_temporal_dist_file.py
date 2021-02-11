import os

def read_tables():

    table_dict = {}
    for item in os.listdir('nrcs_tables'):
        table_id = item.split('.')[0]
        with open(os.path.join('nrcs_tables', item), 'r') as file:
            data = file.readlines()

        header = data.pop(0)

        flat_data = []
        for x in data:
            for a in x.split():
                flat_data.append(a)

        table_dict[table_id] = flat_data

    return table_dict

def write_file(table_dict):
    times = [x/10 for x in range(0, 241)]
    table_ids = list(table_dict.keys())

    lines = []
    for i in range(0, 241):
        line = [str(times[i])]

        for table_id in table_ids:
            line.append(table_dict[table_id][i])

        lines.append(line)

    table_ids.insert(0, 'Time')

    with open('temporal_dist_file.txt', 'w') as file:
        file.write('\t'.join(table_ids))
        file.write('\n')
        for each_line in lines:
            file.write('\t'.join(each_line))
            file.write('\n')

if __name__ == '__main__':
    nrcs_tables = read_tables()
    write_file(nrcs_tables)
