// Background color
image_1 = 'https://static1.squarespace.com/static/555008b3e4b0c62a575b8762/t/556c9751e4b072fc1ba8103d/1433179986764/CPE-Calculator-and-Pen-2.jpg?format=2500w';
image_2 = 'https://www.strath.ac.uk/media/1newwebsite/departmentsubject/mathematicsandstatistics/1600x600/xstochastic-analysis-1600x600.jpg.pagespeed.ic.7FI6Nh473a.jpg';
image_3 = 'http://www.acbnews.com.au/uploadfile/2018/0706/20180706083940134.jpg';

var images = new Array(image_1,image_2,image_3);
var nextimage=0;

var slideIndex = 1;
showDivs(slideIndex);

function plusDivs(n) {
  showDivs(slideIndex += n);
}

function showDivs(n) {
  var i;

  if (n > images.length) {slideIndex = 1} 
  if (n < 1) {slideIndex = images.length} ;

  $("#background")
    .attr("style", "background-image: url("+images[slideIndex-1]+");background-size: 100%; height: 100%;");
}
