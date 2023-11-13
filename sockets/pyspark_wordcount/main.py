import sys
 
from pyspark import SparkContext
from collections import Counter
if __name__ == "__main__":
	
	sc = SparkContext("local","PySpark Word Count Exmaple")	

	# Regular approach
	with open('./test.txt', 'r') as f:
		lines = f.readlines()
		words = []
		for line in lines:
			words += list(line.split(' '))

		print(Counter(words))

	# Approach using pyspark
	words = sc.textFile("./test.txt").flatMap(lambda line: line.split(" "))
	wordCounts = words.map(lambda word: (word, 1)).reduceByKey(lambda a,b:a +b)	
	print(wordCounts)