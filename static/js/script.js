// static/js/script.js
document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const query = document.getElementById('queryInput').value;

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("DEBUG: Received data:", data); // PRINT ALL DATA

        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = ''; // Clear previous results

        // --- Display Gemini Review (First) ---
        if (data.gemini_review) {
            const geminiDiv = document.createElement('div');
            geminiDiv.classList.add('gemini-review'); // Add class for styling
            geminiDiv.innerHTML = marked.parse(data.gemini_review); // USE MARKED.PARSE
            resultsDiv.appendChild(geminiDiv);
        }

         // --- Display Travel Info (if available) ---
        if (data.travel_info) {
            const travelDiv = document.createElement('div');
            travelDiv.innerHTML = `<h2>Travel Information</h2>
                                   <p>Distance: ${data.travel_info.distance}</p>
                                   <p>Duration: ${data.travel_info.duration}</p>`;
            resultsDiv.appendChild(travelDiv);
        }

        // --- Display data for each entity ---
        if (data.entities && data.entities.length > 0) {
            data.entities.forEach(entity => {
                console.log("DEBUG: Processing entity:", entity); // PRINT EACH ENTITY
                const entityDiv = document.createElement('div');
                entityDiv.innerHTML = `<h2>${entity.name}</h2>`;

                // --- Google Sentiment Pie Chart ---
                if (entity.google_sentiment) {
					console.log("DEBUG: google sentiment", entity.google_sentiment)
                    const canvas = document.createElement('canvas');
                    canvas.width = 100;  // Reduced width to 100px (50% of 200px)
                    canvas.height = 100; // Reduced height to 100px
                    canvas.id = `google-chart-${entity.name}`; //MUST BE UNIQUE
                    entityDiv.appendChild(canvas);
                    const ctx = canvas.getContext('2d');
                    const myChart = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: Object.keys(entity.google_sentiment),
                            datasets: [{
                                data: Object.values(entity.google_sentiment),
                                backgroundColor: [
                                    'darkgreen',    // Highly Positive - Dark Green
                                    'lightgreen',   // Positive - Light Green
                                    'lightgray',   // Neutral - Light Gray
                                    'lightcoral',  // Negative - Light Red
                                    'darkred'      // Highly Negative - Dark Red
                                ],
                            }]
                        },
                        options: {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Google Reviews Sentiment'
                                },
                                legend: {
                                    labels: {
                                        generateLabels: function(chart) {
                                            const originalLabels = Chart.overrides.pie.plugins.legend.labels.generateLabels(chart);
                                            const colorMap = {
                                                'Highly Positive': 'darkgreen',
                                                'Positive': 'lightgreen',
                                                'Neutral': 'lightgray',
                                                'Negative': 'lightcoral',
                                                'Highly Negative': 'darkred',
                                            };
                                            originalLabels.forEach(label => {
                                                if (colorMap[label.text]) {
                                                    label.fillStyle = colorMap[label.text];
                                                    label.strokeStyle = colorMap[label.text];
                                                }
                                            });
                                            return originalLabels;
                                        }
                                    }
                                }
                            }
                        }
                    });
                }

                // --- Reddit Sentiment Pie Chart ---
                if (entity.reddit_sentiment) {
					console.log("DEBUG: reddit sentiment", entity.reddit_sentiment)
                    const canvas = document.createElement('canvas');
                    canvas.width = 100;  // Reduced width
                    canvas.height = 100; // Reduced height
                    canvas.id = `reddit-chart-${entity.name}`; //MUST BE UNIQUE
                    entityDiv.appendChild(canvas);
                    const ctx = canvas.getContext('2d');
                    const myChart = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: Object.keys(entity.reddit_sentiment),
                            datasets: [{
                                data: Object.values(entity.reddit_sentiment),
                                backgroundColor: [
                                     'darkgreen',    // Highly Positive - Dark Green
                                    'lightgreen',   // Positive - Light Green
                                    'lightgray',   // Neutral - Light Gray
                                    'lightcoral',  // Negative - Light Red
                                    'darkred'      // Highly Negative - Dark Red
                                ],
                            }]
                        },
                         options: {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Reddit Reviews Sentiment'
                                },
                                legend: {
									labels: {
										generateLabels: function(chart) {
											const originalLabels = Chart.overrides.pie.plugins.legend.labels.generateLabels(chart);
											const colorMap = {
												'Highly Positive': 'darkgreen',
												'Positive': 'lightgreen',
												'Neutral': 'lightgray',
												'Negative': 'lightcoral',
												'Highly Negative': 'darkred',
											};

											originalLabels.forEach(label => {
												if (colorMap[label.text]) {
													label.fillStyle = colorMap[label.text];
													label.strokeStyle = colorMap[label.text];
												}
											});
											return originalLabels;
										}
									}
								}
                            }
                        }
                    });
                }


                // Weather
                if (entity.weather) {
                    entityDiv.innerHTML += '<h3>Weekend Weather</h3>';
                    if (entity.weather.Saturday) {
                        entityDiv.innerHTML += `<p>Saturday: ${entity.weather.Saturday.date}, ${entity.weather.Saturday.temperature}°F, ${entity.weather.Saturday.description}</p>`;
                    }
                    if (entity.weather.Sunday) {
                        entityDiv.innerHTML += `<p>Sunday: ${entity.weather.Sunday.date}, ${entity.weather.Sunday.temperature}°F, ${entity.weather.Sunday.description}</p>`;
                    }
                }
                if (entity.positive_summary) {
                    const positiveSummaryDiv = document.createElement('div');
                    positiveSummaryDiv.innerHTML = `<strong>Positive Summary:</strong> ${entity.positive_summary}`;
                    entityDiv.appendChild(positiveSummaryDiv);
                }
                if (entity.negative_summary) {
                    const negativeSummaryDiv = document.createElement('div');
                    negativeSummaryDiv.innerHTML = `<strong>Negative Summary:</strong> ${entity.negative_summary}`;
                    entityDiv.appendChild(negativeSummaryDiv);
        		}
                resultsDiv.appendChild(entityDiv);
            });
        }
        else {
          resultsDiv.textContent = 'Could not identify any places'
        }


        // --- Display Reviews (as a footnote table) ---
        if (data.entities && data.entities.length > 0) {
            const table = document.createElement('table');
            const thead = document.createElement('thead');
            const tbody = document.createElement('tbody');
            thead.innerHTML = `
                <tr>
                    <th>Source</th>
                    <th>Review</th>
                    <th>Entity</th>
                    <th>Sentiment</th>
                </tr>
            `;
            table.appendChild(thead);
            table.appendChild(tbody);
            data.entities.forEach(entity => {
                if (entity.reviews && entity.reviews.length > 0){
                    entity.reviews.forEach(review => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${review.source}</td>
                        <td>${review.text} (Rating: ${review.rating || 'N/A'})</td>
                        <td>${entity.name}</td>
                        <td>${review.sentiment}</td>
                    `;
                    tbody.appendChild(tr);
                });
               }
            });
            resultsDiv.appendChild(table);

        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('results').textContent = `An error occurred: ${error.message}`;
    });
});