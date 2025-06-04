fetch('stats.json')
  .then(r => r.json())
  .then(data => {
    document.getElementById('total').textContent = data.total;
    document.getElementById('unique').textContent = data.stats.length;
    const tbody = document.querySelector('#stats tbody');
    data.stats.forEach(item => {
      const tr = document.createElement('tr');
      const freq = item.frequency.toFixed(2) + '%';
      tr.innerHTML = `<td>${item.character}</td><td>${item.count}</td><td>${freq}</td>`;
      tbody.appendChild(tr);
    });
  })
  .catch(err => {
    console.error('Failed to load stats:', err);
  });
