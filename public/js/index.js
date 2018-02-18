$(document).ready(function(){
	$("input").keypress(function(e){
    	if(e.keyCode == 13) {
    		$(".searchbtn").click();
    	}
	});


	$(".searchbtn").click(function(e) {
      $.get("/search", {"name": $("input[name='search_box']").val()})
       .done(function(string) {
       	if( string.length == 0) {
       		$(".tbl-header").hide();
       		$(".tbl-content").hide();
        	$("#no_search_results").html('<h3>No stock found by that name Enter a valid name</h3>');
       	} else {
       		$(".tbl-header").show();
        	$(".tbl-content").show().html(string);
       		if(string.length > 1500)
       			$(".tbl-content").addClass('custom-table-overflow');
       		else if((string.length < 1500) && $(".tbl-content").hasClass('custom-table-overflow'))
       			$(".tbl-content").removeClass('custom-table-overflow');
        	$("#no_search_results").html("");
        }
      });
      e.preventDefault();
   	});
   	$(window).on("load resize ", function() {
  		var scrollWidth = $('.tbl-content').width() - $('.tbl-content table').width();
  		$('.tbl-header').css({'padding-right':scrollWidth});
	}).resize();
});