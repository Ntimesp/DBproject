
$(".btn.btn-sm").click(function(){
    $.get("kitchen",
    {
        workid:$(this).attr("id"),
    },function(data,status){
        alert(data);
    })
});