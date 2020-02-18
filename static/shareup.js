
$(".btn.btn-sm").click(function(){
    $.get("shareUp",
    {
        workid:$(this).attr("id"),
    },function(data,status){
        alert(data);
    })
});