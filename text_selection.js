let stories = [];
let currentIndex = 0;

async function loadTokens(name) {
    const [tokenRes, bpmfRes] = await Promise.all([
        fetch(`/story_tokens/${name}`),
        fetch(`/bopomofo_mapping/${name}`)
    ]);
    const tokens = await tokenRes.json();
    const bpmfMap = await bpmfRes.json();
    const container = document.getElementById('text');
    container.innerHTML = '';
    const chineseRE = /[\u4e00-\u9fff]/;
    tokens.forEach(t => {
        if (t === '\n') {
            container.append(document.createElement('br'));
        } else if (chineseRE.test(t)) {
            const span = document.createElement('span');
            span.textContent = t;
            span.dataset.original = t;
            if (bpmfMap[t]) {
                span.dataset.bpmf = bpmfMap[t];
            }
            span.classList.add('word');
            span.addEventListener('click', () => {
                span.classList.toggle('unknown');
            });
            span.addEventListener('mouseenter', () => {
                const bpmf = span.dataset.bpmf;
                if (!bpmf || span.dataset.showing === 'true') return;
                const chars = Array.from(span.dataset.original);
                const readings = bpmf.split(' ');
                const html = chars.map((c, i) => {
                    const r = readings[i] || '';
                    return `<span class="ruby-char">${c}<span class="rt-bpmf">${r}</span></span>`;
                }).join('');
                span.innerHTML = html;
                span.dataset.showing = 'true';
            });
            span.addEventListener('mouseleave', () => {
                if (span.dataset.showing === 'true') {
                    span.textContent = span.dataset.original;
                    span.dataset.showing = 'false';
                }
            });
            container.append(span);
        } else {
            container.append(t);
        }
    });
}

async function loadUnknownWords(name) {
    const res = await fetch(`/unknown_words/${name}`);
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
        const w = span.dataset.original || span.textContent;
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

document.getElementById('submit').addEventListener('click', showResults);

async function loadAudio(name) {
    const audio = document.getElementById('player');
    const url = `/audio/${name}.wav`;
    try {
        const res = await fetch(url, { method: 'HEAD' });
        if (res.ok) {
            audio.src = url;
            audio.style.display = 'block';
        } else {
            audio.removeAttribute('src');
            audio.style.display = 'none';
        }
    } catch {
        audio.removeAttribute('src');
        audio.style.display = 'none';
    }
}

async function loadStory(index) {
    if (!stories.length) {
        const res = await fetch('/stories_list');
        stories = await res.json();
    }
    if (index < 0 || index >= stories.length) return;
    currentIndex = index;
    const name = stories[index];
    document.getElementById('story-name').textContent = name;
    await loadTokens(name);
    await loadUnknownWords(name);
    await loadAudio(name);
}

document.getElementById('prev').addEventListener('click', () => loadStory(currentIndex - 1));
document.getElementById('next').addEventListener('click', () => loadStory(currentIndex + 1));

loadStory(0);
