async function loadSchema() {
    const res = await fetch('/db_schema');
    const data = await res.json();
    const container = document.getElementById('schema');
    container.innerHTML = '';
    Object.entries(data).forEach(([table, columns]) => {
        const div = document.createElement('div');
        const btn = document.createElement('button');
        btn.textContent = `Show ${table} data`;
        btn.addEventListener('click', () => loadTable(table));
        const fields = columns.map(c => `${c.name} (${c.type})`).join(', ');
        div.innerHTML = `<h3>${table}</h3><p>${fields}</p>`;
        div.append(btn);
        container.append(div);
    });
}

async function loadTable(name) {
    const res = await fetch(`/table/${name}`);
    const rows = await res.json();
    const thead = document.querySelector('#data-table thead');
    const tbody = document.querySelector('#data-table tbody');
    thead.innerHTML = '';
    tbody.innerHTML = '';
    if (!rows.length) {
        return;
    }
    const headerRow = document.createElement('tr');
    Object.keys(rows[0]).forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.append(th);
    });
    thead.append(headerRow);
    rows.forEach(row => {
        const tr = document.createElement('tr');
        Object.values(row).forEach(val => {
            const td = document.createElement('td');
            td.textContent = val;
            tr.append(td);
        });
        tbody.append(tr);
    });
}

loadSchema();
