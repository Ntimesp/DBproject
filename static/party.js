
$(".btn.btn-sm").click(function(){
    $.get("party",
    {
        workid:$(this).attr("id"),
    },function(data,status){
        alert(data);
    })
});