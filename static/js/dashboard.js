// Dashboard VoIP - JavaScript

// Variáveis globais
let chamadasChart, providerChart;
let currentPage = 1;
let currentPeriod = 7;

// Inicialização
document.addEventListener("DOMContentLoaded", function () {
  initializeDashboard();
  updateCurrentTime();
  setInterval(updateCurrentTime, 1000);
});

// Inicializar dashboard
function initializeDashboard() {
  loadOverview();
  loadChartData();
  loadInsights();
  loadCallsTable();

  // Configurar datas padrão
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  document.getElementById("start-date").value = yesterday
    .toISOString()
    .split("T")[0];
  document.getElementById("end-date").value = today.toISOString().split("T")[0];
}

// Atualizar hora atual
function updateCurrentTime() {
  const now = new Date();
  const timeString = now.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  document.getElementById("current-time").textContent = timeString;
}

// Carregar dados gerais
async function loadOverview() {
  try {
    showLoading();
    const response = await fetch("/api/overview");
    const data = await response.json();

    if (response.ok) {
      updateOverviewCards(data);
      updateTopLists(data);
    } else {
      showError("Erro ao carregar dados gerais: " + data.error);
    }
  } catch (error) {
    showError("Erro de conexão: " + error.message);
  } finally {
    hideLoading();
  }
}

// Atualizar cards de resumo
function updateOverviewCards(data) {
  const hoje = data.hoje;
  const variacao = data.variacao;

  // Total de chamadas
  document.getElementById("total-chamadas").textContent =
    hoje.total_chamadas_hoje.toLocaleString("pt-BR");

  // Variação
  const variacaoElement = document.getElementById("variacao-chamadas");
  if (variacao > 0) {
    variacaoElement.innerHTML = `<i class="fas fa-arrow-up text-success"></i> +${variacao}% vs ontem`;
  } else if (variacao < 0) {
    variacaoElement.innerHTML = `<i class="fas fa-arrow-down text-danger"></i> ${variacao}% vs ontem`;
  } else {
    variacaoElement.innerHTML = `<i class="fas fa-minus text-muted"></i> 0% vs ontem`;
  }

  // Taxa de sucesso
  const taxaSucesso =
    (hoje.chamadas_sucesso / hoje.total_chamadas_hoje) * 100 || 0;
  document.getElementById("taxa-sucesso").textContent =
    taxaSucesso.toFixed(1) + "%";

  // Duração média
  const duracaoMedia = hoje.duracao_media || 0;
  document.getElementById("duracao-media").textContent =
    Math.round(duracaoMedia) + "s";

  // Custo total
  const custoTotal = hoje.custo_total || 0;
  document.getElementById("custo-total").textContent =
    "R$ " + custoTotal.toFixed(2);
}

// Atualizar listas top
function updateTopLists(data) {
  // Top callers
  const topCallersContainer = document.getElementById("top-callers");
  topCallersContainer.innerHTML = "";

  data.top_callers.forEach((caller, index) => {
    const item = document.createElement("div");
    item.className = "top-item";
    item.innerHTML = `
            <span class="rank">#${index + 1}</span>
            <div class="info">
                <div class="fw-bold">${caller.caller_id}</div>
                <small class="text-muted">${
                  caller.total_chamadas
                } chamadas</small>
            </div>
            <span class="value">${Math.round(
              caller.duracao_total / 60
            )}min</span>
        `;
    topCallersContainer.appendChild(item);
  });

  // Top callees
  const topCalleesContainer = document.getElementById("top-callees");
  topCalleesContainer.innerHTML = "";

  data.top_callees.forEach((callee, index) => {
    const item = document.createElement("div");
    item.className = "top-item";
    item.innerHTML = `
            <span class="rank">#${index + 1}</span>
            <div class="info">
                <div class="fw-bold">${callee.callee_id}</div>
                <small class="text-muted">${
                  callee.total_chamadas
                } chamadas</small>
            </div>
            <span class="value">${callee.total_chamadas}</span>
        `;
    topCalleesContainer.appendChild(item);
  });
}

// Carregar dados dos gráficos
async function loadChartData() {
  try {
    const startDate = document.getElementById("start-date").value;
    const endDate = document.getElementById("end-date").value;

    const response = await fetch(
      `/api/chart-data?start_date=${startDate}&end_date=${endDate}`
    );
    const data = await response.json();

    if (response.ok) {
      createChamadasChart(data.daily_data);
      createProviderChart(data.provider_data);
    } else {
      showError("Erro ao carregar dados dos gráficos: " + data.error);
    }
  } catch (error) {
    showError("Erro de conexão: " + error.message);
  }
}

