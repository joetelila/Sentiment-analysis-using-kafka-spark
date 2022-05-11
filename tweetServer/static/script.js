$(function(){
    window.setInterval(function(){
      load_update()
     },5000)

   function load_update(){
    $.ajax({
      url: "/updatetweetscount",
      type: "POST",
      dataType: "json",
      success: function(data){
       $(tweet_counts).replaceWith(data)
      }
    })
   }
});