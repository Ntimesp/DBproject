
$(".btn.btn-sm").click(function(){
    $.get("wonderland",
    {
        workid:$(this).attr("id"),
    },function(data,status){
        alert(data);
    })
});