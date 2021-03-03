from flask import Flask#importing all the python modules used in the code
from flask import request
from flask import render_template
import nltk
import operator
from operator import itemgetter
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import inflection
from inflection import singularize
from collections import OrderedDict
nltk_words = set(stopwords.words('english'))#setting the stopword index to english version
stop_words=[]
for x in nltk_words:
    stop_words.append(x)
    stop_words.append(x.capitalize())#putting the stopwords in an array for easy looping

stop_words.extend(("us","say","put","look","occur","best","believe","see","like","bring","let"))#some extra stopwords that the original missed

app = Flask(__name__, static_folder="static/dist", template_folder="static")#defines the flask app including the file location for templates

indexpage='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Semantic Text Searcher</title>
<style>
#title{
	font-family:"Comic Sans MS";
	text-align:center;
	}
#form{
	padding-right:100px;
	padding-left:100px;
	text-align:center;
	margin-top:50px;
	
	}
	
#links{
width:100%;
text-align:center;


}

#links a{
margin-left:5px;
margin-right:5px;

}


</style>
</head>
<body>
    <div id="title"><h1>Semantic Text Searcher</h1></div>
    <div id="links">
        <a href="about">About</a>
        <a href="bugs">Known Bugs and Issues</a>
    </div>
    <form id="form" action="process" method="post">
        <textarea name="maintext" rows="30" cols="100" placeholder="Insert your text here. If this is your first time here it is highly recommended that you visit the about and bugs page." id="textspace" style="resize:none;"></textarea>
        <br />
        <br />
        <input type="submit" value="Search">
    </form>
