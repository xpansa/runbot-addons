(function deletePoll(postId){
    $.ajax({
        type: "POST",
        url: "/logs/1",
        data: {
        },
        success: function(result) {
            console.log(result);
        },
        error: function(){

        }
    });

})();
