async function loadStats() {
    const res = await fetch('/stats_data');
    const data = await res.json();
    const tbody = document.querySelector('#stats tbody');
    tbody.innerHTML = '';
    data.forEach(entry => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${entry.word}</td>` +
            `<td>${(entry.probability * 100).toFixed(1)}%</td>` +
            `<td>${entry.interactions}</td>`;
        tbody.append(tr);
    });
}

loadStats();
