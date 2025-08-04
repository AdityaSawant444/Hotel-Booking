// Room count logic for generic counter
function increaseRoom() {
  const button = event.target;
  const counterContainer = button.parentElement;
  const countSpan = counterContainer.querySelector('.room-count');
  let count = parseInt(countSpan.innerText, 10);
  count++;
  countSpan.innerText = count;
}

function decreaseRoom() {
  const button = event.target;
  const counterContainer = button.parentElement;
  const countSpan = counterContainer.querySelector('.room-count');
  let count = parseInt(countSpan.innerText, 10);
  if (count > 1) {
    count--;
    countSpan.innerText = count;
  }
}