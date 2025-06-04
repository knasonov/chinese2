async function loadTokens() {
    const res = await fetch('tokens.json');
    const tokens = await res.json();
    const container = document.getElementById('text');
    const chineseRE = /[\u4e00-\u9fff]/;
    tokens.forEach(t => {
        if (t === '\n') {
            container.append(document.createElement('br'));
        } else if (chineseRE.test(t)) {
            const span = document.createElement('span');
            span.textContent = t;
            span.classList.add('word');
            span.addEventListener('click', () => {
                span.classList.toggle('unknown');
            });
            container.append(span);
        } else {
            container.append(t);
        }
    });
}

function showResults() {
    const words = Array.from(document.querySelectorAll('.word'));
    const known = [];
    const unknown = [];
    words.forEach(span => {
        const w = span.textContent;
        if (span.classList.contains('unknown')) {
            unknown.push(w);
        } else {
            known.push(w);
        }
    });
    const out = document.getElementById('output');
    out.textContent = 'Known: ' + known.join(' ') + '\n\nUnknown: ' + unknown.join(' ');
}

document.getElementById('show').addEventListener('click', showResults);
loadTokens();
