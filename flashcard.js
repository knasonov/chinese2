let index = 0;
let currentWord = null;

async function loadWord() {
    const card = document.getElementById('card');
    card.classList.add('flip');
    setTimeout(() => card.classList.remove('flip'), 600);

    const res = await fetch(`/next_word?offset=${index}`);
    const data = await res.json();
    if (!data.word) {
        document.getElementById('word').textContent = 'No more words';
        document.getElementById('pinyin').textContent = '';
        document.getElementById('meaning').textContent = '';
        document.getElementById('reveal').style.display = 'none';
        document.getElementById('answer').style.display = 'none';
        return;
    }
    currentWord = data.word;
    document.getElementById('word').textContent = data.word;
    document.getElementById('pinyin').textContent = data.pinyin;
    document.getElementById('meaning').textContent = data.meaning;
    document.getElementById('meaning').style.display = 'none';
    document.getElementById('answer').style.display = 'none';
    document.getElementById('button-divider').style.display = 'none';
}

function reveal() {
    document.getElementById('meaning').style.display = 'block';
    document.getElementById('button-divider').style.display = 'block';
    document.getElementById('answer').style.display = 'flex';
}

async function record(known) {
    if (!currentWord) return;
    await fetch('/record_flashcard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word: currentWord, known })
    });
    index++;
    loadWord();
}

document.getElementById('reveal').addEventListener('click', reveal);
document.getElementById('right').addEventListener('click', () => record(true));
document.getElementById('wrong').addEventListener('click', () => record(false));

document.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
        e.preventDefault();
        if (document.getElementById('answer').style.display === 'none') {
            reveal();
        }
    } else if (e.key === '1') {
        if (document.getElementById('answer').style.display !== 'none') {
            record(true);
        }
    } else if (e.key === '2') {
        if (document.getElementById('answer').style.display !== 'none') {
            record(false);
        }
    }
});

loadWord();
