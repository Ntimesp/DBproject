
$(".btn.btn-sm").click(function(){
    $.get("shareup",
    {
        workid:$(this).attr("id"),
    },function(data,status){
        alert(data);
    })
});