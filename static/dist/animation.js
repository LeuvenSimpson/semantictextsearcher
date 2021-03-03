// JavaScript Document



$(document).ready(function(e) {
	
	//the main use of this block of code is to singularize all the plurals in the text since we have singularized all the plurals in the python output. only by doing this, can we match the search results together. the goal here is to get singularized versions of the word, place them in the class value of each element, so when the user hovers over the keyword in the results tab, they light up in the original text tab.
	var maintext=$("#maintext").text()//selecting the entirety of the text
	originalword=maintext.split(" ")//splitting text into an array of words
	maintext = maintext.toLowerCase().split(" ")
	
	for (i=0; i < maintext.length; i++){
		maintext[i]=maintext[i].replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").replace(/\s{2,}/g," ");
		//maintext[i]=maintext[i].replace(/\s{2,}/g," ");//removing punctuation
		}
	
		
	for (i=0; i < maintext.length; i++){
		
		
		maintext[i]=inflection.singularize(maintext[i])//singularizes all the words using the inflection module
		starttag="<a class='" + maintext[i]+ "'>"//builds an opening html tag with the singularized word as the class
		maintext[i]=starttag+originalword[i]+"</a> "//constracts the original word but with the new class tag wrapped around it
		
		
		}
	$("#maintext").html(maintext)//replaces the old text with the new one modified with individual tags around words
		











//this block of code is to highlight the word being clicked and to keep it highlighted
	var selection//this variable will be the id of the keyword which has been clicked
	var selected = false//this binary variable declares whether a word has been selected or not. it is useful when we add the hover function next

	$("body").click(function(event){

		$("." + selection).css("background-color","#FFF")//unhighlights the last selection. this code also proves useful so if the user clicks anywhere else, the previous selection will also be unselected
		selected=false
		
		if(event.target.className=="word"){//if they have clicked on a keyword
			
			$("." + event.target.id).css("background-color","#09F")//highlight the chosen keyword
			selection=event.target.id//declare this variable for the next iteration
			selected=true
			}


		})
	
	











	
	
	$(".word").hover(
		function(e) {// highlight all instances of the selected keyword upon hovering over them in the results tab
			
		
		
			$("." + this.id).css("background-color","#09F")
	
			
		},
		
		function(e) {
			 
			if(selected=true){//if a word has been clicked on, we don't want it to stop highlighting once we stop hovering on it.
				if(selection!=this.id){//this line prevents that from happening by checking if the element we are hovering over is the same as the one we clicked. if not, then we can unhighlight it upon leaving
					$("." + this.id).css("background-color","#fff")
				}
			}else{
				
				$("." + this.id).css("background-color","#fff")
				}
		
		}
	);
	
	
	








	

})