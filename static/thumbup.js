<script type=text/javascript>
        $(function() {
          $('a#test').bind('click', function() {
            $.getJSON('/thumbup',
                function(data) {
              //do nothing
            });
            return false;
          });
        });
</script>

<script>
        window.οnlοad=function(){
            var img1 = document.getElementById('img1'); 
            var b=1;
            img1.οnclick=function(){
                if(b==1){
                    img1.src="{{ url_for('static', filename='img/after.png') }}";
                    b=0;
                }else{
                    img1.src="{{ url_for('static', filename='img/before.png') }}";
                    b=1;
                }               
            }
        };

</script>
