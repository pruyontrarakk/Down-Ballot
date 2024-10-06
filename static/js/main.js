$(document).ready(function () {
    const OPENAI_API_KEY = $('#openai_api_key').text();
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
                    let info = [
                        {
                            'name': 'ava',
                            'c_platform': [{'issue': 'Climate Change', 'policy': ''}, {'issue': '', 'policy': ''}]
                        },
                        {'name': 'pru', 'c_platform': [{'issue': 'Healthcare', 'policy': ''}]}
                    ]

                    getPolicyFromGPT(info).then((value) => {
                        const data = JSON.parse(value);
                        console.log(data)

                        $.ajax({
                            type: "POST",
                            url: "/post_results",
                            data: JSON.stringify(data),
                            contentType: 'application/json',
                            success: function (response) {
                                console.log('Sent to server:', response )
                            },
                            error: function (error) {
                                console.error('Error sending data:', error);
                            }
                        });

                    });
                    // Assuming the server responds with JSON containing elections and representatives
                },
                error: function (error) {
                    console.error('Error sending data:', error);
                }
            });
        } else {
            console.log("form doesn't work")
        }

    });

    async function getPolicyFromGPT(candidate_array) {
        try {
            const response = await axios.post(
                'https://api.openai.com/v1/chat/completions',
                {
                    model: "gpt-4o-mini",  // Replace with the model you want to use
                    messages: [
                        {
                            role: 'user',
                            content: `Here's an array of candidates for the 2024 election. For each issue, fill in the
                            policy field with 1-2 sentence summary of the candidate's position. The array is:
                            ${JSON.stringify(candidate_array, null, 2)}.
                            The output needs to match the input (raw, stringified JSON) except with the policy field filled in for each issue.
                            No need to mark the response as json via backticks! just return the stringified JSON.`
                        },
                        {
                            role: 'system',
                            content: "You are trying to help someone understand the policy positions of the candidates in their local elections. Keep answers minimal and informative."
                        }
                    ],
                    temperature: 0.3,
                },
                {
                    headers: {
                        'Authorization': `Bearer ${OPENAI_API_KEY}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            console.log(response.data);
            return response.data.choices[0].message.content;
        } catch (error) {
            console.error('Error with OpenAI request:', error);
        }
    }

});

function resetAllInputs() {
    $("#street-address").val('');
    $('#policy-interests input[name="choice"]').prop('checked', false);
    $('#levels input[name="choice"]').prop('checked', false);
}


// Function to dynamically display the results on the page
function displayResults(elections, representatives) {
    let resultsContainer = $("<div></div>");

    // Add elections
    if (elections.length > 0) {
        resultsContainer.append("<h3>Upcoming Elections:</h3>");
        let electionsList = $("<ul></ul>");
        elections.forEach(function (election) {
            electionsList.append(`<li>${election.name} on ${election.electionDay}</li>`);
        });
        resultsContainer.append(electionsList);
    }

    // Add representatives
    if (representatives && representatives.officials.length > 0) {
        resultsContainer.append("<h3>Your Representatives:</h3>");
        let repsList = $("<ul></ul>");
        representatives.officials.forEach(function (rep) {
            repsList.append(`<li>${rep.name} (${rep.party})</li>`);
        });
        resultsContainer.append(repsList);
    }


    // Clear previous results and add the new results to the page
    $("#results-section").empty().append(resultsContainer);
}

