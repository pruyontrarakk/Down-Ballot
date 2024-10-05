$(document).ready(function () {
    // Your code here
    console.log("DOM is fully loaded and ready.");
   resetAllInputs();

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

        let policy_choices = [];
        $('#policy-interests input[name="choice"]:checked').each(function () {
            console.log($(this).val())
            policy_choices.push($(this).val());
        });
        formData.append("policy_choices", policy_choices);

        let levels=[]
        $('#levels input[name="choice"]:checked').each(function () {
            policy_choices.push($(this).val());
        });
        formData.append("level_choices", levels);

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
                    console.log(`Got from server:`, response);
                },
                error: function (error) {
                    console.error('Error sending data:', error);
                }
            });
        }
    })
});

function resetAllInputs() {
    $("#street-address").val('');
    $('#policy-interests input[name="choice"]').prop('checked', false);
    $('#levels input[name="choice"]').prop('checked', false);
}