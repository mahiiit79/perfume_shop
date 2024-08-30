function updateTotalPrice(shippingMethodPrice) {
  let totalPriceElement = document.getElementById('total-price');
  if (!totalPriceElement) {
    console.error('Total price element not found!');
    return;
  }

  // Get originalTotalPrice from attribute
  let originalTotalPrice = totalPriceElement.getAttribute('data-original-total-price');

  // Update originalTotalPrice if it's not set
  if (!originalTotalPrice) {
    originalTotalPrice = parseFloat(totalPriceElement.textContent.replace(/[^\d\.]/g, ''));
    totalPriceElement.setAttribute('data-original-total-price', originalTotalPrice);
  }

  // Get previousShippingMethodPrice from attribute
  let previousShippingMethodPrice = totalPriceElement.getAttribute('data-previous-shipping-method-price');

  // Calculate new total price
  let newTotalPrice = originalTotalPrice;

  if (previousShippingMethodPrice) {
    newTotalPrice -= parseFloat(previousShippingMethodPrice); // Subtract previous shipping method price
  }

  newTotalPrice += parseFloat(shippingMethodPrice); // Add new shipping method price

  // Update previousShippingMethodPrice
  totalPriceElement.setAttribute('data-previous-shipping-method-price', shippingMethodPrice);

  // Update totalPriceElement
  totalPriceElement.textContent = newTotalPrice.toLocaleString('fa-IR')+ 'تومان';

  // Update originalTotalPrice with the newTotalPrice
  totalPriceElement.setAttribute('data-original-total-price', newTotalPrice);
}
