/* MSGR site settings — edit here, no other file needs changing.
   leadEndpoint: where the contact form and quiz send enquiries.
     "/api/lead.php"  → the included PHP script (Hostinger / any PHP hosting): sends to Telegram + email.
     ""               → no backend: the form opens the visitor's mail app (fallback).
   The web app will later replace this with its own API URL. */
window.MSGR_CONFIG = {
  leadEndpoint: "/api/lead.php",
  fallbackEmail: "mystudygr1@gmail.com",
  whatsapp: "https://wa.me/306942770701"
};
