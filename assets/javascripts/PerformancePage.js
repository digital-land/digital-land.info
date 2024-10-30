function addDatasetChart() {
  const sql = `
    SELECT
      strftime('%Y-%m', entry_date) AS month_year,
      -- Extract Year-Month from entry_date
      strftime('%Y', entry_date) AS year,
      -- Extract Year
      CASE
        strftime('%m', entry_date)
        WHEN '01' THEN 'January'
        WHEN '02' THEN 'February'
        WHEN '03' THEN 'March'
        WHEN '04' THEN 'April'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'June'
        WHEN '07' THEN 'July'
        WHEN '08' THEN 'August'
        WHEN '09' THEN 'September'
        WHEN '10' THEN 'October'
        WHEN '11' THEN 'November'
        WHEN '12' THEN 'December'
      END AS month,
      -- Convert month number to month name
      COUNT(dataset) AS dataset_count,
      SUM(COUNT(dataset)) OVER (
        ORDER BY
          strftime('%Y-%m', entry_date)
      ) AS cumulative_count
    FROM
      dataset
    WHERE
      collection != ''
    GROUP BY
      month_year
    ORDER BY
      month_year;
  `

  fetch(`https://datasette.planning.data.gov.uk/digital-land.json?sql=${encodeURIComponent(sql)}`)
    .then(res => res.json())
    .then((res) => {
      const data = res.rows.map(row => {
        let formattedRow = {}
        res.columns.forEach((col, index) => formattedRow[col] = row[index])

        return formattedRow
      })

      new Chart(document.getElementById('datasetChart'), {
        data: {
          labels: data.map(d => d.month_year ? `${d.year} - ${d.month}` : "Initial"),
          datasets: [
            {
              type: 'line',
              label: '# of Datasets in total',
              data: data.map(d => d.cumulative_count),
              borderWidth: 2,
              borderColor: "#1d70b8",
              backgroundColor: "#1d70b845",
              fill: true,
              tension: 0.3,
              pointRadius: 0,
            }
          ]
        },
        options: {
          plugins: {
            title: {
              display: true,
              text: 'Cumulative dataset count'
            },
          },
          scales: {
            y: {
              title: {
                display: true,
                text: '# of Datasets'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Total dataset count by month'
              }
            }
          }
        }
      })
    })
    .catch((error) => console.log(error))
}

addDatasetChart()
