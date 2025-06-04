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

async function loadUnknownWords() {
    const res = await fetch('/unknown_words');
    const words = await res.json();
    const list = document.getElementById('unknown-list');
    list.innerHTML = '';
    words.forEach(w => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${w.word}</td>` +
            `<td>${w.pinyin}</td>` +
            `<td>${w.meaning}</td>`;
        list.append(tr);
    });
}

async function showResults() {
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
    out.textContent = 'Known: ' + known.join('') + '\n\nUnknown: ' + unknown.join('');
    try {
        await fetch('/update_words', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ known, unknown })
        });
    } catch (err) {
        console.error('Failed to send results', err);
    }
}

document.getElementById('show').addEventListener('click', showResults);
loadTokens();
loadUnknownWords();
