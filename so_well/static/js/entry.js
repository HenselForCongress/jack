$(document).ready(function() {
    fetchStateOptions();
    fetchDirectionOptions();
    fetchStreetTypeOptions();

    // Toggle direction options
    $('#direction-options-toggle').click(function() {
        $('#direction-options').toggleClass('d-none');
    });

    // Toggle post direction options
    $('#post-direction-options-toggle').click(function() {
        $('#post-direction-options').toggleClass('d-none');
    });

    // Toggle street type options
    $('#street-type-options-toggle').click(function() {
        $('#street-type-options').toggleClass('d-none');
    });

    // Fetch states options -> replace state options
    function fetchStateOptions() {
        $.ajax({
            url: '/advanced_search/states', // Assuming this endpoint returns available states
            method: 'GET',
            success: function(data) {
                data.forEach(function(state) {
                    $('#state').append(`<option value="${state}">${state}</option>`);
                });
            }
        });
    }

    // Fetch unique direction options
    function fetchDirectionOptions() {
        $.ajax({
            url: '/advanced_search/directions', // Assuming this endpoint returns available directions and their counts
            method: 'GET',
            success: function(data) {
                data.directions.forEach(function(direction) {
                    $('#direction-options').append(`<div><input type="checkbox" class="direction-option" value="${direction.value}"> ${direction.value} (${direction.count})</div>`);
                    $('#direction').append(`<option value="${direction.value}">${direction.value}</option>`);
                });

                data.post_directions.forEach(function(postDirection) {
                    $('#post-direction-options').append(`<div><input type="checkbox" class="post-direction-option" value="${postDirection.value}"> ${postDirection.value} (${postDirection.count})</div>`);
                    $('#post-direction').append(`<option value="${postDirection.value}">${postDirection.value}</option>`);
                });
            }
        });
    }

    // Fetch unique street type options
    function fetchStreetTypeOptions() {
        $.ajax({
            url: '/advanced_search/street_types', // Assuming this endpoint returns available street types and their counts
            method: 'GET',
            success: function(data) {
                data.street_types.forEach(function(streetType) {
                    $('#street-type-options').append(`<div><input type="checkbox" class="street-type-option" value="${streetType.value}"> ${streetType.value} (${streetType.count})</div>`);
                    $('#street-type').append(`<option value="${streetType.value}">${streetType.value}</option>`);
                });
            }
        });
    }

    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        let formData = {
            'first_name': $('#first-name').val(),
            'middle_name': $('#middle-name').val(),
            'last_name': $('#last-name').val(),
            'house_number': $('#house-number').val(),
            'house_number_suffix': $('#house-number-suffix').val(),
            'street_name': $('#street-name').val(),
            'street_type': $('#street-type').val(),
            'direction': $('#direction').val(),
            'post_direction': $('#post-direction').val(),
            'apartment_number': $('#apartment-number').val(),
            'city': $('#city').val(),
            'state': $('#state').val(),
            'zip_code': $('#zip-code').val().substring(0, 5) // Only take the first 5 characters for ZIP Code
        };
        $.ajax({
            type: 'POST',
            url: '/advanced_search/',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(data) {
                updateResultsTable(data);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    });

    $('#not-found').on('click', function() {
        $('#not-found-modal').modal('show');
    });

    $('#results-table').on('click', '.btn-match', function() {
        let voterData = $(this).data('voter');
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
        $.ajax({
            type: 'POST',
            url: '/signatures/verify',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(data) {
                $('#match-modal').modal('hide');
                alert('Successfully recorded!');
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
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
        $.ajax({
            type: 'POST',
            url: '/signatures/verify',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(data) {
                $('#not-found-modal').modal('hide');
                alert('Successfully recorded!');
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    });
});

function updateResultsTable(data) {
    let tbody = $('#results-table tbody');
    tbody.empty();
    data.forEach(function(voter) {
        let row = `<tr>
            <td>${voter.first_name}</td>
            <td>${voter.middle_name}</td>
            <td>${voter.last_name}</td>
            <td>${voter.address}</td>
            <td>${voter.city}</td>
            <td>${voter.state}</td>
            <td>${voter.zip_code}</td>
            <td>${voter.status}</td>
            <td><button class="btn btn-primary btn-match" data-voter='${JSON.stringify(voter)}'>Match</button></td>
           </tr>`;
        tbody.append(row);
    });
}