// Criar gráfico de chamadas
function createChamadasChart(dailyData) {
  const ctx = document.getElementById("chamadasChart").getContext("2d");

  if (chamadasChart) {
    chamadasChart.destroy();
  }

  const labels = dailyData.map((item) => {
    const date = new Date(item.data);
    return date.toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
    });
  });

  const datasets = [
    {
      label: "Total de Chamadas",
      data: dailyData.map((item) => item.total_chamadas),
      borderColor: "#4e73df",
      backgroundColor: "rgba(78, 115, 223, 0.1)",
      tension: 0.4,
      fill: true,
    },
    {
      label: "Chamadas com Sucesso",
      data: dailyData.map((item) => item.chamadas_sucesso),
      borderColor: "#1cc88a",
      backgroundColor: "rgba(28, 200, 138, 0.1)",
      tension: 0.4,
    },
    {
      label: "Chamadas com Erro",
      data: dailyData.map((item) => item.chamadas_erro),
      borderColor: "#e74a3b",
      backgroundColor: "rgba(231, 74, 59, 0.1)",
      tension: 0.4,
    },
  ];

  chamadasChart = new Chart(ctx, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
        },
        tooltip: {
          mode: "index",
          intersect: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return value.toLocaleString("pt-BR");
            },
          },
        },
      },
      interaction: {
        mode: "nearest",
        axis: "x",
        intersect: false,
      },
    },
  });
}

// Criar gráfico de providers
function createProviderChart(providerData) {
  const ctx = document.getElementById("providerChart").getContext("2d");

  if (providerChart) {
    providerChart.destroy();
  }

  const colors = [
    "#4e73df",
    "#1cc88a",
    "#f6c23e",
    "#e74a3b",
    "#36b9cc",
    "#6f42c1",
    "#fd7e14",
    "#20c9a6",
    "#5a5c69",
    "#858796",
  ];

  providerChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: providerData.map((item) => item.rateplan || "N/A"),
      datasets: [
        {
          data: providerData.map((item) => item.total),
          backgroundColor: colors.slice(0, providerData.length),
          borderWidth: 2,
          borderColor: "#fff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            padding: 20,
            usePointStyle: true,
          },
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((context.parsed / total) * 100).toFixed(1);
              return `${context.label}: ${context.parsed.toLocaleString(
                "pt-BR"
              )} (${percentage}%)`;
            },
          },
        },
      },
    },
  });
}

// Carregar insights
async function loadInsights() {
  try {
    const response = await fetch("/api/insights");
    const data = await response.json();

    if (response.ok) {
      showInsights(data);
    } else {
      showError("Erro ao carregar insights: " + data.error);
    }
  } catch (error) {
    showError("Erro de conexão: " + error.message);
  }
}

