'''Print the words and their frequencies in this file'''

import operator
import pyspark

def main():
    '''Program entry point'''

    #Intialize a spark context
    with pyspark.SparkContext("local", "PySparkWordCount") as sc:
        #Get a RDD containing lines from this script file  
        lines = sc.textFile(__file__)
        #Split each line into words and assign a frequency of 1 to each word
        words = lines.flatMap(lambda line: line.split(" ")).map(lambda word: (word, 1))
        #count the frequency for words
        counts = words.reduceByKey(operator.add)
        #Sort the counts in descending order based on the word frequency
        sorted_counts =  counts.sortBy(lambda x: x[1], False)
        #Get an iterator over the counts to print a word and its frequency
        for word,count in sorted_counts.toLocalIterator():
            print(u"{} --> {}".format(word, count))

if __name__ == "__main__":
    main()