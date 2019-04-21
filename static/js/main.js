let heightFullWindow = (elm) => {
	if (elm){
		elm.style.height = window.innerHeight + 'px';
	}
}

let container404 = document.getElementById('error-404');
heightFullWindow(container404);

let header = $('header');
let footer = $('footer');
let content = document.querySelector('.content');

if(content && header && footer){
    content.style.minHeight = window.innerHeight - header.outerHeight(true) - footer.outerHeight(true) + 'px';
}

//# sourceMappingURL=main.js.map
function secondsToHours(seconds){
	let hours, minutes;

	hours = parseInt(seconds/3600);
	seconds %= 3600;
	minutes = parseInt( seconds/60 );
	seconds %= 60;
	
	return `${hours}:${minutes}:${seconds}`

}


let gamesTimesHidden = $('.game-remaining-time > div');
let gamesTimer = setInterval(()=>{
	for(let elm of gamesTimesHidden){
		elm = $(elm);
		gameTime = parseInt( elm.text() );

		if(gameTime > 0){
			elm.text(--gameTime);
			console.log(elm.next('a').text(secondsToHours(gameTime)))
		}
	}
},1000);

