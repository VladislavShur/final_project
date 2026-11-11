// Toast Notification
function showToast(msg, isSuccess = true) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = `fixed bottom-6 left-6 z-50 px-5 py-3 rounded-xl shadow-2xl transition-all duration-300 ${isSuccess ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white'}`;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3500);
}

// Tab Switching
function switchTab(tabId) {
    ['tasks', 'assets', 'logs'].forEach(t => {
        document.getElementById(`panel-${t}`).classList.add('hidden');
        document.getElementById(`tab-${t}`).className = 'tab-btn px-4 py-2 rounded-lg text-sm font-semibold transition-all text-slate-400 hover:text-white';
    });
    document.getElementById(`panel-${tabId}`).classList.remove('hidden');
    const activeBtn = document.getElementById(`tab-${tabId}`);
    activeBtn.className = 'tab-btn px-4 py-2 rounded-lg text-sm font-semibold transition-all bg-indigo-600 text-white shadow';

    if (tabId === 'tasks') loadTasks();
    if (tabId === 'assets') loadAssets();
    if (tabId === 'logs') loadLogs();
}

// ==========================================
// 1. TASKS MANAGEMENT (API & UI)
// ==========================================
async function loadTasks() {
    try {
        const res = await fetch('/api/tasks');
        const data = await res.json();
        const tbody = document.getElementById('tasks-table-body');
        if (!data.tasks || data.tasks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">אין משימות במערכת. הוסף משימה ראשונה!</td></tr>';
            return;
        }
        tbody.innerHTML = data.tasks.map((t, idx) => `
            <tr class="hover:bg-slate-700/30 transition">
                <td class="px-6 py-4 text-slate-500 font-mono">${idx}</td>
                <td class="px-6 py-4 font-semibold text-white">${t.name}</td>
                <td class="px-6 py-4 text-slate-300">${t.test_suite || 'General'}</td>
                <td class="px-6 py-4">
                    <span class="px-2.5 py-1 text-xs rounded-full ${t.priority === 'High' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : t.priority === 'Medium' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-slate-700 text-slate-300'}">${t.priority}</span>
                </td>
                <td class="px-6 py-4">
                    <span class="px-2.5 py-1 text-xs rounded-full ${t.status === 'Done' || t.status === 'Completed' ? 'bg-emerald-500/20 text-emerald-400' : t.status === 'In Progress' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-slate-700 text-slate-300'}">${t.status}</span>
                </td>
                <td class="px-6 py-4 flex gap-2">
                    <button onclick="updateTaskStatus(${idx}, 'In Progress')" class="text-xs px-2.5 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg">בתהליך</button>
                    <button onclick="updateTaskStatus(${idx}, 'Done')" class="text-xs px-2.5 py-1 bg-emerald-600/40 hover:bg-emerald-600 text-emerald-200 rounded-lg">הושלם</button>
                    <button onclick="deleteTask(${idx})" class="text-xs px-2.5 py-1 bg-rose-600/30 hover:bg-rose-600 text-rose-200 rounded-lg">🗑️ מחק</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        showToast('שגיאה בטעינת משימות: ' + err, false);
    }
}

async function handleAddTask(e) {
    e.preventDefault();
    const name = document.getElementById('task-name').value;
    const suite = document.getElementById('task-suite').value || 'General';
    const priority = document.getElementById('task-priority').value;

    const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, test_suite: suite, priority, status: 'Pending' })
    });
    const out = await res.json();
    if (out.success) {
        showToast('המשימה נוספה בהצלחה!');
        document.getElementById('task-name').value = '';
        document.getElementById('task-suite').value = '';
        loadTasks();
    } else {
        showToast(out.error || 'שגיאה בהוספת משימה', false);
    }
}

async function updateTaskStatus(idx, status) {
    const res = await fetch('/api/tasks/status', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index: idx, status })
    });
    const out = await res.json();
    if (out.success) {
        showToast('הסטטוס עודכן!');
        loadTasks();
    } else {
        showToast(out.error, false);
    }
}

async function deleteTask(idx) {
    if (!confirm('האם אתה בטוח שברצונך למחוק משימה זו?')) return;
    const res = await fetch(`/api/tasks?index=${idx}`, { method: 'DELETE' });
    const out = await res.json();
    if (out.success) {
        showToast('המשימה נמחקה בהצלחה!');
        loadTasks();
    } else {
        showToast(out.error || 'שגיאה במחיקת משימה', false);
    }
}

// ==========================================
// 2. ASSETS & LICENSES (API & UI)
// ==========================================
async function loadAssets() {
    try {
        const res = await fetch('/api/assets');
        const data = await res.json();
        const tbody = document.getElementById('assets-table-body');
        if (!data.assets || data.assets.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-slate-500">אין פריטים במאגר.</td></tr>';
            return;
        }
        tbody.innerHTML = data.assets.map((a, idx) => `
            <tr class="hover:bg-slate-700/30 transition">
                <td class="px-6 py-4 text-slate-500 font-mono">${idx + 1}</td>
                <td class="px-6 py-4 font-semibold text-white">${a.asset_name}</td>
                <td class="px-6 py-4 text-slate-300">${a.category || 'Hardware'}</td>
                <td class="px-6 py-4 text-cyan-300">${a.assigned_to || '<span class="text-slate-500">ללא עובד</span>'}</td>
                <td class="px-6 py-4">
                    <span class="px-2.5 py-1 text-xs rounded-full ${a.status === 'ASSIGNED' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}">
                        ${a.status}
                    </span>
                </td>
                <td class="px-6 py-4">
                    ${a.status === 'ASSIGNED' ? `<button onclick="returnAsset('${a.asset_name}')" class="text-xs px-2.5 py-1 bg-rose-600/30 hover:bg-rose-600 text-rose-200 rounded-lg">החזר למאגר</button>` : '<span class="text-xs text-slate-500">פנוי</span>'}
                </td>
            </tr>
        `).join('');
    } catch (err) {
        showToast('שגיאה בטעינת נכסים: ' + err, false);
    }
}

async function handleAssignAsset(e) {
    e.preventDefault();
    const asset_name = document.getElementById('asset-name').value;
    const employee = document.getElementById('asset-employee').value;
    const category = document.getElementById('asset-category').value;

    const res = await fetch('/api/assets/assign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset_name, employee, category })
    });
    const out = await res.json();
    if (out.success) {
        showToast(out.message);
        document.getElementById('asset-name').value = '';
        document.getElementById('asset-employee').value = '';
        loadAssets();
    } else {
        showToast(out.error || 'שגיאה בשיוך', false);
    }
}

async function returnAsset(name) {
    const res = await fetch('/api/assets/return', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset_name: name })
    });
    const out = await res.json();
    if (out.success) {
        showToast('הציוד הוחזר למלאי!');
        loadAssets();
    } else {
        showToast(out.error, false);
    }
}

async function exportAssetReport() {
    const res = await fetch('/api/assets/report');
    const data = await res.json();
    if (data.success) {
        alert("דוח נכסים מרוכז:\n\n" + data.content);
    } else {
        showToast('שגיאה בייצוא', false);
    }
}

// ==========================================
// 3. LOGS & ANALYZER (API & UI)
// ==========================================
async function loadLogs() {
    const res = await fetch('/api/logs');
    const data = await res.json();
    if (!data.loaded) return;

    document.getElementById('stat-total').textContent = data.stats.total_tests;
    document.getElementById('stat-passed').textContent = data.stats.passed_count;
    document.getElementById('stat-failed').textContent = data.stats.failed_count;
    document.getElementById('stat-rate').textContent = data.stats.pass_rate_pct.toFixed(1) + '%';
    document.getElementById('log-count-badge').textContent = data.entries.length + ' רשומות';

    const tbody = document.getElementById('logs-table-body');
    tbody.innerHTML = data.entries.map(e => `
        <tr class="hover:bg-slate-700/30 transition">
            <td class="px-6 py-4 text-xs font-mono text-slate-400">${e.timestamp || '-'}</td>
            <td class="px-6 py-4 font-semibold text-white">${e.test_name}</td>
            <td class="px-6 py-4">
                <span class="px-2 py-0.5 text-xs rounded-full ${e.status === 'PASSED' || e.status === 'PASS' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">${e.status}</span>
            </td>
            <td class="px-6 py-4 font-mono text-slate-300">${e.duration_sec.toFixed(2)}s</td>
            <td class="px-6 py-4 text-xs font-bold ${e.severity === 'ERROR' || e.severity === 'CRITICAL' ? 'text-rose-400' : 'text-slate-400'}">${e.severity}</td>
            <td class="px-6 py-4 text-xs text-slate-300">${e.message || '-'}</td>
        </tr>
    `).join('');
}

async function loadSampleLogs() {
    const res = await fetch('/api/logs/sample', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
        showToast(`נטענו ${data.count} רשומות לוג!`);
        loadLogs();
    }
}

// טעינה ראשונית
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
});

