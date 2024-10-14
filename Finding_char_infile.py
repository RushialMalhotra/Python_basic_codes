from sys import argv
char = argv[1]
input_file = argv[2]

total_number = 0

for line in open(input_file):
    for word in line:
            if word == char:
                total_number = total_number+1
print("The number of {} is {}.".format(char, total_number))

