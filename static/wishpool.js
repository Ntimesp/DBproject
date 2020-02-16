$(".btn.btn-sm").click(function(){
    $.get("wishpool",
    {
        thu:$(this).attr("id"),
    },function(data,status){
        alert(data+"hhh");
    })
});