$(document).ready(function () {
    // Your code here
    console.log("DOM is fully loaded and ready.");



    $("user-info").on("submit", function (event) {
        let formData = {
            zipcode: $('#zipcode').val(),
            state: $('#state').val(),
            choices: []
        };
        $('input[name="choice"]:checked').each(function () {
            formData.choices.push($(this).val());
        });


    })
});