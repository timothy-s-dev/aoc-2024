def run(input_file, part):
    result = 0
    for line in input_file:
        values = [int(x) for x in line.split(' ')]
        if is_safe(values):
            result += 1
        elif part == 2:
            for i in range(0, len(values)):
                if is_safe(values[:i] + values[i+1:]):
                    result += 1
                    break
    print(result)

def is_safe(values):
    deltas = [values[i+1] - values[i] for i in range(0, len(values) - 1)]

    positive = [x > 0 for x in deltas]
    negative = [x < 0 for x in deltas]
    if not all(positive) and not all(negative):
        return False

    small = [abs(x) >= 1 and abs(x) <=3 for x in deltas]
    return all(small)