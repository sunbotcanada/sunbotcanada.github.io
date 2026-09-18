/* Build FAQPage JSON-LD from visible FAQ markup so schema cannot drift from page content. */
(function () {
    function plainText(node) {
        return (node.textContent || '').replace(/\s+/g, ' ').trim();
    }

    function buildFaqSchema() {
        var items = document.querySelectorAll('.faq-item');
        if (!items.length) {
            return;
        }

        var mainEntity = [];
        items.forEach(function (item) {
            var questionEl = item.querySelector('.faq-question');
            var answerEl = item.querySelector('.faq-answer');
            if (!questionEl || !answerEl) {
                return;
            }
            mainEntity.push({
                '@type': 'Question',
                name: plainText(questionEl),
                acceptedAnswer: {
                    '@type': 'Answer',
                    text: plainText(answerEl)
                }
            });
        });

        if (!mainEntity.length) {
            return;
        }

        var existing = document.getElementById('faq-jsonld');
        if (existing) {
            existing.remove();
        }

        var script = document.createElement('script');
        script.type = 'application/ld+json';
        script.id = 'faq-jsonld';
        script.text = JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: mainEntity
        });
        document.head.appendChild(script);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildFaqSchema);
    } else {
        buildFaqSchema();
    }
})();
