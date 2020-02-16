$(".btn.btn-sm").click(function(){
    $.get("shareUp",
    {
        thu:$(this).attr("id"),
    },function(data,status){
        alert(data);
    })
});