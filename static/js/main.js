$(document).ready(function () {
    console.log("DOM is fully loaded and ready.");
    resetAllInputs();

    let addr_input = document.getElementById('street-address');
    let addr_autocomplete;
    let address;


    if (addr_input) {
        addr_autocomplete = new google.maps.places.Autocomplete(addr_input);
        addr_autocomplete.setComponentRestrictions({'country': ['us']});
    }

    $("#user-info").on("submit", function (event) {
        event.preventDefault();  // Prevent normal form submission

        $("#spinner-container").removeClass("d-none").addClass("d-flex justify-content-center");
        $("#main-content").hide();

        address = addr_autocomplete.getPlace();
        let formData = new FormData();

        if (address) {
            formData.set('address', address.formatted_address);  // Set address in form data
        }

        let policy_choices = [];
        $('#policy-interests input[name="choice"]:checked').each(function () {
            policy_choices.push($(this).val());
        });
        formData.append("policy_choices", JSON.stringify(policy_choices));

        // Get the selected levels
        let levels = [];
        $('#levels input[name="choice"]:checked').each(function () {
            levels.push($(this).val());
        });
        formData.append("level_choices", JSON.stringify(levels));

        // If the form is valid, make the AJAX call
        if (formData.has('policy_choices') && formData.has('level_choices') && formData.has('address')) {
            $.ajax({
                type: "POST",
                url: "/results",
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    console.log('Data sent successfully');
                    resetAllInputs();
                    window.location.href = "/results";

                    $("#spinner-container").addClass("d-none");
                    $("#main-content").show();
                },
                error: function (error) {
                    console.error('Error sending data:', error);

                    $("#spinner-container").addClass("d-none");
                    $("#main-content").show();
                }
            });
        } else {
            console.log("form doesn't work")

            $("#spinner-container").addClass("d-none");
            $("#main-content").show();
        }

    });

});

function resetAllInputs() {
    $("#street-address").val('');
    $('#policy-interests input[name="choice"]').prop('checked', false);
    $('#levels input[name="choice"]').prop('checked', false);
}


