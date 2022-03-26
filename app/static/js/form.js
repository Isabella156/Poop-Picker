$(document).ready(function() {
    $('form').on('submit', function(event) {
        var activeClass = document.getElementsByClassName('peta tab active');
        var petId = activeClass[0].value;
        var route = '/addFamily/' + petId;
        var usernameid = '#username' + petId;
        var codeid = '#code' + petId;
        var formid = '#' + petId;
        var value1 = $(usernameid).val();
        var value2 = $(codeid).val();


        $.ajax({
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify({ "username": value1, "code": value2 }),
                type: 'POST',
                url: route,
                success: function(data) {

                }
            })

            .done(function(data) {

                if (data.error) {
                    $('#errorAlert').text(data.error).show();
                    $('#successAlert').hide();
                } else {
                    $('#successAlert').text(data.success).show();
                    $('#errorAlert').hide();
                    $(formid).hide();
                }
                $('.alert').fadeOut(3000);
            });

        event.preventDefault();

    });

    $('.alert').fadeOut(3000);

});