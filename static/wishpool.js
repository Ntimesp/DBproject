$(".btn.btn-sm").click(function(){
    $.get("wishpool",
    {
        email:$(this).attr("id"),
    },function(data,status){
        alert(data);
    })
});