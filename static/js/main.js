$(document).ready(function () {
    // Your code here
    console.log("DOM is fully loaded and ready.");

    let addr_input = document.getElementById('street-address');
    let addr_autocomplete = new google.maps.places.Autocomplete(addr_input);
    addr_autocomplete.setComponentRestrictions({'country': ['us']});
    $("user-info").on("submit", function (event) {
        let address = addr_autocomplete.getPlace();
        let formData = {
            addr: address,
            choices: []
        };
        $('input[name="choice"]:checked').each(function () {
            formData.choices.push($(this).val());
        });


    })
});