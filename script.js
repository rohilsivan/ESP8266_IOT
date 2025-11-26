const logTable = document.getElementById("logTable");
const authCount = document.getElementById("authCount");
const unauthCount = document.getElementById("unauthCount");
const nofaceCount = document.getElementById("nofaceCount");

// New last event elements
const lastEventName = document.getElementById("lastEventName");
const lastEventType = document.getElementById("lastEventType");
const lastEventTime = document.getElementById("lastEventTime");
const lastEventIndicator = document.getElementById("lastEventIndicator");

let chart;

// Fetch data every 3 seconds
async function fetchData() {
  try {
    const res = await fetch('/data');
    const data = await res.json();
    console.log("📊 Data received:", data);

    if (data.length > 0) {
      updateTable(data);
      updateStats(data);
      updateChart(data);
      updateLastEvent(data);  // ⭐ NEW
    }

  } catch (error) {
    console.error("❌ Fetch error:", error);
  }
}


// Update Recent Activity Table
function updateTable(data) {
  logTable.innerHTML = "";
  data.slice(-20).reverse().forEach(row => {
    const tr = document.createElement("tr");

    let details;
    try { details = row.Name.reason || JSON.stringify(row.Name); }
    catch { details = row.Name; }

    tr.innerHTML = `
      <td>${row.Timestamp || 'N/A'}</td>
      <td><strong>${row.Label || 'UNKNOWN'}</strong></td>
      <td>${details}</td>
    `;
    logTable.appendChild(tr);
  });
}


// Update authorized / unauthorized / no_face counters
function updateStats(data) {
  let auth = 0, unauth = 0, noface = 0;

  data.forEach(row => {
    if (typeof row.Name === "object") {
      const state = row.Name.state;

      if (state === "authorized") auth++;
      else if (state === "unauthorized") unauth++;
      else if (state === "no_face") noface++;
    }
  });

  authCount.textContent = auth;
  unauthCount.textContent = unauth;
  nofaceCount.textContent = noface;
}


// ⭐ NEW — Update "Last Detected Event"
function updateLastEvent(data) {
  const last = data[data.length - 1];
  if (!last) return;

  let reason = "—";
  let state = "system";

  if (typeof last.Name === "object") {
    reason = last.Name.reason || "—";
    state = last.Name.state || "system";
  } else {
    reason = last.Name;
  }

  lastEventName.textContent = reason;
  lastEventType.textContent = "State: " + state;
  lastEventTime.textContent = "Time: " + (last.Timestamp || "—");

  // Color indicator
  if (state === "authorized") {
    lastEventIndicator.style.background = "#10b981";
    lastEventIndicator.style.boxShadow = "0 0 18px #10b981";
  }
  else if (state === "unauthorized") {
    lastEventIndicator.style.background = "#ef4444";
    lastEventIndicator.style.boxShadow = "0 0 18px #ef4444";
  }
  else if (state === "no_face") {
    lastEventIndicator.style.background = "#f59e0b";
    lastEventIndicator.style.boxShadow = "0 0 18px #f59e0b";
  }
  else {
    lastEventIndicator.style.background = "gray";
    lastEventIndicator.style.boxShadow = "0 0 12px gray";
  }
}


// Chart — event frequency per hour
function updateChart(data) {
  const hourCounts = {};

  data.forEach(row => {
    const hour = new Date(row.Timestamp).getHours();
    hourCounts[hour] = (hourCounts[hour] || 0) + 1;
  });

  const labels = Object.keys(hourCounts).map(h => h + ":00");
  const values = Object.values(hourCounts);

  if (!chart) {
    const ctx = document.getElementById("eventChart").getContext("2d");
    chart = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Events Per Hour",
          data: values,
          backgroundColor: 'rgba(59, 130, 246, 0.6)',
          borderColor: '#3b82f6',
          borderWidth: 2
        }]
      },
      options: {
        plugins: { legend: { labels: { color: '#e2e8f0' } } },
        scales: {
          x: { ticks: { color: '#94a3b8' } },
          y: { ticks: { color: '#94a3b8' } }
        }
      }
    });
  } else {
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.update();
  }
}


setInterval(fetchData, 3000);
fetchData();
