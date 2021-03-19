import sys
import re
import os
import json
import pickle
from lxml import html
# from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# sw = set(stopwords.words('english'))
global documentFinder, AE, FK, LP, QU, VZ, tempAE, tempFK, tempLP, tempQU, tempVZ
AE = {}  # holds tokens that start from A-E ...
FK = {}
LP = {}
QU = {}
VZ = {}  # holds token that start from V-Z || 0-9
tempAE = {}
tempFK = {}
tempLP = {}
tempQU = {}
tempVZ = {}

txtList = ["AE.txt", "FK.txt", "LP.txt", "QU.txt", "VZ.txt"]
fileList = ["AE.p", "FK.p", "LP.p", "QU.p", "VZ.p"]
tempDict = [tempAE, tempFK, tempLP, tempQU, tempVZ]  # list of temp dicts
dictList = [AE, FK, LP, QU, VZ]  # list of main dicts
tokenFrequency = {}


class tokenClass:  # Token class that allows us to reach tf_idf as well as the set of urls
    def __init__(self):
        self.tf_idf = 0
        self.urlSet = set()
        self.url = ""


def hashURL(val, url):
    try:
        with open("hashlibrary.p", "rb") as hashLibrary:  # open hashlibrary picklefile
            hashDict = pickle.load(hashLibrary)
            # if hashValue is not found in keys
            if (val not in hashDict.keys()):
                # we add a new dictionary entry < hashValue: URL >
                hashDict[val] = url
            with open("hashlibrary.p", "wb") as fileWrite:
                pickle.dump(hashDict, fileWrite)
    except:
        with open("hashlibrary.p", "wb") as file:
            hashLibrary = {}
            hashLibrary[val] = url
            pickle.dump(hashLibrary, file)


def mergeFiles(inputMap, pickleFile):  # use this function to save memory
    # using pickle library, load into a variable
    try:
        with open(pickleFile, "rb") as fileName:
            finalMap = pickle.load(fileName)  # load into memory the pickle dictionary
            for key in inputMap:  # for each key in
                if key in finalMap.keys():
                    finalMap[key].urlSet = finalMap[key].urlSet.union(
                        inputMap[key].urlSet)  # combing urlsets
                else:
                    finalMap[key] = tokenClass()
                    finalMap[key].urlSet = inputMap[key].urlSet
        with open(pickleFile, "wb") as fileName:
            pickle.dump(finalMap, fileName)  # dumping the data into the picklefile
    except:
        with open(pickleFile, "wb") as fileName:
            pickle.dump(inputMap, fileName)


def tokenize(resp, url, val):  # tokenize words and put them into their correct files based on alphaetical order
    # tempMap = {}
    hashURL(val, url)
    ps = r"\b[a-zA-Z0-9]+\b"
    tokens = re.findall(ps, resp)
    # regex used for every range of letters
    regexAE = r"\b[a-e]"
    regexFK = r"\b[f-k]"
    regexLP = r"\b[l-p]"
    regexQU = r"\b[q-u]"
    regexVZ = r"\b[v-z0-9]"

    for word in tokens:
        token = word.lower()

        if (re.search(regexAE, token)):
            if (token in tempAE):
                tempAE[token].tf_idf += 1
            else:
                tempAE[token] = tokenClass()
                tempAE[token].tf_idf = 1
                tempAE[token].url = val

        elif (re.search(regexFK, token)):
            if (token in tempFK):
                tempFK[token].tf_idf += 1
            else:
                tempFK[token] = tokenClass()
                tempFK[token].tf_idf = 1
                tempFK[token].url = val

        elif (re.search(regexLP, token)):
            if (token in tempLP):
                tempLP[token].tf_idf += 1
            else:
                tempLP[token] = tokenClass()
                tempLP[token].tf_idf = 1
                tempLP[token].url = val

        elif (re.search(regexQU, token)):
            if (token in tempQU):
                tempQU[token].tf_idf += 1
            else:
                tempQU[token] = tokenClass()
                tempQU[token].tf_idf = 1
                tempQU[token].url = val

        elif (re.search(regexVZ, token)):
            if (token in tempVZ):
                tempVZ[token].tf_idf += 1
            else:
                tempVZ[token] = tokenClass()
                tempVZ[token].tf_idf = 1
                tempVZ[token].url = val


def writeToFile(finalMap, txtFile, num):  # helper function that is used to write the data to text files.
    with open(txtFile, "w") as final_report:
        final_report.write("Number of Documents: " + str(num) + "\n")
        final_report.write("Number of Unique Tokens: " +
                           str(len(finalMap.keys())) + "\n")
        for token in sorted(finalMap.items(), key=lambda x: x[1].tf_idf, reverse=True):
            final_report.write(str(
                token[0]) + ": " + str(token[1].urlSet) + "\n")


def mergeMap(temp, final):  # helper function that is used to merge the temp dictionaries with the final dictionaries
    for key in temp:
        if (key in final.keys()):
            final[key].urlSet.add(
                (temp[key].url, temp[key].tf_idf))
        else:
            final[key] = tokenClass()
            final[key].urlSet.add(
                (temp[key].url, temp[key].tf_idf))


def clearDictionaries(mapList):  # used to clear temp dictionaries in order to save memory
    for dictionary in mapList:
        dictionary.clear()


def sortTxtFiles(txtFile, hashDictionary):
    with open(txtFile, 'r') as f:
        words = f.readlines()

        words = [word.strip() for word in words]
        words.sort()

    with open(txtFile, 'w') as f:
        for line in words:
            location = f.tell()
            f.write(line + "\n")
            x = line.split(":")
            hashDictionary[x[0]] = location


def main():
    breakTrue = False
    numDocuments = 0
    readDocuments = 0
    hashValue = 0
    for root, subdirectories, files in os.walk(r'.\DEV'):  # go through directories and finding files
        for filename in files:
            numDocuments += 1  # increment document count
            print(numDocuments)  # used for knowing where at in console
            result = os.path.join(root, filename)  # join the root directory with the file name
            f = open(result)  # open above file
            current_website = json.load(f)  # use json in order to load website
            soup = BeautifulSoup(current_website["content"], 'lxml')  # bs4 to get the content
            tokenize(soup.get_text(), current_website["url"], hashValue)  # tokenize using found data
            for index in range(5):  # merge temp dictionaries with final dictionaries
                mergeMap(tempDict[index], dictList[index])
            clearDictionaries(tempDict)  # clear temp dictionaries
            if readDocuments == 500:  # after 500 documents merge files, reset count, and clear dictionaries
                for index in range(5):
                    mergeFiles(dictList[index], fileList[index])
                clearDictionaries(dictList)  # clear sum of dictionaries
                readDocuments = 0

            readDocuments += 1
            hashValue += 1

    for index in range(5):  # write the text files
        finalMap = pickle.load(open(fileList[index], "rb"))
        writeToFile(finalMap, txtList[index], numDocuments)
        clearDictionaries(dictList)
    for index in range(5):  # sort and merge the files
        sortTxtFiles(txtList[index], dictList[index])
        mergeFiles(dictList[index], fileList[index])

    hashLibrary = pickle.load(open("hashlibrary.p", "rb"))
    hashLibraryReport = open("hashlibrary.txt", "w")
    hashLibraryReport.write(str(hashLibrary))  # write the hashlibrary into text file


main()  # call to main to run indexer
