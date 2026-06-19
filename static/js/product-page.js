
    //Check if button pressed
    // Using ajax  to send something to the page without refreshing the page

 $(document).on('click', '.add-cart-btn', function(e) {
    e.preventDefault(); 
    
    var currentButton = $(this);
    var targetProductId = currentButton.attr('value'); 
    var product_qty = $("#product-qty").val() || 1;

    var selectedColor = $("input[name='input-radio-color']:checked").val();
    var selectedSize = $("input[name='input-radio-size']:checked").val() || "Standard";

    if (!selectedColor) {
       selectedColor = "Default";
    }

    console.log({
              product_id: targetProductId,
              product_qty: product_qty,
              product_color: selectedColor,
              product_size: selectedSize
              });


    $.ajax({
        type: 'POST',
        url: currentButton.data('url'), // This uses the data-url we added earlier
        data: {
            product_id: targetProductId,
            product_qty: $('#product-qty').val(),
            product_color: $("input[name='input-radio-color']:checked").val(),
            product_size: $("input[name='input-radio-size']:checked").val(),
            // This line grabs the value from the hidden input we added to the HTML
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
    

        // For the cart icon in the navbar
        success: function(json) {
            if (json.qty !== undefined) {
                if (document.getElementById("cart_quantity")) {
                    document.getElementById("cart_quantity").textContent = json.qty;
                }
                if (document.getElementById("cart_header_qty")) {
                    document.getElementById("cart_header_qty").textContent = json.qty;
                }
            }
           alert("Success! Added " + product_qty + " x " + selectedColor + " item(s) to your cart."); 
        },
        error: function(xhr, errmsg, err) {
            console.error('AJAX request failed:', errmsg);
        }
    });
});






$(document).ready(function() {
    $('.stepper-arrow').css({'display': 'block', 'min-width': '20px', 'min-height': '20px'});

    $(document).on('click', '.stepper-arrow', function(e) {
        e.preventDefault();
        
        var parent = $(this).closest('.stepper');
        var input = parent.find('input.stepper-input');
        
        if (input.length === 0) return;
        
        // --- MULTI-PAGE COMPATIBILITY CHECK ---
        var productId = parent.attr('data-product-id'); // Check for product page wrapper attribute
        if (!productId && input.attr('id')) {
            productId = input.attr('id').replace('qty-', ''); // Fallback for Cart summary tracking row
        }
        
        var currentVal = parseInt(input.val()) || 1;
        var newVal = $(this).hasClass('up') ? currentVal + 1 : (currentVal > 1 ? currentVal - 1 : 1);

        // Update the screen value immediately
        input.val(newVal);

        // If we are on the product page, we only want to update the UI value, not run the AJAX update cart yet.
        // We check if we are on the cart summary page by looking for subtotals
        var isCartPage = $('#subtotal-' + productId).length > 0;

        if (isCartPage) {
            // Run the Cart Session Update
            $.ajax({
                type: 'POST',
                url: '{% url "update-cart-item" %}', 
                data: {
                    product_id: productId,
                    product_qty: newVal,
                    csrfmiddlewaretoken: '{{ csrf_token }}', 
                    action: 'post'
                },
                success: function(json) {
                    try {
                        var currentRow = input.closest('tr');
                        var pricePerItem = parseFloat(currentRow.find('.active-price').attr('data-price'));
                        
                        if (!isNaN(pricePerItem)) {
                            var newSubtotal = (pricePerItem * newVal).toFixed(2);
                            $('#subtotal-' + productId).text(newSubtotal);

                            var grandTotal = 0;
                            $('.row-total').each(function() {
                                var rawText = $(this).text().replace(/[^\d.]/g, '');
                                var subValue = parseFloat(rawText);
                                if (!isNaN(subValue)) grandTotal += subValue;
                            });
                            $('#grand-total-val').text(grandTotal.toFixed(2));
                        }
                    } catch (err) {
                        console.error("Calculation error: ", err);
                    }

                    if(document.getElementById("cart_quantity")) {
                        document.getElementById("cart_quantity").textContent = json.qty;
                    }
                },
                error: function(xhr, errmsg, err) {
                    console.log("Error updating session.");
                    input.val(currentVal);
                }
            });
        }
    });
});




// Instagram button
$(document).on('click', '#copy-ig-link', function(e) {
    e.preventDefault();
    
    var pageUrl = $(this).attr('data-url');
    
    // Create a temporary input to run the browser's copy command
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val(pageUrl).select();
    document.execCommand("copy");
    $temp.remove();
    
    // Flash a quick success confirmation text next to the icons
    $('#share-toast').fadeIn().delay(2500).fadeOut();
});

