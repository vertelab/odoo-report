/** @odoo-module **/

// Backend-titeln sätts dynamiskt av Odoos title-service med
// "Odoo" som standard-del ("Odoo - Arbetsordrar" osv.).
// Byt ut "Odoo" mot "Elevata" i flikens titel.
const titleEl = document.querySelector("title");
if (titleEl) {
    const rebrand = () => {
        if (document.title && document.title.includes("Odoo")) {
            document.title = document.title.replace(/Odoo/g, "Elevata");
        }
    };
    new MutationObserver(rebrand).observe(titleEl, {
        childList: true,
        characterData: true,
        subtree: true,
    });
    rebrand();
}
