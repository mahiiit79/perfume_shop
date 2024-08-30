

function addPerfumeToOrder(perfumeId) {
  const perfumeCount = $('#qty').val();
  const volumeId = $('#volume').val();
  $.get('/accounts/add-to-order', {
    perfume_id: perfumeId,
    count: perfumeCount,
    volume_id: volumeId
  }).then(res => {
    Swal.fire({
      title: 'اعلان',
      text: res.text,
      icon: res.icon,
      showCancelButton: false,
      confirmButtonColor: 'purple',
      confirmButtonText: res.confirm_button_text
    }).then((result) => {
      if (result.isConfirmed && res.status === 'not_auth') {
        window.location.href = '/login';
      } else {
        // Update the header component with the new order details
        const headerOrderDetails = document.querySelector('#header-order-details');
        const orderDetailsHtml = res.order_data.order_details.map(od => `
            <div class="product">
                <div class="product-cart-details">
                    <h4 class="product-title text-center">
                        <a href="${od.perfume_title}">${od.perfume_title}</a>
                    </h4>
                    <span class="cart-product-info">
                        <span class="cart-product-qty">${od.count} x </span>
                        ${od.volume_title}
                    </span>
                </div>
                <figure class="product-image-container">
                    <a href="${od.perfume_title}" class="product-image">
                        <img src="${od.image}" alt="محصول">
                    </a>

                </figure>
                <a href="#" class="btn-remove" title="حذف محصول" data-detail-id="${od.id}"><i class="icon-close"></i></a>
            </div>
        `).join('');
        headerOrderDetails.innerHTML = orderDetailsHtml;

        // Add event listener to remove buttons
        const removeButtons = headerOrderDetails.querySelectorAll('.btn-remove');
        removeButtons.forEach(button => {
          button.addEventListener('click', event => {
            const detailId = event.target.dataset.detailId;
            removeHeaderOrderDetail(detailId);
          });
        });

        // Update the cart count and total price
        const headerBasketCount = document.querySelector('#header-basket-count');
        headerBasketCount.textContent = res.order_data.order_details.length;
        const totalPriceElement = document.querySelector('#total-price-header');
        if (totalPriceElement) {
          totalPriceElement.textContent = res.order_data.order_total;
        }

        // Add a "new" class to the last item in the list for a short time
        const lastItem = headerOrderDetails.querySelector('div.product:last-child');
        lastItem.classList.add('new');
        setTimeout(() => lastItem.classList.remove('new'), 2000);
      }
    });
  });}






function removeOrderDetail(detailId){
    $.get('/accounts/remove-basket-detail?detail_id=' + detailId).then(res => {
        if (res.status === 'success') {
            $('#order-detail-content').html(res.body);
        }
    });
}



function changeOrderDetailCount(detailId, state) {
    $.get('/accounts/change-order-detail/', { detail_id: detailId, state: state }).then(res => {
        if (res.status === 'success') {
            $('#order-detail-content').html(res.body);
            $('#total-price').text(res.total_amount_with_shipping.toLocaleString('fa-IR'));
        }
    });
}

//
//function removeHeaderOrderDetail(detailId) {
//  $.ajax({
//    url: '/accounts/remove-header-order-detail/',
//    data: {
//      'detail_id': detailId,
//    },
//    dataType: 'json',
//    success: function(data) {
//      if (data.status === 'success') {
//        // Remove the order detail element from the DOM
//        $(`#header-order-details div.product[data-order-detail-id="${detailId}"]`).remove();
//        // Update the header basket HTML with the new list of order details
//        const headerBasketHtml = data.site_header_component;
//        console.log("HTML updated successfully!");
//        $('#header-order-details').html(headerBasketHtml);
//        // Update the cart count
//        const headerBasketCount = document.querySelector('#header-basket-count');
//        headerBasketCount.textContent = data.header_basket_count;
//        // Remove the remove link for the order detail
//        const removeLink = $(`#header-order-details a[data-order-detail-id="${detailId}"]`);
//        removeLink.remove();
//        console.log("HTML updated successfully!");
//        // Calculate the new total price
//        console.log('data:', data);
//        const newTotalPrice = data.total_price;
//        console.log('newTotalPrice:', newTotalPrice);
//        // Update the total price element in the mini-cart
//        const totalPriceElement = document.querySelector('#total-price');
//        console.log('totalPriceElement:', totalPriceElement);
//        if (totalPriceElement) {
//          totalPriceElement.textContent = newTotalPrice.toLocaleString('fa-IR');
//        } else {
//          console.log('totalPriceElement is undefined');
//        }
//        // Refresh the page
//        location.reload();
//      } else {
//        console.error(data.message);
//      }
//    },
//    error: function(xhr, textStatus, errorThrown) {
//      console.error(xhr.responseText);
//    }
//  });
//}
//


// Get the detail ID from the HTML element
function getDetailId() {
  return new Promise(function(resolve, reject) {
    var detailId = $(this).data('order-detail-id');
    if (detailId) {
      resolve(detailId);
    } else {
      setTimeout(function() {
        getDetailId().then(resolve);
      }, 100);
    }
  });
}

//// Remove header order detail function
//function removeHeaderOrderDetail() {
//  getDetailId().then(function(detailId) {
//    $.ajax({
//      url: '/accounts/remove-header-order-detail/',
//      data: {
//        'detail_id': detailId,
//      },
//      dataType: 'json',
//      success: function(data) {
//        if (data.status === 'success') {
//          // Remove the item from the header basket HTML
//          $(`#header-order-details div.product[data-order-detail-id="${detailId}"]`).remove();
//
//          // Update the header basket count
//          const headerBasketCount = document.querySelector('#header-basket-count');
//          headerBasketCount.textContent = data.header_basket_count;
//
//          // Update the total price
//          const totalPriceElement = document.querySelector('#total-price-header');
//          totalPriceElement.textContent = data.total_price.toLocaleString('fa-IR');
//
//          console.log("HTML updated successfully!");
//        } else {
//          console.error(data.message);
//        }
//      },
//      error: function(xhr, textStatus, errorThrown) {
//        console.error(xhr.responseText);
//      }
//    });
//  });
//}


var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

function removeHeaderOrderDetail(detailId) {
    var detailId = $('#detail-id').val();
    console.log('detailId:', detailId); // Add this line
    $.ajax({
        type: 'POST',
        url: '/accounts/remove-header-order-detail/',
        data: {
            'detailId': detailId,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function(data) {
            if (data.status === 'success') {
                $('#header-order-details').html(data.site_header_component);
                $('#header-basket-count').text(data.header_basket_count);
                $('#total-price-header').text(data.total_price + 'تومان');
            } else {
                console.error(data.message);
            }
        },
        error: function(xhr, status, error) {
            console.log('Error:', error);
        }
    });
}



//function removeHeaderOrderDetail(detailId) {
//    var csrfToken = $.cookie('csrftoken');
//    $.ajax({
//        type: 'POST',
//        url: '/accounts/remove-header-order-detail/',
//        data: {
//            'detailId': detailId,
//            'csrfmiddlewaretoken': csrfToken
//        },
//        success: function(data) {
//            $('#header-basket-count').text(data.count);
//            $('#total-price-header').text(data.total_price + 'ومان');
//            $('#' + detailId).remove();
//        },
//        error: function(xhr, status, error) {
//            console.log('Error:', error);
//        }
//    });
//}
//
//// Call the removeHeaderOrderDetail function when the remove button is clicked
//$(document).on('click', '.remove-header-order-detail', function() {
//  removeHeaderOrderDetail();
//});

