document.addEventListener("DOMContentLoaded", function () {
    // ✅ Handle Budget Chart
    fetch("/api/current-monthly-budgets")
        .then(response => response.json())
        .then(data => {
            const titleEl = document.getElementById("budgetMonthYear");
            if (titleEl) {
                const monthYearText = `${new Date(data.year, data.month - 1)
                    .toLocaleString('default', { month: 'long' })} ${data.year}`;
                titleEl.textContent = `Budget for ${monthYearText}`;
            }

            // ✅ Update Summary Card
            const summaryCard = document.getElementById("summaryCard");
            if (summaryCard) {
                summaryCard.innerHTML = `
                <p class="mb-1"><strong>Total Budget:</strong> ₱${data.total_budget.toLocaleString()}</p>
                <p class="mb-1 text-primary"><strong>Consumed:</strong> ₱${data.total_consumed.toLocaleString()}</p>
                <p class="mb-0 text-success"><strong>Remaining:</strong> ₱${data.remaining.toLocaleString()}</p>
            `;
            }

            // ✅ Render Chart
            const labels = data.budgets.map(item => item.category_name);
            const amounts = data.budgets.map(item => item.budget_amount);
            const backgroundColors = data.budgets.map(item => item.color || "#9CA3AF");

            const ctx = document.getElementById("budgetChart").getContext("2d");
            new Chart(ctx, {
                type: "pie",
                data: {
                    labels: labels,
                    datasets: [{
                        data: amounts,
                        backgroundColor: backgroundColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: "bottom" },
                        tooltip: {
                            callbacks: {
                                label: context => `${context.label}: ₱${parseFloat(context.raw).toLocaleString()}`
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error("Error loading budget chart:", error));


    // ✅ Handle Month Picker for Tables
    const monthPicker = document.getElementById("monthPicker");
    const tables = document.querySelectorAll(".budget-table");

    function filterTables() {
        const selectedValue = monthPicker.value; // Format: "YYYY-MM"
        tables.forEach(table => {
            const year = table.getAttribute("data-year");
            const month = String(table.getAttribute("data-month")).padStart(2, "0");
            if (selectedValue === "" || selectedValue === `${year}-${month}`) {
                table.style.display = "block";
            } else {
                table.style.display = "none";
            }
        });
    }

    // Default: Show all tables
    filterTables();

    // Filter on change
    monthPicker.addEventListener("change", filterTables);
});