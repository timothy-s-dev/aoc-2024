def run(input_file, part):
    column1, column2 = process_file(input_file)
    result = 0
    for i in range(0, len(column1)):
        if part == 1:
            result += abs(column1[i] - column2[i])
        else:
            occurences = column2.count(column1[i])
            result += column1[i] * occurences
    print(result)


def process_file(input_file):
    column1 = []
    column2 = []
    for line in input_file:
        val1, val2 = [int(x) for x in line.split('   ')]
        column1.append(val1)
        column2.append(val2)
    column1.sort()
    column2.sort()
    return column1, column2
