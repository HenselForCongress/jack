// so_well/static/js/entry.js

$(document).ready(function() {
    console.log("Document ready - initializing");

    fetchStateOptions();
    fetchDirectionOptions();
    fetchStreetTypeOptions();

    // Handle form submission and search
    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        console.log("Search form submitted");
        searchVoters(); // Trigger search
    });

    $('#not-found').on('click', function() {
        console.log("Not Found clicked");
        $('#not-found-modal').modal('show');
    });

    $('#results-table').on('click', '.btn-match', function() {
        let voterData = $(this).data('voter');
        console.log("Match button clicked", voterData);
        $('#match-modal').data('voter', voterData).modal('show');
    });

    $('#match-form').on('submit', function(e) {
        e.preventDefault();
        let voterData = $('#match-modal').data('voter');
        let formData = {
            sheet_number: $('#sheet-number').val(),
            row_number: $('#row-number').val(),
            date_collected: $('#date-collected').val(),
            last_four_ssn: $('#last-4').val(),
            voter_id: voterData.voter_id
        };
        console.log("Match form submitted", formData);
        $.ajax({
            type: 'POST',
            url: '/signatures/verify',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(data) {
                console.log("Match recorded successfully");
                $('#match-modal').modal('hide');
                alert('Successfully recorded!');
                resetFormFields(); // Clear the form fields after successful submission
            },
            error: function(xhr, status, error) {
                console.error('Error recording match:', error);
            }
        });
    });

    $('#not-found-form').on('submit', function(e) {
        e.preventDefault();
        let formData = {
            sheet_number: $('#nf-sheet-number').val(),
            row_number: $('#nf-row-number').val(),
            date_signed: $('#nf-date-signed').val(),
            first_name: $('#nf-first-name').val(),
            middle_name: $('#nf-middle-name').val(),
            last_name: $('#nf-last-name').val(),
            address: $('#nf-address').val(),
            apartment_number: $('#nf-apartment-number').val(),
            city: $('#nf-city').val(),
            state: $('#nf-state').val(),
            zip_code: $('#nf-zip-code').val(),
            last_four_ssn: $('#nf-last-4').val()
        };
        console.log("Not Found form submitted", formData);
        $.ajax({
            type: 'POST',
            url: '/signatures/verify',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(data) {
                console.log("Not Found recorded successfully");
                $('#not-found-modal').modal('hide');
                alert('Successfully recorded!');
            },
            error: function(xhr, status, error) {
                console.error('Error recording Not Found:', error);
            }
        });
    });

    function fetchStateOptions() {
        console.log("Fetching state options");
        $.ajax({
            url: '/advanced_search/states',
            method: 'GET',
            success: function(data) {
                console.log('States data:', data);
                data.forEach(function(state) {
                    $('#state').append(`<option value="${state}">${state}</option>`);
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching state options:', error);
            }
        });
    }

    function fetchDirectionOptions() {
        console.log("Fetching direction options");
        $.ajax({
            url: '/advanced_search/directions',
            method: 'GET',
            success: function(data) {
                console.log('Directions data:', data);
                data.directions.forEach(function(direction) {
                    $('#direction-options').append(`<div><input type="checkbox" class="direction-option" value="${direction.value}"> ${direction.value}</div>`);
                });
                data.post_directions.forEach(function(postDirection) {
                    $('#post-direction-options').append(`<div><input type="checkbox" class="post-direction-option" value="${postDirection.value}"> ${postDirection.value}</div>`);
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching direction options:', error);
            }
        });
    }

    function fetchStreetTypeOptions() {
        console.log("Fetching street type options");
        $.ajax({
            url: '/advanced_search/street_types',
            method: 'GET',
            success: function(data) {
                console.log('Street Types data:', data);
                data.street_types.forEach(function(streetType) {
                    $('#street-type-options').append(`<div><input type="checkbox" class="street-type-option" value="${streetType.value}"> ${streetType.value}</div>`);
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching street type options:', error);
            }
        });
    }

    function searchVoters() {
        let formData = {
            'first_name': $('#first-name').val(),
            'middle_name': $('#middle-name').val(),
            'last_name': $('#last-name').val(),
            'house_number': $('#house-number').val(),
            'house_number_suffix': $('#house-number-suffix').val(),
            'street_name': $('#street-name').val(),
            'apartment_number': $('#apartment-number').val(),
            'city': $('#city').val(),
            'state': $('#state').val(),
            'zip_code': $('#zip-code').val().substring(0, 5)  // Only take the first 5 characters for ZIP Code
        };

        console.log("Submitting search with formData:", formData);

        $.ajax({
            type: 'POST',
            url: '/advanced_search/',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(data) {
                console.log("Search results received:", data);
                updateResultsTable(data.results);
            },
            error: function(xhr, status, error) {
                console.error('Error performing search:', error);
            }
        });
    }

    function updateResultsTable(results) {
        console.log("Updating results table with data:", results);

        let tbody = $('#results-table tbody');
        tbody.empty();

        if (results.length === 0) {
            tbody.append('<tr><td colspan="10" class="text-center">No results found</td></tr>');
        } else {
            results.forEach(function(voter) {
                let row = `<tr>
                    <td>${voter.first_name}</td>
                    <td>${voter.middle_name || ''}</td>
                    <td>${voter.last_name}</td>
                    <td>${voter.full_address}</td>
                    <td>${voter.apartment_number || ''}</td>
                    <td>${voter.city}</td>
                    <td>${voter.state}</td>
                    <td>${voter.zip_code}</td>
                    <td>${voter.status}</td>
                    <td><button class="btn btn-primary btn-match" data-voter='${JSON.stringify(voter)}'>Match</button></td>
                </tr>`;
                tbody.append(row);
            });
        }
    }

    function resetFormFields() {
        console.log("Resetting form fields");
        $('#search-form').trigger("reset");
    }
});
