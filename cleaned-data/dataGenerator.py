import csv, sys, re, ast
new_lines = []

def remove_duplicates(values):
	output = []
	seen = set()
	for value in values:
		if value not in seen:
			output.append(value)
			seen.add(value)
	return output

f=open("/Users/Minae/Desktop/test/thirdbatch-nv.txt", 'r')

lines = f.readlines()
lines = lines[len(lines)-1]
#print lines

# start = lines.find("{")
# end = lines.find("}")
# lines=lines[start:end]
# lines = lines+"}"


#converting string to dictionary 
data = ast.literal_eval(lines)



incomplete ={}
#first cutting out incomplete responses:
for key in data.keys():
	if (len(data[key])<47):
		incomplete[key]=data[key]
		del data[key]

#cutting out rejected results **THIS PART NEEDS TO BE CUSTOMIZED**
for key in data.keys():
	if("39686U" in key):
		del data[key]

for key in data.keys():
	print key, data[key]
	print " "

list_data = []
for key in data.keys():
	#this is your list
	data[key].insert(0, key)
	new_line=[]
	new_line_cpy = []
	new_line_cpy2 = []

	for k in data[key]:
		k=str(k)
		new_line.append(k)
		new_line_cpy.append(k)

	#getting first binary string 
	for x in xrange(0,len(new_line)):
		if ("start:" in new_line[x]):
			start = x
			bin_string = ''
			while("trial" not in new_line[x+1]):
				#print "NEW LINE" + new_line[x+1]
				bin_string=bin_string+new_line[x+1]
				new_line_cpy.remove(new_line[x+1])
				#print "BIN STRING1: " + bin_string
				x=x+1

			new_line_cpy.insert(start+1, bin_string)
		
	for item in new_line_cpy:
		new_line_cpy2.append(item)
	#getting second binary string 
	for x in xrange(0, len(new_line_cpy)):
		if "secondStart" in new_line_cpy[x]:
			secondstart = x
			bin_string = ''
			while('secondfinish' not in new_line_cpy[x+1]):
				bin_string = bin_string+new_line_cpy[x+1]
				new_line_cpy2.remove(new_line_cpy[x+1])
				#print "BIN STRING2: " + bin_string
				x=x+1
			new_line_cpy2.insert(secondstart+1, bin_string)
			# print new_line_cpy2
			# print " "

	new_line_cpy3=[]

	#partitioning the list into two parts:
	for i in xrange(0,len(new_line_cpy2)):
		if('round two' in new_line_cpy2[i]):
			new_line_cpy3 = remove_duplicates(new_line_cpy2[:i])
			new_line_cpy3.extend(new_line_cpy2[i:])
			# print "NEWLINE: " + str(new_line_cpy3)
			# print " "

	new_lines.append(new_line_cpy3)



out = open('out-thirdbatch-nv.csv', 'w')
for row in new_lines:
	for column in row:
		out.write('%s,' % column)
	out.write('\n')
out.close()




