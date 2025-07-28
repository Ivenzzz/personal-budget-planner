$(document).ready(function () {
    $('#expensesTable').DataTable({
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'csvHtml5',
                text: 'Export CSV',
                className: 'btn btn-sm btn-success',
                exportOptions: {
                    columns: [0, 1, 2, 3] // Only export Date, Category, Description, Amount
                }
            },
            {
                extend: 'excelHtml5',
                text: 'Export Excel',
                className: 'btn btn-sm btn-primary',
                exportOptions: {
                    columns: [0, 1, 2, 3]
                }
            },
            {
                text: 'Export JSON',
                className: 'btn btn-sm btn-warning',
                action: function (e, dt, button, config) {
                    // Custom JSON export
                    const data = dt.rows({ search: 'applied' }).data().toArray();
                    const filteredData = data.map(row => ({
                        Date: row[0],
                        Category: row[1],
                        Description: row[2],
                        Amount: row[3]
                    }));
                    
                    const jsonString = JSON.stringify(filteredData, null, 2);
                    const blob = new Blob([jsonString], { type: "application/json" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "expenses.json";
                    a.click();
                    URL.revokeObjectURL(url);
                }
            }
        ]
    });
});
