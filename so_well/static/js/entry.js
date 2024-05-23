$(document).ready(function() {
    // Submit search form
    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        let formData = {
            'first_name': $('#first-name').val(),
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
            'zip_code': $('#zip-code').val()
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

    // Click handler for Not Found button
    $('#not-found').on('click', function() {
        $('#not-found-modal').modal('show');
    });

    // Click handler for Match button in results
    $('#results-table').on('click', '.btn-match', function() {
        let voterData = $(this).data('voter');
        $('#match-modal').data('voter', voterData).modal('show');
    });

    // Submit match form
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

    // Submit not found form
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
