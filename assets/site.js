'use strict';
const menu = document.querySelector('.menu-toggle');
menu?.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded', String(open)); document.querySelector('.mainnav').classList.toggle('open', open); });
const search = document.querySelector('#search');
if (search) {
 const cards = [...document.querySelectorAll('[data-product]')];
 const category = document.querySelector('#category');
 const sort = document.querySelector('#sort');
 const update = () => {
  const query = search.value.trim().toLowerCase(); let count = 0;
  cards.forEach(card => {const match = card.dataset.name.includes(query) && (!category.value || card.dataset.category === category.value); card.hidden = !match; if (match) count++;});
  const ordered = [...cards].sort((a,b) => sort.value === 'name' ? a.dataset.name.localeCompare(b.dataset.name) : sort.value === 'price' ? Number(a.dataset.price)-Number(b.dataset.price) : Number(a.dataset.order)-Number(b.dataset.order));
  ordered.forEach(card => card.parentElement.appendChild(card));
  document.querySelector('#result-count').textContent = `${count} ${count === 1 ? 'piece' : 'pieces'}`;
  document.querySelector('#no-results').hidden = count > 0;
 };
 [search,category,sort].forEach(el => el.addEventListener('input',update));update();
 document.querySelector('#reset-search').addEventListener('click',() => {search.value='';category.value='';sort.value='featured';update();search.focus();});
}
const inquiry = document.querySelector('#inquiry');
if (inquiry) {
 const item = new URLSearchParams(location.search).get('piece'); if(item) document.querySelector('#message').value = `Hello, I’m interested in ${item}. Could you share its availability, price, details and additional photos?`;
 inquiry.addEventListener('submit', async event => {
  event.preventDefault();const data = new FormData(inquiry);
  const text = `Hello Black Michael Collection,\n\n${data.get('message')}\n\nName: ${data.get('name')}\nReply to: ${data.get('email')}`;
  const status = document.querySelector('#form-status');
  if(inquiry.dataset.email) {location.href = `mailto:${encodeURIComponent(inquiry.dataset.email)}?subject=${encodeURIComponent('Collection inquiry')}&body=${encodeURIComponent(text)}`;status.textContent = 'Your email app has been requested. Review and send your message there. This website has not sent it.';}
  else {try {await navigator.clipboard.writeText(text);status.textContent='Message copied. Open Instagram below and paste it into a direct message to @blackmichael_collection. Nothing has been sent yet.';} catch {status.textContent='Copy this message and paste it into an Instagram direct message:\n\n'+text;}}
 });
}
