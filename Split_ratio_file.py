from sys import argv
nof = argv[1]
split_ratio = argv[2]

if len(argv) < 3 :
    print("Usage: split.py file.txt ratio")
    print("file.txt must be an existing text file")
    print("ratio must be between 0.0 and 1.0")
    print("Creats two files (before.txt) and after.txt ")

no_of_lines = 0
i = 0

for line in open(nof):
    no_of_lines = no_of_lines + 1

#before.txt
out_file = open("before.txt","w")
original_file = open(argv[1])
lines_to_write = no_of_lines * float(argv[2])
for line in range(int(lines_to_write)):
    out_file.write(original_file.readline())

#after.txt
out_file = open("after.txt", "w")
for line in original_file:
    out_file.write(line)

original_file.close()
out_file.close()
