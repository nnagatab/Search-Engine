import pickle
from collections import defaultdict
from datetime import datetime


global unionDict
unionDict = defaultdict(list)  # initialize defaultdict


def stringConvertToSet(str):  # helper function used to convert from textfile string into the uniondict
    listToAdd = str.split(":")
    if len(listToAdd) > 1:
        listToAdd[1] = eval(listToAdd[1][1:])
        unionDict[listToAdd[0]] = listToAdd[1]


def seekTokens(userTokens):  # function that takes in the users input and finds the location of the word they inputed
    for key in userTokens:
        try:
            if (key[0] <= "e"):
                location = AE.get(key)  # find location from pickle file
                AEtxt.seek(location)  # seek through the text file
                stringConvertToSet(AEtxt.readline())  # take the string and convert it into the dictionary
            elif (key[0] >= "f" and key[0] <= "k"):
                location = FK.get(key)
                FKtxt.seek(location)
                stringConvertToSet(FKtxt.readline())
            elif (key[0] >= "l" and key[0] <= "p"):
                location = LP.get(key)
                LPtxt.seek(location)
                stringConvertToSet(LPtxt.readline())
            elif (key[0] >= "q" and key[0] <= "u"):
                location = QU.get(key)
                QUtxt.seek(location)
                stringConvertToSet(QUtxt.readline())
            elif ((key[0] >= "v" and key[0] <= "z") or (key[0] >= "0" and key[0] <= "9")):
                location = VZ.get(key)
                VZtxt.seek(location)
                stringConvertToSet(VZtxt.readline())
            else:
                print("not a valid input")
        except:
            del unionDict[key]


def retrieveSearch(sortedList):  #
    resultDocuments = set()
    if len(sortedList) == 1:  # checks if userInput is only 1 word
        resultDocuments = unionDict[sortedList[0]]
    else:
        try:
            for i in range(len(sortedList)):
                if len(resultDocuments) == 0:
                    resultDocuments = unionDict[sortedList[i]].intersection(unionDict[sortedList[i + 1]])
                    # intersect through the words to do boolean searching
                else:
                    resultDocuments = resultDocuments.intersection(unionDict[sortedList[i]])
        except IndexError as error:
            print('Ran into indexing error')

    returnList = []
    for i in (list(resultDocuments)):
        returnList.append(i)
        if len(returnList) == 5:
            break

    return returnList  # return list of websites that are intersected


def retrieveHash(searchResults):  # takes in the results and finds the websites urls
    websites = []
    hashvalues = []
    for i in searchResults:  # take the hashvalue from the tuple
        hashvalues.append(i[0])
    for x in hashvalues:  # from the hashtable get the url
        websites.append(hashTable.get(x))
    return websites  # return urls


def main():
    sortedList = []
    userInput = input("Enter search query: ")
    startTime = datetime.now()  # time ourselves
    userTokens = userInput.lower().split()
    seekTokens(userTokens)
    sortedList = sorted(unionDict, key=lambda x: len(x[1]))  # ordered from lowest to highest

    searchResults = retrieveSearch(sortedList)
    urls = retrieveHash(searchResults)
    print("Here are the websites: ")  # print for console
    for i in urls:
        print(i + " ")
    print("This is how long the query took: " + str((datetime.now() - startTime)))


AEtxt = open("AE.txt", "r")
FKtxt = open("FK.txt", "r")
LPtxt = open("LP.txt", "r")
QUtxt = open("QU.txt", "r")
VZtxt = open("VZ.txt", "r")
AE = pickle.load(open("AE.p", "rb"))
FK = pickle.load(open("FK.p", "rb"))
LP = pickle.load(open("LP.p", "rb"))
QU = pickle.load(open("QU.p", "rb"))
VZ = pickle.load(open("VZ.p", "rb"))
global hashTable
hashTable = pickle.load(open("hashlibrary.p", "rb"))

main()

AEtxt.close()
FKtxt.close()
LPtxt.close()
QUtxt.close()
VZtxt.close()