// Mostrar insights
function showInsights(data) {
  const container = document.getElementById("alertas-container");
  container.innerHTML = "";

  data.alertas.forEach((alerta) => {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${
      alerta.tipo === "erro" ? "danger" : "warning"
    } fade-in`;
    alertDiv.innerHTML = `
            <i class="fas fa-${
              alerta.tipo === "erro" ? "exclamation-triangle" : "info-circle"
            } me-2"></i>
            ${alerta.mensagem}
        `;
    container.appendChild(alertDiv);
  });

  if (data.anomalias.length > 0) {
    const anomaliasDiv = document.createElement("div");
    anomaliasDiv.className = "alert alert-info fade-in";
    anomaliasDiv.innerHTML = `
            <i class="fas fa-chart-line me-2"></i>
            <strong>Anomalias detectadas:</strong><br>
            ${data.anomalias
              .map(
                (a) =>
                  `${a.data}: ${a.tipo} volume (${a.volume} vs média ${a.media})`
              )
              .join("<br>")}
        `;
    container.appendChild(anomaliasDiv);
  }
}

// Carregar tabela de chamadas
async function loadCallsTable(page = 1) {
  try {
    showLoading();
    currentPage = page;

    const startDate = document.getElementById("start-date").value;
    const endDate = document.getElementById("end-date").value;
    const callerId = document.getElementById("caller-filter").value;
    const calleeId = document.getElementById("callee-filter").value;
    const statusCode = document.getElementById("status-filter").value;

    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      caller_id: callerId,
      callee_id: calleeId,
      status_code: statusCode,
      page: page,
    });

    const response = await fetch(`/api/calls-table?${params}`);
    const data = await response.json();

    if (response.ok) {
      updateCallsTable(data);
    } else {
      showError("Erro ao carregar tabela: " + data.error);
    }
  } catch (error) {
    showError("Erro de conexão: " + error.message);
  } finally {
    hideLoading();
  }
}

// Atualizar tabela de chamadas
function updateCallsTable(data) {
  const tbody = document.getElementById("calls-tbody");
  tbody.innerHTML = "";

  data.calls.forEach((call) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${call.id}</td>
            <td>${new Date(call.time).toLocaleString("pt-BR")}</td>
            <td>${call.caller_id || "-"}</td>
            <td>${call.callee_id || "-"}</td>
            <td><span class="status-badge status-${call.status_code}">${
      call.status_code
    }</span></td>
            <td>${
              call.duration ? Math.round(call.duration / 60) + "min" : "-"
            }</td>
            <td>${call.cost ? "R$ " + call.cost.toFixed(2) : "-"}</td>
            <td>${call.service || "-"}</td>
            <td>${call.rateplan || "-"}</td>
        `;
    tbody.appendChild(row);
  });

  // Atualizar paginação
  updatePagination(data);

  // Atualizar contador
  document.getElementById("total-records").textContent =
    data.total.toLocaleString("pt-BR");
}

// Atualizar paginação
function updatePagination(data) {
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";

  const totalPages = data.total_pages;
  const currentPage = data.page;

  // Botão anterior
  const prevLi = document.createElement("li");
  prevLi.className = `page-item ${currentPage === 1 ? "disabled" : ""}`;
  prevLi.innerHTML = `<a class="page-link" href="#" onclick="loadCallsTable(${
    currentPage - 1
  })">Anterior</a>`;
  pagination.appendChild(prevLi);

  // Páginas
  const startPage = Math.max(1, currentPage - 2);
  const endPage = Math.min(totalPages, currentPage + 2);

  for (let i = startPage; i <= endPage; i++) {
    const li = document.createElement("li");
    li.className = `page-item ${i === currentPage ? "active" : ""}`;
    li.innerHTML = `<a class="page-link" href="#" onclick="loadCallsTable(${i})">${i}</a>`;
    pagination.appendChild(li);
  }

  // Botão próximo
  const nextLi = document.createElement("li");
  nextLi.className = `page-item ${
    currentPage === totalPages ? "disabled" : ""
  }`;
  nextLi.innerHTML = `<a class="page-link" href="#" onclick="loadCallsTable(${
    currentPage + 1
  })">Próximo</a>`;
  pagination.appendChild(nextLi);
}

// Mudar período dos gráficos
function changePeriod(days) {
  currentPeriod = days;
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  document.getElementById("start-date").value = startDate
    .toISOString()
    .split("T")[0];
  document.getElementById("end-date").value = endDate
    .toISOString()
    .split("T")[0];

  loadChartData();
  loadCallsTable(1);
}

// Mostrar loading
function showLoading() {
  document.getElementById("loading").style.display = "flex";
}

// Esconder loading
function hideLoading() {
  document.getElementById("loading").style.display = "none";
}

// Mostrar erro
function showError(message) {
  const container = document.getElementById("alertas-container");
  const alertDiv = document.createElement("div");
  alertDiv.className = "alert alert-danger fade-in";
  alertDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
    `;
  container.appendChild(alertDiv);

  // Remover após 5 segundos
  setTimeout(() => {
    alertDiv.remove();
  }, 5000);
}

// Atualizar dashboard a cada 5 minutos
setInterval(() => {
  loadOverview();
  loadInsights();
}, 300000);

// Event listeners para filtros
document
  .getElementById("caller-filter")
  .addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      loadCallsTable(1);
    }
  });

document
  .getElementById("callee-filter")
  .addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      loadCallsTable(1);
    }
  });

// Auto-refresh dos gráficos quando as datas mudam
document.getElementById("start-date").addEventListener("change", function () {
  loadChartData();
});

document.getElementById("end-date").addEventListener("change", function () {
  loadChartData();
});
