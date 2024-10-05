$(document).ready(function () {
    // Your code here
    console.log("DOM is fully loaded and ready.");
    $("#street-address").empty()

    let addr_input = document.getElementById('street-address');
    let addr_autocomplete = new google.maps.places.Autocomplete(addr_input);
    let address;
    addr_autocomplete.setComponentRestrictions({'country': ['us']});

    $("#user-info").on("submit", function (event) {
        event.preventDefault()
        address = addr_autocomplete.getPlace();
        let formData = new FormData();

        if (address) {
            formData.set('address', address.formatted_address);
        }

        $('#policy-interests input[name="choice"]:checked').each(function () {
            formData.append('policy_choices', $(this).val());
        });

        $('#levels input[name="choice"]:checked').each(function () {
            formData.append('level_choices', $(this).val());
        });

        if (formData.has('policy_choices') && formData.has('level_choices') &&
        formData.has('address'))
        {
            $.ajax({
                type: "POST",
                url: "/user",
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    console.log(`Stored on server: `, response);
                },
                error: function (error) {
                    console.error('Error sending data:', error);
                }
            });
        }
    })
});