$(document).ready(function () {
    console.log("Document ready - initializing");

    fetchStateOptions();
    fetchDirectionOptions();
    fetchStreetTypeOptions();

    // Prepopulate the date fields with the current date, but do not set the Day value
    prepopulateDateFields();

    // Handle form submission and search
    $('#search-form').on('submit', function (e) {
        e.preventDefault();
        console.log("Search form submitted");
        searchVoters(); // Trigger search
    });

    $('#not-found').on('click', function () {
        console.log("Not Found clicked");
        $('#not-found-modal').modal('show');
    });

    $('#results-table').on('click', '.btn-match', function () {
        let voterData = $(this).data('voter');
        console.log("Match button clicked", voterData);
        $('#match-modal').data('voter', voterData).modal('show');

        // Auto-fill modal sheet number
        $('#sheet-number').val($('#header-sheet-number').val());

        // Pre-populate the date-collected field
        let month = $('#header-month').val();
        let day = $('#header-day').val() || '01'; // Use '01' if day is empty
        let year = $('#header-year').val();
        let collectedDate = null;

        if (month && day && year) {
            collectedDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        } else if (month && year) {
            collectedDate = `${year}-${month.padStart(2, '0')}-01`;
        } else if (year) {
            collectedDate = `${year}-01-01`;
        }

        $('#date-collected').val(collectedDate);
    });

    $('#match-modal').on('show.bs.modal', function () {
        const sheetNumber = $('#header-sheet-number').val();
        if (sheetNumber) {
            $.ajax({
                type: 'GET',
                url: '/sheets/get_max_row_number',
                data: { sheet_id: sheetNumber },
                success: function (response) {
                    const maxRowNumber = response.max_row_number || 0;
                    $('#row-number').val(maxRowNumber + 1);
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching max row number:', error);
                }
            });
        } else {
            $('#row-number').val(1); // Default to 1 if no sheet number is set.
        }
    });

    $('#match-form').on('submit', function (e) {
        e.preventDefault();
        if (validateMatchForm()) {
            submitMatchForm();
        }
    });

    // Listen for the Enter key on the match modal and trigger submit
    $('#match-modal').keypress(function(e) {
        if (e.which === 13) { // Enter key
            if (validateMatchForm()) {
                submitMatchForm();
            }
        }
    });

    function validateMatchForm() {
        let isValid = true;
        $('#match-form').find('input[required]').each(function() {
            if ($(this).val() === '') {
                isValid = false;
                return false; // Exit each loop
            }
        });
        return isValid;
    }

    function submitMatchForm() {
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
                showNotification('Successfully recorded!', 'success');
                resetFormFields(); // Clear the form fields after successful submission

                // Automatically focus on "First Name" field
                $('#first-name').focus();
            },
            error: function(xhr, status, error) {
                console.error('Error recording match:', error);
            }
        });
    }

    $('#not-found-form').on('submit', function (e) {
        e.preventDefault();
        let formData = {
            sheet_number: $('#nf-sheet-number').val(),
            row_number: $('#nf-row-number').val(),
            date_collected: $('#nf-date-signed').val(),
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

        console.log("Submitting Not Found form with formData:", formData);

        $.ajax({
            type: 'POST',
            url: '/signatures/verify',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (data) {
                console.log("Not Found recorded successfully");
                $('#not-found-modal').modal('hide');
                showNotification('Successfully recorded!', 'success');
            },
            error: function (xhr, status, error) {
                console.error('Error recording Not Found:', error);
                showNotification(`Error: ${xhr.responseJSON.error}`, 'danger');
            }
        });
    });

    function fetchStateOptions() {
        console.log("Fetching state options");
        $.ajax({
            url: '/advanced_search/states',
            method: 'GET',
            success: function (data) {
                console.log('States data:', data);
                data.forEach(function (state) {
                    $('#state').append(`<option value="${state}">${state}</option>`);
                });
            },
            error: function (xhr, status, error) {
                console.error('Error fetching state options:', error);
            }
        });
    }

    function fetchDirectionOptions() {
        console.log("Fetching direction options");
        $.ajax({
            url: '/advanced_search/directions',
            method: 'GET',
            success: function (data) {
                console.log('Directions data:', data);
                data.directions.forEach(function (direction) {
                    $('#direction-options').append(`<div><input type="checkbox" class="direction-option" value="${direction.value}"> ${direction.value}</div>`);
                });
                data.post_directions.forEach(function (postDirection) {
                    $('#post-direction-options').append(`<div><input type="checkbox" class="post-direction-option" value="${postDirection.value}"> ${postDirection.value}</div>`);
                });
            },
            error: function (xhr, status, error) {
                console.error('Error fetching direction options:', error);
            }
        });
    }

    function fetchStreetTypeOptions() {
        console.log("Fetching street type options");
        $.ajax({
            url: '/advanced_search/street_types',
            method: 'GET',
            success: function (data) {
                console.log('Street Types data:', data);
                data.street_types.forEach(function (streetType) {
                    $('#street-type-options').append(`<div><input type="checkbox" class="street-type-option" value="${streetType.value}"> ${streetType.value}</div>`);
                });
            },
            error: function (xhr, status, error) {
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
                    <td class="last-row-number" style="display: none;">${voter.identification_number}</td>
                    <td><button class="btn btn-primary btn-match" data-voter='${JSON.stringify(voter)}'>Match</button></td>
                </tr>`;
                tbody.append(row);
            });
        }
    }

    function resetFormFields() {
        console.log("Resetting form fields");
        $('#search-form').trigger("reset");

        // Automatically focus on "First Name" field
        $('#first-name').focus();
    }

    function prepopulateDateFields() {
        let current_date = new Date();
        $('#header-month').val(('0' + (current_date.getMonth() + 1)).slice(-2));
        $('#header-day').val(''); // Leave Day empty
        $('#header-year').val(current_date.getFullYear());
    }

    function showNotification(message, type) {
        $('#notification').removeClass().addClass(`alert alert-${type}`).text(message).fadeIn();

        // Auto-hide notification after 3 seconds
        setTimeout(function() {
            $('#notification').fadeOut();
        }, 3000);
    }

    // Automatically focus on "First Name" field when document is ready
    $('#first-name').focus();

    // Prepopulate with default values on page load
    prepopulateDateFields();
});