</body>
</html>
'''#the home html page to be displayed upon running

@app.route('/')#links url to homepage
def run():
    return(indexpage)


@app.route('/about')#links url to about page
def about():
    return render_template("about.html")


@app.route('/bugs')#links url to bugs page
def bug():
    return render_template("bugs.html")


"""
keywordformat() is the function responsible for identifying keywords within the raw text.
The array keyword is created to facilitate storage of these keywords. 
After splitting the raw text into an array, we remove stopwords, disregard punctuations, and lowercase all the words for easy processing.
We also singularize all the words so plurals and singulars of the same word, which represent the same semantic meaning, can be sorted together.
After completion, we keep a full record of all the keywords so we can count their occurrences later in rank(). Due to the global nature of this, we assign a global variable.
In the keyword array, we make sure each keyword is only added once to save processing time.
"""

def keywordformat(text):

    textarray=text.split()#splits it into an array of separate words
    keywords=[]
    for x in textarray:
        x=x.lower()#sets every word to lowercase for easy processing
        translator = dict.fromkeys(map(ord, """.?!,:;"'()"""), None) #gets rid of punctuation as to not interfere with the search
        x = x.translate(translator)
        if x not in stop_words:#gets rid of stopwords
            keywords.append(inflection.singularize(x))#turns all words to their singular version same idea, can be processed alike


    global completekeywords
    completekeywords=keywords #this is a complete version of keywords. we need this later when we count the number of occurrences.
    holderkeywords=[]#makes sure keywords are only added once. this is to reduce redundant processing of the same word
    for x in keywords:
        if x not in holderkeywords:
            holderkeywords.append(x)
    keywords=holderkeywords
    return keywords


"""
synonymcreator() is to search for the synonyms of each keyword.
It does this by scouring the NLTK Wordnet Database
Each set of synonyms for each keyword is stored in an array.
These arrays are put into the array semanticgroup, hence making it a 2D array.
A common problem was NLTK containing the same synonym more than once. Hence, we loop through the each set of synonyms to make sure they only appear once for each keyword.
We also only want the synonyms which appear in the original text since the user is not interested in those so we have to loop through once more to get rid of any that don't.
"""

def synonymcreator(keywords):

    semanticgroup=[]#this is the vital variable which will store all the grouped keywords of similar ideas.
    for x in keywords: #literally all this does is get synonyms
        synonyms=[]

        for syn in wordnet.synsets(x):#searches NLTK wordnet
            for y in syn.lemmas():
                synonyms.append(y.name()) #creates list of synonyms
        if not synonyms:#in case the word does not appear in the dictionary we add a empty element. this is important for names etc... which have meaning but don't appear in the dictionary
            semanticgroup.append("");

        if synonyms: #makes sure that each synonym is only added once. a common problem was the same synonym being added multiple times
            holdersynonyms=[]#you will notice this function similar to the one on top where we got rid of redundant keywords
            for x in synonyms:
                if x not in holdersynonyms:
                    holdersynonyms.append(x)
            synonyms=holdersynonyms
            semanticgroup.append(synonyms);


    counter=0 #locator for which semantic idea we're iterating through
    for x in semanticgroup:#the main purpose of this loop is to remove any synonyms which don't appear in the original text

        condensedsynonyms=[] #similar to the synonyms[] array above. however this is a condensed version which contains only the ones which appear in the original text. reason for this usage is that set() objects don't support deletion
        for y in x:
            appears=False #assumes the synonym does not appear in the original text
            for z in keywords:
                if y==z:
                    appears=True
            if appears==True: #if it does appear, add it to the shortlist of useful synonyms
                condensedsynonyms.append(y)


        if condensedsynonyms:
            semanticgroup[counter]=condensedsynonyms #replace the old list with the shortlisted one
        else: #if no synonyms made it, only add the original keyword
            semanticgroup[counter]=[keywords[counter]]
        counter+=1

    return semanticgroup


"""
associate() is to associate the keywords of the text with each other so we can group ideas in the same place.
We accomplish this by having 2 loops go through the synonym set of each keyword. This way, the set of every keyword will be compared to each other.
If a match within any of the synonym sets is found, the two keywords are assumed to relate to each other and we merge the two together.

"""

def associate(semanticgroup):


    x=0#this is the function which associates ideas in the text with EACH OTHER. a while loop is needed because we are modifying the array AS WE loop through it. thus, we need counters
    while x < len(semanticgroup):#the tactic here is to iterate through the semantic ideas two times; one loop nested in the other loop. this way, each idea would be compared to each other
        for y in semanticgroup[x]:
            z=0
            while z < len(semanticgroup):#second loop
                for t in semanticgroup[z]:
                    if y==t and x!=z:#if the synonyms are the same, and the idea group is not matching with itself
                        semanticgroup[x].extend(semanticgroup[z])#extend the first idea group with the second
                        del semanticgroup[z]#delete the second

                z+=1
        x+=1


    counter=0 #gets rid of duplicate synonyms after we've combined words with similar meanings
    for x in semanticgroup:#this is similar to the other two duplication functions we had above
        holdergroup=[]
        for y in x:
            if y not in holdergroup:
                holdergroup.append(y)
        semanticgroup[counter]=holdergroup
        counter+=1

    return semanticgroup


"""
The purpose of rank() is to count the number of occurrences for each synonym and each semantic group as a whole, so we can rank them.
groupstotallist counts the number of occurences each set of synonyms gets from all its keywords. It is parallel to the first layer of semanticgroup
so you sort the sets of synonyms
listofscores is a 2D parallel to semanticgroup. It's structure is completely the same. If you go to the same [x][y] within it, you'll find
the number of occurences for which keyword is in [x][y] of semanticgroup
To count the number of occurences, we simply loop through each synonym and the complete list of keywords at the same time, incrementing the score
by 1 each time it appears.
Once we have the count for each synonym and set of synonyms, we need to sort the arrays in descending orders.
This means the ideas with the most occurrences appear first. In each idea, the keyword with the most occurrences appears first.
I simply zip the parallel arrays together and sort with the score keeping array as the target.
"""

def rank(semanticgroup):


    counter=0#a counter variable which keeps track of the loop we're on
    global groupstotallist
    global listofscores
    groupstotallist=[] #an array showing the total number of hits for each semantic group
    listofscores=[] #an array showing the total number of hits for each word WITHIN each semantic group. in other words, it is a 2d array similar in structure to semanticgroup
    for x in semanticgroup:
        groupscorelist=[] #basically the list of hits for each word in this particular semantic group
        for y in x:
            wordscore=0;
            for z in completekeywords:#this is where we need the unshortened list of keywords again. see line 100

                if y==z:
                    wordscore+=1#everytime the word occurs, add 1 to its score
            groupscorelist.append(wordscore)
        semanticgroup[counter]=[y[0] for y in sorted(zip(x,groupscorelist),key=itemgetter(1), reverse=True)]#sorts the keywords in each idea by their occurrence.
        groupscorelist=[y[1] for y in sorted(zip(x,groupscorelist),key=itemgetter(1), reverse=True)]#sorts the scores in the same way. this is important as we'll be passing it on.
        listofscores.append(groupscorelist)
        groupstotallist.append(sum(groupscorelist))
        counter+=1


    semanticgroup=[x[1] for x in sorted(zip(groupstotallist,semanticgroup), key=itemgetter(0), reverse= True)] #resort the ideas by the number of their occurrences

    listofscores=[x[1] for x in sorted(zip(groupstotallist,listofscores), key=itemgetter(0), reverse= True)]#resorts the scores of the ideas the same ways
    groupstotallist=[x[0] for x in sorted(zip(groupstotallist,semanticgroup), key=itemgetter(0), reverse= True)] #resort the array of total scores for each semantic group to positionly correspond with semanticgroup

    return semanticgroup

"""
The process() function below is the main one that runs upon activation. It calls upon all the other functions in the Python process.
It firstly handles the text variable which is just the original input text in raw form.
"""

@app.route('/process', methods=['POST'])#function to be executed upon the program is set to run. the results are displayed on the /process page
def process():

    text=request.form['maintext']#grabs the input text
    keywords=keywordformat(text)


    semanticgroup=synonymcreator(keywords)
    semanticgroup=associate(semanticgroup)
    semanticgroup=rank(semanticgroup)


    """
    In the user interface, we want to display what each set of synonyms semantically represent. The best way to do this is by displaying a group
    of synonyms from the set to give the user an idea of what's going on. For totally arbitrary reasons, this number has been set at 3.
    This means that at most, 3 synonyms from the set will be displayed as the header for the group whilst all the others will appear below.
    The code to facilitate that is below.
    """

    titledisplay=[]#this is to create the header for each semantic group you see on the results page. its point is to give an idea of what this idea is about
    for x in semanticgroup:
        holdergroup=[]
        limit=3#only except the first 3 most occurring keywords at most
        if len(x)<3:
            limit=len(x)
        for y in range(limit):
            holdergroup.append(x[y])
        titledisplay.append(holdergroup)

    return render_template("results.html", maintext=text,semanticgroup = semanticgroup, listofscores=listofscores,groupstotallist=groupstotallist, titledisplay=titledisplay) #sends all the important variables to the template







#the below is some output testing code i used in early development. for the sake of convenience in any future development, i'd like to retain them in comment mode for the time being.
""" output=''
    for x in keywords:
        output+=x
        output+=" "
        


    for x, b in zip(semanticgroup, keywords):

        output+=str(b)
        output+="(((("
        for y in x:
            output+=" "
            output+=str(y)
        output+="))))"

        output+="<br /> <br /> "


    return output
"""



if __name__== "__main__":
    app.run()
#runs the app.
