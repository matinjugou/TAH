import sys

nthreads = 4
ndevice = 6

if len(sys.argv)==1:
	print "Usage[databse_file][test_file]"
	exit()

file_input_database = open(sys.argv[1], 'r')
file_input_test = open(sys.argv[2], 'r')
file_output_database = [open("parallel24/database" + str(i) + ".txt", 'w') for i in range(nthreads * ndevice)]
file_output_test = [open("parallel24/test" + str(i) + ".txt", 'w') for i in range(nthreads * ndevice)]
count = 0
file_input_database_list = []
file_input_test_list = []
while 1:
	lines = file_input_database.readlines(100000)
	if not lines:
		file_input_database.close()
		break
	for line in lines:
		count += 1
		file_input_database_list.append(line)
		pass
	pass
for i in range(count):
	file_output_database[i % (nthreads * ndevice)].write(file_input_database_list[i])
count = 0
while 1:
	lines = file_input_test.readlines(100000)
	if not lines:
		file_input_test.close()
		break
	for line in lines:
		count += 1
		file_input_test_list.append(line)
		pass
	pass
for i in range(count):
	file_output_test[i % (nthreads * ndevice)].write(file_input_test_list[i])
for i in range((nthreads * ndevice)):
	file_output_database[i].close()
	file_output_test[i].close()

