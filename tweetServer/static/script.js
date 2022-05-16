$(function(){
    window.setInterval(function(){
      load_update1();
      load_update2()
     },5000)

   function load_update1(){
    $.ajax({
      url: "/updatetweetscount",
      type: "POST",
      dataType: "json",
      success: function(data){
       $("#tweet_counts").replaceWith(data)
      }
    })
   }

   function load_update2(){
    $.ajax({
      url: "/updatetweetspercent",
      type: "POST",
      dataType: "json",
      success: function(data){
       $("#tweet_percentage").replaceWith(data)
      }
    })
   }
});

// A $( document ).ready() block.
$( document ).ready(function() {
  const monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];
  const d = new Date();
  //document.write("The current month is " + monthNames[d.getMonth()]);
  // set inner text if id to current date.
  document.getElementById("currentDate").innerText = monthNames[d.getMonth()] + ", " + d.getDate();
});


// requesting negative tweet every second.
setInterval(function(){ 
  //code goes here that will be run every 1 seconds.
 // console.log("inside requesting negative tweets");
  $.ajax({
    url: "/get_negative_tweet",
    type: "POST",
    dataType: "json",
    success: function(data){
    console.log("inside requesting negative tweets");
    $("#mean_tweets").append(data)
    }
  })
}, 2000);