
$(document).ready(function() {
    // 1. Ensure arrows are visible and properly sized
    $('.stepper-arrow').css({'display': 'block', 'min-width': '20px', 'min-height': '20px'});

    // 2. Combined Logic for Plus and Minus with AJAX Update
    $(document).on('click', '.stepper-arrow', function(e) {
        console.log("Stepper arrow clicked!");
        e.preventDefault();
        
        // Find the input field and the Product ID
        var parent = $(this).closest('.stepper');
        var input = parent.find('input.stepper-input');
        
        // This strips 'qty-' from the ID to get just the number for Django
       
        
        // Get current value
        var currentVal = parseInt(input.val()) || 1;

        // Calculate the new quantity based on which class was clicked
        var newVal = $(this).hasClass('up') ? currentVal + 1 : (currentVal > 1 ? currentVal - 1 : 1);




        var productId = input.attr('id').replace('qty-', '');
        var productColor = input.data('color');
        var productSize = input.data('size');

        $.ajax({
            type: 'POST',
            url: '{% url "update-cart-item" %}',
            data: {
                product_id: productId,
                product_qty: newVal,
                product_color: productColor,
                product_size: productSize,
                csrfmiddlewaretoken: '{{ csrf_token }}',
                action: 'post'
            },
            success: function(json) {
                input.val(newVal);
        
    
    try {
        var currentRow = input.closest('tr');
        // Ensure we are grabbing the data-price correctly
        var pricePerItem = parseFloat(currentRow.find('.active-price').attr('data-price'));
        
        if (!isNaN(pricePerItem)) {
            var newSubtotal = (pricePerItem * newVal).toFixed(2);
            
            // Update the row subtotal
            // Note: Ensure your HTML has id="subtotal-{{product.id}}"
            $('#subtotal-' + productId).text(newSubtotal);

            // --- GRAND TOTAL CALCULATOR ---
            var grandTotal = 0;
            
            // Use the specific class you have in your HTML
            $('.row-total').each(function() {
                var rawText = $(this).text().replace(/[^\d.]/g, '');
                var subValue = parseFloat(rawText);
                if (!isNaN(subValue)) {
                    grandTotal += subValue;
                }
            });
            console.log("Calculated Grand Total is: ", grandTotal); // Add this line
            
            // Update the 580
            $('#grand-total-val').text(grandTotal.toFixed(2));
        }
    } catch (err) {
        console.error("Calculation error, but buttons will still work: ", err);
    }

    // 3. Update Navbar Cart Count
    if(document.getElementById("cart_quantity")) {
        document.getElementById("cart_quantity").textContent = json.qty;
    }
},
            error: function(xhr, errmsg, err) {
                // If this triggers, check your console (F12) to see the error
                console.log("Error: Could not update the session. Check your URL and View.");
            }
        });
    });
});




// Delete cart

    //Check if button pressed
  $(document).on('click', '.btn-delete', function(e) {
    console.log("Delete button clicked!");
    e.preventDefault();

    var productId = $(this).data('index');
    var productColor = $(this).data('color');
    var productSize = $(this).data('size');

    $.ajax({
        type: 'POST',
        url: '{% url "delete-cart-item" %}',
        data: {
            product_id: productId,
            product_color: productColor,
            product_size: productSize,
            csrfmiddlewaretoken: '{{ csrf_token }}',
            action: 'post'
        },
        success: function(json) {
            location.reload();
        },
        error: function(xhr, errmsg, err) {
            console.error('AJAX request failed:', errmsg);
        }
    });
});




// Same as Billing
document.addEventListener('DOMContentLoaded', function () {
    const checkbox = document.getElementById('sameAddressCheck');
    const shippingContainer = document.getElementById('shipping-form-container');

    if (checkbox && shippingContainer) {
        // Function to handle the toggling logic
        function toggleShipping() {
            if (checkbox.checked) {
                // Hide shipping form smoothly if they are the same
                shippingContainer.style.display = 'none';
            } else {
                // Show shipping form if they are different
                shippingContainer.style.display = 'block';
            }
        }

        // Listen for user clicks on the checkbox
        checkbox.addEventListener('change', toggleShipping);

        // Run once on page load to preserve state if the page reloads
        toggleShipping();
    }
});
