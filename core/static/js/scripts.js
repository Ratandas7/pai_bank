const openMenu = document.getElementById('open_menu');
const closeMenu = document.getElementById('close_menu');
const mobileMenu = document.getElementById('mobile_menu');

const openMProfile = document.getElementById('openM_profile');
const closeMProfile = document.getElementById('closeM_profile');



openMenu.addEventListener('click', () => {
    // mobileMenu.classList.remove('hidden');
    mobileMenu.classList.toggle('hidden');
});

closeMenu.addEventListener('click', () => {
    // mobileMenu.classList.add('hidden');
    mobileMenu.classList.toggle('hidden');
});


openMProfile.addEventListener('click', () => {
    closeMProfile.classList.toggle('hidden');
});


const openProfile = document.getElementById('open_profile');
const closeProfile = document.getElementById('close_profile');

openProfile.addEventListener('click', () => {
    closeProfile.classList.toggle('hidden');
});


document.addEventListener('click', (event) => {
    if (!closeProfile.classList.contains('hidden') && !openProfile.contains(event.target) && !closeProfile.contains(event.target)) {
        closeProfile.classList.add('hidden');
    }
});


const message_btn = document.getElementById('message_btn');
const message_modal = document.getElementById('message_modal');

message_btn.addEventListener('click', () => {
    message_modal.classList.add('hidden');
});