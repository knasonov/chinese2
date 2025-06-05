async function loadSchema() {
    const res = await fetch('/db_schema');
    const data = await res.json();
    const container = document.getElementById('schema');
    container.innerHTML = '';
    Object.entries(data).forEach(([table, columns]) => {
        const section = document.createElement('section');
        const heading = document.createElement('h3');
        heading.textContent = table;
        section.append(heading);

        const colTable = document.createElement('table');
        const thead = document.createElement('thead');
        thead.innerHTML = '<tr><th>Column</th><th>Type</th></tr>';
        const tbody = document.createElement('tbody');
        columns.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${c.name}</td><td>${c.type}</td>`;
            tbody.append(tr);
        });
        colTable.append(thead);
        colTable.append(tbody);
        section.append(colTable);

        const btn = document.createElement('button');
        btn.textContent = `Show ${table} data`;
        btn.addEventListener('click', () => loadTable(table));
        section.append(btn);

        container.append(section);
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
