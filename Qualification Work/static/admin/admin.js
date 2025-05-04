async function fetchLogs(url, elId) {
    const res = await fetch(url);
    if (!res.ok) {
        document.getElementById(elId).textContent = 'Ошибка загрузки';
        return;
    }
    const json = await res.json();
    document.getElementById(elId).textContent = json.lines.join('\n');
}

document.getElementById('btn-run-scheduler').onclick = async () => {
    await fetch('/admin/run/scheduler', { method: 'POST' });
    fetchLogs('/admin/logs/scheduler', 'scheduler-log');
};

document.getElementById('btn-run-file').onclick = async () => {
    const fname = document.getElementById('file-name').value;
    await fetch('/admin/run/file?filename=' + fname, { method: 'POST' });
    fetchLogs('/admin/logs/file/' + fname, 'file-log');
};

setInterval(() => {
    fetchLogs('/admin/logs/scheduler', 'scheduler-log');
    const fname = document.getElementById('file-name').value;
    if (fname) fetchLogs('/admin/logs/file/' + fname, 'file-log');
}, 10000);

fetchLogs('/admin/logs/scheduler', 'scheduler-log');