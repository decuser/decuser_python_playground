import itertools
 
# Get all combinations of [1, 2, 3]
chars = list("abcfrs")
args = []
combs = []
for char in chars:
	args.append(f"-{char}")
for i in range(1,len(args) + 1):
	combs += list(itertools.combinations(args, i))
 
# Print the obtained combinations
for x in combs:
	print("python ../dircmp.py ", end="")
	for y in range(0, len(x)):
		print(f"{x[y]}", end="")
		if y < len(x) + 1:
			print(" ", end="")
	print(" src dst")
