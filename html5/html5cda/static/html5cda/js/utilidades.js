$(function() {
    getCurrenDate = function(){
		var fullDate = new Date();
		var twoDigitMonth = fullDate.getMonth()+1;
		if(twoDigitMonth.length==1)	twoDigitMonth="0" +twoDigitMonth;
		var twoDigitDate = fullDate.getDate()+"";
		if(twoDigitDate.length==1)	twoDigitDate="0" +twoDigitDate;
		var currentDate = fullDate.getFullYear() + "-" + twoDigitMonth + "-" + twoDigitDate ;
		return currentDate;
	};
});