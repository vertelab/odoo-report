/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.portal_pdf_viewer = publicWidget.Widget.extend({
    selector: '.o_portal_pdf_viewer',

    start() {
        return this._super.apply(this, arguments).then(() => {
            this._initPDF();
        });
    },

    async _initPDF() {
        try {
            const pdfUrl = this.el.dataset.pdfUrl;
            if (!pdfUrl) return;

            const pdfjs = await import('/elevata_portal_pdf/static/src/lib/pdf.mjs');
            const { getDocument, GlobalWorkerOptions } = pdfjs;
            GlobalWorkerOptions.workerSrc = '/elevata_portal_pdf/static/src/lib/pdf.worker.mjs';

            const mainContainer = document.createElement('div');
            mainContainer.style.cssText = 'display:flex;flex-direction:column;align-items:center;width:100%;gap:20px;';
            this.el.appendChild(mainContainer);

            const pdfDoc = await getDocument({ url: pdfUrl, withCredentials: true }).promise;
            const A4_RATIO = 297 / 210;
            const containerWidth = this.el.clientWidth;
            const targetWidth = Math.min(containerWidth * 0.98, 800);

            for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
                const pageContainer = document.createElement('div');
                pageContainer.style.cssText = 'padding:8px;width:100%;display:flex;justify-content:center;';

                const canvasWrapper = document.createElement('div');
                canvasWrapper.style.cssText = 'background:white;box-shadow:0 2px 8px rgba(0,0,0,.15),0 4px 16px rgba(0,0,0,.1);border-radius:2px;padding:8px;';

                const canvas = document.createElement('canvas');
                canvasWrapper.appendChild(canvas);
                pageContainer.appendChild(canvasWrapper);
                mainContainer.appendChild(pageContainer);

                const page = await pdfDoc.getPage(pageNum);
                const viewport = page.getViewport({ scale: 1.0 });
                const scale = targetWidth / viewport.width;
                const adjustedViewport = page.getViewport({ scale });

                canvas.width = targetWidth;
                canvas.height = targetWidth * A4_RATIO;
                canvas.style.cssText = `width:100%;height:auto;max-width:${targetWidth}px;display:block;`;

                await page.render({
                    canvasContext: canvas.getContext('2d'),
                    viewport: adjustedViewport,
                }).promise;
            }
        } catch (error) {
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = 'color:red;padding:20px;';
            errorDiv.textContent = 'Error loading PDF: ' + error.message;
            this.el.appendChild(errorDiv);
        }
    },
});
